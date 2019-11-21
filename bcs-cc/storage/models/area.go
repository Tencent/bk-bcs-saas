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
	"encoding/json"

	"bcs_cc/logging"
	"bcs_cc/storage"
	"bcs_cc/utils"

	"github.com/jinzhu/gorm"
)

// Area : 用于存储不同区域配置信息
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type Area struct {
	Model
	Name          string `json:"name" gorm:"size:64;unique_index"`
	Description   string `json:"description" sql:"size:128"`
	Configuration string `json:"configuration" sql:"type:text"`
	ChineseName   string `json:"chinese_name" gorm:"size:64"`
	Source        string `json:"source" gorm:"size:32;default:'BCS'"`
}

// ListInfo : 获取区域列表
func ListInfo(source string) (data []Area, count int, err error) {
	qs := NewAreaQuerySet(storage.GetDefaultSession().DB)
	qs = qs.NameNotIn("sh2", "sz2")
	// filter with source filed
	qs = qs.CustomSourceEq(source)
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
func (area *Area) CreateOrUpdateRecord() error {
	db := storage.GetDefaultSession().DB
	// update
	if count, _ := NewAreaQuerySet(db).NameEq(area.Name).Count(); count > 0 {
		return area.UpdateRecord()
	}
	return area.CreateRecord()
}

// CreateRecord : create one record
func (area *Area) CreateRecord() error {
	db := storage.GetDefaultSession().DB
	if err := area.Create(db); err != nil {
		return err
	}
	return area.retriveRecodeByName(db)
}

// UpdateRecord : update one record
func (area *Area) UpdateRecord() error {
	db := storage.GetDefaultSession().DB
	// recode exist
	qs := NewAreaQuerySet(db).NameEq(area.Name)
	updater := qs.GetUpdater()
	updater = updater.SetDescription(area.Description)
	updater = updater.SetConfiguration(area.Configuration)
	updater = updater.SetChineseName(area.ChineseName)
	if err := updater.Update(); err != nil {
		return err
	}
	return area.retriveRecodeByName(db)
}

// RetriveRecord : retrive one record by name or id
func (area *Area) RetriveRecord() error {
	db := storage.GetDefaultSession().DB
	if area.Name != "" {
		return area.retriveRecodeByName(db)
	}
	return area.retriveRecodeByID(db)
}

func (area *Area) retriveRecodeByName(db *gorm.DB) error {
	qs := NewAreaQuerySet(db)
	return qs.NameEq(area.Name).One(area)
}

func (area *Area) retriveRecodeByID(db *gorm.DB) error {
	qs := NewAreaQuerySet(db)
	return qs.IDEq(area.ID).One(area)
}

// AreaListSLZ :
func AreaListSLZ(areaList []Area) ([]map[string]interface{}, error) {
	var data []map[string]interface{}
	for _, area := range areaList {
		slzData, err := AreaSLZ(area, true)
		if err != nil {
			return nil, err
		}
		data = append(data, slzData)
	}
	return data, nil
}

// AreaSLZ :
func AreaSLZ(area Area, jsonFormat bool) (map[string]interface{}, error) {
	var config map[string]interface{}
	if err := json.Unmarshal([]byte(area.Configuration), &config); err != nil {
		logging.Error("Cannot unmarshal the json ", err)
		return nil, err
	}
	if len(config) != 0 {
		dnsHost, ok := config["dnsHost"]
		if ok {
			switch v := dnsHost.(type) {
			case []interface{}:
				currDNSHost := utils.RandSelector(&v)
				config["dnsHost"] = currDNSHost
				break
			default:
				config["dnsHost"] = v
			}
		}
	}
	configureInfo := map[string]interface{}{
		"id":           area.ID,
		"name":         area.Name,
		"chinese_name": area.ChineseName,
		"description":  area.Description,
		"source":       area.Source,
	}
	// congigure info is json string or map
	if jsonFormat {
		// json serialize
		configJSON, err := json.Marshal(config)
		if err != nil {
			logging.Error("Marshal area configuration error", err)
			return nil, err
		}
		configureInfo["configuration"] = string(configJSON)
	} else {
		configureInfo["configuration"] = config
	}
	return configureInfo, nil
}
