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
	"bcs_cc/config"
	"bcs_cc/storage/models"
	"bcs_cc/utils"
	"errors"
	"fmt"
	"math"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/mitchellh/mapstructure"
	"github.com/tuvistavie/structomap"
)

// GetClusterByIP :
func GetClusterByIP(c *gin.Context) {
	innerIP := c.Params.ByName("ip")
	if innerIP == "" || innerIP == nullParam {
		utils.BadReqJSONResponse(c, errors.New("params[ip] is null"))
		return
	}
	// get the cluster id by ip
	master := &models.ManagerMaster{InnerIP: innerIP}
	if err := master.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// get the cluster detail info
	cluster := &models.Cluster{ClusterID: master.ClusterID}
	if err := cluster.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// compatible with previous logic
	utils.OKJSONResponse(c, map[string]interface{}{"cluster": cluster})
}

// ClusterList : list the cluster info
func ClusterList(c *gin.Context) {
	// get project id from context
	projectID, err := getProjectIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}

	// params for query cluster
	data := new(clusterListParamsForm)
	if err := BindForm(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	// set the default value
	data.setDefaultLimit()

	filter := &models.ClusterFilterParams{
		ProjectID:     projectID,
		InnerIP:       data.InnerIP,
		Name:          data.Name,
		DesireAllData: data.DesireAllData,
		Limit:         data.Limit,
		Offset:        data.Offset,
	}

	clusterList, count, err := filter.ClusterListInfo()
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, map[string]interface{}{"count": count, "results": clusterList})
}

// ClusterInfo : fetch cluster info
func ClusterInfo(c *gin.Context) {
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}

	// get cluster by project id and cluster id
	cluster := models.Cluster{ProjectID: projectID, ClusterID: clusterID}
	if err := cluster.RetriveRecordByProjectIDClusterID(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, cluster)
}

// ClusterAreaInfo : get area info from cluster
func ClusterAreaInfo(c *gin.Context) {
	projectID, clusterID, _ := getProjectIDClusterIDFromContext(c)
	// get cluster info
	// get cluster by project id and cluster id
	cluster := models.Cluster{ProjectID: projectID, ClusterID: clusterID}
	if err := cluster.RetriveRecordByProjectIDClusterID(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	envType := cluster.Environment
	// get zk configure
	zkConf := &models.ZookeeperConfig{Environment: envType}
	if err := zkConf.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	zkConfInfoArray := strings.Split(zkConf.Zookeeper, ";")
	// get area info
	areaInfo := &models.Area{Model: models.Model{ID: uint(cluster.AreaID)}}
	if err := areaInfo.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	areaConfig, err := models.AreaSLZ(*areaInfo, false)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// replace the zhHost info, and assign to area configure
	configureInfo, _ := areaConfig["configuration"].(map[string]interface{})
	configureInfo["zkHosts"] = zkConfInfoArray
	areaConfig["configuration"] = configureInfo
	utils.OKJSONResponse(c, areaConfig)
}

// ClustersListEx : list the cluster info by post method
func ClustersListEx(c *gin.Context) {
	// cluster id list params
	data := new(clusterListDataJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	searchProject := c.Query("search_project")
	var (
		projectID string
		err       error
	)
	if utils.StringInSlice(searchProject, []string{"", "0"}) {
		projectID, err = getProjectIDFromContext(c)
		if err != nil {
			utils.BadReqJSONResponse(c, err)
			return
		}
	}
	// get cluster info
	filter := &models.ClusterFilterParams{ProjectID: projectID, ClusterIDList: data.ClusterIDList}
	clusterList, err := filter.ClusterListByID()
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// return cluster info
	if searchProject != "1" {
		utils.OKJSONResponse(c, clusterList)
		return
	}
	// return cluster info with project cc app id and project code
	projectIDList := getProjectIDList(clusterList)
	projectFilter := models.FilterParams{ProjectIDList: projectIDList}
	projectList, err := projectFilter.ProjectInfoByID()
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	clusterMapList, err := composeClusterWithProject(clusterList, projectList)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, clusterMapList)
}

// GetAllClusterList : get platform all cluster info
// Note: add limit source
func GetAllClusterList(c *gin.Context) {
	clusterList, err := models.ClusterWithoutRemoved(clusterFilterStataus)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, clusterList)
}

// CreateCluster : create cluster
func CreateCluster(c *gin.Context) {
	// get project id
	projectID, err := getProjectIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// cluster id list params
	data := new(createClusterDataJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	data.NotNeedNAT = !data.NeedNAT
	data.ProjectID = projectID
	projectInfo, err := getProjectInfo(projectID)
	err = verifyAreaExist(data.AreaID)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	clusterType, ok := clusterTypeMap[projectInfo.Kind]
	if !ok {
		utils.BadReqJSONResponse(c, errors.New("cluster type must be k8s or mesos"))
		return
	}
	data.Type = clusterType
	if !utils.StringInSlice(data.Environment, config.GlobalConfigurations.AvailableEnvironmentFlags) {
		utils.BadReqJSONResponse(c, errors.New("params[environment] is illegal"))
		return
	}
	// generate cluste num and cluster id
	clusterID, clusterNum, err := generateClusterIDNum(data)
	if err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	data.ClusterID = clusterID
	data.ClusterNum = clusterNum
	// create cluster record
	cluster, masterList, err := getClusterAndMaster(data)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	if err := cluster.CreateRecordWithMaster(masterList); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, cluster)
}

// UpdateCluster : update cluster field
func UpdateCluster(c *gin.Context) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// cluster id list params
	data := new(models.UpdateClusterDataJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	data.ProjectID, data.ClusterID = projectID, clusterID
	if err := data.UpdateRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}

	cluster := &models.Cluster{ProjectID: projectID, ClusterID: clusterID}
	if err := cluster.RetriveRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// update history data
	if data.CapacityUpdatedAt != "" {
		historyData := &models.ClusterHistoryData{}
		if err := mapstructure.Decode(cluster, &historyData); err == nil {
			historyData.CreateRecord()
		}
	}

	utils.OKJSONResponse(c, cluster)
}

// DeleteCluster : delete cluster and related master info
// NOTE: if cluster is not exist, assert this cluster is deleted
func DeleteCluster(c *gin.Context) {
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	cluster := &models.Cluster{ClusterID: clusterID, ProjectID: projectID}
	if err := cluster.DeleteRecord(); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	utils.OKJSONResponse(c, nil)
}

func getProjectInfo(projectID string) (*models.Project, error) {
	project := &models.Project{ProjectID: projectID}
	if err := project.RetriveRecord(); err != nil {
		return project, err
	}
	return project, nil
}

func verifyAreaExist(areaID int) error {
	// check area exist
	area := &models.Area{Model: models.Model{ID: uint(areaID)}}
	if err := area.RetriveRecord(); err != nil {
		return err
	}
	return nil
}

func getProjectIDList(clusterList []models.Cluster) (projectIDList []string) {
	for _, cluster := range clusterList {
		projectIDList = append(projectIDList, cluster.ProjectID)
	}
	return projectIDList
}

func composeClusterWithProject(clusterList []models.Cluster, projectList []models.Project) ([]map[string]interface{}, error) {
	projectIDMap := map[string]map[string]string{}
	for _, info := range projectList {
		projectIDMap[info.ProjectID] = map[string]string{
			"english_name": info.EnglishName,
			"cc_app_id":    fmt.Sprintf("%d", info.CCAppID),
			"project_name": info.Name,
		}
	}
	serializer := structomap.New().UseSnakeCase().PickAll()
	serializer = serializer.Pick("CreatedAt", "UpdatedAt", "ID").Omit("Model")
	clusterMapList, err := serializer.TransformArray(clusterList)
	if err != nil {
		return nil, err
	}
	for _, info := range clusterMapList {
		projectID, _ := info["project_id"].(string)
		projectInfo, ok := projectIDMap[projectID]
		if !ok {
			continue
		}
		info["english_name"] = projectInfo["english_name"]
		info["cc_app_id"] = projectInfo["cc_app_id"]
		info["project_name"] = projectInfo["project_name"]
	}
	return clusterMapList, nil
}

func generateClusterIDNum(data *createClusterDataJSON) (clusterID string, clusterNum int, err error) {
	clusterENV := data.Environment
	// for develop
	if config.GlobalConfigurations.RunENV == develop {
		clusterENV = stagClusterENV
	}

	// note: cluster env not change
	clusterNum, err = models.GetMaxClusterNum(data.Type, data.Environment)
	if err != nil {
		return "", 0, err
	}
	envTypeStart := clusterIDRange[fmt.Sprintf("%v-%v", data.Type, clusterENV)]
	clusterNum = int(math.Max(float64(clusterNum), float64(envTypeStart[0])))
	clusterID = fmt.Sprintf("BCS-%v-%v", strings.ToUpper(data.Type), clusterNum)
	return clusterID, clusterNum, nil
}

func getMasterList(data *createClusterDataJSON) (masterList []models.ManagerMaster, err error) {
	master := models.ManagerMaster{}
	for _, info := range data.MasterIPs {
		if err := mapstructure.Decode(info, &master); err != nil {
			return nil, err
		}
		master.Status = defaultMasterStatus
		masterList = append(masterList, master)
	}
	return masterList, nil
}

func getClusterAndMaster(data *createClusterDataJSON) (*models.Cluster, []models.ManagerMaster, error) {
	cluster := &models.Cluster{}
	if err := mapstructure.Decode(data, &cluster); err != nil {
		return nil, nil, err
	}
	cluster.Status = defaultMasterStatus
	masterList, err := getMasterList(data)
	if err != nil {
		return nil, nil, err
	}
	return cluster, masterList, nil
}
