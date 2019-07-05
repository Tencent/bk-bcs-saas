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
	"fmt"

	"github.com/gin-gonic/gin"
	"github.com/mitchellh/mapstructure"
	"github.com/tuvistavie/structomap"
)

// VersionConfig : query version or snapshot config info
func VersionConfig(c *gin.Context) {
	// check params
	params := new(clusterVersionParams)
	if err := BindForm(c, params); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}

	clusterID := c.Params.ByName("cluster_id")
	// return all cluster snapshot
	if clusterID == nullParam && params.VerID == "" {
		clusterSnapshotData, err := models.AllClusterSnapshotConfig()
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		utils.OKJSONResponse(c, clusterSnapshotData)
		return
	}
	// set the default value
	params.setVersionEnvDefaultValue("prod")
	params.setVersionKindDefaultValue("k8s")
	// return cluster base version
	if clusterID == nullParam {
		baseVersionConfig, err := models.BaseVersionConfig(params.VerID, params.Environment, params.Kind)
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		utils.OKJSONResponse(c, baseVersionConfig)
		return
	}
	versionConf, err := models.ClusterSnapshotConfig(clusterID)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// transform
	serializer := structomap.New().UseSnakeCase().PickAll().AddFunc("configure", func(d interface{}) interface{} {
		return d.(models.ClusterConfigureVersion).Snapshot
	}).Pick("CreatedAt", "UpdatedAt", "ID").Omit("Model", "Snapshot")
	versionConfMap := serializer.Transform(versionConf)
	utils.OKJSONResponse(c, versionConfMap)
}

// CreateClusterBaseVersion : create cluster base version
func CreateClusterBaseVersion(c *gin.Context) {
	// check data
	data := new(createClusterBaseVersionData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// kind must be k8s or mesos
	if !utils.StringInSlice(data.Kind, kindSlice) {
		utils.BadReqJSONResponse(c, fmt.Errorf("params[kind] must be in %v", kindSlice))
		return
	}
	// map to struct
	baseVersion := &models.BaseVersion{}
	if err := mapstructure.Decode(data, &baseVersion); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// create record
	if err := baseVersion.CreateBaseVersion(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, baseVersion)
}

// CreateClusterSnapshot : create
func CreateClusterSnapshot(c *gin.Context) {
	// check data
	data := new(createClusterSnapshotData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// map to struct
	snapshot := &models.ClusterConfigureVersion{}
	if err := mapstructure.Decode(data, &snapshot); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// create record
	if err := snapshot.CreateSnapshot(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, snapshot)
}

// UpdateClusterBaseVersion : update cluster base version
func UpdateClusterBaseVersion(c *gin.Context) {
	// check data
	data := new(updateClusterBaseVersionData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// map to struct
	baseVersion := &models.BaseVersion{}
	if err := mapstructure.Decode(data, &baseVersion); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// update base version
	if err := baseVersion.UpdateBaseVersion(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponseWithMessage(c, nil, "Update cluster base version success")
}
