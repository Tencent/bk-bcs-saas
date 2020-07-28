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
	"bcs_cc/logging"
	"bcs_cc/storage/models"
	"errors"
	"strings"

	"github.com/gin-gonic/gin"
)

// getProjectIDFromContext : get project id from context
func getProjectIDFromContext(c *gin.Context) (projectID string, err error) {
	projectID = c.Params.ByName("project_id")
	if projectID == "" {
		return "", errors.New("param[project_id] and [project_code] are null")
	}
	appCode, _ := getAppCodeFromContext(c)
	if appCode == skipAppCode {
		return projectID, nil
	}
	// Firstly，assert the value of project code is projectID
	project := &models.Project{EnglishName: projectID}
	if err := project.RetriveRecordByProjectCode(); err != nil {
		return projectID, nil
	}
	return project.ProjectID, nil
}

// get project id and cluster id
func getProjectIDClusterIDFromContext(c *gin.Context) (projectID string, clusterID string, err error) {
	projectID, err = getProjectIDFromContext(c)
	clusterID = c.Params.ByName("cluster_id")
	if err != nil {
		return "", clusterID, err
	}
	if clusterID == nullParam {
		clusterID = c.Query("cluster_id")
	}
	return projectID, clusterID, nil
}

// getAppCodeFromContext : get project code from context
func getAppCodeFromContext(c *gin.Context) (appCode string, err error) {
	appCode = c.GetString("AppCode")
	if appCode == "" {
		return "", errors.New("param[app_code] is null")
	}
	return appCode, nil
}

// getUsernameFromContext : get username from context
func getUsernameFromContext(c *gin.Context) (username string, err error) {
	username = c.GetString("Username")
	if username == "" {
		return "", errors.New("username is null")
	}
	return username, nil
}

// GetPojectFromAuthData : get the project id/code from auth response data
func GetPojectFromAuthData(respData interface{}) (data []string, err error) {
	switch respData := respData.(type) {
	case []interface{}:
		for _, val := range respData {
			switch assertVal := val.(type) {
			case string:
				valList := strings.Split(assertVal, ":")
				if len(valList) < 2 {
					logging.Error("auth project format error, data is %v", assertVal)
					return nil, errors.New("project of auth project format error")
				}
				data = append(data, valList[1])
			case map[string]interface{}:
				projectID, _ := assertVal["project_id"].(string)
				data = append(data, projectID)
			}
		}
		return data, nil
	default:
		return nil, errors.New("project of auth response format is unknow")
	}
}

// 转换集群类型
// 兼容k8s，转换k8s到bcs-k8s
func convertClusterType(clusterType string) string {
	// TODO: 是否枚举所有类型，严格限制下类型
	if clusterType == "k8s" {
		return "bcs-k8s"
	}
	return clusterType
}
