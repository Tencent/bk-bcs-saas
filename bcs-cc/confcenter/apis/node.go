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

package apis

import (
	"errors"
	"strings"

	"bcs_cc/confcenter/tasks"
	"bcs_cc/config"
	"bcs_cc/logging"
	"bcs_cc/storage/models"
	"bcs_cc/utils"

	"github.com/gin-gonic/gin"
	"github.com/mitchellh/mapstructure"
)

// NodeList : Node list info
func NodeList(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// params for query cluster
	data := new(nodeListParamsForm)
	if err := BindForm(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	data.setDefaultLimit()
	// transfer the inner ip
	filter := models.NodeFilterData{
		ProjectID:     projectID,
		ClusterID:     clusterID,
		InnerIPList:   strings.Split(data.InnerIPS, ","),
		Limit:         data.Limit,
		Offset:        data.Offset,
		ExcludeStatus: nodeFilterStatus,
		DesireAllData: data.DesireAllData,
	}
	nodeList, count, err := filter.NodeList()
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// add a task, search online nodes of cluster by bcs api, and add/update node record
	if config.GlobalConfigurations.EnableSyncNodes {
		go tasks.SyncNodes(projectID, clusterID)
	}

	utils.OKJSONResponse(c, map[string]interface{}{"count": count, "results": nodeList})
}

// NodeInfo : get single node info
func NodeInfo(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	if clusterID == nullParam {
		clusterID = c.Query("cluster_id")
	}
	nodeIDStr := c.Params.ByName("node_id")
	nodeIDInt, err := utils.String2Int(nodeIDStr)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// get cluster id list
	clusterIDList, err := models.GetClusterIDListByNode(projectID, []string{clusterID})
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// check node exist in cluster
	if !models.VerifyNodeExist(clusterIDList, []uint{uint(nodeIDInt)}) {
		utils.DBErrorResponse(c, errors.New("Node and cluster are not matched"))
		return
	}
	node := &models.Node{Model: models.Model{ID: uint(nodeIDInt)}}
	if err := node.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, node)
}

// CreateNode : create one node
// Note:
func CreateNode(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// params for query cluster
	data := new(nodeCreateDataJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// check cluster exist
	if err := models.ValidateProjectCluster(projectID, clusterID); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// save node info
	node := &models.Node{ProjectID: projectID, ClusterID: clusterID, Status: nodeInitializingStatus}
	if err := mapstructure.Decode(data, &node); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}

	if err := node.CreateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, node)
}

// BatchOperateNodes : create many node record
func BatchOperateNodes(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// params for query cluster
	data := new(nodeBatchOperateDataJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// check cluster exist
	if projectID != "null" {
		if err := models.ValidateProjectCluster(projectID, clusterID); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	}
	// split create or update
	createNodeList := data.Creates
	updateNodeList := data.Updates
	var nodeListInfo []models.Node
	if len(createNodeList) > 0 {
		nodeListInfo, err = batchCreateRecord(projectID, clusterID, createNodeList)
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	} else {
		nodeListInfo, err = batchUpdateRecord(projectID, clusterID, updateNodeList)
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	}

	utils.OKJSONResponse(c, nodeListInfo)
}

// UpdateNode : update single node info
func UpdateNode(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	if clusterID == "" {
		clusterID = c.Query("cluster_id")
	}
	// params for query cluster
	data := new(nodeUpdateDataByID)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// get cluster id list
	clusterIDList, err := models.GetClusterIDListByNode(projectID, []string{clusterID})
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	nodeIDInt, err := utils.String2Int(c.Params.ByName("node_id"))
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// check node exist in cluster
	if !models.VerifyNodeExist(clusterIDList, []uint{uint(nodeIDInt)}) {
		utils.DBErrorResponse(c, errors.New("Node and cluster are not matched"))
		return
	}

	node := &models.Node{Model: models.Model{ID: uint(nodeIDInt)}}
	if err := mapstructure.Decode(data, &node); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	if err := node.UpdateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, node)
}

func batchCreateRecord(projectID string, clusterID string, createNodeList []nodeCreateDataJSON) ([]models.Node, error) {
	var nodeList []models.Node
	for _, info := range createNodeList {
		node := &models.Node{ProjectID: projectID, ClusterID: clusterID, Status: nodeInitializingStatus}
		if err := mapstructure.Decode(info, &node); err != nil {
			return nil, err
		}
		nodeList = append(nodeList, *node)
	}
	return models.BatchCreateRecord(nodeList)
}

// batch update node info
func batchUpdateRecord(projectID string, clusterID string, updateNodeList []nodeUpdateDataJSON) ([]models.Node, error) {
	var nodeList []models.Node
	for _, info := range updateNodeList {
		node := &models.Node{ProjectID: projectID, ClusterID: clusterID}
		if err := mapstructure.Decode(info, &node); err != nil {
			return nil, err
		}
		nodeList = append(nodeList, *node)
	}
	return models.BatchUpdateRecord(nodeList, nodeFilterStatus)
}

// UpdateNodeList : update node list
func UpdateNodeList(c *gin.Context) {
	// get project id from context
	projectID, err := getProjectIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// params for query cluster
	data := new(nodeListUpdateDataJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	var clusterIDList []string
	for _, node := range data.Updates {
		clusterIDList = append(clusterIDList, node.ClusterID)
	}
	// check cluster exist
	if !checkClusterInProject(projectID, clusterIDList) {
		utils.BadReqJSONResponse(c, errors.New("project and cluster not match"))
		return
	}
	// update records
	if _, err := batchUpdateRecordWithClusterID(projectID, data.Updates); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, "update success")
}

// GetAllNodeList : get the entire node info
func GetAllNodeList(c *gin.Context) {
	clusterType := c.DefaultQuery("mesos_k8s", "k8s")
	desireAllData := c.Query("desire_all_data")
	// cluster id list for node
	clusterIDList := []string{}
	// filter with cluster type, cluster type is empty when the scene of searching all
	if desireAllData != "1" {
		clusterList, err := models.ClusterList(clusterType, clusterStatusSlice)
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}

		for _, clusterInfo := range clusterList {
			clusterIDList = append(clusterIDList, clusterInfo.ClusterID)
		}
	}

	// search node list
	data, err := models.NodeListByCluster(clusterIDList, nodeFilterStatus)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, data)
}

// check cluster in project
// Note: remove the duplidated element
func checkClusterInProject(projectID string, clusterIDList []string) bool {
	clusterIDList = removeDuplicateElement(clusterIDList)
	// real searched cluster id list
	realClusterIDList, err := models.GetClusterIDListByNode(projectID, clusterIDList)
	if err != nil {
		logging.Error("get cluster list error, detail: %v", err)
		return false
	}
	if len(realClusterIDList) == len(clusterIDList) {
		return true
	}
	return false
}

// componse batch update record with cluster id
func batchUpdateRecordWithClusterID(projectID string, updateNodeList []updateNodeParams) ([]models.Node, error) {
	var nodeList []models.Node
	for _, info := range updateNodeList {
		node := models.Node{
			ProjectID:   projectID,
			ClusterID:   info.ClusterID,
			InnerIP:     info.InnerIP,
			Description: info.Description,
			Status:      info.Status,
		}
		nodeList = append(nodeList, node)
	}
	return models.BatchUpdateRecord(nodeList, []string{})
}

// remove duplicated elem
func removeDuplicateElement(addrs []string) []string {
	result := make([]string, 0, len(addrs))
	temp := map[string]struct{}{}
	for _, item := range addrs {
		if _, ok := temp[item]; !ok {
			temp[item] = struct{}{}
			result = append(result, item)
		}
	}
	return result
}
