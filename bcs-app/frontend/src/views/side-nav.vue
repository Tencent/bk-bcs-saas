<template>
    <div>
        <p class="biz-side-title">
            <img src="@open/images/bcs2.svg" class="icon">
            <span>容器服务</span>
            <i class="biz-conf-btn bk-icon icon-cog" v-bktooltips.bottom="'项目信息'" @click="showProjectConfDialog"></i>
        </p>
        <div class="side-nav">
            <bk-menu :list="menuList" :menu-change-handler="menuSelected"></bk-menu>
            <p class="biz-copyright">Copyright © 2012-{{curYear}} Tencent BlueKing. All Rights Reserved</p>
        </div>

        <bk-dialog
            :width="550"
            :title="projectConfDialog.title"
            :quick-close="false"
            :is-show.sync="projectConfDialog.isShow"
            :has-footer="!isHasCluster"
            @cancel="projectConfDialog.isShow = false">
            <template slot="content">
                <form class="bk-form mb30">
                    <div class="bk-form-item">
                        <label class="bk-label" style="width:150px;">英文缩写：</label>
                        <div class="bk-form-content" style="margin-left:150px;">
                            <span style="line-height: 34px;">{{englishName}}</span>
                        </div>
                    </div>
                    <div class="bk-form-item is-required">
                        <label class="bk-label" style="width:150px;">编排类型：</label>
                        <div class="bk-form-content" style="margin-left:150px;">
                            <label class="bk-form-radio">
                                <input type="radio" value="1" name="kind" v-model="kind" :disabled="!canFormEdit">
                                <i class="bk-radio-text">Kubernetes</i>
                            </label>
                            <label class="bk-form-radio">
                                <input type="radio" value="2" name="kind" v-model="kind" :disabled="!canFormEdit">
                                <i class="bk-radio-text">Mesos</i>
                            </label>
                        </div>
                    </div>

                    <div class="bk-form-item is-required">
                        <label class="bk-label" style="width:150px;">关联CMDB业务：</label>
                        <div class="bk-form-content" style="margin-left:150px;">
                            <div style="display: inline-block;" class="mr5">
                                <template v-if="ccList.length && !isHasCluster">
                                    <bk-selector
                                        style="width: 250px;"
                                        placeholder="请选择"
                                        :searchable="true"
                                        :setting-key="'id'"
                                        :display-key="'name'"
                                        :selected.sync="ccKey"
                                        :list="ccList"
                                        :disabled="!canFormEdit">
                                    </bk-selector>
                                </template>
                                <template v-else>
                                    <input type="text" class="bk-form-input" disabled v-model="curProject.cc_app_name" style="width: 250px;">
                                </template>
                            </div>
                            <bk-tooltip placement="top" content="关联业务后，您可以从对应的业务下选择机器，搭建容器集群">
                                <span style="font-size: 12px;cursor: pointer;">
                                    <i class="bk-icon icon-info-circle"></i>
                                </span>
                            </bk-tooltip>
                            <template v-if="!canEdit && !isHasCluster">
                                <p class="desc mt15" style="text-align: left;">当前账号没有管理员权限，不可编辑，<br />请<a :href="bkAppHost" target="_blank" class="bk-text-button">点击申请权限</a></p>
                            </template>
                            <template v-else-if="!ccList.length && !isHasCluster">
                                <p class="desc mt15" style="text-align: left;">当前账号在蓝鲸配置平台无业务，请联系运维在蓝鲸配置平台关联业务，<a :href="bkCCHost" target="_blank" class="bk-text-button">点击查看业务和运维信息</a></p>
                            </template>
                        </div>
                    </div>
                    <div class="bk-form-item" v-if="isHasCluster">
                        <label class="bk-label" style="width:150px;"></label>
                        <div class="bk-form-content" style="margin-left: 150px; width: 260px;">
                            该项目下已有集群信息，如需更改编排类型和绑定业务信息，请先删除已有集群
                        </div>
                    </div>
                </form>
            </template>

            <template slot="footer">
                <div class="biz-footer">
                    <template v-if="!canEdit">
                        <bk-tooltip content="没有管理员权限" placement="top">
                            <bk-button type="primary" :disabled="true">保存</bk-button>
                        </bk-tooltip>
                    </template>
                    <template v-else-if="!ccList.length">
                        <bk-tooltip content="请选择要关联的CMDB业务" placement="top">
                            <bk-button type="primary" :disabled="true">保存</bk-button>
                        </bk-tooltip>
                    </template>
                    <template v-else>
                        <bk-button type="primary" :disabled="!canEdit || !ccList.length" @click="updateProject" :loading="isLoading">保存</bk-button>
                    </template>
                    <bk-button type="default" @click="projectConfDialog.isShow = false">取消</bk-button>
                </div>
            </template>
        </bk-dialog>
    </div>
</template>

<script>
    import bkMenu from '@open/components/menu'
    import { catchErrorHandler } from '@open/common/util'

    export default {
        name: 'side-nav',
        components: {
            bkMenu
        },
        data () {
            return {
                isLoading: false,
                clusterRouters: [
                    'clusterMain',
                    'clusterCreate',
                    'clusterOverview',
                    'clusterInfo',
                    'clusterNode',
                    'clusterNodeOverview',
                    'containerDetailForNode'
                ],
                configurationRouters: [
                    'mesosTemplatesetApplication',
                    'mesosTemplatesetDeployment',
                    'mesosTemplatesetService',
                    'mesosTemplatesetConfigmap',
                    'mesosTemplatesetSecret',

                    'k8sTemplatesetDeployment',
                    'k8sTemplatesetService',
                    'k8sTemplatesetSecret',
                    'k8sTemplatesetConfigmap',
                    'k8sTemplatesetDaemonset',
                    'k8sTemplatesetJob',
                    'k8sTemplatesetStatefulset',
                    'k8sTemplatesetIngress'
                ],
                projectIdTimer: null,
                projectConfDialog: {
                    isShow: false,
                    title: ''
                },
                bkCCHost: window.BK_CC_HOST + '/#/business',
                ccKey: '',
                canEdit: false,
                ccList: [],
                englishName: '',
                kind: 1 // 业务编排类型
            }
        },
        computed: {
            bkAppHost () {
                // bkApplyHost: window.BK_IAM_APP_URL,
                if (window.BK_IAM_APP_URL) {
                    return window.BK_IAM_APP_URL
                } else {
                    return `${window.DEVOPS_HOST}/console/perm/apply-join-project?project_code=${this.projectCode}`
                }
            },
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            },
            curProject () {
                const project = this.$store.state.curProject
                if (!project.cc_app_name) {
                    project.cc_app_name = ''
                }
                return project
            },
            clusterList () {
                return this.$store.state.cluster.clusterList
            },
            menuList () {
                if (this.curProject && this.curProject.kind === 1) {
                    return this.$store.state.sideMenu.k8sMenuList
                }
                return this.$store.state.sideMenu.menuList
            },
            curYear () {
                return (new Date()).getFullYear()
            },
            isHasCluster () {
                return this.clusterList.length > 0
            },
            isHasCC () {
                return this.ccList.length > 0
            },
            canFormEdit () {
                // 有权限并且没有集群
                return this.canEdit && !this.isHasCluster
            }
        },
        watch: {
            '$route' (to, from) {
                if (to.name !== 'imageDetail') {
                    this.$store.dispatch('updateMenuListSelected', {
                        pathName: to.name,
                        idx: 'bcs'
                    })
                }
            },
            'projectId' () {
                this.$store.dispatch('updateMenuListSelected', {
                    pathName: this.$route.name,
                    idx: 'bcs'
                })
            }
        },
        created () {
            this.$store.commit('updateCurProject', this.projectCode)
            this.$store.dispatch('updateMenuListSelected', {
                pathName: this.$route.name,
                idx: 'bcs',
                projectType: (this.curProject && this.curProject.kind === 1) ? 'k8s' : ''
            })
        },
        methods: {
            /**
             * 显示项目配置窗口
             */
            async showProjectConfDialog () {
                this.getProject()
                await this.fetchCCList()
                this.kind = this.curProject.kind
                this.ccKey = this.curProject.cc_app_id
                this.englishName = this.curProject.english_name
                this.projectConfDialog.isShow = true
                this.projectConfDialog.title = `项目【${this.curProject.project_name}】`
            },

            /**
             * 左侧导航 menu 选择事件
             *
             * @param {Object} data menu 数据
             */
            menuSelected (data) {
                const curSelected = data.child || data.item
                const projectCode = this.projectCode
                if (!curSelected.pathName) {
                    return false
                }
                if (curSelected.externalLink) {
                    const url = `${DEVOPS_HOST}${curSelected.externalLink}${projectCode}/?project_id=${this.projectId}`
                    window.top.location.href = url
                } else {
                    this.$router.push({
                        name: curSelected.pathName[0],
                        params: {
                            needCheckPermission: true
                        }
                    })
                }
                return this.$store.state.allowRouterChange
            },

            /**
             * 获取关联 CC 的数据
             */
            async fetchCCList () {
                try {
                    const res = await this.$store.dispatch('getCCList')
                    this.ccList = [...(res.data || [])]

                    // 判断cc列表是否含有当前项目业务，如果没有把当前项加入
                    if (this.curProject.cc_app_id) {
                        const curCCItem = this.ccList.filter(item => {
                            return String(item.id) === String(this.curProject.cc_app_id)
                        })

                        if (!curCCItem.length) {
                            this.ccList.unshift({
                                id: this.curProject.cc_app_id,
                                name: this.curProject.cc_app_name
                            })
                        }
                    }
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 获取当前项目数据
             */
            async getProject () {
                try {
                    const res = await this.$store.dispatch('getProject', { projectId: this.projectId })
                    this.curProject.cc_app_id = res.data.cc_app_id
                    this.curProject.cc_app_name = res.data.cc_app_name

                    this.canEdit = res.data.can_edit
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 更新项目信息
             */
            async updateProject () {
                if (this.isLoading) return
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

                    this.projectConfDialog.isShow = false
                    this.$bkMessage({
                        theme: 'success',
                        message: '更新成功！'
                    })

                    setTimeout(() => {
                        // 导航项目切换时，iframe依然保存上个项目的路由信息
                        const matchs = this.$route.path.match(/\/bcs\/(\w+)\//)
                        let url = this.$route.fullPath
                        if (matchs && matchs.length > 1) {
                            const projectCode = matchs[1]
                            url = url.replace(projectCode, this.projectCode)
                        }
                        window.$syncUrl(url.replace(new RegExp(`^${SITE_URL}`), ''), true)
                    }, 200)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isLoading = false
                }
            }
        }
    }
</script>

<style scoped lang="postcss">
    .biz-side-title {
        position: relative;
    }
    .biz-conf-btn {
        position: absolute;
        right: 10px;
        top: 13px;
        font-size: 16px;
        cursor: pointer;
        width: 30px;
        height: 30px;
        text-align: center;
        line-height: 30px;
    }
    .biz-footer {
        text-align: right;
        padding: 0 20px;
    }
</style>
