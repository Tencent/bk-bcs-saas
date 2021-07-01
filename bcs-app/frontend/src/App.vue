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
                <bcs-unregistry :cc-list="ccList"
                    :default-kind="kind"
                    @kind-change="handleKindChange"
                    @cc-change="handleCmdbChange"
                    @update-project="updateProject">
                </bcs-unregistry>
            </div>
        </template>
        <app-apply-perm ref="bkApplyPerm"></app-apply-perm>
    </div>
</template>
<script>
    import { bus } from '@open/common/bus'
    import { getProjectByCode } from '@open/common/util'
    import Img403 from '@/images/403.png'
    import BcsUnregistry from '@open/components/bcs-unregistry/unregistry.vue'

    export default {
        name: 'app',
        components: {
            BcsUnregistry
        },
        data () {
            return {
                routerKey: +new Date(),
                systemCls: 'mac',
                minHeight: 768,
                isUserBKService: true,
                curProject: null,
                isIEGProject: true,
                height: 0,
                ccKey: '',
                ccList: [],
                kind: 1, // 业务编排类型
                // 前一次选中的编排类型，用于选中 tke 请求失败后，单选框恢复到上一个状态
                prevKind: 1,
                enableBtn: false, // 提交按钮是否可用
                projectId: '',
                projectCode: '',
                isLoading: true
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
            },
            kind (v, old) {
                this.prevKind = old
                this.fetchCCList()
            },
            '$store.state.curClusterId' () {
                this.routerKey = +new Date()
                this.$store.dispatch('getFeatureFlag')
            }
        },
        async created () {
            const platform = window.navigator.platform.toLowerCase()
            if (platform.indexOf('win') === 0) {
                this.systemCls = 'win'
            }

            if (this.$store.state.isEn) {
                this.systemCls += ' english'
            }

            window.addEventListener('change::$currentProjectId', async e => {
                this.isLoading = true

                const curProjectCode = e.detail.currentProjectId
                this.initProjectId(curProjectCode)

                // 项目切换时，先将集群列表清空
                this.$store.commit('cluster/forceUpdateClusterList', [])

                if (localStorage.getItem('curProjectCode') !== curProjectCode) {
                    this.$store.commit('updateCurClusterId', '')
                    this.$refs.appHeader.selectProject(curProjectCode)
                }

                // 从配置中心拉取项目列表，顶导的项目列表信息里，项目中关于容器服务的信息可能更新不及时
                const projectList = await this.$store.dispatch('getProjectList')
                await this.checkProject()
                if (this.isUserBKService) {
                    await this.$store.dispatch('getFeatureFlag')
                    const curBcsProject = (projectList || []).find(item => item.project_code === curProjectCode)
                    // eslint-disable-next-line camelcase
                    if (curBcsProject?.project_id) {
                        await this.$store.dispatch('cluster/getClusterList', curBcsProject.project_id)
                    }
                }
                this.isLoading = false
            })
        },
        mounted () {
            document.title = this.$t('容器服务')

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
                    + '<i class="bcs-icon bcs-icon-arrows-left back"></i>'
                    + '<span></span>'
                    + '</div>'
                    + '</div>'
                    + '<div class="bk-exception bk-exception-center">'
                    + `<img src="${Img403}"/>`
                    + '<h2 class="exception-text">'
                    + `<p class="f14">${self.$t('Sorry，您的权限不足，请去')}`
                    + `<a class="bk-text-button" href="${data.data.apply_url}&project_code=${projectCode}" target="_blank">${self.$t('申请')}</a>`
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
                                this.checkUser()
                                // IEG 项目，只有内部版才判断是否是 IEG 项目
                                if (String(project.bg_id) !== '956') {
                                    this.isIEGProject = false
                                } else {
                                    await this.fetchCCList()
                                    if (project.cc_app_id !== 0) {
                                        this.ccKey = project.cc_app_id
                                    }
                                }
                            }
                        }
                    }
                }
            },

            async checkUser () {
                try {
                    const res = await this.$store.dispatch('getUserBgInfo')
                    if (!res.data.is_ieg) {
                        this.$bkInfo({
                            clsName: 'not-ieg-user-infobox',
                            type: 'default',
                            quickClose: false,
                            title: this.$t('非IEG用户请使用对应BG的容器服务平台')
                        })
                        return
                    }
                } catch (e) {
                    console.log(e)
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
                    const res = await this.$store.dispatch('getCCList', {
                        project_kind: this.kind,
                        project_id: this.curProject.project_id
                    })
                    this.ccList = [...(res.data || [])]
                } catch (e) {
                    this.kind = this.prevKind
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
                }
            },

            /**
             * 改变 routerKey，刷新 router
             */
            reloadCurPage () {
                this.routerKey = +new Date()
            },
            handleKindChange (kind) {
                this.kind = kind
            },
            handleCmdbChange (ccKey) {
                this.ccKey = ccKey
            }
        }
    }
</script>
<style lang="postcss">
    @import '@/css/reset.css';
    @import '@/css/app.css';
    @import '@/css/animation.css';

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
    .biz-guide-box {
        .desc {
            width: auto;
            margin: 0 auto 25px;
            position: relative;
            top: 12px;
        }
        .biz-app-form {
            .form-item {
                .form-item-inner {
                    width: 340px;
                    .bk-form-radio {
                        width: 115px;
                    }
                }
            }
        }
    }
    .biz-list-operation {
        .item {
            float: none;
        }
    }

    .not-ieg-user-infobox {
        .bk-dialog-style {
            width: 500px;
        }
    }
</style>
