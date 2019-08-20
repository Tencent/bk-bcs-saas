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
	"fmt"
	"time"

	"bcs_cc/config"
	"bcs_cc/storage"
	"bcs_cc/utils"

	"github.com/jinzhu/gorm"
)

// Cluster Model : cluster info
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type Cluster struct {
	Model
	Name              string     `json:"name" gorm:"size:64;unique_index:uix_project_id_name"`
	Creator           string     `json:"creator" gorm:"size:32"`
	Description       string     `json:"description" sql:"size:128"`
	ProjectID         string     `json:"project_id" gorm:"size:32;index;unique_index:uix_project_id_name"`
	RelatedProjects   string     `json:"related_projects" sql:"type:text"`
	ClusterID         string     `json:"cluster_id" gorm:"size:64;unique_index"`
	ClusterNum        int64      `json:"cluster_num" gorm:"unique"`
	Status            string     `json:"status" gorm:"size:64"`     // 初始化的状态 uninitialized, initializing, initialized, initialize_failed
	Disabled          bool       `json:"disabled"`                  // 是否禁用掉了，default false
	Type              string     `json:"type" gorm:"size:8"`        // mesos,k8s
	Environment       string     `json:"environment" gorm:"size:8"` // stag,debug,prod
	AreaID            int        `json:"area_id"`
	ConfigSvrCount    int        `json:"config_svr_count"`
	MasterCount       int        `json:"master_count"`
	NodeCount         int        `json:"node_count"`
	IPResourceTotal   int        `json:"ip_resource_total"`
	IPResourceUsed    int        `json:"ip_resource_used"`
	Artifactory       string     `json:"artifactory" gorm:"size:256"`
	TotalMem          float64    `json:"total_mem"`
	RemainMem         float64    `json:"remain_mem"`
	TotalCPU          float64    `json:"total_cpu"`
	RemainCPU         float64    `json:"remain_cpu"`
	TotalDisk         float64    `json:"total_disk"`
	RemainDisk        float64    `json:"remain_disk"`
	CapacityUpdatedAt *time.Time `json:"capacity_updated_at"`
	NotNeedNAT        bool       `json:"not_need_nat" gorm:"default:false"`
	ExtraClusterID    string     `json:"extra_cluster_id" gorm:"size:64"`
}

// ClusterFilterParams :
// note: include the embedded struct
type ClusterFilterParams struct {
	ProjectID     string
	InnerIP       string
	ClusterIDList []string
	Name          string
	DesireAllData string
	Limit         int
	Offset        int
	ClusterType   string
	FilterStatus  []string
	ExcludeStatus []string
}

// UpdateClusterDataJSON :
type UpdateClusterDataJSON struct {
	ProjectID         string    `json: "project_id"`
	ClusterID         string    `json:"cluster_id"`
	Name              string    `json:"name"`
	Description       *string   `json:"description"`
	Status            string    `json:"status"`
	Disabled          *bool     `json:"disabled"`
	Environment       string    `json:"environment"`
	AreaID            *int      `json:"area_id"`
	ConfigSvrCount    *int      `json:"config_svr_count"`
	MasterCount       *int      `json:"master_count"`
	NodeCount         *int      `json:"node_count"`
	Artifactory       string    `json:"artifactory"`
	TotalMem          *float64  `json:"total_mem"`
	RemainMem         *float64  `json:"remain_mem"`
	TotalCPU          *float64  `json:"total_cpu"`
	RemainCPU         *float64  `json:"remain_cpu"`
	TotalDisk         *float64  `json:"total_disk"`
	RemainDisk        *float64  `json:"remain_disk"`
	CapacityUpdatedAt string    `json:"capacity_updated_at"`
	IPResourceTotal   *int      `json:"ip_resource_total"`
	IPResourceUsed    *int      `json:"ip_resource_used"`
	NeedNAT           *bool     `json:"need_nat"`
	AgentList         *[]string `json:"agent_list"`
	RelatedProjects   *[]string `json:"related_projects"`
	ExtraClusterID    *string   `json:"extra_cluster_id"`
}

func clusterListBase(filter ClusterFilterParams) (clusterList []Cluster, err error) {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	// filter
	qs = qs.ClusterListByProjectID(
		filter.ProjectID,
	).ClusterIDInWithoutError(
		filter.ClusterIDList...,
	).ClusterTypeEqWithoutExist(
		filter.ClusterType,
	).ClusterStatusNotInWithoutError(
		filter.ExcludeStatus...,
	).ClusterStatusInWithoutError(filter.FilterStatus...)
	if err := qs.All(&clusterList); err != nil {
		return nil, err
	}
	return clusterList, nil
}

// ClusterWithoutRemoved :
func ClusterWithoutRemoved(excludeStatus []string) ([]Cluster, error) {
	return clusterListBase(ClusterFilterParams{ExcludeStatus: excludeStatus})
}

// ClusterList : fetch cluster list by params
func ClusterList(clusterType string, filterStatus []string) ([]Cluster, error) {
	return clusterListBase(ClusterFilterParams{
		ClusterType: clusterType, FilterStatus: filterStatus,
	})
}

// FetchPublicClusterList : fetch public cluster info
func FetchPublicClusterList(projectID string) (data []Cluster, err error) {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	if err := qs.RelatedProjectsLike(projectID).All(&data); err != nil {
		return nil, err
	}
	return data, nil
}

// FetchPublicClusterIDList : get public cluster id by project id
func FetchPublicClusterIDList(projectID string) (clusterIDList []string, err error) {
	clusterList, err := FetchPublicClusterList(projectID)
	if err != nil {
		return nil, err
	}
	for _, clusterInfo := range clusterList {
		clusterIDList = append(clusterIDList, clusterInfo.ClusterID)
	}
	return clusterIDList, nil
}

// ValidateProjectCluster : cluster of project is valid
func ValidateProjectCluster(projectID string, clusterID string) error {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	if err := qs.ClusterListByProjectID(
		projectID,
	).ClusterIDEq(clusterID).One(&Cluster{}); err != nil {
		return errors.New("cluster not found in project")
	}
	return nil
}

// RetriveRecord : get a record
func (cluster *Cluster) RetriveRecord() error {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	if err := qs.ClusterIDEq(cluster.ClusterID).One(cluster); err != nil {
		return err
	}
	return nil
}

// RetriveRecordByProjectIDClusterID : get a record
func (cluster *Cluster) RetriveRecordByProjectIDClusterID() error {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	if err := qs.EnvironmentIn(
		config.GlobalConfigurations.AvailableEnvironmentFlags...,
	).ClusterListByProjectID(
		cluster.ProjectID,
	).ClusterIDEq(cluster.ClusterID).One(cluster); err != nil {
		return err
	}
	return nil
}

// FetchPrivateClusterByProjectID : get project private cluster info
func FetchPrivateClusterByProjectID(projectID string) (data []Cluster, err error) {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	if err := qs.ProjectIDEq(projectID).All(&data); err != nil {
		return nil, err
	}
	return data, nil
}

// FetchPrivateClusterIDByProjectID : get project private cluster id
func FetchPrivateClusterIDByProjectID(projectID string) (clusterIDList []string, err error) {
	clusterList, err := FetchPrivateClusterByProjectID(projectID)
	if err != nil {
		return nil, err
	}
	for _, clusterInfo := range clusterList {
		clusterIDList = append(clusterIDList, clusterInfo.ClusterID)
	}
	return clusterIDList, nil
}

func (qs *ClusterQuerySet) queryClusterWithDesireAll(filter *ClusterFilterParams) (clusterList []Cluster, err error) {
	if err := qs.ClusterListByProjectID(filter.ProjectID).All(&clusterList); err != nil {
		return nil, err
	}
	return clusterList, nil
}

func getClusterIDList(clusterList []Cluster) (clusterIDList []string) {
	for _, clusterInfo := range clusterList {
		clusterIDList = append(clusterIDList, clusterInfo.ClusterID)
	}
	return clusterIDList
}

// queryClusterIDWithDesireAll : get project all cluster id
func (filter *ClusterFilterParams) clusterIDListWithAll(qs ClusterQuerySet) (clusterIDList []string, err error) {
	var clusterList []Cluster
	if err := qs.ClusterListByProjectID(filter.ProjectID).All(&clusterList); err != nil {
		return nil, err
	}

	return getClusterIDList(clusterList), nil
}

// get cluster id list by filter params
func (filter *ClusterFilterParams) clusterIDList(qs ClusterQuerySet) (clusterIDList []string, err error) {
	clusterID := ""
	// get cluster id by master ip
	if filter.InnerIP != "" {
		master := &ManagerMaster{InnerIP: filter.InnerIP, ProjectID: filter.ProjectID}
		if err := master.RetriveRecord(); err != nil {
			clusterID = NotExistClusterID
		} else {
			clusterID = master.ClusterID
		}
	}
	var clusterList []Cluster
	tempQuerySet := qs.ClusterIDEqWithEmpty(clusterID).NameEqWithEmpty(
		filter.Name,
	).ClusterListByProjectID(filter.ProjectID)
	if err := tempQuerySet.All(&clusterList); err != nil {
		return nil, err
	}
	return getClusterIDList(clusterList), nil
}

// ClusterListInfo : get cluster list
func (filter *ClusterFilterParams) ClusterListInfo() (data []Cluster, count int, err error) {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	var clusterIDList []string
	if filter.DesireAllData != "1" {
		clusterIDList, err = filter.clusterIDList(qs)
		if err != nil {
			return nil, 0, err
		}
	} else {
		clusterIDList, err = filter.clusterIDListWithAll(qs)
		if err != nil {
			return nil, 0, err
		}
	}
	// if length of cluster id list is 0,  return nil, 0, nil
	if len(clusterIDList) == 0 {
		return nil, 0, nil
	}
	// final filter cluster
	qs = qs.ClusterIDIn(clusterIDList...)
	count, err = qs.Count()
	if err != nil {
		return nil, 0, err
	}
	// limit and offset for cluster pagination
	if filter.DesireAllData != "1" {
		qs = qs.Limit(filter.Limit).Offset(filter.Offset)
	}
	if err := qs.All(&data); err != nil {
		return nil, 0, err
	}
	return data, count, nil
}

// ClusterListByID : get cluster info by cluster id list
func (filter *ClusterFilterParams) ClusterListByID() (data []Cluster, err error) {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	var clusterList []Cluster
	qs = qs.ClusterListByProjectID(filter.ProjectID).ClusterIDIn(filter.ClusterIDList...)
	if err := qs.All(&clusterList); err != nil {
		return nil, err
	}
	return clusterList, nil
}

// DeleteRecord : delete a cluster with master by db transaction
func (cluster *Cluster) DeleteRecord() error {
	db := storage.GetDefaultSession().DB
	tx := db.Begin()
	// delete master records
	masterQuerySet := NewManagerMasterQuerySet(tx)
	if err := masterQuerySet.ClusterIDEq(cluster.ClusterID).DeleteUnscoped(); err != nil {
		tx.Rollback()
		return err
	}
	// 修改集群名称
	clusterQuerySet := NewClusterQuerySet(tx)
	clusterQuerySet = clusterQuerySet.ClusterIDEq(cluster.ClusterID)
	updater := clusterQuerySet.GetUpdater()
	if err := updater.SetName("deleted:" + cluster.ClusterID).Update(); err != nil {
		tx.Rollback()
		return err
	}
	// delete cluster record
	if err := clusterQuerySet.Delete(); err != nil {
		tx.Rollback()
		return err
	}
	tx.Commit()
	return nil
}

// GetMaxClusterNum : get the max cluster id number
func GetMaxClusterNum(clusterType string, clusterEnv string) (clusterNum int, err error) {
	db := storage.GetDefaultSession().DB
	sql := fmt.Sprintf("select max(cluster_num) as max_num from clusters where type='%v' and environment='%v'", clusterType, clusterEnv)
	var maxInst struct{ MaxNum int }
	if err := db.Raw(sql).Scan(&maxInst).Error; err != nil {
		return 0, err
	}
	return maxInst.MaxNum + 1, nil
}

// CreateRecordWithMaster :
func (cluster *Cluster) CreateRecordWithMaster(masterList []ManagerMaster) error {
	db := storage.GetDefaultSession().DB
	tx := db.Begin()
	if err := cluster.CreateRecordWithDB(tx); err != nil {
		tx.Rollback()
		return err
	}
	for _, master := range masterList {
		master.ProjectID = cluster.ProjectID
		master.ClusterID = cluster.ClusterID
		if err := master.CreateRecordWithDB(tx); err != nil {
			tx.Rollback()
			return err
		}
	}
	tx.Commit()
	if err := cluster.RetriveRecord(); err != nil {
		return err
	}
	return nil
}

// CreateRecord : create a cluster info
func (cluster *Cluster) CreateRecord() error {
	return nil
}

// CreateRecordWithDB :
func (cluster *Cluster) CreateRecordWithDB(db *gorm.DB) error {
	if err := cluster.Create(db); err != nil {
		return err
	}
	return nil
}

// UpdateRecord :
func (updaterData UpdateClusterDataJSON) UpdateRecord() error {
	currTime, err := time.ParseInLocation(
		"2006-01-02 15:04:05", updaterData.CapacityUpdatedAt, time.Local,
	)
	if err != nil {
		currTime = time.Now()
	}
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	qs = qs.ClusterListByProjectID(updaterData.ProjectID).ClusterIDEq(updaterData.ClusterID)
	var cluster Cluster
	if err := qs.One(&cluster); err != nil {
		return err
	}
	clusterUpdater := qs.GetUpdater()
	clusterUpdater = clusterUpdater.SetNameWithoutEmpty(
		updaterData.Name).SetDescriptionWithoutNil(
		updaterData.Description).SetDisableWithoutNil(
		updaterData.Disabled).SetAreaIDWithoutNil(
		updaterData.AreaID).SetTotalCPUWithoutNil(
		updaterData.TotalCPU).SetRemainCPUWithoutNil(
		updaterData.RemainCPU).SetTotalDiskWithoutNil(
		updaterData.TotalDisk).SetRemainDiskWithoutNil(
		updaterData.RemainDisk).SetTotalMemWithoutNil(
		updaterData.TotalMem).SetRemainMemWithoutNil(
		updaterData.RemainMem).SetStatusWithoutEmpty(
		updaterData.Status).SetCapacityUpdatedAt(
		&currTime).SetIPResourceTotalWithoutNil(
		updaterData.IPResourceTotal).SetIPResourceUsedWithoutNil(
		updaterData.IPResourceUsed).SetNotNeedNATWithoutNil(
		updaterData.NeedNAT).SetExtraClusterIDWithoutNil(updaterData.ExtraClusterID)
	updateRelatedProjects := ""
	relatedProjects := updaterData.RelatedProjects
	if relatedProjects != nil {
		projectList := utils.StringSplit(cluster.RelatedProjects, ";")
		for _, id := range *relatedProjects {
			if utils.StringInSlice(id, projectList) {
				continue
			}
			if id != "" {
				projectList = append(projectList, id)
			}
		}
		updateRelatedProjects = utils.ListJoinWithString(&projectList, ";")
	}
	clusterUpdater = clusterUpdater.SetRelatedProjectsWithoutEmpty(updateRelatedProjects)
	if err := clusterUpdater.Update(); err != nil {
		return err
	}
	return nil
}

// ClusterListWithoutRemoved : get cluster list by project info
func ClusterListWithoutRemoved(status []string) (data []Cluster, err error) {
	qs := NewClusterQuerySet(storage.GetDefaultSession().DB)
	if err := qs.StatusNotIn(status...).All(&data); err != nil {
		return nil, err
	}
	return data, nil
}
