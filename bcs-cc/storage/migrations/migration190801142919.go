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

package migrations

import (
	"time"

	"github.com/jinzhu/gorm"
)

// HandleMigrate190801142919 :
func (c *MigrationCommand) HandleMigrate190801142919(db *gorm.DB) error {
	type Model struct {
		ID        uint `gorm:"primary_key"`
		CreatedAt time.Time
		UpdatedAt time.Time
		DeletedAt *time.Time
		Extra     string `json:"extra" sql:"type:text"`
	}
	type Cluster struct {
		Model
		Name              string     `json:"name" gorm:"size:64;unique_index:uix_project_id_name"`
		Creator           string     `json:"creator" gorm:"size:32"`
		Description       string     `json:"description" sql:"size:128"`
		ProjectID         string     `json:"project_id" gorm:"size:32;index;unique_index:uix_project_id_name"`
		RelatedProjects   string     `json:"related_projects" sql:"type:text"`
		ClusterID         string     `json:"cluster_id" gorm:"size:64;unique_index"`
		ClusterNum        int64      `json:"cluster_num" gorm:"unique"`
		Status            string     `json:"status" gorm:"size:64"`
		Disabled          bool       `json:"disabled"`
		Type              string     `json:"type" gorm:"size:8"`
		Environment       string     `json:"environment" gorm:"size:8"`
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
	type ManagerMaster struct {
		Model
		InnerIP      string `json:"inner_ip" gorm:"size:64;unique_index"`
		ClusterID    string `json:"cluster_id" gorm:"size:128"`
		ProjectID    string `json:"project_id" gorm:"size:32"`
		ExtendedInfo string `json:"extended_info" sql:"type:text"`
		Num          int    `json:"num"`
		Backup       string `json:"backup" gorm:"size:128"`
		Hostname     string `json:"hostname" gorm:"size:128"`
		Status       string `json:"status" gorm:"size:16"`
		InstanceID   string `json:"instance_id" gorm:"size:64"`
	}
	type Node struct {
		Model
		Name        string  `json:"name" gorm:"size:63"`
		Creator     string  `json:"creator" gorm:"size:31"`
		Description string  `json:"description" sql:"size:127"`
		ProjectID   string  `json:"project_id" gorm:"size:32;index"`
		ClusterID   string  `json:"cluster_id" gorm:"size:32;index"`
		Status      string  `json:"status" gorm:"size:16"`
		Kind        string  `json:"kind" gorm:"size:16"`
		InnerIP     string  `json:"inner_ip" gorm:"size:64;unique_index"`
		OutterIP    string  `json:"outter_ip" gorm:"size:255"`
		DeviceClass string  `json:"device_class" gorm:"text"`
		CPU         float64 `json:"cpu" gorm:"default:0"`
		MEM         float64 `json:"mem" gorm:"default:0"`
		Disk        float64 `json:"disk" gorm:"default:0"`
		IPResources float64 `json:"ip_resources" gorm:"default:0"`
		InstanceID  string  `json:"instance_id" gorm:"size:64"`
	}

	return db.AutoMigrate(&Cluster{}, &ManagerMaster{}, &Node{}).Error
}

// HandleRollback190801142919 : rollback handler for HandleMigrate190801142919
func (c *MigrationCommand) HandleRollback190801142919(db *gorm.DB) error {
	return nil
}
