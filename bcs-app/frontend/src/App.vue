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
                    <p class="title">{{$t('容器服务未启用')}}{{isIEGProject ? $t('，请完善以下信息') : ''}}</p>
                    <template v-if="!isIEGProject">
                        <p class="desc">{{$t('您当前的项目')}}“{{curProject.project_name}}”{{$t('没有启用蓝鲸部署服务，如需开启使用，请联系')}}<a href="wxwork://message/?username=BCS">【{{$t('蓝鲸容器助手')}}】</a></p>
                        <p style="font-size: 14px">
                            <a :href="PROJECT_CONFIG.doc.quickStart" target="_blank">{{$t('请点击了解更多')}}<i class="bk-icon icon-angle-double-right"></i></a>
                        </p>
                    </template>
                    <template v-else>
                        <main class="bk-form biz-app-form">
                            <div class="form-item">
                                <label>{{$t('业务编排类型')}}：</label>
                                <div class="form-item-inner">
                                    <label class="bk-form-radio">
                                        <input type="radio" value="1" name="kind" v-model="kind">
                                        <i class="bk-radio-text">BCS-K8S</i>
                                    </label>
                                    <label class="bk-form-radio">
                                        <input type="radio" value="2" name="kind" v-model="kind">
                                        <i class="bk-radio-text">BCS-Mesos</i>
                                    </label>
                                </div>
                            </div>
                            <div class="form-item" v-if="ccList.length" style="margin-bottom: 30px;">
                                <label>{{$t('关联CMDB业务')}}：<span class="red">*</span></label>
                                <div class="form-item-inner">
                                    <div style="display: inline-block;" class="mr5">
                                        <bk-selector
                                            style="width: 250px;"
                                            :placeholder="$t('请选择')"
                                            :searchable="true"
                                            :setting-key="'id'"
                                            :display-key="'name'"
                                            :selected.sync="ccKey"
                                            :list="ccList">
                                        </bk-selector>
                                    </div>
                                    <bk-tooltip placement="top" :content="$t('关联业务后，您可以从对应的业务下选择机器，搭建容器集群')">
                                        <span style="font-size: 12px;cursor: pointer;">
                                            <i class="bk-icon icon-info-circle"></i>
                                        </span>
                                    </bk-tooltip>
                                </div>
                            </div>
                            <div class="form-item" v-else>
                                <label>{{$t('关联CMDB业务')}}：<span class="red">*</span></label>
                                <div class="form-item-inner" style="margin-top: -20px;">
                                    <p class="desc">
                                        {{$t('当前账号无运维角色权限的业务，请到')}}<a :href="bkIamAppUrl" target="_blank">{{$t('权限中心')}}</a>{{$t('申请，')}}<a href="javascript: void(0)" @click="showGuide">{{$t('查看帮助')}}</a>
                                    </p>
                                </div>
                            </div>
                            <button class="bk-button bk-primary" :class="enableBtn ? '' : 'is-disabled'"
                                style="margin-left: -40px;"
                                @click="updateProject"
                                :disabled="!enableBtn">
                                {{$t('启用容器服务')}}
                            </button>
                        </main>
                    </template>
                </div>
            </div>
        </template>
        <bk-dialog
            :is-show.sync="guideDialogConf.isShow"
            :width="guideDialogConf.width"
            :title="guideDialogConf.title"
            :close-icon="guideDialogConf.closeIcon"
            :ext-cls="'perm-guide-dialog'"
            :quick-close="true"
            @cancel="hideGuide">
            <div slot="content" class="content">
                <div class="tip">{{$t('点击图片放大')}}</div>
                <img :title="$t('点击图片放大')" src="./images/guide1.jpg" @click="setFullsreenImg(1)" />
                <img :title="$t('点击图片放大')" src="./images/guide2.jpg" @click="setFullsreenImg(2)" />
                <img :title="$t('点击图片放大')" src="./images/guide3.jpg" @click="setFullsreenImg(3)" />
            </div>
        </bk-dialog>
        <div class="fullscreen-img" v-if="fullscreenImg">
            <img :title="$t('点击图片还原')" :src="fullscreenImg" @click="fullscreenImg = ''" />
        </div>
        <app-apply-perm ref="bkApplyPerm"></app-apply-perm>
    </div>
</template>
<script>
    import { bus } from '@open/common/bus'
    import { getProjectByCode } from '@open/common/util'
    import Img403 from '@open/images/403.png'
    import imgGuide1 from './images/guide1.jpg'
    import imgGuide2 from './images/guide2.jpg'
    import imgGuide3 from './images/guide3.jpg'

    export default {
        name: 'app',
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
                enableBtn: false, // 提交按钮是否可用
                projectId: '',
                projectCode: '',
                isLoading: true,
                bkCCHost: window.BK_CC_HOST + '/#/business',
                bkIamAppUrl: window.BK_IAM_APP_URL + '/apply-custom-perm',
                guideDialogConf: {
                    isShow: false,
                    width: 1000,
                    title: this.$t('帮助'),
                    closeIcon: true
                },
                fullscreenImg: ''
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
                    this.$refs.appHeader.selectProject(curProjectCode)
                }

                // 从配置中心拉取项目列表，顶导的项目列表信息里，项目中关于容器服务的信息可能更新不及时
                await this.$store.dispatch('getProjectList')
                await this.checkProject()

                this.isLoading = false
            })
        },
        mounted () {
            document.title = this.$t('容器服务')
            if (window.$changeDocumentTitle) {
                window.$changeDocumentTitle(this.$t('蓝鲸容器管理平台'))
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
             * 显示指引信息
             */
            showGuide () {
                this.guideDialogConf.isShow = true
            },

            /**
             * 隐藏指引信息
             */
            hideGuide () {
                this.guideDialogConf.isShow = false
                this.fullscreenImg = ''
            },

            setFullsreenImg (idx) {
                if (idx === 1) {
                    this.fullscreenImg = imgGuide1
                } else if (idx === 2) {
                    this.fullscreenImg = imgGuide2
                } else if (idx === 3) {
                    this.fullscreenImg = imgGuide3
                } else {
                    this.fullscreenImg = ''
                }
            },

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
                    if (res.data) {
                        this.ccList = [...(res.data || [])]
                    }
                } catch (e) {
                    // this.bkMessageInstance = this.$bkMessage({
                    //     theme: 'error',
                    //     message: e.message || e.data.msg || e.statusText
                    // })
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
<style lang="postcss">
    @import '@open/css/reset.css';
    @import '@open/css/app.css';
    @import '@open/css/animation.css';
    @import '@open/css/mixins/scroller.css';

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

    .perm-guide-dialog {
        .bk-dialog-header,
        .bk-dialog-footer {
            display: none;
        }
        .content {
            @mixin scroller #eee;
            height: 500px;
            overflow: scroll;
            .tip {
                font-size: 14px;
                color: #737987;
                position: absolute;
                top: 20px;
            }
            img {
                cursor: pointer;
                width: 100%;
            }
        }
    }

    .fullscreen-img {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        z-index: 2500;
        img {
            cursor: pointer;
            width: 100%;
        }
    }
</style>
