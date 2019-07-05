/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

// 集群首页
const Cluster = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster')
// 创建集群
const ClusterCreate = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/create.external')
// 集群总览
const ClusterOverview = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/overview')
// 节点详情
const ClusterNode = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/node.external')
// 集群信息
const ClusterInfo = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/info')
const ClusterNodeOverview = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/node-overview')
const ContainerDetailForNode = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/container')

const childRoutes = [
    {
        path: ':projectCode',
        redirect: {
            name: 'clusterMain'
        }
    },
    {
        path: ':projectCode/',
        redirect: {
            name: 'clusterMain'
        }
    },
    // domain/bcs/projectId => domain/bcs/projectCode/cluster 容器服务的首页是具体项目的集群页面
    // 集群首页
    {
        path: ':projectCode/cluster',
        name: 'clusterMain',
        component: Cluster
    },
    // 创建集群
    {
        path: ':projectCode/cluster/create',
        name: 'clusterCreate',
        component: ClusterCreate
    },
    // 集群总览
    {
        path: ':projectCode/cluster/:clusterId/overview',
        name: 'clusterOverview',
        component: ClusterOverview,
        alias: ':projectCode/cluster/:clusterId'
    },
    // 集群里的节点列表
    {
        path: ':projectCode/cluster/:clusterId/node',
        name: 'clusterNode',
        component: ClusterNode
    },
    // 集群里的集群信息
    {
        path: ':projectCode/cluster/:clusterId/info',
        name: 'clusterInfo',
        component: ClusterInfo
    },
    // 集群里的具体节点
    {
        path: ':projectCode/cluster/:clusterId/node/:nodeId',
        name: 'clusterNodeOverview',
        component: ClusterNodeOverview
    },
    // 节点详情页面跳转的容器详情页面
    {
        path: ':projectCode/cluster/:clusterId/node/:nodeId/container/:containerId',
        name: 'containerDetailForNode',
        component: ContainerDetailForNode
    }
]

export default childRoutes
