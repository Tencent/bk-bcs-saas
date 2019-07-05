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

import (
	"errors"
	"fmt"
	"io/ioutil"
	"os"

	yaml "gopkg.in/yaml.v2"
)

// Mode :
var Mode = "default"

// Debug is false by default
var Debug = false

// AvailableEnvironmentFlags : set the cluster env
var AvailableEnvironmentFlags = []string{"prod", "stag"}

// ConfVersion : configuration version
var ConfVersion = "v1.0.0"

// DefaultIntervalUnit : interval
var DefaultIntervalUnit = 60

// DisableEncrypt : db/redis pwd encrypt or not
var DisableEncrypt = false

// CCAppCode : app code
var CCAppCode = ""

// CCAppSecret : app secret
var CCAppSecret = ""

// BCSHost : bcs host info
var BCSHost = ""

// JWTPath : jwt public info
var JWTPath = ""

// SKIPAPPCODE : skip app code
var SKIPAPPCODE = []string{}

// DESIGNATEDAPPCODE : Designated app code in order to get project id from url
var DESIGNATEDAPPCODE = ""

// EnableClusterMetric : update cluster metric info
var EnableClusterMetric = true

// RunENV: current run env
var RunENV = "prod"

// Configurations : manage all configurations
type Configurations struct {
	Version                   string   `yaml:"version"`
	Location                  string   `yaml:"location"`
	Debug                     bool     `yaml:"debug"`
	AvailableEnvironmentFlags []string `yaml:"available_environment_flags"`
	SKIPAPPCODE               []string `yaml:"skip_app_code"`
	DESIGNATEDAPPCODE         string   `yaml:"cluster_keeper_app_code"`
	// access auth api
	AuthConf *AuthConfInfo `yaml:"authconf"`
	// db conf
	Database *DBConf `yaml:"database"`
	// configure center conf
	ConfCenter *ConfCenter `yaml:"confcenter"`
	// redis conf
	RedisConf *RedisConf `yaml:"redisconf"`
	// log conf
	Logging *LogConf `yaml:"logging"`
	// interval time
	Interval int `yaml:"interval"`
	//DisableEncrypt
	DisableEncrypt bool `yaml:"disable_encrypt"`

	CCAppCode   string `yaml:"app_code"`
	CCAppSecret string `yaml:"app_secret"`

	JWTPath string `yaml:"jwt_path"`

	EnableClusterMetric bool `yaml:"enable_cluster_metric"`

	// apigw conf
	APIGWConf *APIGWConfInfo `yaml:"apigwconf"`

	RunENV string `yaml:"run_env"`
}

// Init : init all configurations
func (c *Configurations) Init() error {
	c.Version = ConfVersion
	c.Location = "Local"
	c.Debug = Debug
	c.AvailableEnvironmentFlags = AvailableEnvironmentFlags
	c.SKIPAPPCODE = SKIPAPPCODE
	c.DESIGNATEDAPPCODE = DESIGNATEDAPPCODE

	// main process
	c.ConfCenter = &ConfCenter{}
	c.ConfCenter.Init()

	// db
	c.Database = &DBConf{}
	c.Database.Init()

	// redis
	c.RedisConf = &RedisConf{}
	c.RedisConf.Init()

	// logging
	c.Logging = &LogConf{}
	c.Logging.Init()

	// auth
	c.AuthConf = &AuthConfInfo{}
	c.AuthConf.Init()

	// apigw
	c.APIGWConf = &APIGWConfInfo{}
	c.APIGWConf.Init()

	c.Interval = DefaultIntervalUnit

	c.DisableEncrypt = DisableEncrypt
	c.CCAppCode = CCAppCode
	c.CCAppSecret = CCAppSecret

	c.JWTPath = JWTPath
	c.EnableClusterMetric = EnableClusterMetric
	c.RunENV = RunENV

	return nil
}

// GlobalConfigurations :
var GlobalConfigurations = &Configurations{}

// ReadFrom : read from file
func (c *Configurations) ReadFrom(path string) error {
	c.Init()

	data, err := ioutil.ReadFile(path)
	if err != nil {
		return err
	}
	err = yaml.Unmarshal(data, &GlobalConfigurations)
	if err != nil {
		return err
	}
	if GlobalConfigurations.Version != ConfVersion {
		return errors.New("Version unknown")
	}
	return nil
}

// Command : command to print config
type Command struct{}

// ParseFlag : parse flag
func (c *Command) ParseFlag() (string, error) {
	return "Print cofiguration", nil
}

// Start : print cofigurations
func (c *Command) Start() error {
	data, err := yaml.Marshal(&GlobalConfigurations)
	if err != nil {
		return err
	}
	fmt.Fprintf(os.Stdout, "\nservice configuration\n: %s\n", string(data))
	return nil
}
