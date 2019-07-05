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

package confcenter

import (
	"fmt"
	"os"

	"bcs_cc/confcenter/metrics"
	"bcs_cc/config"
	"bcs_cc/storage"

	"github.com/gin-gonic/gin"
	"github.com/robfig/cron"
)

// Command : command for auth server
type Command struct {
	Engine *gin.Engine
}

func (c *Command) routeConf() {
	URLConf(c.Engine)
}

// ParseFlag : parse arguments
func (c *Command) ParseFlag() (string, error) {
	return "Run configure center server", nil
}

// Start : start to run
func (c *Command) Start() error {
	confBase := config.GlobalConfigurations
	confcenter := confBase.ConfCenter
	// DB Client
	dbSession := storage.GetDefaultSession()
	defer dbSession.Close()
	// Redis Client
	if !confBase.DisableEncrypt {
		redisSession := storage.GetDefaultRedisSession()
		defer redisSession.Close()
	}

	if !confBase.Debug {
		gin.SetMode(gin.ReleaseMode)
	}
	c.Engine = gin.Default()
	c.routeConf()

	if confBase.EnableClusterMetric {
		cronTask := cron.New()
		// set the time interval by config for crontab task
		cronSpec := fmt.Sprintf("@every %vs", confBase.Interval)
		cronTask.AddFunc(cronSpec, metrics.ClusterMetric)
		cronTask.Start()
		defer cronTask.Stop()
	}
	fmt.Fprintf(os.Stdout, "bcs cc is running ... \n")

	return c.Engine.Run(
		fmt.Sprintf("%v:%v", confcenter.Host, confcenter.Port),
	)
}
