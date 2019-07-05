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
	"strconv"

	"bcs_cc/storage/models"
	"bcs_cc/utils"

	"github.com/gin-gonic/gin"
	"github.com/mitchellh/mapstructure"
)

// AreaListInfo :
func AreaListInfo(c *gin.Context) {
	data, count, err := models.ListInfo()
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// serialize the area list
	retData, err := models.AreaListSLZ(data)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}

	results := map[string]interface{}{
		"count":   count,
		"results": retData,
	}

	utils.OKJSONResponseWithMessage(c, results, "Query success!")
}

// CreateArea :
func CreateArea(c *gin.Context) {
	data := new(createAreaJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	area := &models.Area{}
	if err := mapstructure.Decode(data, &area); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// Compatible logic, create record when record exist; update record when record exist
	if err := area.CreateOrUpdateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	retData, err := models.AreaSLZ(*area, true)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponseWithMessage(c, retData, "Create success!")
}

// AreaInfo : get area info
func AreaInfo(c *gin.Context) {
	idStr := c.Params.ByName("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}

	area := &models.Area{Model: models.Model{ID: uint(id)}}
	if err := area.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	retData, err := models.AreaSLZ(*area, true)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponseWithMessage(c, retData, "Query success!")
}

// UpdateArea : update area record
func UpdateArea(c *gin.Context) {
	idStr := c.Params.ByName("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	data := new(updateAreaJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}

	area := &models.Area{Model: models.Model{ID: uint(id)}}
	// record exist
	if err := area.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	if err := mapstructure.Decode(data, &area); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// update record
	if err := area.UpdateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	retData, err := models.AreaSLZ(*area, true)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponseWithMessage(c, retData, "Update success!")
}
