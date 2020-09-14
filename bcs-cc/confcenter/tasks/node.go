/*
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

package tasks

import (
	"bcs_cc/components/auth"
	"bcs_cc/components/bcs"
	"bcs_cc/logging"
	"bcs_cc/storage/models"
	"bcs_cc/utils"

	set "gopkg.in/fatih/set.v0"
)

var (
	normalStatus     = utils.Normal
	mesosClusterType = "mesos"
	bcsEnv           = map[string]string{
		"stag":  "uat",
		"debug": "debug",
		"prod":  "prod",
	}
)

type nodeParams struct {
	projectID    string
	clusterID    string
	ipResource   []map[string]string
	ipStatusList []map[string]string
	creator      string
	ipSet        set.Interface
}

func getClusterInfo(projectID string, clusterID string) ([]map[string]string, string, string) {
	var (
		clusterList []map[string]string
		clusterType string
		creator     string
	)
	if clusterID == "" {
		clusterData, err := models.FetchPrivateClusterByProjectID(projectID)
		if err != nil {
			logging.Error("get cluster by project error, %v", err)
			return nil, "", ""
		}
		for _, info := range clusterData {
			if info.Status == normalStatus {
				// 因为项目下只能有一种容器编排类型, 且集群创建者唯一
				// 获取集群创建者，以便于在添加节点时，使用集群创建者作为节点创建者
				clusterType = info.Type
				creator = info.Creator
				clusterList = append(clusterList, map[string]string{
					"cluster_id": info.ClusterID,
					"env":        info.Environment,
					"type":       info.Type,
					"state":      info.State,
				})
			}
		}
	} else {
		clusterRecord := models.Cluster{ProjectID: projectID, ClusterID: clusterID}
		if err := clusterRecord.RetriveRecord(); err != nil {
			logging.Error("get cluster by cluster id error, %v", err)
			return nil, "", ""
		}
		if clusterRecord.Status == normalStatus {
			clusterType = clusterRecord.Type
			creator = clusterRecord.Creator
			clusterList = append(clusterList, map[string]string{
				"cluster_id": clusterRecord.ClusterID,
				"env":        clusterRecord.Environment,
				"type":       clusterRecord.Type,
				"state":      clusterRecord.State,
			})
		}
	}

	return clusterList, clusterType, creator
}

// get node ip list in cluster, in order to diff online node records
func getNodeIPList(clusterID string) ([]map[string]string, set.Interface, error) {
	// query nodes of cluster
	var ipStatusList []map[string]string // format: [{"ip": "xxx", "status": "xxx"}]
	ipSet := set.New(set.ThreadSafe)
	filter := models.NodeFilterData{
		ClusterID:     clusterID,
		DesireAllData: "1", // 获取所有节点
	}
	nodeList, _, err := filter.NodeList()
	if err != nil {
		return nil, ipSet, err
	}
	for _, info := range nodeList {
		ipStatusList = append(ipStatusList, map[string]string{"ip": info.InnerIP, "status": info.Status})
		ipSet.Add(info.InnerIP)
	}
	return ipStatusList, ipSet, nil
}

func handleNodes(params nodeParams) error {
	var (
		updateNodeList []models.Node
		addNodeList    []models.Node
	)
	// 创建set，便于后续处理属于db，并且线上不存在的记录
	clusterIPSet := set.New(set.ThreadSafe)
	for _, info := range params.ipResource {
		node := models.Node{
			InnerIP:   info["ip"],
			Status:    info["status"],
			ProjectID: params.projectID,
			ClusterID: params.clusterID,
		}
		clusterIPSet.Add(info["ip"])
		// 为了减少db的操作，获取需要更新的操作
		existFlag := false
		for _, ipStatus := range params.ipStatusList {
			if info["ip"] != ipStatus["ip"] {
				continue
			}
			existFlag = true
			// 如果线上和db记录都处于停止调度状态，则不进行更新
			if info["status"] == utils.ToRemoved && utils.StringInSlice(
				ipStatus["status"], []string{utils.ToRemoved, utils.Removeable}) {
				break
			}
			if info["status"] != ipStatus["status"] {
				updateNodeList = append(updateNodeList, node)
			}
		}
		if !existFlag {
			node.Creator = params.creator
			addNodeList = append(addNodeList, node)
		}
	}
	// 更新db中存在，线上不存在的node，更新为not_ready状态，然后允许用户使用`异常删除`操作
	notReadyIPSet := set.Difference(params.ipSet, clusterIPSet)
	for _, ip := range notReadyIPSet.List() {
		ipStr, _ := ip.(string)
		node := models.Node{
			InnerIP:   ipStr,
			Status:    utils.NotReady,
			ProjectID: params.projectID,
			ClusterID: params.clusterID,
			Creator:   params.creator,
		}
		updateNodeList = append(updateNodeList, node)
	}

	var err error
	if len(updateNodeList) > 0 {
		_, err = models.BatchUpdateRecord(updateNodeList, []string{})
	}
	if len(addNodeList) > 0 {
		_, err = models.BatchCreateRecord(addNodeList)
	}
	return err
}

func handleMesosNodes(projectID string, clusterList []map[string]string, accessToken string, creator string) error {
	// query and update by cluster id
	for _, info := range clusterList {
		ipStatusList, ipSet, err := getNodeIPList(info["cluster_id"])
		if err != nil {
			return err
		}
		ipResource, err := bcs.MesosIPResource(info["cluster_id"], bcsEnv[info["env"]], accessToken)
		if err != nil {
			return err
		}
		mesosNodeParams := nodeParams{
			projectID:    projectID,
			clusterID:    info["cluster_id"],
			ipResource:   ipResource,
			ipStatusList: ipStatusList,
			creator:      creator,
			ipSet:        ipSet,
		}
		if err := handleNodes(mesosNodeParams); err != nil {
			return err
		}
	}
	return nil
}

func handleK8sNodes(projectID string, clusterList []map[string]string, accessToken string, creator string) error {
	for _, info := range clusterList {
		ipStatusList, ipSet, err := getNodeIPList(info["cluster_id"])
		if err != nil {
			return err
		}
		ipResource, err := bcs.K8sIPResource(
			projectID, info["cluster_id"], bcsEnv[info["env"]], accessToken, info["clusterState"],
		)
		if err != nil {
			return err
		}
		k8sNodeParams := nodeParams{
			projectID:    projectID,
			clusterID:    info["cluster_id"],
			ipResource:   ipResource,
			ipStatusList: ipStatusList,
			creator:      creator,
			ipSet:        ipSet,
		}
		if err := handleNodes(k8sNodeParams); err != nil {
			return err
		}
	}

	return nil
}

// SyncNodes : sync node info, and add/update node db record
func SyncNodes(projectID string, clusterID string) {
	defer func() {
		if err := recover(); err != nil {
			logging.Error("recovered from error, %v", err)
		}
	}()
	logging.Info("sync node task started")
	// get access token, in order to request bcs api
	accessToken, err := auth.GetAccessToken()
	if err != nil {
		logging.Error("get access token error, %v", err)
		return
	}
	// compose cluster id list, cluster id maybe not exist
	// when cluster id is not exist, query cluster id from project id
	clusterList, clusterType, creator := getClusterInfo(projectID, clusterID)
	if len(clusterList) == 0 {
		return
	}
	if clusterType == mesosClusterType {
		// TODO: handleMesosNodes? updateAddMesosNodes?
		if err := handleMesosNodes(projectID, clusterList, accessToken, creator); err != nil {
			logging.Error("add or update mesos node error, %v", err)
			return
		}
	} else {
		if err := handleK8sNodes(projectID, clusterList, accessToken, creator); err != nil {
			logging.Error("add or update k8s node error, %v", err)
			return
		}
	}
	return
}
