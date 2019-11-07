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

// BCSConf : bcs conf
type BCSConf struct {
	Hosts                   map[string]string `yaml:"hosts"`
	MesosResourcePath       string            `yaml:"mesos_resource_path"`
	K8sQueryClusterIDPath   string            `yaml:"k8s_query_cluster_id_path"`
	K8sQueryCredentialsPath string            `yaml:"k8s_query_credentials_path"`
	K8sQueryNodesPath       string            `yaml:"k8s_query_nodes_path"`
	Authorization           string            `yaml:"authorization"`
}

// Init : init default redis config
func (c *BCSConf) Init() error {
	// only for development
	c.Hosts = map[string]string{}
	c.MesosResourcePath = ""
	c.K8sQueryClusterIDPath = ""
	c.K8sQueryCredentialsPath = ""
	c.K8sQueryNodesPath = ""
	c.Authorization = ""
	return nil
}
