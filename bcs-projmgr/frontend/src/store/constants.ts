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

export const SET_USER_INFO: string = 'SET_USER_INFO'
export const SET_PROJECT_LIST: string = 'SET_PROJECT_LIST'
export const FETCH_ERROR: string = 'FETCH_ERROR'
export const SET_SERVICES: string = 'SET_SERVICES'
export const SET_LINKS: string = 'SET_LINKS'
export const SET_DEMO_PROJECT: string = 'SET_DEMO_PROJECT'
export const SET_DEMO_PIPELINE_ID: string = 'SET_DEMO_PIPELINE_ID'
export const UPDATE_NEW_PROJECT: string = 'UPDATE_NEW_PROJECT'
export const TOGGLE_PROJECT_DIALOG: string = 'TOGGLE_PROJECT_DIALOG'
export const UPDATE_PROJECT_MUTATION: string = 'UPDATE_PROJECT_MUTATION'
export const RESET_NEW_PROJECT: string = 'RESET_NEW_PROJECT'
export const SET_POPUP_SHOW = 'SET_POPUP_SHOW'
export const UPDATE_HEADER_CONFIG = 'UPDATE_HEADER_CONFIG'
export const CLOSE_PREVIEW_TIPS = 'CLOSE_PREVIEW_TIPS'
export const TOGGLE_MODULE_LOADING = 'TOGGLE_MODULE_LOADING'
export const SET_PROJECT_INFO = 'SET_PROJECT_INFO'

export const PROJECT_API_URL_PREFIX = 'api/nav'

// 服务列表
const serviceList = [
    'backend',
    'support',
    'process',
    'plugin',
    'artifactory',
    'dispatch',
    'environment',
    'log',
    'measure',
    'notify',
    'repository',
    'ticket'
]
export const [
    BACKEND_API_URL_PREFIX,
    SUPPORT_API_URL_PREFIX,
    PROCESS_API_URL_PREFIX,
    PLUGIN_API_URL_PREFIX,
    ARTIFACTORY_API_URL_PREFIX,
    DISPATCH_API_URL_PREFIX,
    ENVIRONMENT_API_URL_PREFIX,
    LOG_API_URL_PREFIX,
    MEASURE_API_URL_PREFIX,
    NOTIFY_API_URL_PREFIX,
    REPOSITORY_API_URL_PREFIX,
    TICKET_API_URL_PREFIX
] = serviceList.map(s => `${s}/api`)

export const EMPTY_PROJECT: Project = {
    project_name: '',
    english_name: '',
    project_type: '',
    description: '',
    bg_id: '',
    bg_name: '',
    dept_id: '',
    dept_name: '',
    center_id: '',
    center_name: '',
    is_secrecy: false,
    deploy_type: [],
    kind: '0'
}
