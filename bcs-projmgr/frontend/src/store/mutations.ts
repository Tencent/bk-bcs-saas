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

/// <reference path='../typings/vuex.d.ts' />
import Vue from 'vue'
import { MutationTree } from 'vuex'
import {
    SET_USER_INFO,
    SET_PROJECT_LIST,
    FETCH_ERROR,
    SET_SERVICES,
    SET_LINKS,
    SET_DEMO_PROJECT,
    SET_DEMO_PIPELINE_ID,
    UPDATE_NEW_PROJECT,
    RESET_NEW_PROJECT,
    TOGGLE_PROJECT_DIALOG,
    SET_POPUP_SHOW,
    UPDATE_HEADER_CONFIG,
    CLOSE_PREVIEW_TIPS,
    TOGGLE_MODULE_LOADING,
    SET_PROJECT_INFO
} from './constants'

const mutations: MutationTree<RootState> = {
    [UPDATE_HEADER_CONFIG]: (state: RootState, headerConfig: object) => {
        Vue.set(state, 'headerConfig', {
            ...state.headerConfig,
            ...headerConfig
        })
        return state
    },
    [SET_USER_INFO]: (state: RootState, { user }: any) => {
        Vue.set(state, 'user', user)
        return state
    },
    [SET_PROJECT_LIST]: (state: RootState, { projectList }: any) => {
        Vue.set(state, 'projectList', projectList)
        return state
    },
    [SET_PROJECT_INFO]: (state: RootState, { projectInfo, hrefId }: any) => {
        Vue.set(state, 'hrefProjectId', projectInfo ? projectInfo.project_name : hrefId)
        return state
    },
    [SET_SERVICES]: (state: RootState, { services }: any) => {
        Vue.set(state, 'services', services)
        return state
    },
    [SET_LINKS]: (state: RootState, { links, type }: any) => {
        Vue.set(state, type, links)
        return state
    },
    [FETCH_ERROR]: (state: RootState, error: object) => {
        console.warn(error)
        Vue.set(state, 'fetchError', error)
    },
    [SET_DEMO_PROJECT]: (state: RootState, { project }: any) => {
        Vue.set(state, 'demo', {
            projectId: project.project_code,
            projectName: project.project_name
        })
        return state
    },
    [SET_DEMO_PIPELINE_ID]: (state: RootState, { pipelineId }: any) => {
        Vue.set(state, 'demo', {
            ...state.demo,
            pipelineId
        })
        return state
    },
    [UPDATE_NEW_PROJECT]: (state: RootState, payload: any) => {
        Vue.set(state, 'newProject', {
            ...state.newProject,
            ...payload
        })
        return state
    },
    [RESET_NEW_PROJECT]: (state: RootState, project: Project) => {
        Vue.set(state, 'newProject', {
            ...project
        })
        return state
    },
    [TOGGLE_PROJECT_DIALOG]: (state: RootState, payload: any) => {
        Vue.set(state, 'showProjectDialog', payload.showProjectDialog)
    },
    [SET_POPUP_SHOW]: (state: RootState, isAnyPopupShow: boolean) => {
        Vue.set(state, 'isAnyPopupShow', isAnyPopupShow)
    },
    [CLOSE_PREVIEW_TIPS]: (state: RootState) => {
        Vue.set(state, 'isShowPreviewTips', false)
    },
    [TOGGLE_MODULE_LOADING]: (state: RootState, moduleLoading: boolean) => {
        Vue.set(state, 'moduleLoading', moduleLoading)
    },
}

export default mutations
