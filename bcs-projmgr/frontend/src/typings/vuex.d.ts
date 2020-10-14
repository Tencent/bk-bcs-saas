
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

/// <reference path='./index.d.ts' />
interface RootState {
    services: object[]
    user: object | null
    projectList: object[] | null
    related: Link[] | null
    news: Link[] | null
    demo: Demo | null
    newProject: Project | null
    showProjectDialog: boolean
    isAnyPopupShow: boolean
    isShowPreviewTips: boolean
    fetchError: object
    headerConfig: object,
    moduleLoading: boolean
}

interface Link {
    name: string
    link: string
    create_time: string
}

interface Demo {
    projectId: string
    projectName: string
    pipelineId: string
}

interface Project {
    project_code?: string
    project_id?: string
    project_name: string
    english_name: string
    description: string
    project_type: string
    use_bk?: boolean
    cc_app_id?: number
    deploy_type?: object[]
    kind?: string
    bg_id?: string
    bg_name?: string
    dept_id?: string
    dept_name?: string
    center_id?: string
    center_name?: string
    is_secrecy?: boolean
    cc_app_name?: string
    approval_status?: number
    is_offlined?: boolean
    permissions?: object
}
