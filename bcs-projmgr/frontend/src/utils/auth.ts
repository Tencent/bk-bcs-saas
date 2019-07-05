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

import request from './request'
import { transformObj } from './util'
import { PROJECT_API_URL_PREFIX } from '../store/constants'

let currentUser: User

export default {

    getCurrentUser () {
        return currentUser
    },
    getAnonymousUser () {
        return {
            id: '',
            isAuthenticated: false,
            username: 'anonymous',
            chineseName: 'anonymous'
        }
    },
    redirectToLogin () {
        window.location.href = LOGIN_SERVICE_URL + '/?c_url=' + window.location.href
    },
    async requestCurrentUser (refresh = false) {
       if (currentUser && !refresh) { // 如果已经获取到用户了， 直接返回
            return currentUser
        }

        const endpoint = `${PROJECT_API_URL_PREFIX}/user/users`
        const response = await request.get(endpoint)
        // 存储当前用户信息(全局)
        currentUser = {
            ...transformObj(response),
            isAuthenticated: true
        }
        return currentUser
    }
}
