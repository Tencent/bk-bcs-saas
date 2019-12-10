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
	"bcs_cc/storage"
)

/*
# Node `status` desc
	- 未初始化 `uninitialized`
	- 初始化中 `initializing`
	- 正常状态 `normal`
	- 初始化失败 `initial_failed`
	- 待移除 `to_removed`
	- 可移除 `removable`
	- 移除中 `removing`
	- 移除失败 `remove_failed`
	- 已移除 `removed`

## node status flow
	`uninitialized` ==> `initializing`
	`initializing` ==> `initial_failed`
	`initializing` ==> `normal`
	`initial_failed` ==> `removed`
	`normal` ==> `to_removed`
	`to_removed` ==> `removable`
	`removable` ==> `removing`
	`removing` ==> `removed`
	`removing` ==> `remove_failed`
	`remove_failed` ==> `removing`
*/

// Node :
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
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

// NodeFilterData :
type NodeFilterData struct {
	ProjectID     string
	ClusterID     string
	InnerIPList   []string
	DesireAllData string
	Limit         int
	Offset        int
	ExcludeStatus []string
}

// GetClusterIDListByNode : get cluster id list
func GetClusterIDListByNode(projectID string, clusterIDList []string) ([]string, error) {
	// get cluster id
	clusterList, err := clusterListBase(ClusterFilterParams{
		ProjectID:     projectID,
		ClusterIDList: clusterIDList,
	})
	if err != nil {
		return nil, err
	}
	return getClusterIDList(clusterList), nil
}

// NodeList : list the node info
func (filter NodeFilterData) NodeList() (data []Node, count int, err error) {
	clusterIDList, err := GetClusterIDListByNode(filter.ProjectID, []string{filter.ClusterID})
	if err != nil {
		return nil, 0, err
	}
	nodeQuerySet := NewNodeQuerySet(storage.GetDefaultSession().DB)
	if len(clusterIDList) == 0 {
		nodeQuerySet = nodeQuerySet.ProjectIDEq(filter.ProjectID)
	}
	nodeQuerySet = nodeQuerySet.ClusterIDInWithoutError(clusterIDList...)
	if filter.DesireAllData != "1" {
		nodeQuerySet = nodeQuerySet.StatusNotInWithoutError(filter.ExcludeStatus...)
		nodeQuerySet = nodeQuerySet.InnerIPInWithoutError(filter.InnerIPList...)
	}
	count, err = nodeQuerySet.Count()
	if err != nil {
		return nil, 0, err
	}
	if filter.DesireAllData != "1" {
		nodeQuerySet = nodeQuerySet.Limit(filter.Limit).Offset(filter.Offset)
	}
	if err := nodeQuerySet.All(&data); err != nil {
		return nil, 0, err
	}
	return data, count, nil
}

// VerifyNodeExist : verify node exist
func VerifyNodeExist(clusterIDList []string, nodeIDList []uint) bool {
	nodeQuerySet := NewNodeQuerySet(storage.GetDefaultSession().DB)
	nodeQuerySet = nodeQuerySet.ClusterIDInWithoutError(clusterIDList...)
	var nodeList []Node
	if err := nodeQuerySet.IDIn(nodeIDList...).All(&nodeList); err != nil {
		return false
	}
	if len(nodeList) == len(nodeIDList) {
		return true
	}
	return false
}

// RetriveRecord :
func (node *Node) RetriveRecord() error {
	nodeQuerySet := NewNodeQuerySet(storage.GetDefaultSession().DB)
	if err := nodeQuerySet.IDEq(node.ID).One(node); err != nil {
		return err
	}
	return nil
}

// CreateRecord :
func (node *Node) CreateRecord() error {
	db := storage.GetDefaultSession().DB
	if err := node.Create(db); err != nil {
		return err
	}
	return nil
}

// BatchCreateRecord :
func BatchCreateRecord(data []Node) (nodeListInfo []Node, err error) {
	db := storage.GetDefaultSession().DB
	tx := db.Begin()
	for _, node := range data {
		if err := node.Create(tx); err != nil {
			tx.Rollback()
			return nil, err
		}
		nodeListInfo = append(nodeListInfo, node)
	}
	tx.Commit()
	return nodeListInfo, nil
}

// BatchUpdateRecord :
func BatchUpdateRecord(data []Node, excludeStatus []string) (nodeListInfo []Node, err error) {
	db := storage.GetDefaultSession().DB
	tx := db.Begin()
	var innerIPList []string
	nodeQuerySet := NewNodeQuerySet(tx).StatusNotInWithoutError(excludeStatus...)
	for _, node := range data {
		updater := nodeQuerySet.InnerIPEq(node.InnerIP).GetUpdater()
		updater = updater.SetProjectIDWithEmpty(node.ProjectID).SetClusterID(node.ClusterID)
		updater = updater.SetStatusWithEmpty(node.Status).SetDescription(node.Description)
		if err := updater.SetInstanceIDWithoutEmpty(node.InstanceID).Update(); err != nil {
			tx.Rollback()
			return nil, err
		}
		innerIPList = append(innerIPList, node.InnerIP)
	}
	tx.Commit()

	nodeQuerySet = NewNodeQuerySet(db).StatusNotInWithoutError(excludeStatus...).InnerIPIn(innerIPList...)
	if err := nodeQuerySet.All(&nodeListInfo); err != nil {
		return nil, err
	}
	return nodeListInfo, nil
}

// UpdateRecord :
func (node *Node) UpdateRecord() error {
	db := storage.GetDefaultSession().DB
	nodeQuerySet := NewNodeQuerySet(db).IDEq(node.ID)
	updater := nodeQuerySet.GetUpdater()
	updater = updater.SetStatusWithEmpty(node.Status).SetDescription(node.Description).SetName(node.Name)
	if err := updater.SetInstanceIDWithoutEmpty(node.InstanceID).Update(); err != nil {
		return err
	}
	if err := node.RetriveRecord(); err != nil {
		return err
	}
	return nil
}

// NodeListByCluster : search node info by cluster type
func NodeListByCluster(clusterIDList []string, excludeStatus []string) (data []Node, err error) {
	nodeQuerySet := NewNodeQuerySet(storage.GetDefaultSession().DB)
	nodeQuerySet = nodeQuerySet.ClusterIDInWithoutError(clusterIDList...).StatusNotInWithoutError(excludeStatus...)
	if err := nodeQuerySet.All(&data); err != nil {
		return nil, err
	}
	return data, nil
}

// UpdateNodeStatus : update node status, only status in [normal, not_ready, initializing]
// if ip in nodeIPList, set status as normal, else set not_ready
func UpdateNodeStatus(clusterID string, nodeIPList []string) error {
	db := storage.GetDefaultSession().DB
	queryset := NewNodeQuerySet(db).ClusterIDEq(clusterID).StatusIn("normal", "not_ready", "initializing")
	normalUpdater := queryset.InnerIPIn(nodeIPList...).GetUpdater()
	if err := normalUpdater.SetStatus("normal").Update(); err != nil {
		return err
	}
	notReadyUpdater := queryset.InnerIPNotIn(nodeIPList...).GetUpdater()
	if err := notReadyUpdater.SetStatus("not_ready").Update(); err != nil {
		return err
	}
	return nil
}
