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

	"github.com/jinzhu/gorm"
	"github.com/tuvistavie/structomap"
)

// ManagerMaster : cluster master info
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
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

// CheckInnerIPList : check inner ip
// if isExist is true, the length of innerIPList must be equal masterList
// else the length of masterList must be zore
func CheckInnerIPList(innerIPList []string, isExist bool) error {
	qs := NewManagerMasterQuerySet(storage.GetDefaultSession().DB)
	masterList := []ManagerMaster{}
	if err := qs.InnerIPIn(innerIPList...).All(&masterList); err != nil {
		return err
	}
	masterListLength := len(masterList)
	if isExist {
		if masterListLength != len(innerIPList) {
			return errors.New("replace inner ips do not exist")
		}
	} else {
		if masterListLength != 0 {
			return errors.New("new inner ips exist")
		}
	}
	return nil
}

// MasterList :
func MasterList(clusterIDList []string, filterWithClusterID bool) ([]map[string]interface{}, error) {
	qs := NewManagerMasterQuerySet(storage.GetDefaultSession().DB)
	masterList := []ManagerMaster{}
	if err := qs.ClusterIDInWithoutError(filterWithClusterID, clusterIDList...).All(&masterList); err != nil {
		return nil, err
	}
	serializer := structomap.New().UseSnakeCase().Pick("ClusterID", "InnerIP", "Status")
	return serializer.TransformArray(masterList)
}

// MasterFilter : Master params
type MasterFilter struct {
	ProjectID string
	ClusterID string
	InnerIP   string
}

// MasterDetailListWithCount :
func (filter *MasterFilter) MasterDetailListWithCount() (masterList []ManagerMaster, count int, err error) {
	qs := NewManagerMasterQuerySet(storage.GetDefaultSession().DB)
	qs = qs.ClusterMasterFilter(map[string]string{
		"project_id": filter.ProjectID,
		"cluster_id": filter.ClusterID,
		"inner_ip":   filter.InnerIP,
	}, masterFilterString)
	count, err = qs.Count()
	if err != nil {
		return nil, 0, err
	}
	if err := qs.All(&masterList); err != nil {
		return nil, 0, err
	}
	return masterList, count, nil
}

// CreateRecord : create one record
func (master *ManagerMaster) CreateRecord() error {
	db := storage.GetDefaultSession().DB
	if err := ValidateProjectCluster(master.ProjectID, master.ClusterID); err != nil {
		return err
	}
	if err := master.Create(db); err != nil {
		return err
	}
	return master.RetriveRecord()
}

// CreateRecordWithDB : create one record
func (master *ManagerMaster) CreateRecordWithDB(db *gorm.DB) error {
	if err := master.Create(db); err != nil {
		return err
	}
	return nil
}

// UpdateRecord : update one record
func (master *ManagerMaster) UpdateRecord() error {
	db := storage.GetDefaultSession().DB
	qs := NewManagerMasterQuerySet(db).InnerIPEq(master.InnerIP)
	updater := qs.GetUpdater()
	if err := updater.SetStatus(master.Status).SetInstanceIDWithoutEmpty(master.InstanceID).Update(); err != nil {
		return err
	}
	return master.RetriveRecord()
}

// RetriveRecord : fetch a record
func (master *ManagerMaster) RetriveRecord() error {
	qs := NewManagerMasterQuerySet(storage.GetDefaultSession().DB)
	return qs.ProjectIDEqWithNull(master.ProjectID).InnerIPEq(master.InnerIP).One(master)
}

// BatchCreateMasterRecords :
func BatchCreateMasterRecords(batchMasterInfo []ManagerMaster) error {
	db := storage.GetDefaultSession().DB
	// Transaction
	tx := db.Begin()
	for _, master := range batchMasterInfo {
		if err := tx.Create(&master).Error; err != nil {
			tx.Rollback()
			return err
		}
	}
	tx.Commit()
	return nil
}

// ReplaceMaster : replace existing ip by new ip
// 1. delete the existing ip list
// 2. add new ip list
func ReplaceMaster(replaceInnerIPList []string, NewMasterInfo []ManagerMaster) error {
	db := storage.GetDefaultSession().DB
	tx := db.Begin()
	// delete existing master
	qs := NewManagerMasterQuerySet(tx).InnerIPIn(replaceInnerIPList...)
	if err := qs.DeleteUnscoped(); err != nil {
		tx.Rollback()
		return err
	}
	// add new master
	for _, master := range NewMasterInfo {
		if err := tx.Create(&master).Error; err != nil {
			tx.Rollback()
			return err
		}
	}
	tx.Commit()
	return nil
}

// DeleteRecord : delete a record
func (master *ManagerMaster) DeleteRecord() error {
	qs := NewManagerMasterQuerySet(storage.GetDefaultSession().DB)
	qs = qs.ProjectIDEqWithNull(master.ProjectID).ClusterIDEq(master.ClusterID)
	return qs.InnerIPEq(master.InnerIP).DeleteUnscoped()
}
