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

export default {
    menuList: [
        {
            name: '集群',
            icon: 'icon-jq-colony',
            pathName: [
                'clusterMain', 'clusterCreate', 'clusterOverview',
                'clusterNode', 'clusterInfo', 'clusterNodeOverview', 'containerDetailForNode'
            ],
            roleId: 'cluster:menu'
        },
        {
            name: '节点',
            icon: 'icon-jd-node',
            pathName: ['nodeMain'],
            roleId: 'node:menu'
        },
        {
            name: '命名空间',
            icon: 'icon-namespace',
            roleId: 'configuration:menu',
            pathName: ['namespace']
        },
        { name: 'line' },
        {
            name: '模板集',
            icon: 'icon-templateset',
            roleId: 'configuration:menu',
            pathName: [
                'templateset',
                'mesosTemplatesetApplication',
                'mesosTemplatesetDeployment',
                'mesosTemplatesetService',
                'mesosTemplatesetConfigmap',
                'mesosTemplatesetSecret',
                'instantiation'
            ]
        },
        {
            name: '变量管理',
            icon: 'icon-var',
            roleId: 'configuration:menu',
            pathName: ['var']
        },
        { name: 'line' },
        {
            name: '应用',
            icon: 'icon-yy-apply',
            pathName: ['mesos', 'instanceDetail', 'instanceDetail2', 'containerDetail', 'containerDetail2', 'mesosInstantiation'],
            roleId: 'app:menu'
        },
        {
            name: '网络',
            icon: 'icon-wl-network',
            roleId: 'network:menu',
            children: [
                {
                    name: 'Service',
                    pathName: ['service']
                },
                {
                    name: 'LoadBalance',
                    pathName: ['loadBalance', 'loadBalanceDetail']
                }
            ]
        },
        {
            name: '资源',
            icon: 'icon-zy-resource',
            roleId: 'resource:menu',
            children: [
                {
                    name: 'Configmaps',
                    pathName: ['resourceConfigmap']
                },
                {
                    name: 'Secrets',
                    pathName: ['resourceSecret']
                }
            ]
        },
        { name: 'line' },
        {
            name: '仓库',
            icon: 'icon-ck-store',
            roleId: 'repo:menu',
            children: [
                {
                    name: '公共镜像',
                    pathName: ['imageLibrary']
                },
                {
                    name: '项目镜像',
                    pathName: ['projectImage']
                }
            ]
        },
        { name: 'line' },
        {
            name: '操作审计',
            icon: 'icon-operate-audit',
            pathName: ['operateAudit']
        },
        {
            name: '事件查询',
            icon: 'icon-event-query',
            pathName: ['eventQuery']
        },
        { name: 'line' },
        {
            name: '监控中心',
            icon: 'icon-monitors',
            externalLink: '/console/monitor/',
            pathName: []
        }
    ],
    k8sMenuList: [
        {
            name: '集群',
            icon: 'icon-jq-colony',
            pathName: [
                'clusterMain', 'clusterCreate', 'clusterOverview',
                'clusterNode', 'clusterInfo', 'clusterNodeOverview', 'containerDetailForNode'
            ],
            roleId: 'cluster:menu'
        },
        {
            name: '节点',
            icon: 'icon-jd-node',
            pathName: ['nodeMain'],
            roleId: 'node:menu'
        },
        {
            name: '命名空间',
            icon: 'icon-namespace',
            roleId: 'configuration:menu',
            pathName: ['namespace']
        },
        { name: 'line' },
        {
            name: '模板集',
            icon: 'icon-templateset',
            roleId: 'configuration:menu',
            pathName: [
                'templateset',
                'k8sTemplatesetDeployment',
                'k8sTemplatesetDaemonset',
                'k8sTemplatesetJob',
                'k8sTemplatesetStatefulset',
                'k8sTemplatesetService',
                'k8sTemplatesetConfigmap',
                'k8sTemplatesetSecret',
                'k8sTemplatesetIngress',
                'instantiation'
            ]
        },
        {
            name: '变量管理',
            icon: 'icon-var',
            roleId: 'configuration:menu',
            pathName: ['var']
        },
        { name: 'line' },
        {
            name: 'Helm',
            icon: 'icon-helm',
            children: [
                {
                    name: 'Release列表',
                    pathName: ['helms', 'helmAppDetail']
                },
                {
                    name: 'Chart仓库',
                    pathName: [
                        'helmTplList',
                        'helmTplDetail',
                        'helmTplInstance'
                    ]
                }
            ]
        },
        { name: 'line' },
        {
            name: '应用',
            icon: 'icon-yy-apply',
            roleId: 'app:menu',
            children: [
                {
                    name: 'Deployment',
                    pathName: [
                        'deployments', 'deploymentsInstanceDetail', 'deploymentsInstanceDetail2',
                        'deploymentsContainerDetail', 'deploymentsContainerDetail2', 'deploymentsInstantiation'
                    ]
                },
                {
                    name: 'DaemonSet',
                    pathName: [
                        'daemonset', 'daemonsetInstanceDetail', 'daemonsetInstanceDetail2',
                        'daemonsetContainerDetail', 'daemonsetContainerDetail2', 'daemonsetInstantiation'
                    ]
                },
                {
                    name: 'Job',
                    pathName: [
                        'job', 'jobInstanceDetail', 'jobInstanceDetail2',
                        'jobContainerDetail', 'jobContainerDetail2', 'jobInstantiation'
                    ]
                },
                {
                    name: 'StatefulSet',
                    pathName: [
                        'statefulset', 'statefulsetInstanceDetail', 'statefulsetInstanceDetail2',
                        'statefulsetContainerDetail', 'statefulsetContainerDetail2', 'statefulsetInstantiation'
                    ]
                }
            ]
        },
        {
            name: '网络',
            icon: 'icon-wl-network',
            roleId: 'network:menu',
            children: [
                {
                    name: 'Service',
                    pathName: ['service']
                },
                {
                    name: 'Ingress',
                    pathName: ['resourceIngress']
                },
                {
                    name: 'LoadBalance',
                    pathName: ['loadBalance', 'loadBalanceDetail']
                }
            ]
        },
        {
            name: '资源',
            icon: 'icon-zy-resource',
            roleId: 'resource:menu',
            children: [
                {
                    name: 'Configmaps',
                    pathName: ['resourceConfigmap']
                },
                {
                    name: 'Secrets',
                    pathName: ['resourceSecret']
                }
            ]
        },
        { name: 'line' },
        {
            name: '仓库',
            icon: 'icon-ck-store',
            roleId: 'repo:menu',
            children: [
                {
                    name: '公共镜像',
                    pathName: ['imageLibrary']
                },
                {
                    name: '项目镜像',
                    pathName: ['projectImage']
                }
            ]
        },
        { name: 'line' },
        {
            name: '操作审计',
            icon: 'icon-operate-audit',
            pathName: ['operateAudit']
        },
        {
            name: '事件查询',
            icon: 'icon-event-query',
            pathName: ['eventQuery']
        },
        { name: 'line' },
        {
            name: '监控中心',
            icon: 'icon-monitors',
            externalLink: '/console/monitor/',
            pathName: []
        }
    ]
}
