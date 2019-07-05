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

import Vue from 'vue'
import Vuex from 'vuex'
import getters from './getters'
import actions from './actions'
import mutations from './mutations'
import { transformObj } from '../utils/util'
import {
    EMPTY_PROJECT
} from './constants'

const allServices: ObjectMap[] = window.allServices
const projectList: ObjectMap[] = window.projectList
const userInfo: User = transformObj(window.userInfo)
const modules:ObjectMap = {}


for(let key in window.Pages) {
    modules[key] = window.Pages[key].store
}
Vue.use(Vuex)
export default new Vuex.Store<RootState>({
    modules,
    mutations,
    actions,
    getters,
    state: {
        projectList,
        fetchError: null,
        moduleLoading: false,
        user: userInfo,
        services: allServices,
        related: null,
        news: null,
        demo: null,
        showProjectDialog: false,
        isAnyPopupShow: false,
        isShowPreviewTips: true,
        newProject: {
            ...EMPTY_PROJECT
        },
        headerConfig: {
            showProjectList: false,
            showNav: true
        }
    }
})
