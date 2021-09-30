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
)

// ZookeeperConfig : zookeeper configure
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type ZookeeperConfig struct {
	Model
	Name         string `json:"name" gorm:"size:32"`
	Desc         string `json:"desc" sql:"type:text"`
	Zookeeper    string `json:"zookeeper" sql:"type:text"`
	BCSZookeeper string `json:"bcs_zookeeper" sql:"type:text"`
	Environment  string `json:"environment" gorm:"size:8;unique_index"`
	Creator      string `json:"creator" gorm:"size:16"`
	Updator      string `json:"updator" gorm:"size:16"`
	Kind         uint8  `json:"kind" gorm:"default:2"`
}

// RetriveRecord : get a zk configure
func (zk *ZookeeperConfig) RetriveRecord() error {
	zkQuerySet := NewZookeeperConfigQuerySet(storage.GetDefaultSession().DB)
	if err := zkQuerySet.NameEqWithEmpty(zk.Name).EnvironmentEqEqWithEmpty(zk.Environment).One(zk); err != nil {
		return err
	}
	return nil
}

// ZKListInfo :
func ZKListInfo(environment string) (data []ZookeeperConfig, err error) {
	zkQuerySet := NewZookeeperConfigQuerySet(storage.GetDefaultSession().DB)
	if environment != "all" {
		zkQuerySet = zkQuerySet.EnvironmentEqEqWithEmpty(environment)
	}
	if err := zkQuerySet.All(&data); err != nil {
		return nil, err
	}
	return data, nil
}
