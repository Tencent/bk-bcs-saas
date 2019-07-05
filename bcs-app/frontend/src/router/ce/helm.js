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

// Helm应用列表
const helms = () => import(/* webpackChunkName: 'helm' */'@open/views/helm')

// Helm模板列表
const helmTplList = () => import(/* webpackChunkName: 'helm' */'@open/views/helm/tpl-list.vue')

// Helm模板详情
const helmTplDetail = () => import(/* webpackChunkName: 'helm' */'@open/views/helm/tpl-detail.vue')

// Helm实例化
const helmTplInstance = () => import(/* webpackChunkName: 'helm' */'@open/views/helm/tpl-instance.vue')

// Helm app详情
const helmAppDetail = () => import(/* webpackChunkName: 'helm' */'@open/views/helm/app-detail.vue')

const childRoutes = [
    {
        path: ':projectCode/helm',
        name: 'helms',
        component: helms
    },
    {
        path: ':projectCode/helm/list',
        name: 'helmTplList',
        component: helmTplList
    },
    {
        path: ':projectCode/helm/tpl/:tplId',
        name: 'helmTplDetail',
        component: helmTplDetail
    },
    {
        path: ':projectCode/helm/instance/:tplId',
        name: 'helmTplInstance',
        component: helmTplInstance
    },
    {
        path: ':projectCode/helm/app/:appId',
        name: 'helmAppDetail',
        component: helmAppDetail
    }
]

export default childRoutes
