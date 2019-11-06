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
	"fmt"

	"bcs_cc/components/auth"
	"bcs_cc/components/bcs"
	"bcs_cc/config"
	"bcs_cc/logging"
	"bcs_cc/storage/models"
)

var (
	clusterNormalStatus = "normal"
	mesosClusterType    = "mesos"
)

func getClusterInfo(projectID string, clusterID string) (clusterList []map[string]string, clusterType string) {
	if clusterID == "" {
		clusterData, err := models.FetchPrivateClusterByProjectID(projectID)
		if err != nil {
			logging.Error("get cluster by project error, %v", err)
			return
		}
		for _, info := range clusterData {
			if info.Status == clusterNormalStatus {
				// 因为项目下只能有一种容器编排类型
				clusterType = info.Type
				clusterList = append(clusterList, map[string]string{
					"cluster_id": info.ClusterID, "env": info.Environment, "type": info.Type})
			}
		}
	} else {
		clusterRecord := models.Cluster{ProjectID: projectID, ClusterID: clusterID}
		if err := clusterRecord.RetriveRecord(); err != nil {
			logging.Error("get cluster by cluster id error, %v", err)
			return
		}
		if clusterRecord.Status == clusterNormalStatus {
			clusterType = clusterRecord.Type
			clusterList = append(clusterList, map[string]string{
				"cluster_id": clusterRecord.ClusterID, "env": clusterRecord.Environment, "type": clusterRecord.Type})
		}
	}

	return clusterList, clusterType
}

func getNormalIPListForMesos(clusterIDList []map[string]string) (normalIPList []string) {
	for _, info := range clusterIDList {
		fmt.Println(info)
	}
}

func getNormalIPListForK8s(clusterIDList []map[string]string) {
	for _, info := range clusterIDList {
		fmt.Println(info)
	}
}

// SyncNodes : sync node info, and add/update node db record
func SyncNodes(projectID string, clusterID string) {
	if !config.GlobalConfigurations.EnableSyncNodes {
		return
	}
	// get access token, in order to request bcs api
	accessToken, err := auth.GetAccessToken()
	if err != nil {
		logging.Error("get access token error, %v", err)
		return
	}
	// compose cluster id list, cluster id maybe not exist
	// when cluster id is not exist, query cluster id from project id
	clusterList, clusterType := getClusterInfo(projectID, clusterID)
	fmt.Println(clusterList, clusterType)
	if len(clusterList) == 0 {
		return
	}
	if clusterType == mesosClusterType {
		ipResource := getNormalIPListForMesos(clusterList)
	} else {

	}
	fmt.Println(bcs.MesosIPResource("BCS-MESOS-10038", "stag", accessToken))
}
