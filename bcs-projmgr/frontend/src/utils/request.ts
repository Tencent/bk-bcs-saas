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

import axios from 'axios'
import Vue from 'vue'
import eventBus from './eventBus'
import * as cookie from 'js-cookie'

const request = axios.create({
    baseURL: GW_URL_PREFIX,
    validateStatus: status => {
        if (status > 400) {
            console.warn(`HTTP 请求出错 status: ${status}`)
        }
        return status >= 200 && status <= 503
    },
    withCredentials: true
})

function errorHandler(error: object) {
    console.log('error catch', error)
    return Promise.reject({
        message: '网络出现问题，请检查你的网络是否正常'
    })
}

request.interceptors.response.use(response => {
    injectCSRFTokenToHeaders() // 注入csrfToken
    const { data: { code, data, message, status }, status: httpStatus } = response
    if (httpStatus === 401) {
        // eventBus.$emit('toggle-login-dialog', true)
        window.location.href = LOGIN_SERVICE_URL + '/?c_url=' + window.location.href
        return Promise.reject(response.data)
    } else if (httpStatus === 503) {
        return Promise.reject({
            status: httpStatus,
            message: '服务维护中，请稍候...'
        })

    } else if (httpStatus === 418) {
        console.log('no permission')

    } else if ((typeof code !== 'undefined' && code !== 0) || (typeof status !== 'undefined' && status !== 0)) {
        if (code === 40101) {
            // 未登录
            window.location.href = LOGIN_SERVICE_URL + '/?c_url=' + window.location.href
            return Promise.reject(response.data)
        } else {
            let msg = message
            if (Object.prototype.toString.call(message) === '[object Object]') {
                msg = Object.keys(message).map(key => message[key].join(';')).join(';')
            } else if (Object.prototype.toString.call(message) === '[object Array]') {
                msg = message.join(';')
            }
            const errorMsg = { httpStatus, message: msg, code: code || status, data }
            return Promise.reject(errorMsg)
        }
        
    }

    return data
}, errorHandler)


const injectCSRFTokenToHeaders = () => {
    const CSRFToken = cookie.get('backend_csrftoken')
    if (CSRFToken !== undefined) {
        request.defaults.headers.common['X-CSRFToken'] = CSRFToken
    } else {
        console.warn('Can not find backend_csrftoken in document.cookie')
    }
}

Vue.prototype.$ajax = request

export default request
