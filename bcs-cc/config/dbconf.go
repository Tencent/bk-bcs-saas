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

package config

import "os"

// DBConf :
type DBConf struct {
	Type         string `yaml:"type"`
	Host         string `yaml:"host"`
	Port         int    `yaml:"port"`
	User         string `yaml:"user"`
	Password     string `yaml:"password"`
	DBName       string `yaml:"db_name"`
	Charset      string `yaml:"charset"`
	MaxIdleConns int    `yaml:"max_idle_conns"`
	MaxOpenConns int    `yaml:"max_open_conns"`
	InstanceKey  string `yaml:"instance_key"`
}

// Init :
func (c *DBConf) Init() {
	port, _ := strconv.Atoi(os.Getenv("GCS_MYSQL_PORT"))
	c.Type = "mysql"
	c.Host = os.Getenv("GCS_MYSQL_HOST")
	c.Port = port
	c.User = os.Getenv("GCS_MYSQL_USER")
	c.Password = os.Getenv("GCS_MYSQL_PASSWORD")
	c.DBName = os.Getenv("GCS_MYSQL_NAME")

	c.MaxIdleConns = 10
	c.MaxOpenConns = 100
	c.Charset = "utf8"
}
