/*
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 *
 */

import { GetterTree } from 'vuex'
import { isShallowEqual } from '../utils/util'
import { EMPTY_PROJECT } from './constants'


const getters: GetterTree<RootState, any> = {
    getCollectServices: (state: RootState) => {
        return state.services.reduce((collects: any, service: any) => {
            Array.isArray(service.children) && service.children.map((child: any) => {
               if (child.collected) {
                    collects.push(child)
               }
            })
            return collects
        }, [])
    },

    isEmptyProject: (state: RootState) => (project: Project): boolean => {
        return isShallowEqual(project, EMPTY_PROJECT)
    },

    onlineProjectList: (state: RootState) => {
        return state.projectList.filter((project: ObjectMap) => project.approval_status === 2 && !project.is_offlined && project.permission !== false)
    },

    approvalingProjectList: (state: RootState) => {
        return state.projectList.filter((project: ObjectMap) => project.approval_status === 1 )
    }
    
    
}

export default getters