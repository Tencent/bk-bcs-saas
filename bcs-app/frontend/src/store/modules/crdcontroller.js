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

import http from '@open/api'
import { json2Query } from '@open/common/util'

export default {
    namespaced: true,
    state: {
        crdInstanceList: [],
        nameSpaceList: []
    },
    mutations: {
        /**
         * 更新crdInstanceList
         * @param {Object} state store state
         * @param {Object} data data
         */
        updateCrdInstanceList (state, data) {
            state.crdInstanceList = data
        },

        /**
         * 更新namespace 列表
         *
         * @param {Object} state store state
         * @param {Object} data data
         */
        updateNameSpaceList (state, data) {
            state.nameSpaceList.splice(0, state.nameSpaceList.length, ...data)
        },
    },
    actions: {
        /**
         * 获取组件库
         *
         * @param {Object} context store 上下文对象
         * @param {Object} projectId, clusterId
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getCrdControllersByCluster (context, { projectId, clusterId }, config = {}) {
            console.log('clusterId', clusterId)
            const url = `${DEVOPS_BCS_API_URL}/api/projects/${projectId}/bcs_crd/clusters/${clusterId}/crd_controllers/`
            return http.get(url, {}, config)
        },

        /**
         * 查询crd列表 (老)
         *
         * @param {Object} context store 上下文对象
         * @param {Object} projectId, clusterId, crdKind
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getCrdInstanceList (context, { projectId, clusterId, params = {} }, config = {}) {
            context.commit('updateCrdInstanceList', [])
            const url = `${DEVOPS_BCS_API_URL}/api/projects/${projectId}/bcs_crd/clusters/${clusterId}/crd_instances/?${json2Query(params)}`
            return http.get(url, {}, config).then(res => {
                context.commit('updateCrdInstanceList', res.data)
                return res
            })
        },

        /**
         * 查询crd列表 (新)
         *
         * @param {Object} context store 上下文对象
         * @param {Object} projectId, clusterId, crdKind
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getBcsCrdsList (context, { projectId, params = {} }, config = {}) {
            context.commit('updateCrdInstanceList', [])
            const url = `${DEVOPS_BCS_API_URL}/api/projects/${projectId}/bcs_crd/crds/?${json2Query(params)}`
            return http.get(url, {}, config).then(res => {
                context.commit('updateCrdInstanceList', res.data)
                return res
            })
        },

        /**
         * 查询单个crd
         *
         * @param {Object} context store 上下文对象
         * @param {Object} projectId, clusterId, crdId
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getCrdInstanceDetail (context, { projectId, clusterId, crdId }, config = {}) {
            const url = `${DEVOPS_BCS_API_URL}/api/projects/${projectId}/bcs_crd/clusters/${clusterId}/crd_instances/${crdId}/`
            return http.get(url, {}, config)
        },

        /**
         * 获取当前集群下的namespace 列表
         *
         * @param {Object} context store 上下文对象
         * @param {Object} projectId, clusterId
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getNameSpaceListByCluster (context, { projectId, clusterId }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/namespace/?cluster_id=${clusterId}`, {}, config).then(res => {
                context.commit('updateNameSpaceList', res.data)
                return res
            })
        },

        /**
         * 添加crdInstance
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数，包含：projectId, data
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addCrdInstance (context, { projectId, data }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/projects/${projectId}/bcs_crd/crds/`, data, config)
        },

        /**
         * 更新crdInstance
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数，包含：projectId, data
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateCrdInstance (context, { projectId, data }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/projects/${projectId}/bcs_crd/crds/`, data, config)
        },

        /**
         * 删除单个crd
         *
         * @param {Object} context store 上下文对象
         * @param {Object} projectId, clusterId, crdId
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        deleteCrdInstance (context, { projectId, clusterId, crdId }, config = {}) {
            const url = `${DEVOPS_BCS_API_URL}/api/projects/${projectId}/bcs_crd/clusters/${clusterId}/crd_instances/${crdId}/`
            return http.delete(url, {}, config)
        },
    }
}
