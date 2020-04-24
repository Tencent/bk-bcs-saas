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

// 首页
const Configuration = () => import(/* webpackChunkName: 'configuration' */'@open/views/configuration')

// 命名空间
const Namespace = () => import(/* webpackChunkName: 'namespace' */'@open/views/configuration/namespace')

// 变量管理
const Variable = () => import(/* webpackChunkName: 'variable' */'@open/views/variable')

// 模板集
const Templateset = () => import(/* webpackChunkName: 'templateset' */'@open/views/configuration/templateset')

// 模板实例化
const Instantiation = () => import(/* webpackChunkName: 'templateset' */'@open/views/configuration/instantiation')

// 创建 mesos 资源
const MesosConfigurationCreate = () => import(/* webpackChunkName: 'mesosTemplateset' */'@open/views/configuration/mesosCreate')

// 添加模板集 - application
const MesosCreateApplication = () => import(/* webpackChunkName: 'mesosTemplateset' */'@open/views/configuration/mesos-create/application')

// 添加模板集 - deployment
const MesosCreateDeployment = () => import(/* webpackChunkName: 'mesosTemplateset' */'@open/views/configuration/mesos-create/deployment')

// 添加模板集 - service
const MesosCreateService = () => import(/* webpackChunkName: 'mesosTemplateset' */'@open/views/configuration/mesos-create/service')

// 添加模板集 - secret
const MesosCreateSecret = () => import(/* webpackChunkName: 'mesosTemplateset' */'@open/views/configuration/mesos-create/secret')

// 添加模板集 - configmap
const MesosCreateConfigmap = () => import(/* webpackChunkName: 'mesosTemplateset' */'@open/views/configuration/mesos-create/configmap')

// 创建 k8s 资源
const K8sConfigurationCreate = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8sCreate')

// 添加模板集 - deployment
const K8sCreateDeployment = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8s-create/deployment')

// 添加模板集 - service
const K8sCreateService = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8s-create/service')

// 添加模板集 - configmap
const K8sCreateConfigmap = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8s-create/configmap')

// 添加模板集 - secret
const K8sCreateSecret = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8s-create/secret')

// 添加模板集 - daemonset
const K8sCreateDaemonset = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8s-create/daemonset')

// 添加模板集 - job
const K8sCreateJob = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8s-create/job')

// 添加模板集 - statefulset
const K8sCreateStatefulset = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8s-create/statefulset')

// 添加模板集 - ingress
const K8sCreateIngress = () => import(/* webpackChunkName: 'k8sTemplateset' */'@open/views/configuration/k8s-create/ingress')

// 添加yaml模板集 - yaml templateset
const K8sYamlTemplateset = () => import(/* webpackChunkName: 'K8sYamlTemplateset' */'@open/views/configuration/k8s-create/yaml-mode')

const childRoutes = [
    {
        path: ':projectCode/configuration',
        name: 'configurationMain',
        component: Configuration,
        children: [
            {
                path: 'namespace',
                component: Namespace,
                name: 'namespace',
                alias: ''
            },
            {
                path: 'templateset',
                name: 'templateset',
                component: Templateset
            },
            {
                path: 'templateset/:templateId/instantiation',
                name: 'instantiation',
                component: Instantiation
            },
            {
                path: 'mesos',
                name: 'mesosConfigurationCreate',
                component: MesosConfigurationCreate,
                children: [
                    {
                        path: 'templateset/application/:templateId',
                        name: 'mesosTemplatesetApplication',
                        component: MesosCreateApplication,
                        alias: 'templateset/create'
                    },
                    {
                        path: 'templateset/deployment/:templateId',
                        name: 'mesosTemplatesetDeployment',
                        component: MesosCreateDeployment
                    },
                    {
                        path: 'templateset/service/:templateId',
                        name: 'mesosTemplatesetService',
                        component: MesosCreateService
                    },
                    {
                        path: 'templateset/configmap/:templateId',
                        name: 'mesosTemplatesetConfigmap',
                        component: MesosCreateConfigmap
                    },
                    {
                        path: 'templateset/secret/:templateId',
                        name: 'mesosTemplatesetSecret',
                        component: MesosCreateSecret
                    }
                ]
            },
            {
                path: 'k8s',
                name: 'k8sConfigurationCreate',
                component: K8sConfigurationCreate,
                children: [
                    {
                        path: 'templateset/deployment/:templateId',
                        name: 'k8sTemplatesetDeployment',
                        component: K8sCreateDeployment
                    },
                    {
                        path: 'templateset/service/:templateId',
                        name: 'k8sTemplatesetService',
                        component: K8sCreateService
                    },
                    {
                        path: 'templateset/configmap/:templateId',
                        name: 'k8sTemplatesetConfigmap',
                        component: K8sCreateConfigmap
                    },
                    {
                        path: 'templateset/secret/:templateId',
                        name: 'k8sTemplatesetSecret',
                        component: K8sCreateSecret
                    },
                    {
                        path: 'templateset/daemonset/:templateId',
                        name: 'k8sTemplatesetDaemonset',
                        component: K8sCreateDaemonset
                    },
                    {
                        path: 'templateset/job/:templateId',
                        name: 'k8sTemplatesetJob',
                        component: K8sCreateJob
                    },
                    {
                        path: 'templateset/statefulset/:templateId',
                        name: 'k8sTemplatesetStatefulset',
                        component: K8sCreateStatefulset
                    },
                    {
                        path: 'templateset/ingress/:templateId',
                        name: 'k8sTemplatesetIngress',
                        component: K8sCreateIngress
                    },
                    {
                        path: 'yaml-templateset/:templateId',
                        name: 'K8sYamlTemplateset',
                        component: K8sYamlTemplateset
                    }
                ]
            },
            {
                path: 'var',
                name: 'var',
                component: Variable
            }
        ]
    }
]

export default childRoutes
