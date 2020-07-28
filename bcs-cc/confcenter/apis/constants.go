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

package apis

// kind type list
var kindSlice = []string{"mesos", "k8s", "tke"}

var skipAppCode = "bcsclusterkeeper"

// cluster status list
var clusterStatusSlice = []string{"normal", "removable", "to_removed", "remove_failed"}

// default master status is initializing
var defaultMasterStatus = "initializing"

// cluster exclude status
var clusterFilterStataus = []string{"removed"}

// cluster type
var clusterTypeFromProject = map[uint]string{1: "k8s", 2: "mesos", 3: "k8s"}

var clusterIDRange = map[string]([]int){
	"mesos-stag":  []int{10000, 15000},
	"mesos-debug": []int{20000, 25000},
	"mesos-prod":  []int{30000, 399999},
	"k8s-stag":    []int{15001, 19999},
	"k8s-debug":   []int{25001, 29999},
	"k8s-prod":    []int{40000, 1000000},
}

// node exclude status
var nodeFilterStatus = []string{}

// node initlizing status
var nodeInitializingStatus = "initializing"

// project mesos kind
var mesosKind uint = 2

// empty flag
var nullParam = "null"

// develop run envrionment
var develop = "dev"
var stagClusterENV = "stag"
