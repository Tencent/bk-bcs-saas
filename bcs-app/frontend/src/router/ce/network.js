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

const Service = () => import(/* webpackChunkName: 'network' */'@open/views/network/service')
const LoadBalance = () => import(/* webpackChunkName: 'network' */'@open/views/network/loadbalance')
const LoadBalanceDetail = () => import(/* webpackChunkName: 'network' */'@open/views/network/loadbalance-detail')
const childRoutes = [
    {
        path: ':projectCode/service',
        name: 'service',
        component: Service
    },
    {
        path: ':projectCode/loadbalance',
        name: 'loadBalance',
        component: LoadBalance
    },
    {
        path: ':projectCode/loadbalance/:lbId/detail',
        name: 'loadBalanceDetail',
        component: LoadBalanceDetail
    }
]

export default childRoutes
