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

const App = () => import(/* webpackChunkName: 'app-entry' */'@open/views/app')

const childRoutes = [
    // domain/bcs/projectId/app 应用页面
    {
        path: ':projectCode/app',
        component: App,
        children: [
            // mesos 应用
            {
                path: 'mesos',
                name: 'mesos',
                children: [
                    // mesos 应用里的实例详情页面
                    {
                        path: ':instanceId',
                        name: 'instanceDetail'
                    },

                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory',
                        name: 'instanceDetail2'
                    },
                    // mesos 应用里的容器详情页面
                    {
                        path: ':instanceId/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'containerDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'containerDetail2'
                    },
                    {
                        path: ':templateId/instantiation/:category/:tmplAppName/:tmplAppId',
                        name: 'mesosInstantiation'
                    }
                ]
            },
            // k8s deployments 应用
            {
                path: 'deployments',
                name: 'deployments',
                children: [
                    // k8s deployments 应用里的实例详情页面
                    {
                        path: ':instanceId',
                        name: 'deploymentsInstanceDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory',
                        name: 'deploymentsInstanceDetail2'
                    },
                    // k8s deployments 应用里的容器详情页面
                    {
                        path: ':instanceId/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'deploymentsContainerDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'deploymentsContainerDetail2'
                    },
                    // k8s deployments 应用里的应用实例化页面
                    {
                        path: ':templateId/instantiation/:category/:tmplAppName/:tmplAppId',
                        name: 'deploymentsInstantiation'
                    }
                ]
            },
            // k8s daemonset 应用
            {
                path: 'daemonset',
                name: 'daemonset',
                children: [
                    // k8s daemonset 应用里的实例详情页面
                    {
                        path: ':instanceId',
                        name: 'daemonsetInstanceDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory',
                        name: 'daemonsetInstanceDetail2'
                    },
                    // k8s daemonset 应用里的容器详情页面
                    {
                        path: ':instanceId/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'daemonsetContainerDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'daemonsetContainerDetail2'
                    },
                    // k8s daemonset 应用里的应用实例化页面
                    {
                        path: ':templateId/instantiation/:category/:tmplAppName/:tmplAppId',
                        name: 'daemonsetInstantiation'
                    }
                ]
            },
            // k8s job 应用
            {
                path: 'job',
                name: 'job',
                children: [
                    // k8s job 应用里的实例详情页面
                    {
                        path: ':instanceId',
                        name: 'jobInstanceDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory',
                        name: 'jobInstanceDetail2'
                    },
                    // k8s job 应用里的容器详情页面
                    {
                        path: ':instanceId/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'jobContainerDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'jobContainerDetail2'
                    },
                    // k8s job 应用里的应用实例化页面
                    {
                        path: ':templateId/instantiation/:category/:tmplAppName/:tmplAppId',
                        name: 'jobInstantiation'
                    }
                ]
            },
            // k8s statefulset 应用
            {
                path: 'statefulset',
                name: 'statefulset',
                children: [
                    // k8s statefulset 应用里的实例详情页面
                    {
                        path: ':instanceId',
                        name: 'statefulsetInstanceDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory',
                        name: 'statefulsetInstanceDetail2'
                    },
                    // k8s statefulset 应用里的容器详情页面
                    {
                        path: ':instanceId/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'statefulsetContainerDetail'
                    },
                    {
                        path: ':instanceName/:instanceNamespace/:instanceCategory/taskgroups/:taskgroupName/containers/:containerId',
                        name: 'statefulsetContainerDetail2'
                    },
                    // k8s statefulset 应用里的应用实例化页面
                    {
                        path: ':templateId/instantiation/:category/:tmplAppName/:tmplAppId',
                        name: 'statefulsetInstantiation'
                    }
                ]
            }
        ]
    }
]

export default childRoutes
