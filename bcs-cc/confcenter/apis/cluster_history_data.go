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
	"time"

	"bcs_cc/storage/models"
	"bcs_cc/utils"

	"github.com/gin-gonic/gin"
)

// ClusterHistoryData : get cluster history data
func ClusterHistoryData(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// validate params
	data := new(queryClusterHistoryParams)
	if err := BindForm(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	startAt, err := parseLocalTime(c.Query("start_at"))
	if err != nil {
		utils.BadReqJSONResponse(c, errors.New("start_at format error"), err)
		return
	}
	endAt, err := parseLocalTime(c.Query("end_at"))
	if err != nil {
		utils.BadReqJSONResponse(c, errors.New("end_at format error"), err)
		return
	}
	if endAt.Sub(startAt) < time.Hour*0 || endAt.Sub(startAt) > time.Hour*24*31 {
		utils.BadReqJSONResponse(c, errors.New("start_at must less end_at"))
		return
	}
	// check cluster id exist
	cluster := &models.Cluster{ClusterID: clusterID, ProjectID: projectID}
	if err := cluster.RetriveRecordByProjectIDClusterID(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}

	// get history data
	filter := &models.ClusterHistoryDataFilter{ClusterID: clusterID, StartAt: startAt, EndAt: endAt}
	historyData, err := filter.RetriveRecord()
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}

	utils.OKJSONResponse(c, map[string]interface{}{"count": len(historyData), "results": historyData})
}

func parseLocalTime(param string) (time.Time, error) {
	localTime, err := time.ParseInLocation("2006-01-02 15:04:05", param, time.Local)
	if err != nil {
		return time.Time{}, err
	}
	return localTime, nil
}
