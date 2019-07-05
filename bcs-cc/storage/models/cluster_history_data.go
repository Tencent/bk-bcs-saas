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
	"time"

	"bcs_cc/storage"
)

// ClusterHistoryData : save the cluster history resource info
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type ClusterHistoryData struct {
	ID                uint      `gorm:"primary_key"`
	CreatedAt         time.Time `json:"created_at"`
	ProjectID         string    `json:"project_id" gorm:"size:32;index"`
	ClusterID         string    `json:"cluster_id" gorm:"size:64;index"`
	Environment       string    `json:"environment" gorm:"size:8"` // stag,debug,prod
	TotalMem          float64   `json:"total_mem"`
	RemainMem         float64   `json:"remain_mem"`
	TotalCPU          float64   `json:"total_cpu"`
	RemainCPU         float64   `json:"remain_cpu"`
	TotalDisk         float64   `json:"total_disk"`
	RemainDisk        float64   `json:"remain_disk"`
	CapacityUpdatedAt time.Time `json:"capacity_updated_at" gorm:"index"`
}

// ClusterHistoryDataFilter :
type ClusterHistoryDataFilter struct {
	ClusterID string
	StartAt   time.Time
	EndAt     time.Time
}

// CreateRecord : create history record
func (historyData *ClusterHistoryData) CreateRecord() error {
	db := storage.GetDefaultSession().DB
	if err := historyData.Create(db); err != nil {
		return err
	}
	return nil
}

// RetriveRecord : get cluster history data
func (filter *ClusterHistoryDataFilter) RetriveRecord() (data []ClusterHistoryData, err error) {
	qs := NewClusterHistoryDataQuerySet(storage.GetDefaultSession().DB)
	if err := qs.ClusterIDEq(
		filter.ClusterID,
	).CapacityUpdatedAtGte(
		filter.StartAt,
	).CapacityUpdatedAtLte(
		filter.EndAt,
	).All(&data); err != nil {
		return nil, err
	}
	return data, nil
}
