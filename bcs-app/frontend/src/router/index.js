/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import Vue from 'vue'
import VueRouter from 'vue-router'
import { bus } from '@open/common/bus'
import store from '@open/store'
import http from '@open/api'
import preload from '@open/common/preload'
import { routes as ceRoutes } from './ce'

Vue.use(VueRouter)

const routes = ceRoutes

const router = new VueRouter({
    mode: 'history',
    routes: routes
})

const cancelRequest = async () => {
    const allRequest = http.queue.get()
    const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange)
    await http.cancel(requestQueue.map(request => request.requestId))
}

let preloading = true
let canceling = true
let pageMethodExecuting = true

router.beforeEach(async (to, from, next) => {
    bus.$emit('close-apply-perm-modal')

    canceling = true
    await cancelRequest()
    canceling = false
    next()

    // 解决 sideslider 组件跳转后导致滚动条失效
    const node = document.documentElement
    const className = 'bk-sideslider-show has-sideslider-padding'
    const classNames = className.split(' ')
    const rtrim = /^\s+|\s+$/
    let setClass = ' ' + node.className + ' '

    classNames.forEach(cl => {
        setClass = setClass.replace(' ' + cl + ' ', ' ')
    })
    node.className = setClass.replace(rtrim, '')

    setTimeout(() => {
        window.scroll(0, 0)
    }, 100)
})

router.afterEach(async (to, from) => {
    store.commit('setMainContentLoading', true)
    preloading = true
    await preload()
    preloading = false

    const pageDataMethods = []
    const routerList = to.matched
    routerList.forEach(r => {
        const fetchPageData = r.instances.default && r.instances.default.fetchPageData
        if (fetchPageData && typeof fetchPageData === 'function') {
            pageDataMethods.push(r.instances.default.fetchPageData())
        }
    })

    pageMethodExecuting = true
    await Promise.all(pageDataMethods)
    pageMethodExecuting = false

    if (!preloading && !canceling && !pageMethodExecuting) {
        store.commit('setMainContentLoading', false)
    }
})

export default router
