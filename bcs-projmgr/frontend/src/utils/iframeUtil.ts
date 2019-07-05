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

import eventBus from "./eventBus"

interface UrlParam {
    url: string
    refresh: boolean
}

function iframeUtil (router: any) {
    let utilMap: ObjectMap = {}
    function init () {
        if (window.addEventListener) {   
            window.addEventListener('message', onMessage) 
        } else if (window.attachEvent) {   
            window.attachEvent('onmessage', onMessage)
        } 
    }

    function onMessage (e) {
        // if (/\.oa\.com(\:\d+)?$/.test(e.origin)) {
            parseMessage(e.data)
        // }
    }

    function send (target, action, params) {
        target.postMessage({
            action,
            params
        }, '*') 
    }

    utilMap.syncUrl = function ({url, refresh = false}: UrlParam): void {
        const pathname = `${location.pathname.replace(/^\/(\w+)\/(\w+)\/(\S+)$/, '/$1/$2')}${url}`
        
        if (refresh) {
            location.pathname = pathname
        } else {
            router.replace(pathname)
        }
    }

    utilMap.showAskPermissionDialog = function (params) {
        eventBus.$showAskPermissionDialog(params)
    }

    utilMap.toggleLoginDialog = function (isShow) {
        eventBus.$emit('toggle-login-dialog', isShow)
    }

    utilMap.popProjectDialog = function (project: Project): void {
        eventBus.$emit('show-project-dialog', project)
    }
 
    utilMap.toggleProjectMenu = function (show): void {
        show ? eventBus.$emit('show-project-menu') : eventBus.$emit('hide-project-menu')
    }

    utilMap.syncTopProjectId = function ({ projectId }): void {
        eventBus.$emit('update-project-id', projectId)
    }

    utilMap.showTips = function (tips): void {
        if (tips.message === 'Network Error') {
            tips.message = '网络出现问题，请检查你的网络是否正常'
        }
        tips.message = tips.message || tips.msg || ''
        eventBus.$bkMessage(tips)
    }
 
    utilMap.syncProjectList = function (target, projectList: object[]): void {
        send(target, 'syncProjectList', projectList)
    }

    utilMap.syncProjectId = function (target, projectId: string): void {
        send(target, 'receiveProjectId', projectId)
    }
    
    utilMap.syncUserInfo = function (target, userInfo: object): void {
        send(target, 'syncUserInfo', userInfo)
    }

    utilMap.goHome = function (target: object): void {
        send(target, 'backHome', '')
    }

    utilMap.changeDocumentTitle = function (title: string): void {
        if (typeof title === 'string') {
            document.title = title
        }
    }
 
    function parseMessage(data) {
        try {
            const cb = utilMap[data.action]
            return cb(data.params)
        } catch (e) {
            console.warn(e)
        }   
    }
    

    init()

    return utilMap
}

export default iframeUtil