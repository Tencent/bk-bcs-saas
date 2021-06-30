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
import Router, { RouteMeta } from 'vue-router'
import { updateRecentVisitServiceList, urlJoin } from '../utils/util'
import { getServiceAliasByPath, importScript, importStyle } from '../utils/util'
import compilePath from '../utils/pathExp'
import request from '../utils/request'

// 404
const None = () => import('../views/None.vue')
const App = () => import('../views/App.vue')

// 首页 - index
const Index = () => import('../views/Index.vue')

const IFrame = () => import('../views/IFrame.vue')

const ProjectManage = () => import('../views/ProjectManage.vue')

const Docs = () => import('../views/Docs.vue')

const Maintaining = () => import('../views/503.vue')

Vue.use(Router)


let mod: Route[] = []
for(let key in window.Pages) {
    mod = mod.concat(window.Pages[key].routes)
}

const iframeRoutes = window.serviceObject.iframeRoutes.map( r => ({
    path: urlJoin('/console', r.path, ':restPath*'),
    name: r.name,
    component: IFrame,
    meta: r.meta,
    pathToRegexpOptions: {
        strict: true,
        end: false
    }
}))

const routes = [
    {
        path: '/console',
        component: Index,
        children: [
            // {
            //     path: '',
            //     name: 'home',
            //     component: Home,
            //     meta: {
            //         showProjectList: false,
            //         showNav: true
            //     }
            // },
            // {
            //     path: 'quickstart',
            //     name: 'quickstart',
            //     component: QuickStart,
            //     meta: {
            //         showProjectList: false,
            //         showNav: true
            //     }
            // },
            {
                path: '',
                name: 'pm',
                component: ProjectManage,
                meta: {
                    showProjectList: false,
                    showNav: true
                }
            },
            ...iframeRoutes,
            ...mod,
            {
                path: 'maintaining',
                name: '503',
                component: Maintaining
            }
        ]
    },
    {
        path: '/console/docs',
        name: 'docs',
        component: Docs,
        meta: {
            showProjectList: false,
            showNav: false
        }
    }
]

function isAmdModule (currentPage: subService): boolean {
    return currentPage && currentPage.inject_type === 'amd'
}


const createRouter = (store: any) => {
    // counterUser() // 统计用户信息
    const router = new Router({
        mode: 'history',
        routes: routes
    })
    
    let loadedModule = {}

    if (isAmdModule(window.currentPage)) {
        const serviceAlias = getServiceAliasByPath(window.currentPage.link_new)
        loadedModule = {
            [serviceAlias]: true
        }
    }
    
    router.beforeEach((to, from, next) => {
        const serviceAlias = getServiceAliasByPath(to.path)
        const currentPage = window.serviceObject.serviceMap[serviceAlias]
        
        window.currentPage = currentPage
        if (!currentPage) {  // console 首页
            next()
            return
        }
        const { css_url, js_url } = currentPage
        
        if (isAmdModule(currentPage) && !loadedModule[serviceAlias]) {
            store.dispatch('toggleModuleLoading', true)
            Promise.all([
                importStyle(css_url, document.head),
                importScript(js_url, document.body)
            ]).then(() => {
                const module = window.Pages[serviceAlias]
                store.registerModule(serviceAlias, module.store)
                const dynamicRoutes = [{
                    path: '/console/',
                    component: Index,
                    children: module.routes
                }]
                
                router.addRoutes(dynamicRoutes)
                setTimeout( () => {
                    store.dispatch('toggleModuleLoading', false)
                }, 0)
            })  
            loadedModule[serviceAlias] = true
        }
        const newPath = initProjectId(to, store)
        if (to.path !== newPath) {
            next({
                path: newPath,
                query: to.query,
                hash: to.hash
            })
        } else {
            next()
        }
    })

    router.afterEach(route => {
        updateRecentVisitServiceList(route.path)
        
        store.dispatch('upadteHeaderConfig', updateHeaderConfig(route.meta))
    })
    return router
}

function updateHeaderConfig (meta: RouteMeta) {
    return {
        showProjectList: meta.showProjectList || (window.currentPage && window.currentPage.show_project_list && typeof meta.showProjectList === 'undefined'),
        showNav: meta.showNav || (window.currentPage && window.currentPage.show_nav && typeof meta.showNav === 'undefined')
    }
}

/**
 * 上报用户信息
 */
function counterUser (): void {
    const userId = window.userInfo.username
    const os = parseOS()
    
    request.post('/project/api/user/count/login', {
        os,
        userId
    })
}


function parseOS (): string {
    const { userAgent } = window.navigator
    switch (true) {
        case userAgent.indexOf('Linux') > -1:
            return /android/i.test(userAgent) ? 'ANDROID' : 'LINUX'
        case userAgent.indexOf('iPhone') > -1:
            return 'IOS'
        case userAgent.indexOf('iPad') > -1:
            return 'iPad'
        case userAgent.indexOf('Mac') > -1:
            return 'MACOS'
        case userAgent.indexOf('Win') > -1:
            return 'WINDOWS'
        
    }
    return 'WINDOWS'
}

function getProjectId (store, params): string {
    const projectId = localStorage.getItem('projectId') || store.getters.onlineProjectList[0].project_code
    return params.projectId != '0' && params.projectId ? params.projectId : projectId
}

function initProjectId (to, store): string {
    try {
        const { matched, params } = to
        const projectId: string = getProjectId(store, params)
        const lastMatched = matched[matched.length - 1]
        
        const options = projectId ? {
            ...params,
            projectId
        } : params
        
        return matched.length ? compilePath(lastMatched.path)(options) : to.path
    } catch (e) {
        console.log(e)
        return to.path
    }
    
}
export default createRouter
