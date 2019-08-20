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
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gin-gonic/gin/binding"
	"gopkg.in/go-playground/validator.v8"
)

// Pagination :
/* Pagination : pagination start */
type Pagination struct {
	Limit  int `form:"limit"`
	Offset int `form:"offset"`
}

func (p *Pagination) setDefaultLimit() {
	if p.Limit == 0 {
		p.Limit = 20
	}
}

/* pagination end */

/* areas start */
// create area params
type createAreaJSON struct {
	Name          string `binding:"required" json:"name"`
	Description   string `json:"description"`
	Configuration string `binding:"required" json:"configuration"`
	ChineseName   string `binding:"required" json:"chinese_name"`
}

// update area params
type updateAreaJSON struct {
	models.Model
	Description   string `json:"description"`
	Configuration string `json:"configuration"`
	ChineseName   string `json:"chinese_name"`
}

/* areas end */

/* project start*/
// fetch project params
type queryProjectParams struct {
	ProjectIDs     string `form:"project_ids"`
	EnglishNames   string `form:"english_names"`
	ApprovalStatus string `form:"approval_status"`
	Creator        string `form:"creator"`
	ProjectType    string `form:"project_type"`
	IsSecrecy      string `form:"is_secrecy"`
	IsOfflined     string `form:"is_offline"`
	DesireAllData  string `form:"desire_all_data"`
}

type queryprojectData struct {
	ProjectIDList   []string `json:"project_ids"`
	EnglishNameList []string `json:"project_codes"`
}

// create project data
type createProjectData struct {
	ProjectID      string `binding:"required" json:"project_id"`
	Name           string `binding:"required,max=64" json:"project_name"`
	EnglishName    string `binding:"required,max=32" json:"english_name"`
	ProjectType    uint   `binding:"exists" json:"project_type"`
	UseBK          bool   `binding:"exists" json:"use_bk"`
	BGID           uint   `json:"bg_id"`
	BGName         string `json:"bg_name"`
	DeptID         uint   `json:"dept_id"`
	DeptName       string `json:"dept_name"`
	CenterID       uint   `json:"center_id"`
	CenterName     string `json:"center_name"`
	CCAppID        uint   `json:"cc_app_id"`
	Creator        string `binding:"required" json:"creator"`
	Description    string `json:"description"`
	Kind           uint   `json:"kind"`
	DeployTypeList []uint `json:"deploy_type"`
	DataID         uint   `json:"data_id"`
	IsSecrecy      bool   `json:"is_secrecy"`
	LogoAddr       string `json:"logo_addr"`
}

// update project data
type updateProjectData struct {
	Name           string  `binding:"max=64" json:"project_name"`
	Description    string  `json:"description"`
	IsOfflined     *bool   `json:"is_offlined"`
	ProjectType    *uint   `json:"project_type"`
	UseBK          *bool   `json:"use_bk"`
	BGID           *uint   `json:"bg_id"`
	BGName         *string `json:"bg_name"`
	DeptID         *uint   `json:"dept_id"`
	DeptName       *string `json:"dept_name"`
	CenterID       *uint   `json:"center_id"`
	CenterName     *string `json:"center_name"`
	CCAppID        *uint   `json:"cc_app_id"`
	Kind           *uint   `json:"kind"`
	DeployTypeList []uint  `json:"deploy_type"`
	Updator        string  `binding:"required" json:"updator"`
	DataID         *uint   `json:"data_id"`
	IsSecrecy      *bool   `json:"is_secrecy"`
	ApprovalStatus *uint   `json:"approval_status"`
	LogoAddr       *string `json:"logo_addr"`
	Remark         *string `json:"remark"`
	Extra          *string `json:"extra"`
}

/* project end */

/* cluster version start */
type clusterVersionParams struct {
	VerID       string `form:"ver_id"`
	Environment string `form:"environment"`
	Kind        string `form:"kind"`
}

// set the default value for environment
func (params *clusterVersionParams) setVersionEnvDefaultValue(defaultValue string) {
	if params.Environment == "" {
		params.Environment = defaultValue
	}
}

// set the default value for kind
func (params *clusterVersionParams) setVersionKindDefaultValue(defaultValue string) {
	if params.Kind == "" {
		params.Kind = defaultValue
	}
}

// create base version data
type createClusterBaseVersionData struct {
	Creator     string `json:"creator" binding:"required"`
	Kind        string `json:"kind" binding:"required"`
	Version     string `json:"version" binding:"required"`
	SubVersion  string `json:"sub_version"`
	Environment string `json:"environment" binding:"required"`
	Configure   string `json:"configure" binding:"required"`
}

// update base version data
type updateClusterBaseVersionData struct {
	Version     string `json:"version" binding:"required"`
	Environment string `json:"environment" binding:"required"`
	Kind        string `json:"kind" binding:"required"`
	Configure   string `json:"configure" binding:"required"`
}

type createClusterSnapshotData struct {
	Creator   string `json:"creator" binding:"required"`
	ClusterID string `json:"cluster_id" binding:"required"`
	Snapshot  string `json:"configure" binding:"required"`
}

/* cluster version end */

/* master start */
type createMasterData struct {
	InnerIP      string `binding:"required" json:"inner_ip"`
	ExtendedInfo string `json:"extended_info"`
	Backup       string `json:"backup"`
	Hostname     string `json:"hostname"`
	Status       string `json:"status"`
}

// update master info
type updateMasterData struct {
	InnerIP    string `binding:"required" json:"inner_ip"`
	Status     string `binding:"required" json:"status"`
	InstanceID string `json:"instance_id"`
}

type batchCreateMasterData struct {
	NewInnerIPList []createMasterData `binding:"required,dive" json:"new_inner_ip_list"`
}

type replaceMasterParams struct {
	ReplaceInnerIPList []string           `binding:"required" json:"replace_inner_ip_list"`
	NewIPListInfo      []createMasterData `binding:"required,dive" json:"new_inner_ip_list"`
}

/* master end */

/* cluster start */
type clusterListParamsForm struct {
	InnerIP       string `form:"ip"`
	Name          string `form:"name"`
	DesireAllData string `form:"desire_all_data"`
	Pagination
}

type clusterListDataJSON struct {
	ClusterIDList []string `binding:"required" json:"cluster_ids"`
}

type createClusterDataJSON struct {
	ProjectID       string             `json:"project_id"`
	ClusterID       string             `json:"cluster_id"`
	ClusterNum      int                `json:"cluster_num"`
	Name            string             `binding:"required" json:"name"`
	Creator         string             `binding:"required" json:"creator"`
	Description     string             `json:"description"`
	Type            string             `json:"type"`
	Environment     string             `binding:"required" json:"environment"`
	AreaID          int                `binding:"required" json:"area_id"`
	Status          string             `json:"status"`
	ConfigSvrCount  int                `json:"config_svr_count"`
	MasterCount     int                `json:"master_count"`
	Artifactory     string             `json:"artifactory"`
	IPResourceTotal int                `json:"ip_resource_total"`
	IPResourceUsed  int                `json:"ip_resource_used"`
	MasterIPs       []createMasterData `binding:"required,dive" json:"master_ips"`
	NeedNAT         bool               `json:"need_nat"`
	NotNeedNAT      bool               `json:"not_need_nat"`
	ExtraClusterID  string             `json:"extra_cluster_id"`
}

/* cluster end*/

/* node start */
type nodeListParamsForm struct {
	InnerIPS      string `form:"inner_ip_in"`
	DesireAllData string `form:"desire_all_data"`
	Pagination
}

type nodeCreateDataJSON struct {
	Name        string `json:"name"`
	Creator     string `binding:"required" json:"creator"`
	Description string `json:"description"`
	InnerIP     string `binding:"required" json:"inner_ip"`
	OutterIP    string `json:"outter_ip"`
	Kind        string `json:"kind"`
	DeviceClass string `json:"device_class"`
	InstanceID  string `json:"instance_id"`
}

type nodeUpdateDataJSON struct {
	InnerIP     string `binding:"required" json:"inner_ip"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Status      string `json:"status"`
	InstanceID  string `json:"instance_id"`
}

type nodeBatchOperateDataJSON struct {
	Creates []nodeCreateDataJSON `json:"objects"`
	Updates []nodeUpdateDataJSON `json:"updates"`
}

type nodeUpdateDataByID struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Status      string `json:"status"`
	InstanceID  string `json:"instance_id"`
}

type updateNodeParams struct {
	nodeUpdateDataJSON
	ClusterID string `json:"cluster_id" binding:"required"`
}

type nodeListUpdateDataJSON struct {
	Updates []updateNodeParams `json:"updates" binding:"required,dive"`
}

/* node end */

/* namespace start */
type namespaceListForm struct {
	DesireAllData string `form:"desire_all_data"`
	Pagination
}

type createNamespaceDataJSON struct {
	Name           string `binding:"required" json:"name"`
	Creator        string `binding:"required" json:"creator"`
	Description    string `json:"description"`
	EnvType        string `binding:"required" json:"env_type"`
	HasImageSecret bool   `json:"has_image_secret"`
}

type updateNamespaceDataJSON struct {
	Name           string `json:"name"`
	Description    string `json:"description"`
	Status         string `json:"status"`
	EnvType        string `json:"env_type"`
	HasImageSecret *bool  `json:"has_image_secret"`
}

/* namespace end */

/* cluster history start */
type queryClusterHistoryParams struct {
	StartAt time.Time `binding:"required" form:"start_at" time_format:"2006-01-02 15:04:05" time_utc:"1"`
	EndAt   time.Time `binding:"required" form:"end_at" time_format:"2006-01-02 15:04:05" time_utc:"1" validate:"ltecsfield=StartAt"`
	Metric  string    `binding:"required" form:"metric"`
}

/* cluster history end */

// BindForm : binding form with github.com/json-iterator/go
func BindForm(c *gin.Context, obj interface{}) error {
	return c.ShouldBindWith(obj, binding.Form)
}

// BindJSON : binding json with github.com/json-iterator/go
func BindJSON(c *gin.Context, obj interface{}) error {
	return c.ShouldBindWith(obj, binding.JSON)
}

// ValidationError : validate message
func ValidationError(obj interface{}) (err error) {
	result, ok := obj.(validator.ValidationErrors)
	if !ok {
		return fmt.Errorf("%v", obj)
	}
	errStrList := []string{}
	for _, err := range result {
		field := utils.Camel2Snake(err.Field)
		switch err.Tag {
		case "required":
			errStrList = append(errStrList, fmt.Sprintf("param[%s] is null", field))
			continue
		case "max":
			errStrList = append(errStrList, fmt.Sprintf("param[%s] is more than %s", field, err.Param))
			continue
		case "min":
			errStrList = append(errStrList, fmt.Sprintf("param[%s] is less than %s", field, err.Param))
			continue
		}
		errStrList = append(errStrList, fmt.Sprintf("param[%s] is unavailable", field))
	}
	// 返回数据
	return fmt.Errorf("params error, %s", strings.Join(errStrList, ";"))
}
