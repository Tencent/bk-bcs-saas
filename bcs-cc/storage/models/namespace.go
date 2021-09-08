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
	"bcs-cc/storage"

	"github.com/tuvistavie/structomap"
)

// Namespace :
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type Namespace struct {
	Model
	Name           string `json:"name" gorm:"size:63;unique_index"`
	Creator        string `json:"creator" gorm:"size:31"`
	Description    string `json:"description" sql:"size:127"`
	ProjectID      string `json:"project_id" gorm:"size:32;index"`
	ClusterID      string `json:"cluster_id" gorm:"size:32;index"`
	EnvType        string `json:"env_type" gorm:"size:16"`
	Status         string `json:"status" gorm:"size:16"`
	HasImageSecret bool   `json:"has_image_secret" gorm:"default:false"` // 是否有secret
}

// KubernetesNamespace :
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type KubernetesNamespace struct {
	Model
	Name           string `json:"name" gorm:"size:63;unique_index:idx_name_code"`
	Creator        string `json:"creator" gorm:"size:31"`
	Description    string `json:"description" sql:"size:127"`
	ProjectID      string `json:"project_id" gorm:"size:32"`
	ClusterID      string `json:"cluster_id" gorm:"size:32;unique_index:idx_name_code"`
	EnvType        string `json:"env_type" gorm:"size:16"`
	Status         string `json:"status" gorm:"size:16"`
	HasImageSecret bool   `json:"has_image_secret" gorm:"default:false"`
}

// NamespaceFilterParams :
type NamespaceFilterParams struct {
	ProjectID     string
	ClusterID     string
	DesireAllData string
	Limit         int
	Offset        int
}

// K8SNamespaceUpdate :
type K8SNamespaceUpdate struct {
	Namespace        *KubernetesNamespace
	ImageSecretExist bool
}

// MesosNamespaceUpdate :
type MesosNamespaceUpdate struct {
	Namespace        *Namespace
	ImageSecretExist bool
}

// K8SNamespaceList :
func K8SNamespaceList(filter NamespaceFilterParams) (data []map[string]interface{}, count int, err error) {
	nsQuerySet := NewKubernetesNamespaceQuerySet(storage.GetDefaultSession().DB)
	nsQuerySet = nsQuerySet.ProjectIDEq(filter.ProjectID).ClusterIDEqWithEmpty(filter.ClusterID)
	count, err = nsQuerySet.Count()
	if err != nil {
		return nil, 0, err
	}
	if filter.DesireAllData != "1" {
		nsQuerySet = nsQuerySet.Limit(filter.Limit).Offset(filter.Offset)
	}
	var nsList []KubernetesNamespace
	if err := nsQuerySet.All(&nsList); err != nil {
		return nil, 0, err
	}
	serializer := structomap.New().UseSnakeCase().PickAll()
	serializer = serializer.Pick("CreatedAt", "UpdatedAt", "ID").Omit("Model")
	data, err = serializer.TransformArray(nsList)
	if err != nil {
		return nil, 0, err
	}
	return data, count, nil
}

// MesosNamespaceList :
func MesosNamespaceList(filter NamespaceFilterParams) (data []map[string]interface{}, count int, err error) {
	nsQuerySet := NewNamespaceQuerySet(storage.GetDefaultSession().DB)
	nsQuerySet = nsQuerySet.ProjectIDEq(filter.ProjectID).ClusterIDEqWithEmpty(filter.ClusterID)
	count, err = nsQuerySet.Count()
	if err != nil {
		return nil, 0, err
	}
	if filter.DesireAllData != "1" {
		nsQuerySet = nsQuerySet.Limit(filter.Limit).Offset(filter.Offset)
	}
	var nsList []Namespace
	if err := nsQuerySet.All(&nsList); err != nil {
		return nil, 0, err
	}
	serializer := structomap.New().UseSnakeCase().PickAll()
	serializer = serializer.Pick("CreatedAt", "UpdatedAt", "ID").Omit("Model")
	data, err = serializer.TransformArray(nsList)
	if err != nil {
		return nil, 0, err
	}
	return data, count, nil
}

// RetriveRecord : fetch a k8s namespace info
func (namespace *KubernetesNamespace) RetriveRecord() error {
	nsQuerySet := NewKubernetesNamespaceQuerySet(storage.GetDefaultSession().DB)
	nsQuerySet = nsQuerySet.ProjectIDEq(namespace.ProjectID).ClusterIDEqWithEmpty(namespace.ClusterID)
	if err := nsQuerySet.IDEq(namespace.ID).One(namespace); err != nil {
		return err
	}
	return nil
}

// RetriveRecord : fetch a mesos namespace info
func (namespace *Namespace) RetriveRecord() error {
	nsQuerySet := NewNamespaceQuerySet(storage.GetDefaultSession().DB)
	nsQuerySet = nsQuerySet.ProjectIDEq(namespace.ProjectID).ClusterIDEqWithEmpty(namespace.ClusterID)
	if err := nsQuerySet.IDEq(namespace.ID).One(namespace); err != nil {
		return err
	}
	return nil
}

// DeleteRecord : delete a k8s namespace
func (namespace *KubernetesNamespace) DeleteRecord() error {
	if err := namespace.RetriveRecord(); err != nil {
		return err
	}
	db := storage.GetDefaultSession().DB
	// delete record
	if err := namespace.DeleteUnscoped(db); err != nil {
		return err
	}
	return nil
}

// DeleteRecord : delete a mesos namespace
func (namespace *Namespace) DeleteRecord() error {
	if err := namespace.RetriveRecord(); err != nil {
		return err
	}
	db := storage.GetDefaultSession().DB
	// delete record
	if err := namespace.DeleteUnscoped(db); err != nil {
		return err
	}
	return nil
}

// DeleteK8SClusterNamespaces :delete all namespace in k8s cluster
func DeleteK8SClusterNamespaces(projectID string, clusterID string) error {
	nsQuerySet := NewKubernetesNamespaceQuerySet(storage.GetDefaultSession().DB)
	nsQuerySet = nsQuerySet.ProjectIDEq(projectID).ClusterIDEq(clusterID)
	if err := nsQuerySet.DeleteUnscoped(); err != nil {
		return err
	}
	return nil
}

// DeleteMesosClusterNamespaces : delete all namespace in mesos cluster
func DeleteMesosClusterNamespaces(projectID string, clusterID string) error {
	nsQuerySet := NewNamespaceQuerySet(storage.GetDefaultSession().DB)
	nsQuerySet = nsQuerySet.ProjectIDEq(projectID).ClusterIDEq(clusterID)
	if err := nsQuerySet.DeleteUnscoped(); err != nil {
		return err
	}
	return nil
}

// CreateRecord : create k8s namespace record
func (namespace *KubernetesNamespace) CreateRecord() error {
	db := storage.GetDefaultSession().DB
	if err := namespace.Create(db); err != nil {
		return err
	}
	nsQuerySet := NewKubernetesNamespaceQuerySet(db)
	if err := nsQuerySet.NameEq(namespace.Name).One(namespace); err != nil {
		return err
	}
	return nil
}

// CreateRecord : create mesos namespace record
func (namespace *Namespace) CreateRecord() error {
	db := storage.GetDefaultSession().DB
	if err := namespace.Create(db); err != nil {
		return err
	}
	nsQuerySet := NewNamespaceQuerySet(db)
	if err := nsQuerySet.NameEq(namespace.Name).One(namespace); err != nil {
		return err
	}
	return nil
}

// UpdateRecord :
func (updater *K8SNamespaceUpdate) UpdateRecord() error {
	namespace := updater.Namespace
	nsQuerySet := NewKubernetesNamespaceQuerySet(storage.GetDefaultSession().DB)
	nsQuerySet = nsQuerySet.ProjectIDEq(namespace.ProjectID).ClusterIDEq(namespace.ClusterID).IDEq(namespace.ID)
	k8sUpdater := nsQuerySet.GetUpdater()
	k8sUpdater = k8sUpdater.SetNameWithEmpty(
		namespace.Name,
	).SetEnvTypeWithEmpty(
		namespace.EnvType,
	).SetStatusWithEmpty(
		namespace.Status,
	).SetDescription(namespace.Description)
	if updater.ImageSecretExist {
		k8sUpdater = k8sUpdater.SetHasImageSecret(namespace.HasImageSecret)
	}
	if err := k8sUpdater.Update(); err != nil {
		return err
	}
	if err := namespace.RetriveRecord(); err != nil {
		return err
	}
	return nil
}

// UpdateRecord :
func (updater *MesosNamespaceUpdate) UpdateRecord() error {
	namespace := updater.Namespace
	nsQuerySet := NewNamespaceQuerySet(storage.GetDefaultSession().DB)
	nsQuerySet = nsQuerySet.ProjectIDEq(namespace.ProjectID).ClusterIDEq(namespace.ClusterID).IDEq(namespace.ID)
	mesosUpdater := nsQuerySet.GetUpdater()
	mesosUpdater = mesosUpdater.SetNameWithEmpty(
		namespace.Name,
	).SetEnvTypeWithEmpty(
		namespace.EnvType,
	).SetStatusWithEmpty(
		namespace.Status,
	).SetDescription(namespace.Description)
	if updater.ImageSecretExist {
		mesosUpdater = mesosUpdater.SetHasImageSecret(namespace.HasImageSecret)
	}
	if err := mesosUpdater.Update(); err != nil {
		return err
	}
	if err := namespace.RetriveRecord(); err != nil {
		return err
	}
	return nil
}

// NamespaceListByProject : get namespace list by project id list
func NamespaceListByProject(projectIDList []string) (data []map[string]interface{}, err error) {
	db := storage.GetDefaultSession().DB
	// k8s
	k8sQuerySet := NewKubernetesNamespaceQuerySet(db)
	var k8sData []KubernetesNamespace
	if err := k8sQuerySet.ProjectIDInWithoutError(projectIDList...).All(&k8sData); err != nil {
		return nil, err
	}
	k8sSerializer := structomap.New().UseSnakeCase().Pick("ClusterID", "ProjectID", "ID", "Name")
	k8sMapList, err := k8sSerializer.TransformArray(k8sData)
	if err != nil {
		return nil, err
	}
	// mesos
	mesosQuerySet := NewNamespaceQuerySet(db)
	var mesosData []Namespace
	if err := mesosQuerySet.ProjectIDInWithoutError(projectIDList...).All(&mesosData); err != nil {
		return nil, err
	}
	mesosSerializer := structomap.New().UseSnakeCase().Pick("ClusterID", "ProjectID", "ID", "Name")
	mesosMapList, err := mesosSerializer.TransformArray(mesosData)
	if err != nil {
		return nil, err
	}
	// merge k8s and mesos data
	return append(k8sMapList, mesosMapList...), nil
}
