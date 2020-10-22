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

import {
    PROJECT_API_URL_PREFIX
} from '../store/constants'
import eventBus from './eventBus'

const customeRules = {
    projectNameUnique: { //较验项目名称是否重复
        // getMessage: field => '项目名称已存在',
        validate: function (value, [projectId]) {
            return new Promise(async (resolve, reject) => {
                try {
                    const response = await eventBus.$ajax.put(`${PROJECT_API_URL_PREFIX}/user/projects/project_name/names/${value}/validate/${projectId ? `?project_id=${projectId}` : ''}`)
                    resolve({
                        valid: response
                    })
                } catch (e) {
                    console.log(e)
                    resolve({
                        valid: false
                    })
                }
            })
        }
    },

    projectEnglishNameUnique: { //较验项目英文名称是否重复
        // getMessage: field => '英文缩写已存在',
        validate: function (value) {
            return new Promise(async (resolve, reject) => {
                try {
                    const response = await eventBus.$ajax.get(`${PROJECT_API_URL_PREFIX}/projects/?project_code=${value}&with_permissions_field=false`)
                    resolve({
                        valid: typeof response === 'object' && Object.keys(response).length === 0
                    })
                } catch (e) {
                    console.log(e)
                    resolve({
                        valid: false
                    })
                }
            })
        }
    },

    projectEnglishNameReg: { //较验项目英文名称格式
        // getMessage: field => '英文缩写必须由小写字母+数字组成，以小写字母开头，长度限制2-32字符！',
        validate: function (value) {
            return /^[a-z][a-z0-9]{1,32}$/.test(value)
        }
    }
}

function ExtendsCustomRules (_extends) {
    if (typeof _extends !== 'function') {
        console.warn('VeeValidate.Validator.extend必须是一个函数！')
        return
    }
    for (let key in customeRules) {
        if (customeRules.hasOwnProperty(key)) {
            _extends(key, customeRules[key])
        }
    }
}

export default ExtendsCustomRules
