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

package storage

import (
	"fmt"

	"bcs-cc/bkcrypt"
	"bcs-cc/config"

	"github.com/jinzhu/gorm"
	// import pkg :
	_ "github.com/jinzhu/gorm/dialects/mysql"
)

// DBSession :
type DBSession struct {
	DB *gorm.DB
}

// Open :
func (db *DBSession) Open() error {
	var (
		dbConfig = config.GlobalConfigurations.Database
		err      error
	)

	dbhost := fmt.Sprintf("tcp(%s:%d)", dbConfig.Host, dbConfig.Port)
	var pwd string
	if config.GlobalConfigurations.DisableEncrypt {
		pwd = dbConfig.Password
	} else {
		pwd = bkcrypt.Decrypt(dbConfig.InstanceKey, dbConfig.Password)
	}

	db.DB, err = gorm.Open(dbConfig.Type, fmt.Sprintf(
		"%s:%s@%s/%s?charset=%s&parseTime=True&loc=%s",
		dbConfig.User,
		pwd,
		dbhost,
		dbConfig.DBName,
		dbConfig.Charset,
		config.GlobalConfigurations.Location,
	))
	if err != nil {
		return err
	}

	sqldb := db.DB.DB()
	sqldb.SetMaxIdleConns(dbConfig.MaxIdleConns)
	sqldb.SetMaxOpenConns(dbConfig.MaxOpenConns)
	sqldb.Ping()

	if config.Debug {
		db.DB.LogMode(true)
	}

	return nil

}

// Close :
func (db *DBSession) Close() {
	if db.DB != nil {
		db.DB.Close()
	}
}
