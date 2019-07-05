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

interface User {
    [index: string]: any
    id?: string
    isAuthenticated?: boolean
    username?: string
    avatarUrl?: string
    chineseName?: string
    phone?: string
    email?: string
}

interface ObjectMap {
    [index: string]: any
}

interface Route {
    path: string,
    name: string,
    component: any,
    children: any[],
    meta: any
}
interface Window {
    Pages: any
    eventBus: object
    devops: object
    iframeUtil: ObjectMap
    allServices: ObjectMap[]
    projectList: ObjectMap[]
    serviceObject: ObjectMap
    currentPage: subService
    userInfo: User
    attachEvent(event: string, listener: EventListener): boolean
    detachEvent(event: string, listener: EventListener): void
}
interface subService {
    collected: boolean
    css_url: string
    id: string
    iframe_url: string
    inject_type: string
    show_project_list: boolean
    show_nav: boolean
    js_url: string
    link: string
    name: string
    status: string
    link_new: string
}

interface Permission {
    resource: string
    option: string
}


declare const LOGIN_SERVICE_URL: string
declare const GW_URL_PREFIX: string
declare const DOCS_URL_PREFIX: string
declare const DEVOPS_LS_VERSION: string
declare module '*.png'
declare const require: any

