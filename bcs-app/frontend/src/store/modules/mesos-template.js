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

export default {
    namespaced: true,
    state: {
        curTemplate: {
            name: '',
            desc: '',
            is_locked: false,
            locker: '',
            permissions: {
                create: true,
                delete: true,
                list: true,
                view: true,
                edit: true,
                use: true
            }
        },
        curVersion: 0,
        curTemplateId: 0,
        curShowVersionId: 0,
        templateList: [],
        applications: [],
        deployments: [],
        services: [],
        secrets: [],
        ingresss: [],
        HPAs: [],
        configmaps: [],
        versionList: [],
        imageList: [],
        isTemplateSaving: false,
        canTemplateBindVersion: false,
        linkApps: [],
        metricList: []
    },
    mutations: {
        clearCurTemplateData (state) {
            state.curTemplate = {
                name: '',
                desc: '',
                is_locked: false,
                locker: '',
                permissions: {
                    create: true,
                    delete: true,
                    list: true,
                    view: true,
                    edit: true,
                    use: true
                }
            }
            state.curVersion = 0
            state.curTemplateId = 0
            state.curTemplate.id = 0
            state.curTemplate.latest_version_id = 0
            state.curShowVersionId = 0

            state.applications.splice(0, state.applications.length, ...[])
            state.deployments.splice(0, state.deployments.length, ...[])
            state.services.splice(0, state.services.length, ...[])
            state.secrets.splice(0, state.secrets.length, ...[])
            state.ingresss.splice(0, state.ingresss.length, ...[])
            state.HPAs.splice(0, state.HPAs.length, ...[])
            state.configmaps.splice(0, state.configmaps.length, ...[])

            state.linkApps.splice(0, state.linkApps.length, ...[])
            state.metricList.splice(0, state.metricList.length, ...[])

            state.isTemplateSaving = false
            state.canTemplateBindVersion = false
        },
        updateMetricList (state, list) {
            state.metricList.splice(0, state.metricList.length, ...list)
        },
        updateTemplateList (state, list) {
            state.templateList.splice(0, state.templateList.length, ...list)
        },
        updateBindVersion (state, data) {
            state.canTemplateBindVersion = data
        },
        updateLinkApps (state, data) {
            state.linkApps.splice(0, state.linkApps.length, ...data)
        },
        updateIsTemplateSaving (state, data) {
            state.isTemplateSaving = data
        },
        updateCurShowVersionId (state, data) {
            state.curShowVersionId = data
        },
        updateCurTemplateId (state, data) {
            state.curTemplateId = data
            state.curTemplate.id = data
        },
        updateCurTemplate (state, data) {
            state.curTemplate = data
        },
        updateImageList (state, data) {
            state.imageList = data
        },
        updateCurVersion (state, data) {
            state.curVersion = data
            state.curTemplate.latest_version_id = data
        },
        updateVersionList (state, data) {
            if (data && data.forEach) {
                data.forEach(item => {
                    item.isSelected = false
                })
                state.versionList = data
            }
        },
        addVersion (state, data) {
            data.isSelected = false
            state.versionList.unshift(data)
        },
        updateResources (state, data) {
            if (data.application) {
                data.application.forEach(item => {
                    item.isEdited = false
                    if (String(item.id).indexOf('local_') > -1) {
                        item.isEdited = true
                    } else {
                        item.isEdited = false
                    }

                    if (!item.config.webCache) {
                        item.config.webCache = {}
                    }
                    if (!item.config.webCache.metricIdList) {
                        item.config.webCache.isMetric = false
                        item.config.webCache.metricIdList = []
                    }

                    if (!item.config.webCache.logLabelListCache) {
                        item.config.customLogLabel = {}
                        item.config.webCache.logLabelListCache = [
                            {
                                key: '',
                                value: ''
                            }
                        ]
                    }

                    if (!item.config.monitorLevel) {
                        item.config.monitorLevel = 'general'
                    }

                    item.config.spec.template.spec.containers.forEach(container => {
                        if (!container.logListCache) {
                            container.logListCache = [
                                {
                                    value: ''
                                }
                            ]
                        }
                        if (container.image && !container.imageVersion) {
                            const arr = container.image.split(':')
                            if (arr.length > 1) {
                                container.imageVersion = arr[arr.length - 1]
                            }
                        }
                        if (!container.hasOwnProperty('workingDir')) {
                            container.workingDir = ''
                        }

                        // 将挂载卷的用户数据回填
                        let volumeUsers = {}
                        if (item.config.webCache.volumeUsers) {
                            volumeUsers = item.config.webCache.volumeUsers[container.name] || {}
                        }
                        container.volumes.forEach(volumeItem => {
                            if (!volumeItem.volume.user) {
                                volumeItem.volume.user = ''
                            }
                            const userKey = `${volumeItem.type}:${volumeItem.name}:${volumeItem.volume.hostPath}:${volumeItem.volume.mountPath}` 
                            for (const key in volumeUsers) {
                                if (key === userKey) {
                                    volumeItem.volume.user = volumeUsers[key]
                                }
                            }
                        })
                    })
                })

                state.applications.splice(0, state.applications.length, ...data.application)
            } else {
                state.applications.splice(0, state.applications.length)
            }

            if (data.deployment) {
                data.deployment.forEach(item => {
                    if (String(item.id).indexOf('local_') > -1) {
                        item.isEdited = true
                    } else {
                        item.isEdited = false
                    }
                    const rollingupdate = item.config.strategy.rollingupdate
                    if (!rollingupdate.hasOwnProperty('rollingManually')) {
                        rollingupdate.rollingManually = false
                    }
                })
                state.deployments.splice(0, state.deployments.length, ...data.deployment)
            } else {
                state.deployments.splice(0, state.deployments.length)
            }

            if (data.service) {
                data.service.forEach(item => {
                    item.serviceIPs = item.config.spec.clusterIP.join(',')
                    if (String(item.id).indexOf('local_') > -1) {
                        item.isEdited = true
                    } else {
                        item.isEdited = false
                    }
                    if (!item.config.webCache) {
                        item.config.webCache = {}
                    }
                    if (!item.config.webCache.link_app) {
                        item.config.webCache.link_app = []
                        item.config.webCache.link_app_weight = []
                    }
                })
                state.services.splice(0, state.services.length, ...data.service)
            } else {
                state.services.splice(0, state.services.length)
            }

            if (data.configmap) {
                data.configmap.forEach(item => {
                    if (String(item.id).indexOf('local_') > -1) {
                        item.isEdited = true
                    } else {
                        item.isEdited = false
                    }

                    const list = []
                    const keys = item.config.datas
                    if (!item.configmapKeyList) {
                        item.configmapKeyList = []
                    }
                    for (const [key, value] of Object.entries(keys)) {
                        list.push({
                            key: key,
                            type: value.type,
                            isEdit: false,
                            content: value.content
                        })
                    }

                    item.configmapKeyList.splice(0, item.configmapKeyList.length, ...list)
                })

                state.configmaps.splice(0, state.configmaps.length, ...data.configmap)
            } else {
                state.configmaps.splice(0, state.configmaps.length)
            }

            if (data.secret) {
                data.secret.forEach(item => {
                    if (String(item.id).indexOf('local_') > -1) {
                        item.isEdited = true
                    } else {
                        item.isEdited = false
                    }
                    const list = []
                    const keys = item.config.datas
                    if (!item.secretKeyList) {
                        item.secretKeyList = []
                    }
                    for (const [key, value] of Object.entries(keys)) {
                        list.push({
                            key: key,
                            isEdit: false,
                            content: value.content
                        })
                    }
                    this.curKeyIndex = 0
                    if (list.length) {
                        this.curKeyParams = list[0]
                    } else {
                        this.curKeyParams = null
                    }

                    item.secretKeyList.splice(0, item.secretKeyList.length, ...list)
                })
                state.secrets.splice(0, state.secrets.length, ...data.secret)
            } else {
                state.secrets.splice(0, state.secrets.length)
            }

            if (data.ingress) {
                data.ingress.forEach(item => {
                    if (String(item.id).indexOf('local_') > -1) {
                        item.isEdited = true
                    } else {
                        item.isEdited = false
                    }
                })
                state.ingresss.splice(0, state.ingresss.length, ...data.ingress)
            } else {
                state.ingresss.splice(0, state.ingresss.length)
            }
            if (data.hpa) {
                data.hpa.forEach(item => {
                    if (String(item.id).indexOf('local_') > -1) {
                        item.isEdited = true
                    } else {
                        item.isEdited = false
                    }
                })
                state.HPAs.splice(0, state.HPAs.length, ...data.hpa)
            } else {
                state.HPAs.splice(0, state.HPAs.length)
            }
        },
        updateApplications (state, data) {
            state.applications.splice(0, state.applications.length, ...data)
        },
        updateApplicationById (state, { application, preId }) {
            for (const item of state.applications) {
                if (item.id === preId) {
                    item.id = application.id
                    delete item.cache
                }
            }

            const list = JSON.parse(JSON.stringify(state.applications))
            state.applications.splice(0, state.applications.length, ...list)
        },
        updateDeploymentById (state, { deployment, preId }) {
            for (const item of state.deployments) {
                if (item.id === preId) {
                    item.id = deployment.id
                }
            }
            const list = JSON.parse(JSON.stringify(state.deployments))
            state.deployments.splice(0, state.deployments.length, ...list)
        },
        updateServiceById (state, { service, preId }) {
            for (const item of state.services) {
                if (item.id === preId) {
                    item.id = service.id
                }
            }
            const list = JSON.parse(JSON.stringify(state.services))
            state.services.splice(0, state.services.length, ...list)
        },
        updateConfigmapById (state, { configmap, targetData, preId }) {
            for (const item of state.configmaps) {
                if (item.id === preId) {
                    item.config = targetData.config
                    item.id = configmap.id
                }
            }
            const list = JSON.parse(JSON.stringify(state.configmaps))
            state.configmaps.splice(0, state.configmaps.length, ...list)
        },
        updateSecretById (state, { secret, preId }) {
            for (const item of state.secrets) {
                if (item.id === preId) {
                    item.id = secret.id
                }
            }
            const list = JSON.parse(JSON.stringify(state.secrets))
            state.secrets.splice(0, state.secrets.length, ...list)
        },
        updateIngressById (state, { ingress, preId }) {
            for (const item of state.ingresss) {
                if (item.id === preId) {
                    item.id = ingress.id
                }
            }
            const list = JSON.parse(JSON.stringify(state.ingresss))
            state.ingresss.splice(0, state.ingresss.length, ...list)
        },
        updateHPAById (state, { HPA, preId }) {
            for (const item of state.HPAs) {
                if (item.id === preId) {
                    item.id = HPA.id
                }
            }
            const list = JSON.parse(JSON.stringify(state.HPAs))
            state.HPAs.splice(0, state.HPAs.length, ...list)
        },
        updateDeployments (state, data) {
            state.deployments.splice(0, state.deployments.length, ...data)
        },
        updateServices (state, data) {
            if (data.length) {
                data.forEach(item => {
                    if (!item.config.webCache) {
                        item.config.webCache = {}
                    }
                    if (!item.config.webCache.link_app) {
                        item.config.webCache.link_app = []
                        item.config.webCache.link_app_weight = []
                    }
                })
            }
            state.services.splice(0, state.services.length, ...data)
        },
        updateSecrets (state, data) {
            state.secrets.splice(0, state.secrets.length, ...data)
        },
        updateIngresss (state, data) {
            state.ingresss.splice(0, state.ingresss.length, ...data)
        },
        updateHPAs (state, data) {
            state.HPAs.splice(0, state.HPAs.length, ...data)
        },
        updateConfigmaps (state, data) {
            state.configmaps.splice(0, state.configmaps.length, ...data)
        }
    },
    actions: {
        /**
         * 更新templateData
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateTemplateDraft (context, { projectId, templateId, data }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/draft/`, data)
        },

        /**
         * 获取version list
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getVersionList (context, { projectId, templateId }, config = {}) {
            const url = `${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/show/version/`
            return http.get(url).then(res => {
                if (res && res.data) {
                    context.commit('updateVersionList', res.data)
                } else {
                    context.commit('updateVersionList', [])
                }
                return res
            }, res => {
                context.commit('updateVersionList', [])
            })
        },

        /**
         * 添加version
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addVersion (context, { projectId, templateId, data }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/show/versions/${templateId}/`, data).then(res => {
                return res
            })
        },

        /**
         * 删除version
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        removeVersion (context, { projectId, templateId, versionId }, config = {}) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/show/version/${versionId}/`)
        },

        /**
         * 根据版本号获取template内容
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getTemplateByVersion (context, { projectId, templateId, versionId }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/show/version/${versionId}/`).then(res => {
                if (res && res.data) {
                    context.commit('updateResources', res.data)
                    context.commit('updateCurShowVersionId', versionId)
                    context.commit('updateCurVersion', res.data.version)
                }
                return res
            })
        },

        /**
         * 获取ports
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getPortsByApps (context, { projectId, version, apps }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/ports/${version}/?app_ids=${apps.join(',')}`)
        },

        /**
         * 获取模板集列表
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getTemplateList (context, projectId, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/templates/`)
        },

        /**
         * 获取单个模板集
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getTemplateById (context, { projectId, templateId }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/`)
        },

        /**
         * 获取version list
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateTemplate (context, { projectId, templateId, data }) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/`, data, { cancelWhenRouteChange: false })
        },

        /**
         * 获取application list
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getApplicationList (context, { projectId, templateId, version }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/version/0/`)
        },

        /**
         * 获取所有资源
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getTemplateResource (context, { projectId, templateId, version }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/show/version/${version}/`).then(res => {
                context.commit('updateCurShowVersionId', version)
                return res
            })
        },

        /**
         * 删除模板集
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        removeTemplate (context, { templateId, projectId }, config = {}) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/`)
        },

        /**
         * 添加模板集
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addTemplate (context, { templateParams, projectId }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/templates/`, templateParams)
        },

        /**
         * 添加新application
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addApplication (context, { data, version, projectId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/application/0/`, data)
        },

        /**
         * 更新application
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateApplication (context, { data, version, projectId, applicationId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/application/${applicationId}/`, data)
        },

        /**
         * 添加第一个application
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addFirstApplication (context, { data, templateId, projectId }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/application/`, data)
        },

        /**
         * 删除application
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        removeApplication (context, { applicationId, version, projectId }, config = {}) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/application/${applicationId}/`)
        },

        /**
         * 拉取镜像列表
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getImageList (context, { projectId }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/depot/available/images/${projectId}/`)
        },

        /**
         * 拉取某个镜像版本
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getImageVertionList (context, { projectId, imageId, isPub }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/depot/available/tags/${projectId}/?repo=${imageId}&is_pub=${isPub}`)
        },

        /**
         * 获取对应version 的application  list
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getApplicationsByVersion (context, { projectId, version }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/apps/${version}/`).then(res => {
                if (res.data.length) {
                    context.commit('updateLinkApps', res.data)
                }
                return res
            })
        },

        /**
         * 创建deployment
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addDeployment (context, { data, version, projectId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/deployment/0/`, data)
        },

        /**
         * 添加第一个Deployment
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addFirstDeployment (context, { data, templateId, projectId }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/deployment/`, data)
        },

        /**
         * 更新deployment
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateDeployment (context, { data, version, projectId, deploymentId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/deployment/${deploymentId}/`, data)
        },

        /**
         * 删除deployment
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        removeDeployment (context, { deploymentId, version, projectId }, config = {}) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/deployment/${deploymentId}/`)
        },

        /**
         * 创建service
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addService (context, { data, version, projectId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/service/0/`, data)
        },

        /**
         * 更新service获取version list
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateService (context, { data, version, projectId, serviceId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/service/${serviceId}/`, data)
        },

        /**
         * 删除Service
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        removeService (context, { serviceId, version, projectId }, config = {}) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/service/${serviceId}/`)
        },

        /**
         * 添加第一个service
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addFirstService (context, { data, templateId, projectId }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/service/`, data)
        },

        /**
         * 创建configmap
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addConfigmap (context, { data, version, projectId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/configmap/0/`, data)
        },

        /**
         * 更新configmap
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateConfigmap (context, { data, version, projectId, configmapId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/configmap/${configmapId}/`, data)
        },

        /**
         * 点击更新时查询单个configmap
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateSelectConfigmap (context, { projectId, namespace, name }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/resource/${projectId}/configmaps/?namespace=${namespace}&name=${name}&decode=1`)
        },

        /**
         * 更新单个configmap
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateSingleConfigmap (context, { projectId, clusterId, namespace, name, data }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/resource/${projectId}/configmaps/clusters/${clusterId}/namespaces/${namespace}/endpoints/${name}/`, data)
        },

        /**
         * 删除Configmap
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        removeConfigmap (context, { configmapId, version, projectId }, config = {}) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/configmap/${configmapId}/`)
        },

        /**
         * 删除单个Configmap
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        deleteConfigmap (context, { projectId, clusterId, namespace, name }, config = {}) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/resource/${projectId}/configmaps/clusters/${clusterId}/namespaces/${namespace}/endpoints/${name}/`)
        },

        /**
         * 删除Configmaps
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        deleteConfigmaps (context, { projectId, data }, config = {}) {
            const params = {
                data: data
            }
            return http.post(`${DEVOPS_BCS_API_URL}/api/resource/${projectId}/configmaps/batch/`, params)
        },

        /**
         * 添加第一个configmap
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addFirstConfigmap (context, { data, templateId, projectId }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/configmap/`, data)
        },

        /**
         * 创建secret
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addSecret (context, { data, version, projectId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/secret/0/`, data)
        },

        /**
         * 更新secret
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        updateSecret (context, { data, version, projectId, secretId }, config = {}) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/secret/${secretId}/`, data)
        },

        /**
         * 删除Secret
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        removeSecret (context, { secretId, version, projectId }, config = {}) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/secret/${secretId}/`)
        },

        /**
         * 添加第一个secret
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        addFirstSecret (context, { data, templateId, projectId }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/secret/`, data)
        },

        /**
         * 创建Ingress
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 包括data, version, projectId
         *
         * @return {Promise} promise 对象
         */
        addIngress (context, { data, version, projectId }) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/ingress/0/`, data)
        },

        /**
         * 更新Ingress
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 包括data, version, projectId, ingressId
         *
         * @return {Promise} promise 对象
         */
        updateIngress (context, { data, version, projectId, ingressId }) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/ingress/${ingressId}/`, data)
        },

        /**
         * 删除Ingress
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 包括version, projectId, ingressId
         *
         * @return {Promise} promise 对象
         */
        removeIngress (context, { ingressId, version, projectId }) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/ingress/${ingressId}/`)
        },

        /**
         * 添加第一个Ingress
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 包括data, templateId, ingressId
         *
         * @return {Promise} promise 对象
         */
        addFirstIngress (context, { data, templateId, projectId }) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/ingress/`, data)
        },

        /**
         * 获取HPA metric类型
         *
         * @param {Object} context store 上下文对象
         * @param {Number} projectId project id
         *
         * @return {Promise} promise 对象
         */
        getHPAMetric (context, projectId) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/hpa/projects/${projectId}/metrics/`)
        },

        /**
         * 创建HPA
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 包括data, version, projectId
         *
         * @return {Promise} promise 对象
         */
        addHPA (context, { data, version, projectId }) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/hpa/0/`, data)
        },

        /**
         * 更新HPA
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 包括data, version, projectId, HPAId
         *
         * @return {Promise} promise 对象
         */
        updateHPA (context, { data, version, projectId, HPAId }) {
            return http.put(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/hpa/${HPAId}/`, data)
        },

        /**
         * 删除HPA
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 包括version, projectId, HPAId
         *
         * @return {Promise} promise 对象
         */
        removeHPA (context, { HPAId, version, projectId }) {
            return http.delete(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/version/${version}/hpa/${HPAId}/`)
        },

        /**
         * 添加第一个HPA
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 包括data, templateId, HPAId
         *
         * @return {Promise} promise 对象
         */
        addFirstHPA (context, { data, templateId, projectId }) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/hpa/`, data)
        },

        /**
         * 拉取挂载卷/环境变量configmaps
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getConfigmaps (context, { projectId, version }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/configmap/${version}/`)
        },

        /**
         * 保存版本
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        saveVersion (context, { projectId, templateId, params }, config = {}) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/${templateId}/show/version/`, params)
        },

        /**
         * 拉取挂载卷/环境变量secrets
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getSecrets (context, { projectId, version }, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/secret/${version}/`)
        },

        /**
         * check 端口是否已经关联
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        checkPortIsLink (context, { projectId, version, portId }, config = {}) {
            if (projectId && version && portId) {
                return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/check/version/${version}/port/${portId}/`)
            }
        },

        /**
         * 拉取metric 列表
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         * @param {Object} config 请求的配置
         *
         * @return {Promise} promise 对象
         */
        getMetricList (context, projectId, config = {}) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/metric/${projectId}/`).then(res => {
                context.commit('updateMetricList', res.data)
                return res
            })
        },

        /**
         * 加锁
         *
         * @param {Object} context store 上下文对象
         * @param {Object} 请求参数，包括projectId, templateId
         */
        lockTemplateset (context, { projectId, templateId }) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/lock/${templateId}/`)
        },

        /**
         * 解锁
         *
         * @param {Object} context store 上下文对象
         * @param {Object} 请求参数，包括projectId, templateId
         */
        unlockTemplateset (context, { projectId, templateId }) {
            return http.post(`${DEVOPS_BCS_API_URL}/api/configuration/${projectId}/template/unlock/${templateId}/`)
        },

        /**
         * 获取对应version 的deployment list
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
        getDeploymentsByVersion (context, { projectId, version }) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/configuration/projects/${projectId}/deployment/${version}/`)
        },

        /**
         * 获取对应service list
         *
         * @param {Object} context store 上下文对象
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */
        getServicesByVersion (context, { projectId, version }) {
            return http.get(`${DEVOPS_BCS_API_URL}/api/projects/${projectId}/mesos/service/${version}/`)
        }
    }
}
