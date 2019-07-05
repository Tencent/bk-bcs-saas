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

var devopsUtil = {};
var globalVue

(function (win, exports) {
    var Vue = win.Vue
    globalVue = Vue ? new Vue() : null
    var SYNC_TOP_URL = 'syncUrl'
    var SYNC_TOP_PROJECT_ID = 'syncTopProjectId'
    var SYNC_PROJECT_LIST = 'syncProjectList'
    var SYNC_USER_INFO = 'syncUserInfo'
    var RECEIVE_PROJECT_ID = 'receiveProjectId'
    var TOGGLE_PROJECT_MENU = 'toggleProjectMenu'
    var POP_PROJECT_DIALOG = 'popProjectDialog'
    var SHOW_ASK_PERMISSION_DIALOG = 'showAskPermissionDialog'
    var TOGGLE_LOGIN_DIALOG = 'toggleLoginDialog'
    var SHOW_TIPS = 'showTips'
    var BACK_HOME = 'backHome'
    var CHANGE_DOCUMENT_TITLE = 'changeDocumentTitle'

    function init() {
        if (win.addEventListener) {
            win.addEventListener('message', onMessage)
        } else if (win.attachEvent) {
            win.attachEvent('onmessage', onMessage)
        }
    }

    function onMessage(e) {
        parseMessage(e.data)
    }

    function parseMessage(data) {
        try {
            fun = exports[data.action]
            return fun(data.params)
        } catch (e) {
            console.warn(e)
        }
    }

    function triggerEvent(eventName, payload, ele) {
        if (Vue) {
            globalVue.$emit(eventName, payload)
        } else { // 使用其它前端框架时，触发自定义事件
            var cs = new CustomEvent(eventName, {
                detail: payload
            })
            win.dispatchEvent(cs)
        }
    }

    function communicateOuter(data) {
        if (window.postMessage) {
            try {
                top.postMessage(data, '*');
            } catch (e) {
                console.warn('communicate fail', e)
            }
        }
    }

    //  globalVue = new win.Vue()
    function addToGlobal(prop, val) {
        if (Vue) {
            Vue.prototype['$' + prop] = val
            globalVue.$emit('', {
                [prop]: val
            })
        } else {
            win['$' + prop] = val
        }

        triggerEvent('change::$' + prop, {
            [prop]: val
        })
    }

    /**
     * 同步父窗口URL
     * @method syncUrl
     * @param {url} str 要同步到父窗口的url
     * @param {refresh} boolean 是否刷新页面
     */
    exports[SYNC_TOP_URL] = function (url, refresh) {
        communicateOuter({
            action: SYNC_TOP_URL,
            params: {
                url: url,
                refresh
            }
        })
    }

    /**
     * 弹出权限弹窗
     * @method showAskPermissionDialog
     * @param {权限对象} obj 要申请的权限对象, 包含以下三个字段
     *      title               string  权限弹窗标题，可不传，默认为（无权限操作）
     *      noPermissionList    array  要申请的权限列表，[{resource: '流水线', option: '操作'}, ...]
     *      applyPermissionUrl  string 申请权限跳转地址
     */
    exports[SHOW_ASK_PERMISSION_DIALOG] = function (params) {
        communicateOuter({
            action: SHOW_ASK_PERMISSION_DIALOG,
            params
        })
    }


    /**
     * 弹出信息
     * @method showTips
     * @param {tips} object 提示信息对象, 传入$bkMessage
     */
    exports[SHOW_TIPS] = function (tips) {
        console.log(tips)
        communicateOuter({
            action: SHOW_TIPS,
            params: tips
        })
    }

    /**
     * 登录弹窗
     * @method toggleLoginDialog
     * @param {isShow} boolean 是否显示登录弹窗
     */
    exports[TOGGLE_LOGIN_DIALOG] = function (isShow) {
        communicateOuter({
            action: TOGGLE_LOGIN_DIALOG,
            params: isShow
        })
    }

    /**
     * 同步父窗口的ProjectId
     * @method syncTopProjectId
     * @param {projectId} str 要同步到父窗口的ProjectId
     */
    exports[SYNC_TOP_PROJECT_ID] = function (projectId) {
        communicateOuter({
            action: SYNC_TOP_PROJECT_ID,
            params: {
                projectId
            }
        })
    }

    /**
     * 关闭或显示项目下拉菜单
     * @method toggleProjectMenu
     * @param {show} boolean 是否显示
     */
    exports[TOGGLE_PROJECT_MENU] = function (show) {
        communicateOuter({
            action: TOGGLE_PROJECT_MENU,
            params: show
        })
    }

    /**
     * 弹出项目编辑窗口
     * @method popProjectDialog
     * @param {project} object 项目对象
     */
    exports[POP_PROJECT_DIALOG] = function (project) {
        communicateOuter({
            action: POP_PROJECT_DIALOG,
            params: project
        })
    }

    exports[CHANGE_DOCUMENT_TITLE] = function (title) {
        communicateOuter({
            action: CHANGE_DOCUMENT_TITLE,
            params: title
        })
    }

    /**
     * 获取父窗口的ProjectId
     * @method receiveProjectId
     * @param {projectId} str 父窗口的ProjectId
     */
    exports[RECEIVE_PROJECT_ID] = function (projectId) {
        addToGlobal('currentProjectId', projectId)
    }

    /**
     * 接收父窗口的项目列表
     * @method syncProjectList
     * @param {projectList} str 父窗口的项目列表
     */
    exports[SYNC_PROJECT_LIST] = function (projectList) {
        addToGlobal('projectList', projectList)
    }

    /**
     * 获取父窗口的用户信息
     * @method syncUserInfo
     * @param {userInfo} str 父窗口的用户信息
     */
    exports[SYNC_USER_INFO] = function (userInfo) {
        addToGlobal('userInfo', userInfo)
    }

    /**
     * 触发返回首页事件
     * @method backHome
     */
    exports[BACK_HOME] = function () {
        triggerEvent('order::' + BACK_HOME)
    }
    

    for (var key in exports) {
        if (exports.hasOwnProperty(key)) {
            const cb = exports[key]
            addToGlobal(key, cb)
        }
    }



    init()
})(window, devopsUtil)