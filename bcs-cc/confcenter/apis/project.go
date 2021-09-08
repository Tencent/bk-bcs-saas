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
	"bcs-cc/storage/models"
	"bcs-cc/utils"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/mitchellh/mapstructure"
	"github.com/tuvistavie/structomap"
)

// ProjectListInfo : get project list info
func ProjectListInfo(c *gin.Context) {
	data := new(queryProjectParams)
	if err := BindForm(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// split the project id and english name
	idList := strings.Split(data.ProjectIDs, ",")
	englishNameList := strings.Split(data.EnglishNames, ",")
	projectNameList := strings.Split(data.ProjectNames, ",")

	filter := &models.FilterParams{
		ProjectIDList:   idList,
		EnglishNameList: englishNameList,
		ProjectNameList: projectNameList,
		ApprovalStatus:  data.ApprovalStatus,
		Creator:         data.Creator,
		ProjectType:     data.ProjectType,
		IsSecrecy:       data.IsSecrecy,
		IsOfflined:      data.IsOfflined,
		DesireAllData:   data.DesireAllData,
	}
	retData, count, err := filter.ProjectListInfo()
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// 兼容逻辑, 返回带有count数据
	if data.DesireAllData == "0" || data.DesireAllData == "" {
		results := map[string]interface{}{
			"count":   count,
			"results": projectListSLZ(retData),
		}
		utils.OKJSONResponseWithMessage(c, results, "Query success!")
		return
	}

	utils.OKJSONResponseWithMessage(c, projectListSLZ(retData), "Query success!")
}

// ProjectsListEx : get auth project list info by post method
func ProjectsListEx(c *gin.Context) {
	data := new(queryprojectData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	filter := &models.FilterParams{
		ProjectIDList:   data.ProjectIDList,
		EnglishNameList: data.EnglishNameList,
	}
	retData, _, err := filter.ProjectListInfo()
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}

	utils.OKJSONResponseWithMessage(c, projectListSLZ(retData), "Query success!")
}

// CreateProject : create project
func CreateProject(c *gin.Context) {
	data := new(createProjectData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// 兼容处理，如果没有传递ProjectID，则自动生成ProjectID
	if data.ProjectID == "" {
		data.ProjectID = utils.NewUUID()
	}
	// 兼容历史，需要绑定CC业务
	if data.UseBK && data.CCAppID == 0 {
		utils.BadReqJSONResponse(c, errors.New("binding biz is null"))
		return
	}
	// 处理deploy_type
	deployTypeByte, err := json.Marshal(data.DeployTypeList)
	if err != nil {
		utils.BadReqJSONResponse(c, fmt.Errorf("Marshal deploy_type err, %v", err))
		return
	}

	project := &models.Project{ApprovalTime: time.Now(), ApprovalStatus: 2, DeployType: string(deployTypeByte)}
	if err := mapstructure.Decode(data, &project); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}

	if err := project.CreateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	projectInfo := projectSLZ(*project)
	utils.OKJSONResponseWithMessage(c, projectInfo, "create success!")
}

// ProjectInfo :
func ProjectInfo(c *gin.Context) {
	projectID, err := getProjectIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	project := &models.Project{ProjectID: projectID}
	if err := project.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	projectInfo := projectSLZ(*project)
	utils.OKJSONResponseWithMessage(c, projectInfo, "Query success!")
}

// UpdateProject :
func UpdateProject(c *gin.Context) {
	projectID, err := getProjectIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}

	data := new(updateProjectData)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}

	// project must be exist
	project := &models.Project{ProjectID: projectID}
	if err := project.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// project name must be uniq
	if data.Name != "" && project.Name != data.Name {
		project.Name = data.Name
		if err := project.RetriveRecordByProjectName(); err == nil {
			utils.BadReqJSONResponse(c, errors.New("project name must be unique"))
			return
		}
	}
	// deploy_type
	deployTypeByte, err := json.Marshal(data.DeployTypeList)
	if err != nil {
		utils.BadReqJSONResponse(c, fmt.Errorf("Marshal deploy_type error, %v", err))
		return
	}
	project.DeployType = string(deployTypeByte)

	// 当项目下有集群时，不允许更改项目调度类型和绑定的业务ID
	if project.ProjectHasCluster() {
		data.CCAppID = &project.CCAppID
		data.Kind = &project.Kind
	} else {
		if data.CCAppID != nil && *data.CCAppID == 0 {
			data.CCAppID = &project.CCAppID
		}
		if data.Kind != nil && *data.Kind == 0 {
			data.Kind = &project.Kind
		}
	}
	if err := mapstructure.Decode(data, &project); err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	if err := project.UpdateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	projectInfo := projectSLZ(*project)
	utils.OKJSONResponseWithMessage(c, projectInfo, "Query success!")
}

// ProjectsResource : get project resource, include: project info, cluster info and namespace info
func ProjectsResource(c *gin.Context) {
	// get cluster list info by project
	clusters, err := models.ClusterListWithoutRemoved(clusterFilterStataus)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	projectIDList := getProjectIDListByClusters(clusters)
	// get project list info by project id
	projects, err := models.ProjectListWithoutOffline(projectIDList)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// get namespace list info by project
	namespaces, err := models.NamespaceListByProject(projectIDList)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	projectMapCluster := composeProjectCluster(clusters)
	clusterMapNS := composeClusterNS(clusters, namespaces)
	resource := composeData(projects, projectMapCluster, clusterMapNS)

	utils.OKJSONResponseWithMessage(c, resource, "Query resource success")
}

func getProjectIDListByClusters(clusters []models.Cluster) (projectIDList []string) {
	for _, info := range clusters {
		projectIDList = append(projectIDList, info.ProjectID)
	}
	return projectIDList
}

func composeClusterNS(clusters []models.Cluster, namespaces []map[string]interface{}) map[string][]map[string]interface{} {
	clusterMapNS := make(map[string][]map[string]interface{})
	for _, nsInfo := range namespaces {
		clusterID, _ := nsInfo["cluster_id"].(string)
		ns := map[string]interface{}{"id": nsInfo["id"], "name": nsInfo["name"]}
		if _, ok := clusterMapNS[clusterID]; ok {
			clusterMapNS[clusterID] = append(clusterMapNS[clusterID], ns)
		} else {
			clusterMapNS[clusterID] = make([]map[string]interface{}, 0, 1)
			clusterMapNS[clusterID] = append(clusterMapNS[clusterID], ns)
		}
	}
	return clusterMapNS
}

func composeProjectCluster(clusters []models.Cluster) map[string][]map[string]interface{} {
	projectMapCluster := make(map[string][]map[string]interface{})
	for _, cluster := range clusters {
		projectID := cluster.ProjectID
		// public cluster flag
		isPublic := false
		if len(cluster.RelatedProjects) > 0 {
			isPublic = true
		}
		// cluster info
		clusterInfoObj := map[string]interface{}{
			"id":             cluster.ClusterID,
			"name":           cluster.Name,
			"namespace_list": []map[string]interface{}{},
			"is_public":      isPublic,
		}
		if _, ok := projectMapCluster[projectID]; ok {
			projectMapCluster[projectID] = append(projectMapCluster[projectID], clusterInfoObj)
		} else {
			projectMapCluster[projectID] = make([]map[string]interface{}, 0, 1)
			projectMapCluster[projectID] = append(projectMapCluster[projectID], clusterInfoObj)
		}
	}
	return projectMapCluster
}

// compose the final data
func composeData(projects []models.Project, projectMapCluster map[string][]map[string]interface{}, clusterMapNS map[string][]map[string]interface{}) (resource []map[string]interface{}) {
	for _, project := range projects {
		projectID := project.ProjectID
		clusterList, ok := projectMapCluster[projectID]
		if !ok && clusterList == nil {
			continue
		}
		var tempData []map[string]interface{}
		for _, cluster := range clusterList {
			if cluster == nil {
				continue
			}
			clusterID, _ := cluster["id"].(string)
			nsList, ok := clusterMapNS[clusterID]
			if ok && nsList != nil {
				cluster["namespace_list"] = nsList
			}
			tempData = append(tempData, cluster)
		}
		resource = append(resource, map[string]interface{}{
			"id":           projectID,
			"name":         project.Name,
			"code":         project.EnglishName,
			"cluster_list": tempData,
		})
	}
	return resource
}

func composeStructomap() structomap.Serializer {
	serializer := structomap.New().UseSnakeCase().PickAll()
	serializer = serializer.AddFunc("project_name", func(p interface{}) interface{} {
		return p.(models.Project).Name
	}).AddFunc("bg_id", func(p interface{}) interface{} {
		return p.(models.Project).BGID
	}).Pick("CreatedAt", "UpdatedAt", "ID").Omit("Model")
	return serializer
}

func projectSLZ(project models.Project) map[string]interface{} {
	serializer := composeStructomap()
	return serializer.Transform(project)
}

func projectListSLZ(projectList []models.Project) (data []map[string]interface{}) {
	serializer := composeStructomap()
	data, _ = serializer.TransformArray(projectList)
	return data
}
