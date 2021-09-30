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

package models

import (
	"errors"
	"time"

	"bcs-cc/storage"
)

// Project :
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type Project struct {
	Model
	Name           string    `json:"name" gorm:"size:64;unique"`
	EnglishName    string    `json:"english_name" gorm:"size:64;unique;index"`
	Creator        string    `json:"creator" gorm:"size:32"`
	Updator        string    `json:"updator" gorm:"size:32"`
	Description    string    `json:"desc" sql:"type:text"`
	ProjectType    uint      `json:"project_type"`
	IsOfflined     bool      `json:"is_offlined" gorm:"default:false"`
	ProjectID      string    `json:"project_id" gorm:"size:32;unique;index"`
	UseBK          bool      `json:"use_bk" gorm:"default:false"`
	CCAppID        uint      `json:"cc_app_id"`
	Kind           uint      `json:"kind"`        // 1:k8s, 2:mesos
	DeployType     string    `json:"deploy_type"` // 1: 物理机部署, 2: 容器部署
	BGID           uint      `json:"bg_id"`
	BGName         string    `json:"bg_name"`
	DeptID         uint      `json:"dept_id"`
	DeptName       string    `json:"dept_name"`
	CenterID       uint      `json:"center_id"`
	CenterName     string    `json:"center_name"`
	DataID         uint      `json:"data_id"`
	IsSecrecy      bool      `json:"is_secrecy" gorm:"default:false"`
	ApprovalStatus uint      `json:"approval_status" gorm:"default:2"` // 1.待审批 2.已审批 3.已驳回
	LogoAddr       string    `json:"logo_addr" sql:"type:text"`        // project logo address
	Approver       string    `json:"approver" gorm:"size:32"`
	Remark         string    `json:"remark" sql:"type:text"`
	ApprovalTime   time.Time `json:"approval_time"`
}

// FilterParams :
type FilterParams struct {
	ProjectIDList   []string
	EnglishNameList []string
	ProjectNameList []string
	ApprovalStatus  string
	Creator         string
	ProjectType     string
	IsSecrecy       string
	IsOfflined      string
	DesireAllData   string
}

// ProjectInfoByID : get project info by project id
func (filterParams *FilterParams) ProjectInfoByID() (data []Project, err error) {
	qs := NewProjectQuerySet(storage.GetDefaultSession().DB)
	qs = qs.ProjectIDInWithoutError(filterParams.ProjectIDList...)
	if err := qs.All(&data); err != nil {
		return nil, err
	}
	return data, nil
}

// ProjectListInfo :
func (filterParams *FilterParams) ProjectListInfo() (data []Project, count int, err error) {
	qs := NewProjectQuerySet(storage.GetDefaultSession().DB)
	// filter
	if filterParams.DesireAllData == "0" || filterParams.DesireAllData == "" {
		qs = qs.ProjectIDInWithoutError(
			filterParams.ProjectIDList...).EnglishNameInWithoutError(
			filterParams.EnglishNameList...).ProjectNameInWithoutError(
			filterParams.ProjectNameList...)
		// (field is uint type) approval_status or project_type filter
		qs = qs.Filter(map[string]string{
			"approval_status": filterParams.ApprovalStatus,
			"project_type":    filterParams.ProjectType,
		}, filterUint)
		// (field is bool type) is_secrecy or is_offline filter
		qs = qs.Filter(map[string]string{
			"is_secrecy": filterParams.IsSecrecy,
			"is_offline": filterParams.IsOfflined,
		}, filterBool)
		// creator filter
		qs = qs.Filter(map[string]string{
			"creator": filterParams.Creator,
		}, filterString)
	}

	count, err = qs.Count()
	if err != nil {
		return nil, 0, err
	}
	if err := qs.All(&data); err != nil {
		return nil, 0, err
	}
	return data, count, nil
}

// CreateOrUpdateRecord :
func (project *Project) CreateOrUpdateRecord() error {
	db := storage.GetDefaultSession().DB
	// update
	if count, _ := NewProjectQuerySet(db).ProjectIDEq(project.ProjectID).Count(); count > 0 {
		return project.UpdateRecord()
	}
	return project.CreateRecord()
}

// CreateRecord : create one record
func (project *Project) CreateRecord() error {
	db := storage.GetDefaultSession().DB
	if err := project.Create(db); err != nil {
		return err
	}
	return project.RetriveRecord()
}

// UpdateRecord : update one record
func (project *Project) UpdateRecord() error {
	db := storage.GetDefaultSession().DB
	fieldList := []ProjectDBSchemaField{
		"name", "description", "is_offlined", "project_type", "bg_id", "bg_name",
		"dept_id", "dept_name", "center_id", "center_name", "cc_app_id", "kind",
		"deploy_type", "updator", "data_id", "is_secrecy", "approval_status",
		"logo_addr", "remark", "extra",
	}
	if err := project.CustomeUpdate(db, fieldList...); err != nil {
		return err
	}
	return project.RetriveRecord()
}

// RetriveRecord :
func (project *Project) RetriveRecord() error {
	qs := NewProjectQuerySet(storage.GetDefaultSession().DB)
	return qs.ProjectIDEq(project.ProjectID).One(project)
}

// RetriveRecordByProjectCode :
func (project *Project) RetriveRecordByProjectCode() error {
	qs := NewProjectQuerySet(storage.GetDefaultSession().DB)
	return qs.EnglishNameEq(project.EnglishName).One(project)
}

// RetriveRecordByProjectName :
func (project *Project) RetriveRecordByProjectName() error {
	qs := NewProjectQuerySet(storage.GetDefaultSession().DB)
	count, err := qs.ProjectIDNe(project.ProjectID).NameEq(project.Name).Count()
	if count == 0 {
		return errors.New("record not found")
	}
	return err
}

// ProjectHasCluster : if cluster is not existed in project
func (project *Project) ProjectHasCluster() bool {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	if err := qs.ClusterListByProjectID(project.ProjectID).One(&Cluster{}); err != nil {
		return false
	}
	return true
}

// ProjectListWithoutOffline : get project info without offlined scene
func ProjectListWithoutOffline(projectIDList []string) (data []Project, err error) {
	qs := NewProjectQuerySet(storage.GetDefaultSession().DB)
	if err := qs.ProjectIDInWithoutError(projectIDList...).IsOfflinedNe(true).All(&data); err != nil {
		return nil, err
	}
	return data, nil
}
