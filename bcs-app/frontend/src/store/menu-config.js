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

/**
 * 生成左侧导航菜单
 *
 * @param {string} lang 当前语言标识 en-US 英文 zh-CN 中文
 *
 * @return {Object} 左侧导航菜单对象
 */
export default function menuConfig (lang) {
    let cluster = '集群'
    let node = '节点'
    let namespace = '命名空间'
    let templateset = '模板集'
    let variable = '变量管理'
    let app = '应用'
    let network = '网络'
    let resource = '资源'
    let imageHub = '仓库'
    let publicImage = '公共镜像'
    let projectImage = '项目镜像'
    let operateAudit = '操作审计'
    let eventQuery = '事件查询'
    let monitor = '监控中心'
    let release = 'Release列表'
    let chart = 'Chart仓库'

    if (lang === 'en-US') {
        cluster = 'Clusters'
        node = 'Nodes'
        namespace = 'Namespaces'
        templateset = 'TemplateSets'
        variable = 'Variables'
        app = 'Applications'
        network = 'Network'
        resource = 'Resource'
        imageHub = 'ImageHub'
        publicImage = 'Public'
        projectImage = 'Private'
        operateAudit = 'Operate Audit'
        eventQuery = 'Event Query'
        monitor = 'Monitor'
        release = 'Release'
        chart = 'Chart'
    }

    return {
        menuList: [
            {
                name: cluster,
                icon: 'icon-jq-colony',
                pathName: [
                    'clusterMain', 'clusterCreate', 'clusterOverview',
                    'clusterNode', 'clusterInfo', 'clusterNodeOverview', 'containerDetailForNode'
                ],
                roleId: 'cluster:menu'
            },
            {
                name: node,
                icon: 'icon-jd-node',
                pathName: ['nodeMain'],
                roleId: 'node:menu'
            },
            {
                name: namespace,
                icon: 'icon-namespace',
                roleId: 'configuration:menu',
                pathName: ['namespace']
            },
            { name: 'line' },
            {
                name: templateset,
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
                name: variable,
                icon: 'icon-var',
                roleId: 'configuration:menu',
                pathName: ['var']
            },
            { name: 'line' },
            {
                name: app,
                icon: 'icon-yy-apply',
                pathName: ['mesos', 'instanceDetail', 'instanceDetail2', 'containerDetail', 'containerDetail2', 'mesosInstantiation'],
                roleId: 'app:menu'
            },
            {
                name: network,
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
                name: resource,
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
                name: imageHub,
                icon: 'icon-ck-store',
                roleId: 'repo:menu',
                children: [
                    {
                        name: publicImage,
                        pathName: ['imageLibrary']
                    },
                    {
                        name: projectImage,
                        pathName: ['projectImage']
                    }
                ]
            },
            { name: 'line' },
            {
                name: operateAudit,
                icon: 'icon-operate-audit',
                pathName: ['operateAudit']
            },
            {
                name: eventQuery,
                icon: 'icon-event-query',
                pathName: ['eventQuery']
            },
            { name: 'line' },
            {
                name: monitor,
                icon: 'icon-monitors',
                externalLink: '/console/monitor/',
                pathName: []
            }
        ],
        k8sMenuList: [
            {
                name: cluster,
                icon: 'icon-jq-colony',
                pathName: [
                    'clusterMain', 'clusterCreate', 'clusterOverview',
                    'clusterNode', 'clusterInfo', 'clusterNodeOverview', 'containerDetailForNode'
                ],
                roleId: 'cluster:menu'
            },
            {
                name: node,
                icon: 'icon-jd-node',
                pathName: ['nodeMain'],
                roleId: 'node:menu'
            },
            {
                name: namespace,
                icon: 'icon-namespace',
                roleId: 'configuration:menu',
                pathName: ['namespace']
            },
            { name: 'line' },
            {
                name: templateset,
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
                name: variable,
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
                        name: release,
                        pathName: ['helms', 'helmAppDetail']
                    },
                    {
                        name: chart,
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
                name: app,
                icon: 'icon-yy-apply',
                roleId: 'app:menu',
                children: [
                    {
                        name: 'Deployments',
                        pathName: [
                            'deployments', 'deploymentsInstanceDetail', 'deploymentsInstanceDetail2',
                            'deploymentsContainerDetail', 'deploymentsContainerDetail2', 'deploymentsInstantiation'
                        ]
                    },
                    {
                        name: 'DaemonSets',
                        pathName: [
                            'daemonset', 'daemonsetInstanceDetail', 'daemonsetInstanceDetail2',
                            'daemonsetContainerDetail', 'daemonsetContainerDetail2', 'daemonsetInstantiation'
                        ]
                    },
                    {
                        name: 'Jobs',
                        pathName: [
                            'job', 'jobInstanceDetail', 'jobInstanceDetail2',
                            'jobContainerDetail', 'jobContainerDetail2', 'jobInstantiation'
                        ]
                    },
                    {
                        name: 'StatefulSets',
                        pathName: [
                            'statefulset', 'statefulsetInstanceDetail', 'statefulsetInstanceDetail2',
                            'statefulsetContainerDetail', 'statefulsetContainerDetail2', 'statefulsetInstantiation'
                        ]
                    }
                ]
            },
            {
                name: network,
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
                name: resource,
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
                name: imageHub,
                icon: 'icon-ck-store',
                roleId: 'repo:menu',
                children: [
                    {
                        name: publicImage,
                        pathName: ['imageLibrary']
                    },
                    {
                        name: projectImage,
                        pathName: ['projectImage']
                    }
                ]
            },
            { name: 'line' },
            {
                name: operateAudit,
                icon: 'icon-operate-audit',
                pathName: ['operateAudit']
            },
            {
                name: eventQuery,
                icon: 'icon-event-query',
                pathName: ['eventQuery']
            },
            { name: 'line' },
            {
                name: monitor,
                icon: 'icon-monitors',
                externalLink: '/console/monitor/',
                pathName: []
            }
        ]
    }
}
