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

const Depot = () => import(/* webpackChunkName: 'depot' */'@open/views/depot')
const ImageLibrary = () => import(/* webpackChunkName: 'depot' */'@open/views/depot/image-library')
const ImageDetail = () => import(/* webpackChunkName: 'depot' */'@open/views/depot/image-detail')
const ProjectImage = () => import(/* webpackChunkName: 'depot' */'@open/views/depot/project-image')

const childRoutes = [
    // 这里没有把 depot 作为 cluster 的 children
    // 是因为如果把 depot 作为 cluster 的 children，那么必须要在 Cluster 的 component 中
    // 通过 router-view 来渲染子组件，但在业务逻辑中，depot 和 cluster 是平级的
    {
        path: ':projectCode/depot',
        name: 'depotMain',
        component: Depot,
        children: [
            // domain/bcs/projectCode/depot => domain/bcs/projectCode/depot/image-library
            {
                path: 'image-library',
                component: ImageLibrary,
                name: 'imageLibrary',
                alias: ''
            },
            {
                path: 'image-detail',
                component: ImageDetail,
                name: 'imageDetail',
                alias: ''
            },
            {
                path: 'project-image',
                name: 'projectImage',
                component: ProjectImage
            }
        ]
    }
]

export default childRoutes
