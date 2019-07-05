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

import depotRoutes from './depot'
import mcRoutes from './mc'
import nodeRoutes from './node'
import resourceRoutes from './resource'
import clusterRoutes from './cluster'
import appRoutes from './app'
import configurationRoutes from './configuration'
import networkRoutes from './network'
import helmRoutes from './helm'

const ContainerServiceEntry = () => import(/* webpackChunkName: 'containerserviceentry' */'@open/views')
const None = () => import(/* webpackChunkName: 'none' */'@open/views/none')

const children = clusterRoutes.concat(
    nodeRoutes,
    appRoutes,
    configurationRoutes,
    networkRoutes,
    resourceRoutes,
    depotRoutes,
    mcRoutes,
    helmRoutes
)

export const routes = [
    {
        // domain/bcs
        // path: '/bcs',
        path: `${SITE_URL}`,
        name: 'containerServiceMain',
        component: ContainerServiceEntry,
        children: children
    },
    // 404
    {
        path: '*',
        name: '404',
        component: None
    }
]
