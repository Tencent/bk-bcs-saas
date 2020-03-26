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

// HandleMigrate200325203634 :
func (c *MigrationCommand) HandleMigrate200325203634(db *gorm.DB) error {
	type Model struct {
		ID        uint `gorm:"primary_key"`
		CreatedAt time.Time
		UpdatedAt time.Time
		DeletedAt *time.Time
		Extra     string `json:"extra" sql:"type:text"`
	}

	type BcsServiceConf struct {
		Model
		KindName      string `json:"kind_name" gorm:"size:16"`
		Environment   string `json:"environment" gorm:"size:16;unique_index:uix_kind_name_environment"`
		Description   string `json:"description" sql:"size:256"`
		Configuration string `json:"configuration" sql:"type:text"`
		Creator       string `json:"creator" gorm:"size:32"`
	}

	return db.AutoMigrate(&BcsServiceConf{}).Error
}

// HandleRollback200325203634 : rollback handler for HandleMigrate200325203634
func (c *MigrationCommand) HandleRollback200325203634(db *gorm.DB) error {
	return nil
}
