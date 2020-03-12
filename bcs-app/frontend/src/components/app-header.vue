<template>
    <app-auth ref="bkAuth"></app-auth>
</template>

<script>
    import { bus } from '@open/common/bus'
    import { getProjectById, getProjectByCode } from '@open/common/util'

    export default {
        data () {
            // 切换顶导项目时，如果 router 是如下数组中的，那么就会跳转到特定的 router
            // 如果希望切换项目时 router 保持，那么这里就不需要配置
            return {
                clusterRouters: [
                    'clusterMain',
                    'clusterCreate',
                    'clusterOverview',
                    'clusterInfo',
                    'clusterNode',
                    'clusterNodeOverview',
                    'containerDetailForNode',
                    '404'
                ],
                configurationRouters: [
                    'mesosTemplatesetApplication',
                    'mesosTemplatesetDeployment',
                    'mesosTemplatesetService',
                    'mesosTemplatesetConfigmap',
                    'mesosTemplatesetSecret',
                    'mesosTemplatesetIngress',
                    'mesosTemplatesetHPA',
                    'instantiation',

                    'k8sTemplatesetDeployment',
                    'k8sTemplatesetService',
                    'k8sTemplatesetConfigmap',
                    'k8sTemplatesetSecret',
                    'k8sTemplatesetDaemonset',
                    'k8sTemplatesetJob',
                    'k8sTemplatesetStatefulset',
                    'k8sTemplatesetIngress',
                    'k8sTemplatesetHPA'
                ],
                loadBalanceRouters: [
                    'loadBalance',
                    'loadBalanceDetail'
                ],
                depotRouters: [
                    'imageDetail'
                ],
                helmRouters: [
                    'helms',
                    'helmTplList',
                    'helmTplDetail',
                    'helmTplInstance',
                    'helmAppDetail'
                ],
                metricRouters: [
                    'metricManage'
                ]
            }
        },
        computed: {
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            },
            projectCode () {
                const route = this.$route
                // 从路由获取 projectCode
                if (route.params.projectCode) {
                    this.setLocalStorage(route.params.projectCode)
                    return route.params.projectCode
                }

                // 从缓存获取projectId
                if (localStorage.curProjectCode) {
                    const projectCode = localStorage.curProjectCode
                    for (const item of this.onlineProjectList) {
                        if (item.project_code === projectCode) {
                            return projectCode
                        }
                    }
                }

                // 直接显示第一个项目
                if (this.onlineProjectList.length) {
                    return this.onlineProjectList[0].project_code
                }

                return ''
            },
            projectId () {
                const route = this.$route
                // 从路由获取projectId
                if (route.params.projectId) {
                    this.setLocalStorage(route.params.projectId)
                    return route.params.projectId
                }

                // 从缓存获取projectId
                if (localStorage.curProjectId) {
                    const projectId = localStorage.curProjectId
                    for (const item of this.onlineProjectList) {
                        if (item.project_id === projectId) {
                            return projectId
                        }
                    }
                }

                // 直接显示第一个项目
                if (this.onlineProjectList.length) {
                    const projectId = this.onlineProjectList[0].project_id
                    this.setLocalStorage(projectId)
                    return projectId
                }

                return ''
            },
            parentRouteName () {
                const bcsRouteKeys = [
                    'containerServiceMain',
                    'clusterMain',
                    'clusterCreate',
                    'clusterOverview',
                    'clusterInfo',
                    'clusterNodeOverview',
                    'containerDetailForNode',
                    'mesos',
                    'instanceDetail',
                    'instanceDetail2',
                    'containerDetail',
                    'containerDetail2',
                    'mesosInstantiation',
                    'deployments',
                    'deploymentsInstanceDetail',
                    'deploymentsInstanceDetail2',
                    'deploymentsContainerDetail',
                    'deploymentsContainerDetail2',
                    'deploymentsInstantiation',
                    'daemonset',
                    'daemonsetInstanceDetail',
                    'daemonsetInstanceDetail2',
                    'daemonsetContainerDetail',
                    'daemonsetContainerDetail2',
                    'daemonsetInstantiation',
                    'job',
                    'jobInstanceDetail',
                    'jobInstanceDetail2',
                    'jobContainerDetail',
                    'jobContainerDetail2',
                    'jobInstantiation',
                    'statefulset',
                    'statefulsetInstanceDetail',
                    'statefulsetInstanceDetail2',
                    'statefulsetContainerDetail',
                    'statefulsetContainerDetail2',
                    'statefulsetInstantiation',

                    'service',
                    'loadBalance',
                    'loadBalanceDetail',
                    'resourceMain',
                    'resourceConfigmap',
                    'resourceSecret',
                    'depotMain',
                    'imageLibrary',
                    'projectImage',
                    'clusterNode',
                    'nodeMain',
                    'myCollect',
                    'mcMain',
                    'operateAudit',
                    'eventQuery',
                    'configurationMain',
                    'namespace',
                    'templateset',
                    'configurationCreate',
                    'mesosTemplatesetApplication',
                    'mesosTemplatesetDeployment',
                    'mesosTemplatesetService',
                    'mesosTemplatesetConfigmap',
                    'mesosTemplatesetSecret',
                    'k8sTemplatesetApplication',
                    'k8sTemplatesetDeployment',
                    'k8sTemplatesetService',
                    'k8sTemplatesetConfigmap',
                    'k8sTemplatesetSecret',
                    'k8sTemplatesetIngress',
                    'k8sTemplatesetHPA',
                    'instantiation',
                    'metricManage'
                ]

                const routeName = this.$route.name

                let parentRouteName = ''

                if (bcsRouteKeys.includes(routeName)) {
                    parentRouteName = 'clusterMain'
                    document.title = '容器服务'
                }
                return parentRouteName
            }
        },
        created () {
            // 点击导航模块名称时，会触发返回当前模块首页事件，由iframe内部进行返回首页的跳转
            window.addEventListener('order::backHome', () => {
                this.reloadPage(this.parentRouteName)
            })
        },
        mounted () {
            const self = this
            bus.$on('show-login-modal', data => {
                self.$refs.bkAuth && self.$refs.bkAuth.showLoginModal(data)
            })
            bus.$on('close-login-modal', () => {
                self.$refs.bkAuth && self.$refs.bkAuth.hideLoginModal()
            })
        },
        methods: {
            /**
             * 保存 projectId 和 projectCode 到本地存储中
             *
             * @param {string} projectId 项目 id
             */
            setLocalStorage (projectId) {
                const project = getProjectById(projectId)
                const projectCode = project.project_code
                localStorage.setItem('curProjectId', projectId)
                localStorage.setItem('curProjectCode', projectCode)
            },

            /**
             * 刷新当前页
             *
             * @param {string} routeName 当前路由名称
             */
            reloadPage (routeName) {
                const projectId = this.projectId
                const projectCode = this.projectCode || getProjectById(projectId).project_code
                const curRouteName = this.$route.name
                if (routeName === curRouteName) {
                    this.$emit('reloadCurPage')
                } else {
                    this.$router.push({
                        name: routeName,
                        params: {
                            projectId: projectId,
                            projectCode: projectCode,
                            needCheckPermission: true
                        }
                    })
                }
            },

            /**
             * 选中项目
             *
             * @param {string} projectCode 项目 code
             */
            selectProject (projectCode) {
                const routeName = this.$route.name
                if (!routeName) {
                    return false
                }
                // console.error('selectProject', projectCode)
                const projectId = getProjectByCode(projectCode).project_id

                this.setLocalStorage(projectId)

                // 这么做是因为如果在总览页面或者节点列表页面或者节点详情页面时，切换项目的时候，新切换的项目可能会没有当前的 clusterId
                if (this.clusterRouters.indexOf(routeName) > -1) {
                    this.$router.push({
                        name: 'clusterMain',
                        params: {
                            projectCode: projectCode,
                            projectId: projectId,
                            needCheckPermission: true
                        },
                        query: this.$route.query || {}
                    })
                } else if (this.configurationRouters.indexOf(routeName) > -1) {
                    this.$router.push({
                        name: 'templateset',
                        params: {
                            projectCode: projectCode,
                            projectId: projectId,
                            needCheckPermission: true
                        },
                        query: this.$route.query || {}
                    })
                } else if (this.loadBalanceRouters.indexOf(routeName) > -1) {
                    // 如果当前是LoadBalance下，返回到LoadBalance 列表
                    this.$router.push({
                        name: 'loadBalance',
                        params: {
                            projectId: projectId,
                            projectCode: projectCode,
                            needCheckPermission: true
                        },
                        query: this.$route.query || {}
                    })
                } else if (this.depotRouters.indexOf(routeName) > -1) {
                    this.$router.push({
                        name: 'imageLibrary',
                        params: {
                            projectId: projectId,
                            projectCode: projectCode,
                            needCheckPermission: true
                        },
                        query: this.$route.query || {}
                    })
                } else if (this.helmRouters.indexOf(routeName) > -1) {
                    this.$router.push({
                        name: 'helms',
                        params: {
                            projectId: projectId,
                            projectCode: projectCode,
                            needCheckPermission: true
                        },
                        query: this.$route.query || {}
                    })
                } else if (this.metricRouters.indexOf(routeName) > -1) {
                    this.$router.push({
                        name: 'metricManage',
                        params: {
                            projectId: projectId,
                            projectCode: projectCode,
                            needCheckPermission: true
                        },
                        // 这里去掉 url 参数
                        query: {}
                    })
                }
            }
        }
    }
</script>
