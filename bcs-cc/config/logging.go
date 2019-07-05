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

// LogConf : config for logging
type LogConf struct {
	Level      string `yaml:"level"`
	FileDir    string `yaml:"file_dir"`
	MaxSize    uint64 `yaml:"max_size"`
	Stderr     bool   `yaml:"stderr"`
	LogToRedis bool   `yaml:"log_to_redis"`
}

// Init : init default logging config
func (c *LogConf) Init() error {
	// only for development
	c.Level = "info"
	c.FileDir = ""
	c.MaxSize = 1
	c.Stderr = true
	c.LogToRedis = true
	return nil
}
