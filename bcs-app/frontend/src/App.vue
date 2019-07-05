<template>
    <div id="app" class="biz-app" :class="systemCls">
        <app-header ref="appHeader" @reloadCurPage="reloadCurPage"></app-header>
        <div style="height: 100%;" v-if="isLoading">
            <div class="bk-loading" style="background-color: rgba(255, 255, 255, 1)">
                <div class="bk-loading-wrapper">
                    <div class="bk-dot-loading" style="height: 20px;">
                        <div class="point point1"></div>
                        <div class="point point2"></div>
                        <div class="point point3"></div>
                        <div class="point point4"></div>
                    </div>
                </div>
            </div>
        </div>
        <template v-else>
            <div class="app-container" :style="{ minHeight: minHeight + 'px' }" v-if="isUserBKService">
                <router-view :key="routerKey" />
            </div>
            <div v-else>
                <div class="biz-guide-box" style="border: none; box-shadow: none; margin-top: 0;" :style="{ height: `${height}px` }">
                    <p class="title">容器服务未启用，请完善以下信息</p>
                    <main class="bk-form biz-app-form">
                        <div class="form-item">
                            <label>业务编排类型：</label>
                            <div class="form-item-inner">
                                <label class="bk-form-radio">
                                    <input type="radio" value="1" name="kind" v-model="kind">
                                    <i class="bk-radio-text">Kubernetes</i>
                                </label>
                                <label class="bk-form-radio">
                                    <input type="radio" value="2" name="kind" v-model="kind">
                                    <i class="bk-radio-text">Mesos</i>
                                </label>
                            </div>
                        </div>
                        <div class="form-item" v-if="ccList.length" style="margin-bottom: 30px;">
                            <label>关联CMDB业务：<span class="red">*</span></label>
                            <div class="form-item-inner">
                                <div style="display: inline-block;" class="mr5">
                                    <bk-selector
                                        style="width: 250px;"
                                        placeholder="请选择"
                                        :searchable="true"
                                        :setting-key="'id'"
                                        :display-key="'name'"
                                        :selected.sync="ccKey"
                                        :list="ccList">
                                    </bk-selector>
                                </div>
                                <bk-tooltip placement="top" content="关联业务后，您可以从对应的业务下选择机器，搭建容器集群">
                                    <span style="font-size: 12px;cursor: pointer;">
                                        <i class="bk-icon icon-info-circle"></i>
                                    </span>
                                </bk-tooltip>
                            </div>
                        </div>
                        <div class="form-item" v-else>
                            <label>关联CMDB业务：<span class="red">*</span></label>
                            <div class="form-item-inner" style="margin-top: -20px;">
                                <p class="desc">当前账号在蓝鲸配置平台无业务，请联系运维在蓝鲸配置平台关联业务，<a :href="bkCCHost" target="_blank">点击查看业务和运维信息</a></p>
                            </div>
                        </div>
                        <button class="bk-button bk-primary" :class="enableBtn ? '' : 'is-disabled'"
                            style="margin-left: -40px;"
                            @click="updateProject"
                            :disabled="!enableBtn">
                            启用容器服务
                        </button>
                    </main>
                </div>
            </div>
        </template>
        <app-apply-perm ref="bkApplyPerm"></app-apply-perm>
    </div>
</template>
<script>
    import Img403 from '@open/images/403.png'
    import { bus } from '@open/common/bus'
    import { getProjectByCode } from '@open/common/util'

    export default {
        name: 'app',
        data () {
            return {
                routerKey: +new Date(),
                systemCls: 'mac',
                minHeight: 768,
                isUserBKService: true,
                curProject: null,
                height: 0,
                ccKey: '',
                ccList: [],
                kind: 1, // 业务编排类型
                enableBtn: false, // 提交按钮是否可用
                projectId: '',
                projectCode: '',
                isLoading: true,
                bkCCHost: window.BK_CC_HOST + '/#/business'
            }
        },
        computed: {
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            }
        },
        watch: {
            '$route' (to, from) {
                this.checkProject()
                this.initProjectId()
                if (window.$syncUrl) {
                    const path = this.$route.fullPath.replace(new RegExp(`^${SITE_URL}`), '')
                    window.$syncUrl(path)
                }
            },
            ccKey (val) {
                this.enableBtn = val !== null && val !== undefined
            }
        },
        async created () {
            const platform = window.navigator.platform.toLowerCase()
            if (platform.indexOf('win') === 0) {
                this.systemCls = 'win'
            }

            window.addEventListener('change::$currentProjectId', async e => {
                this.isLoading = true

                const curProjectCode = e.detail.currentProjectId
                this.initProjectId(curProjectCode)

                // 项目切换时，先将集群列表清空
                this.$store.commit('cluster/forceUpdateClusterList', [])

                if (localStorage.getItem('curProjectCode') !== curProjectCode) {
                    this.$refs.appHeader.selectProject(curProjectCode)
                }

                // 从配置中心拉取项目列表，顶导的项目列表信息里，项目中关于容器服务的信息可能更新不及时
                await this.$store.dispatch('getProjectList')
                await this.checkProject()

                this.isLoading = false
            })
        },
        mounted () {
            document.title = '容器服务'
            if (window.$changeDocumentTitle) {
                window.$changeDocumentTitle('蓝鲸容器管理平台')
            }

            this.initContainerSize()
            window.onresize = () => {
                this.initContainerSize()
                this.height = window.innerHeight
            }

            this.height = window.innerHeight

            const self = this
            bus.$on('show-apply-perm-modal', data => {
                const projectCode = self.$route.params.projectCode
                self.$refs.bkApplyPerm && self.$refs.bkApplyPerm.show(projectCode, data)
            })
            bus.$on('show-error-message', data => {
                self.$bkMessage({
                    theme: 'error',
                    message: data
                })
            })
            bus.$on('show-apply-perm', data => {
                const projectCode = self.$route.params.projectCode
                const content = ''
                    + '<div class="biz-top-bar">'
                    + '<div class="biz-back-btn" onclick="history.back()">'
                    + '<i class="bk-icon icon-arrows-left back"></i>'
                    + '<span></span>'
                    + '</div>'
                    + '</div>'
                    + '<div class="bk-exception bk-exception-center">'
                    + `<img src="${Img403}"/>`
                    + '<h2 class="exception-text">'
                    + '<p class="f14">Sorry，您的权限不足，请去'
                    + `<a class="bk-text-button" href="${data.data.apply_url}&project_code=${projectCode}" target="_blank">申请</a>`
                    + '</p>'
                    + '</h2>'
                    + '</div>'

                document.querySelector('.biz-content').innerHTML = content
            })
            bus.$on('close-apply-perm-modal', data => {
                self.$refs.bkApplyPerm && self.$refs.bkApplyPerm.hide()
            })
        },
        methods: {
            /**
             * 初始化容器最小高度
             */
            initContainerSize () {
                const WIN_MIN_HEIGHT = 768
                const APP_FOOTER_HEIGHT = 210
                const winHeight = window.innerHeight
                if (winHeight <= WIN_MIN_HEIGHT) {
                    this.minHeight = WIN_MIN_HEIGHT
                } else {
                    this.minHeight = winHeight - APP_FOOTER_HEIGHT
                }
            },

            /**
             * 检测项目是否是 IEG 项目，是否使用了蓝鲸服务
             */
            async checkProject () {
                const projectCode = window.$currentProjectId
                if (projectCode && this.onlineProjectList.length) {
                    for (const project of this.onlineProjectList) {
                        if (project.project_code === projectCode) {
                            this.curProject = project
                            this.isUserBKService = project.kind !== 0
                            if (!this.isUserBKService) {
                                await this.fetchCCList()
                                if (project.cc_app_id !== 0) {
                                    this.ccKey = project.cc_app_id
                                }
                            }
                        }
                    }
                }
            },

            /**
             * 初始化时，将通过 projectCode 值获取 projectId 并存储在路由中
             */
            initProjectId (projectCode = window.$currentProjectId || this.$route.params.projectCode) {
                if (window.$currentProjectId) {
                    this.projectCode = window.$currentProjectId
                    this.$route.params.projectCode = this.projectCode
                    const project = getProjectByCode(this.projectCode)
                    const projectId = project.project_id
                    if (projectId) {
                        this.$route.params.projectId = projectId
                        this.projectId = projectId
                    }
                }
            },

            /**
             * 获取关联 CC 的数据
             */
            async fetchCCList () {
                try {
                    const res = await this.$store.dispatch('getCCList')
                    this.ccList = [...(res.data || [])]
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 启用容器服务 更新项目
             */
            async updateProject () {
                try {
                    this.isLoading = true
                    await this.$store.dispatch('editProject', Object.assign({}, this.curProject, {
                        // deploy_type 值固定，就是原来页面上的：部署类型：容器部署
                        deploy_type: [2],
                        // kind 业务编排类型：1 Kubernetes, 2 Mesos
                        kind: parseInt(this.kind, 10),
                        // use_bk 值固定，就是原来页面上的：使用蓝鲸部署服务
                        use_bk: true,
                        cc_app_id: this.ccKey
                    }))

                    // await this.$store.dispatch('getProjectList')

                    this.$nextTick(() => {
                        window.location.reload()
                        // 这里不需要设置 isLoading 为 false，页面刷新后，isLoading 的值会重置为 true
                        // 如果设置了后，页面会闪烁一下
                        // this.isLoading = false
                    })
                } catch (e) {
                    console.error(e)
                    this.isLoading = false
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 改变 routerKey，刷新 router
             */
            reloadCurPage () {
                this.routerKey = +new Date()
            }
        }
    }
</script>
<style>
    @import './css/reset.css';
    @import './css/app.css';
    @import './css/animation.css';

    .app-container {
        min-width: 1280px;
        min-height: 768px;
        position: relative;
        display: flex;
        background: #fafbfd;
        min-height: 100% !important;
        padding-top: 0;
    }
    .app-content {
        flex: 1;
        background: #fafbfd;
    }
</style>
