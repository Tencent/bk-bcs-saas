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

	"bcs-cc/storage"

	"github.com/tuvistavie/structomap"
)

// BaseVersion : initial the base version info
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type BaseVersion struct {
	Model
	Creator     string `json:"creator" gorm:"size:32"`
	Kind        string `json:"kind" gorm:"size:16;default:'k8s';unique_index:uix_version_kind_environment"`
	Version     string `json:"version" gorm:"size:64";unique_index:uix_version_kind_environment`
	SubVersion  string `json:"sub_version" gorm:"size:64"`
	Environment string `json:"environment" gorm:"size:64;default:'prod'";unique_index:uix_version_kind_environment`
	Configure   string `json:"configure" sql:"type:text"`
}

// ClusterConfigureVersion : snapshot for cluster configure
//go:generate goqueryset -in ${GOFILE} -out qs${GOFILE}
// gen:qs
type ClusterConfigureVersion struct {
	Model
	Creator   string `json:"creator" gorm:"size:32"`
	ClusterID string `json:"cluster_id" gorm:"size:64"`
	Snapshot  string `json:"snapshot" sql:"type:text"`
}

type clusterSnapshotInfo struct {
	ClusterID string `json:"cluster_id"`
	Snapshot  string `json:"snapshot"`
	Creator   string `json:"creator"`
}

// AllClusterSnapshotConfig : fetch cluster snapshot info
func AllClusterSnapshotConfig() (data []map[string]interface{}, err error) {
	db := storage.GetDefaultSession().DB
	var resultList []clusterSnapshotInfo
	// sql return ： the last record for every cluster
	rawSQL := "select info.cluster_id, info.snapshot, info.creator from (select * from cluster_configure_versions order by updated_at desc) as info group by info.cluster_id"
	if err := db.Raw(rawSQL).Scan(&resultList).Error; err != nil {
		return nil, err
	}
	// struct to map in array
	serializer := structomap.New().UseSnakeCase().Pick("ClusterID", "Snapshot", "Creator")
	return serializer.TransformArray(resultList)
}

// BaseVersionConfig : fetch the base cluster config by ver_id、env and kind
func BaseVersionConfig(verID string, env string, kind string) (BaseVersion, error) {
	qs := NewBaseVersionQuerySet(storage.GetDefaultSession().DB)
	// queryset filter
	qs = qs.Filter(map[string]string{
		"version":     verID,
		"environment": env,
		"kind":        kind,
	}, baseVersionFilterString)
	qs = qs.OrderDescByID()
	baseVersion := BaseVersion{}
	// get last one
	err := qs.One(&baseVersion)
	return baseVersion, err
}

// ClusterSnapshotConfig : fetch cluster snapshort by
func ClusterSnapshotConfig(clusterID string) (ClusterConfigureVersion, error) {
	qs := NewClusterConfigureVersionQuerySet(storage.GetDefaultSession().DB)
	qs = qs.ClusterIDEq(clusterID).OrderDescByID()
	clusterConfig := ClusterConfigureVersion{}
	err := qs.One(&clusterConfig)
	return clusterConfig, err
}

// CreateBaseVersion : create cluster base version
func (baseVersion *BaseVersion) CreateBaseVersion() error {
	db := storage.GetDefaultSession().DB
	if err := baseVersion.Create(db); err != nil {
		return err
	}
	return nil
}

// UpdateBaseVersion : update base version
func (baseVersion *BaseVersion) UpdateBaseVersion() error {
	qs := NewBaseVersionQuerySet(storage.GetDefaultSession().DB)
	qs = qs.VersionEq(baseVersion.Version).EnvironmentEq(baseVersion.Environment).KindEq(baseVersion.Kind)
	if count, err := qs.Count(); err != nil || count == 0 {
		return errors.New("record not found")
	}
	qsUpdater := qs.GetUpdater()
	return qsUpdater.SetConfigure(baseVersion.Configure).Update()
}

// CreateSnapshot : create cluster snapshot
func (snapshot *ClusterConfigureVersion) CreateSnapshot() error {
	db := storage.GetDefaultSession().DB
	if err := snapshot.Create(db); err != nil {
		return err
	}
	return nil
}

// ClusterVersion : fetch the cluster version info
func ClusterVersion(verID string, env string, kind string) ([]BaseVersion, error) {
	qs := NewBaseVersionQuerySet(storage.GetDefaultSession().DB)
	// queryset filter
	qs = qs.Filter(map[string]string{
		"version":     verID,
		"environment": env,
		"kind":        kind,
	}, baseVersionFilterString)
	qs = qs.OrderDescByID()
	clusterVersion := []BaseVersion{}
	err := qs.All(&clusterVersion)
	return clusterVersion, err
}
