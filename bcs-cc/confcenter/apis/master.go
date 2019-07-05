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
	"bcs_cc/storage/models"
	"bcs_cc/utils"

	"github.com/gin-gonic/gin"
	"github.com/mitchellh/mapstructure"
)

// MasterListByType : fetch master list, support cluster type(mesos/k8s)
func MasterListByType(c *gin.Context) {
	// default cluster type is k8s
	clusterType := c.DefaultQuery("mesos_k8s", "k8s")
	desireAllData := c.Query("desire_all_data")
	// filterWithClusterID mean filter with cluster id
	clusterIDList, filterWithClusterID := []string{}, false
	// filter with cluster type
	if desireAllData != "1" {
		clusterList, err := models.ClusterList(clusterType, clusterStatusSlice)
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		for _, clusterInfo := range clusterList {
			clusterIDList = append(clusterIDList, clusterInfo.ClusterID)
		}
		filterWithClusterID = true
	}
	// return master info
	masterList, err := models.MasterList(clusterIDList, filterWithClusterID)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, masterList)
}

// FetchMasterList :
func FetchMasterList(c *gin.Context) {
	projectID, err := getProjectIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// fetch params by url
	clusterID := c.Params.ByName("cluster_id")
	innerIP := c.Query("inner_ip")
	// filter params
	filter := models.MasterFilter{ClusterID: clusterID, InnerIP: innerIP}
	// get the public list
	if clusterID != nullParam {
		publicClusterIDList, err := models.FetchPublicClusterIDList(projectID)
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		if utils.StringInSlice(clusterID, publicClusterIDList) {
			filter.ProjectID = projectID
		}
	}

	masterList, count, err := filter.MasterDetailListWithCount()
	if err != nil {
		utils.DBErrorResponse(c, err)
	}

	utils.OKJSONResponse(c, map[string]interface{}{"count": count, "results": masterList})
}

// CreateMaster : create single master
func CreateMaster(c *gin.Context) {
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// get create cluster data
	data := new(createMasterData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	masterInfo := &models.ManagerMaster{ProjectID: projectID, ClusterID: clusterID}
	if err := mapstructure.Decode(data, &masterInfo); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	if err := masterInfo.CreateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, masterInfo)
}

// UpdateMaster : update a sigle master
func UpdateMaster(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// get update cluster data
	data := new(updateMasterData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// update record
	masterInfo := &models.ManagerMaster{ProjectID: projectID, ClusterID: clusterID}
	if err := mapstructure.Decode(data, &masterInfo); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	if err := masterInfo.UpdateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, masterInfo)
}

// ReplaceMaster : delete existed master ip, and add new ips
func ReplaceMaster(c *gin.Context) {
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// get params
	data := new(replaceMasterParams)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// check replace ip list exist
	if err := models.CheckInnerIPList(data.ReplaceInnerIPList, true); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// check new ip not exist
	newInnerIPList := composeInnerIPList(data.NewIPListInfo)
	if err := models.CheckInnerIPList(newInnerIPList, false); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// start replace
	batchMasterInfo, err := composeMasterInfo(projectID, clusterID, data.NewIPListInfo)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	if err := models.ReplaceMaster(data.ReplaceInnerIPList, batchMasterInfo); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponseWithMessage(c, nil, "replace master success")
}

// BatchCreateMaster : create master record by request data
func BatchCreateMaster(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// many master data
	data := new(batchCreateMasterData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// compose master model params
	batchMasterInfo, err := composeMasterInfo(projectID, clusterID, data.NewInnerIPList)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// batch insert record
	if err := models.BatchCreateMasterRecords(batchMasterInfo); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponseWithMessage(c, nil, "create success")
}

func composeMasterInfo(projectID string, clusterID string, masterListInfo []createMasterData) (batchMasterInfo []models.ManagerMaster, err error) {
	for _, info := range masterListInfo {
		// single master info
		masterInfo := &models.ManagerMaster{ProjectID: projectID, ClusterID: clusterID}
		if err := mapstructure.Decode(info, &masterInfo); err != nil {
			return nil, err
		}
		if masterInfo.Status == "" {
			masterInfo.Status = defaultMasterStatus
		}
		batchMasterInfo = append(batchMasterInfo, *masterInfo)
	}
	return batchMasterInfo, nil
}

func composeInnerIPList(masterData []createMasterData) (innerIPList []string) {
	for _, data := range masterData {
		innerIPList = append(innerIPList, data.InnerIP)
	}
	return innerIPList
}
