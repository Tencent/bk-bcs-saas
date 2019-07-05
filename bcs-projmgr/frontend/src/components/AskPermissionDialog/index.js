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

import Vue from 'vue'
import eventBus from '../../utils/eventBus'
import{ isObject } from '../../utils/util'
import AskPermissionDialog from './AskPermissionDialog'

const DialogCreator = Vue.extend(AskPermissionDialog)
let instance = null

export default function showAskPermissionDialog (props) {
    if (!isObject(props)) {
        console.warn('权限弹窗需要传入一个对象')
        return
    }
    if (instance) { // 存在时更新内部props
        eventBus.$emit('update-permission-props', props)
        return 
    }
    instance = new DialogCreator({
        propsData: props,
        data: {
            showDialog: true
        },
        methods: {
            close
        }
    })

    instance.viewmodel = instance.$mount()
    document.body.appendChild(instance.viewmodel.$el)
}