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

import { ActionTree, ActionContext } from 'vuex'
import Request from '../utils/request'
import {
    SET_USER_INFO,
    SET_PROJECT_LIST,
    FETCH_ERROR,
    SET_LINKS,
    SET_DEMO_PROJECT,
    SET_DEMO_PIPELINE_ID,
    UPDATE_NEW_PROJECT,
    TOGGLE_PROJECT_DIALOG,
    BACKEND_API_URL_PREFIX,
    PROCESS_API_URL_PREFIX,
    PROJECT_API_URL_PREFIX,
    SUPPORT_API_URL_PREFIX,
    EMPTY_PROJECT,
    RESET_NEW_PROJECT,
    SET_POPUP_SHOW,
    UPDATE_HEADER_CONFIG,
    CLOSE_PREVIEW_TIPS,
    TOGGLE_MODULE_LOADING,
    SET_PROJECT_INFO
} from './constants'

const actions: ActionTree<RootState, any> = {
    toggleModuleLoading({ commit }: ActionContext<RootState, any>, moduleLoading: boolean) {
        commit(TOGGLE_MODULE_LOADING, moduleLoading)
    },
    upadteHeaderConfig({ commit }: ActionContext<RootState, any>, headerConfig: object) {
        commit(UPDATE_HEADER_CONFIG, headerConfig)
    },
    setUserInfo({ commit }: ActionContext<RootState, any>, payload: any) {
        commit(SET_USER_INFO, payload)
    },
    async toggleServiceCollect({ commit }: ActionContext<RootState, any>, { serviceId, isCollected }: any) {
        return Request.put(`${PROJECT_API_URL_PREFIX}/user/services/${serviceId}?collector=${isCollected}`)
    },
    async fetchLinks({ commit }, { type }) {
        try {
            const links = await Request.get(`${PROJECT_API_URL_PREFIX}/user/activities/types/${type}`)
            commit(SET_LINKS, {
                links,
                type
            })
        } catch (e) {
            commit(FETCH_ERROR, e)
        }
    },
    createDemo({ commit }, payload) {
        return Request.post(`${PROCESS_API_URL_PREFIX}/user/accesses/`, payload)
    },
    async getProjects({ commit }) {
        const projectList = await Request.get(`${PROJECT_API_URL_PREFIX}/user/projects/`)
        commit(SET_PROJECT_LIST, { projectList })
    },
    checkProjectField({ commit }, { field, value, projectId }) {
        if (field === 'project_name') {
            return Request.get(`${PROJECT_API_URL_PREFIX}/user/projects/${field}/validate/?project_name=${value}${projectId ? `&project_id=${projectId}` : ''}`)
        } else {
            return Request.get(`${PROJECT_API_URL_PREFIX}/user/projects/${field}/${value}/validate/`)
        }
    },
    getDepartmentInfo({ commit }, { type, id }) {
        return Request.get(`${PROJECT_API_URL_PREFIX}/user/organizations/types/${type}/ids/${id}`)
    },
    ajaxUpdatePM({ commit }, { id, data }) {
        return Request.put(`${PROJECT_API_URL_PREFIX}/user/projects/${id}/`, data)
    },
    ajaxAddPM({ commit }, data) {
        return Request.post(`${PROJECT_API_URL_PREFIX}/user/projects/`, data)
    },
    async ajaxCheckProjectId({ commit }, hrefId) {
        const projectInfo = await Request.get(`${PROJECT_API_URL_PREFIX}/user/projects/getProjectByCode/${hrefId}`)
        commit(SET_PROJECT_INFO, { projectInfo, hrefId })
    },
    getMyDepartmentInfo({ commit }, projectId) {
        return Request.get(`${PROJECT_API_URL_PREFIX}/user/users/detail/`)
    },
    selectDemoProject({ commit }, { project }) {
        commit(SET_DEMO_PROJECT, {
            project
        })
    },
    setDemoPipelineId({ commit }, { pipelineId }) {
        commit(SET_DEMO_PIPELINE_ID, {
            pipelineId
        })
    },
    updateNewProject({ commit }, payload) {
        commit(UPDATE_NEW_PROJECT, payload)
    },
    resetNewProject({ commit }, project = EMPTY_PROJECT) {
        commit(RESET_NEW_PROJECT, project)
    },
    toggleProjectDialog({ commit, dispatch }, payload) {
        commit(RESET_NEW_PROJECT, payload.project || EMPTY_PROJECT)
        commit(TOGGLE_PROJECT_DIALOG, payload)
    },
    togglePopupShow({ commit, dispatch }, payload) {
        commit(SET_POPUP_SHOW, payload)
    },
    getDocList({ commit }) {
        return Request.get(`${BACKEND_API_URL_PREFIX}/ci/docs/?format=json`)
    },
    changeProjectLogo({ commit }, { projectId, formData }) {
        return Request.put(`${PROJECT_API_URL_PREFIX}/user/projects/${projectId}/logo/`, formData)
    },
    closePreviewTips({ commit, dispatch }) {
        commit(CLOSE_PREVIEW_TIPS);
    },
    getAnnouncement({ commit }) {
        return Request.get(`${SUPPORT_API_URL_PREFIX}/user/notice/valid`)
    }
}

export default actions
