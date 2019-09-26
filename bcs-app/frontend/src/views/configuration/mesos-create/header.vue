<template>
    <div class="biz-top-bar" :style="{ marginBottom: (isNewTemplate || !canTemplateEdit) ? '0px' : '55px' }">
        <i class="biz-back bk-icon icon-arrows-left" @click="beforeLeave"></i>

        <template v-if="exceptionCode">
            <div class="biz-templateset-title">
                <span>返回模板集</span>
            </div>
        </template>
        <template v-esle>
            <div class="biz-templateset-title">
                <span v-show="!isEditName">{{curTemplate.name}}</span>
                <input
                    type="text"
                    placeholder="30个以内的字符，Enter保存" maxlength="30" class="bk-form-input"
                    v-model="editTemplate.name"
                    v-bk-focus
                    v-if="isEditName"
                    @blur="saveTemplate"
                    @keyup.enter="saveTemplate" />
                <a href="javascript:void(0)" class="bk-text-button bk-default" v-show="!isEditName" @click="editTemplateName">
                    <i class="bk-icon icon-edit"></i>
                </a>
            </div>
            <div class="biz-templateset-desc">
                <span v-show="!isEditDesc">{{curTemplate.desc}}</span>
                <input type="text" placeholder="输入50个以内的字符，Enter保存" maxlength="50" class="bk-form-input" v-model="editTemplate.desc" v-bk-focus v-if="isEditDesc" @blur="saveTemplate" @keyup.enter="saveTemplate">
                <a href="javascript:void(0)" class="bk-text-button bk-default" v-show="!isEditDesc" @click="editTemplateDesc" @keyup.enter="saveTemplate">
                    <i class="bk-icon icon-edit"></i>
                </a>
            </div>
            <div class="biz-templateset-action" v-if="!exceptionCode && !isTemplateLoading">
                <!-- 如果不是新增状态的模板集并且有权限编辑才可查看加锁状态 -->
                <template v-if="String(curTemplateId) !== '0'">
                    <template v-if="templateLockStatus.isLocked">
                        <template v-if="templateLockStatus.isCurLocker">
                            <div class="biz-lock-box" v-if="curTemplate.permissions.edit">
                                <div class="lock-wrapper warning">
                                    <i class="bk-icon icon-info-circle-shape"></i>
                                    <strong class="desc">
                                        您已经对此模板集加锁，只有解锁后，其他用户才可操作此模板集。
                                        <span v-if="lateShowVersionName">（当前版本号：{{lateShowVersionName}}）</span>
                                    </strong>
                                    <div class="action">
                                        <bk-switcher
                                            :selected="templateLockStatus.isLocked"
                                            size="small"
                                            @change="updateTemplateLockStatus">
                                        </bk-switcher>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <div class="biz-lock-box" v-if="curTemplate.permissions.edit">
                                <div class="lock-wrapper warning">
                                    <i class="bk-icon icon-info-circle-shape"></i>
                                    <strong class="desc">
                                        {{`${templateLockStatus.locker}正在操作，您如需编辑请联系${templateLockStatus.locker}解锁。`}}
                                        <span v-if="lateShowVersionName">（当前版本号：{{lateShowVersionName}}）</span>
                                    </strong>
                                    <div class="action">
                                        <a href="javascript: void(0);" class="bk-text-button" @click="reloadTemplateset">点击刷新</a>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </template>
                    <template v-else>
                        <div class="biz-lock-box" v-if="curTemplate.permissions.edit">
                            <div class="lock-wrapper">
                                <i class="bk-icon icon-info-circle-shape"></i>
                                <strong class="desc">
                                    为避免多成员同时编辑，引起内容或版本冲突，建议在编辑时，开启保护功能。
                                    <span v-if="lateShowVersionName">（当前版本号：{{lateShowVersionName}}）</span>
                                </strong>
                                <div class="action">
                                    <bk-switcher
                                        :selected="templateLockStatus.isLocked"
                                        size="small"
                                        @change="updateTemplateLockStatus">
                                    </bk-switcher>
                                </div>
                            </div>
                        </div>
                    </template>
                </template>

                <!-- 如果模板集没有加锁或者当前用户是加锁者才可以操作 -->
                <template v-if="curTemplate.permissions.edit">
                    <template v-if="templateLockStatus.isLocked && !templateLockStatus.isCurLocker">
                        <button href="javascript:void(0)" class="bk-button bk-default" disabled>保存草稿</button>
                        <button href="javascript:void(0)" class="bk-button bk-primary" style="width: 70px;" disabled>保存</button>
                    </template>
                    <template v-else>
                        <button href="javascript:void(0)" class="bk-button bk-default" @click.stop.prevent="saveTemplateDraft">保存草稿</button>
                        <button href="javascript:void(0)" :class="['bk-button bk-primary', { 'is-loading': isDataSaveing, 'is-disabled': !isTemplateCanSave }]" style="width: 70px;" @click.stop.prevent="saveTemplateData">保存</button>
                    </template>
                </template>
                <template v-else>
                    <bk-tooltip :delay="300" placement="bottom">
                        <button href="javascript:void(0)" class="bk-button bk-default" disabled>保存草稿</button>
                        <template slot="content">
                            <p class="biz-permission-tip">
                                无权限，请去<a :href="createApplyPermUrl({
                                    policy: 'edit',
                                    projectCode: projectCode,
                                    idx: 'templates'
                                })" class="biz-link" target="_blank">申请</a>
                            </p>
                        </template>
                    </bk-tooltip>
                    <bk-tooltip :delay="300" placement="bottom">
                        <button href="javascript:void(0)" class="bk-button bk-success" disabled>保存</button>
                        <template slot="content">
                            <p class="biz-permission-tip">
                                无权限，请去<a :href="createApplyPermUrl({
                                    policy: 'edit',
                                    projectCode: projectCode,
                                    idx: 'templates'
                                })" class="biz-link" target="_blank">申请</a>
                            </p>
                        </template>
                    </bk-tooltip>
                </template>

                <template v-if="curTemplate.permissions.use">
                    <button href="javascript:void(0)" style="width: 70px; padding: 0;" @click.stop.prevent="createInstance" :class="['bk-button bk-default', { 'is-disabled': !canCreateInstance }]">
                        实例化
                    </button>
                </template>
                <template v-else>
                    <bk-tooltip :delay="300" placement="bottom">
                        <button href="javascript:void(0)" class="bk-button bk-default" disabled>实例化</button>
                        <template slot="content">
                            <p class="biz-permission-tip">
                                无权限，请去<a :href="createApplyPermUrl({
                                    policy: 'use',
                                    projectCode: projectCode,
                                    idx: 'templates'
                                })" class="biz-link" target="_blank">申请</a>
                            </p>
                        </template>
                    </bk-tooltip>
                </template>

                <template v-if="curTemplate.permissions.view">
                    <button href="javascript:void(0)" :class="['bk-button bk-default']" @click.stop.prevent="showVersionPanel">版本列表</button>
                </template>
                <template v-else>
                    <bk-tooltip :delay="300" placement="bottom">
                        <button href="javascript:void(0)" class="bk-button bk-default is-disabled" disabled>版本列表</button>
                        <template slot="content">
                            <p class="biz-permission-tip">
                                无权限，请去<a :href="createApplyPermUrl({
                                    policy: 'view',
                                    projectCode: projectCode,
                                    idx: 'templates'
                                })" class="biz-link" target="_blank">申请</a>
                            </p>
                        </template>
                    </bk-tooltip>
                </template>
            </div>
        </template>

        <bk-dialog
            :is-show.sync="versionDialogConf.isShow"
            :width="versionDialogConf.width"
            :has-header="false"
            :quick-close="false"
            :ext-cls="'create-project-dialog'"
            :content="versionDialogConf.content"
            @cancel="hideVersionBox">
            <template slot="content">
                <div class="version-box">
                    <p class="title">保存修改到：</p>
                    <ul class="version-list">
                        <template v-if="allVersionList.length && curShowVersionId !== -1">
                            <li class="item">
                                <label class="bk-form-radio">
                                    <input type="radio" name="save-version-way" value="cur" v-model="saveVersionWay">
                                    <i class="bk-radio-text" style="display: inline-block; min-width: 70px;">当前版本号：{{lateShowVersionName}}</i>
                                </label>
                            </li>

                            <li class="item">
                                <label class="bk-form-radio" style="margin-right: 0;">
                                    <input type="radio" name="save-version-way" value="new" v-model="saveVersionWay">
                                    <i class="bk-radio-text" style="display: inline-block; min-width: 70px;">新版本：</i>
                                    <input type="text" class="bk-form-input" placeholder="请输入版本号" @focus="saveVersionWay = 'new'" style="display: inline-block; width: 176px;" v-model="versionKeyword" />
                                </label>
                            </li>

                            <li class="item" v-if="withoutCurVersionList.length">
                                <label class="bk-form-radio" style="margin-right: 0;">
                                    <input type="radio" name="save-version-way" value="old" v-model="saveVersionWay">
                                    <i class="bk-radio-text" style="display: inline-block; min-width: 70px;">其它版本：</i>
                                    <bk-selector
                                        style="width: 176px;"
                                        placeholder="请选择版本号"
                                        :setting-key="'show_version_id'"
                                        :selected.sync="selectedVersion"
                                        :list="withoutCurVersionList"
                                        @item-selected="selectVersion">
                                    </bk-selector>
                                </label>
                            </li>
                        </template>
                        <template v-else>
                            <li class="item">
                                <label class="bk-form-radio" style="margin-right: 0;">
                                    <i class="bk-radio-text">新版本：</i>
                                    <input type="text" class="bk-form-input" placeholder="请输入版本号" @focus="saveVersionWay = 'new'" style="display: inline-block; width: 217px;" v-model="versionKeyword" />
                                </label>
                            </li>
                        </template>
                    </ul>
                </div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isCreating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            保存中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <template v-if="!canVersionSave">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled" style="background-color: #fafafa; border-color: #e6e6e6; color: #ccc;">
                                确定
                            </button>
                        </template>
                        <template v-else>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="saveVersion(0)">
                                确定
                            </button>
                        </template>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideVersionBox">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-sideslider
            :quick-close="true"
            :is-show.sync="versionSidePanel.isShow"
            :title="versionSidePanel.title"
            :width="'640'">
            <div class="p30" slot="content" v-bkloading="{ isLoading: isVersionListLoading }">
                <table class="bk-table biz-data-table has-table-bordered">
                    <thead>
                        <tr>
                            <th>版本号</th>
                            <th>更新时间</th>
                            <th>最后更新人</th>
                            <th style="width: 128px;">操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-if="versionList.length">
                            <tr v-for="versionData in versionList" :key="versionData.show_version_id">
                                <td>
                                    <span>{{versionData.name}}</span>
                                    <span v-if="versionData.show_version_id === curShowVersionId">{{'(当前)'}}</span>
                                </td>
                                <td>{{versionData.updated}}</td>
                                <td>{{versionData.updator}}</td>
                                <td>
                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="getTemplateByVersion(versionData.show_version_id)">加载</a>
                                    <!-- 只有一个版本时不能删除 -->
                                    <template v-if="versionList.length <= 1">
                                        <bk-tooltip :delay="300" placement="right">
                                            <a href="javascript:void(0);" class="bk-text-button is-disabled ml5" disabled>删除</a>
                                            <template slot="content">
                                                <p class="biz-permission-tip">
                                                    必须保留至少一个版本
                                                </p>
                                            </template>
                                        </bk-tooltip>
                                    </template>
                                    <template v-else>
                                        <!-- 有编辑权限 -->
                                        <template v-if="curTemplate.permissions.edit">
                                            <template v-if="!templateLockStatus.isLocked || (templateLockStatus.isLocked && templateLockStatus.isCurLocker)">
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="removeVersion(versionData)">删除</a>
                                            </template>
                                            <template v-else>
                                                <bk-tooltip :delay="300" placement="right">
                                                    <a href="javascript:void(0);" class="bk-text-button is-disabled ml5" disabled>删除</a>
                                                    <template slot="content">
                                                        <p class="biz-permission-tip">
                                                            {{templateLockStatus.locker}}正在操作，您如需编辑请联系{{templateLockStatus.locker}}解锁！
                                                        </p>
                                                    </template>
                                                </bk-tooltip>
                                            </template>
                                        </template>
                                        <template v-else>
                                            <bk-tooltip :delay="300" placement="top">
                                                <a href="javascript:void(0);" class="bk-text-button is-disabled" disabled>删除</a>
                                                <template slot="content">
                                                    <p class="biz-permission-tip">
                                                        无权限，请去<a :href="createApplyPermUrl({
                                                            policy: 'edit',
                                                            projectCode: projectCode,
                                                            idx: 'templates'
                                                        })" class="biz-link" target="_blank">申请</a>
                                                    </p>
                                                </template>
                                            </bk-tooltip>
                                        </template>
                                    </template>
                                </td>
                            </tr>
                        </template>
                        <template v-else>
                            <tr>
                                <td colspan="4">
                                    <div class="biz-app-list">
                                        <div class="bk-message-box" style="min-height: auto;">
                                            <p class="message empty-message" style="margin: 30px;">无数据</p>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </bk-sideslider>
    </div>
</template>

<script>
    import applyPerm from '@open/mixins/apply-perm'

    export default {
        mixins: [applyPerm],
        data () {
            return {
                saveVersionWay: 'cur',
                isEditName: false,
                isEditDesc: false,
                isCreating: false,
                editTemplate: {
                    name: '',
                    desc: ''
                },
                isTemplateLocking: false,
                isVersionListLoading: true,
                exceptionCode: null,
                versionSidePanel: {
                    isShow: false,
                    title: '版本列表'
                },
                versionDialogConf: {
                    isShow: false,
                    width: 400,
                    closeIcon: false
                },
                versionMetadata: {
                    show_version_id: -1,
                    name: '',
                    real_version_id: 0
                },
                isTemplateLoading: true,
                isDataSaveing: false,
                newTemplateId: 0,
                versionKeyword: '',
                canCreateInstance: false,
                selectedVersion: ''
            }
        },
        computed: {
            projectCode () {
                return this.$route.params.projectCode
            },
            canVersionSave () {
                if (this.saveVersionWay === 'cur' && this.curVersion) {
                    return true
                } else if (this.saveVersionWay === 'old' && this.selectedVersion) {
                    return true
                } else if (this.saveVersionWay === 'new' && this.versionKeyword) {
                    return true
                }
                return false
            },
            lateShowVersionName () {
                let name = ''
                this.allVersionList.forEach(item => {
                    if (item.show_version_id === this.curShowVersionId) {
                        name = item.name
                    }
                })
                return name
            },
            metricList () {
                const ids = []
                const list = this.$store.state.mesosTemplate.metricList
                list.forEach(item => {
                    ids.push(item.id)
                })
                return ids
            },
            isTemplateCanSave () {
                // 如果没有创建模板，查看是否有资源已经编辑过
                if (!this.curShowVersionId) {
                    const applications = this.applications
                    const deployments = this.deployments
                    const services = this.services
                    const configmaps = this.configmaps
                    const secrets = this.secrets

                    for (const application of applications) {
                        if (application.isEdited) {
                            return true
                        }
                    }

                    for (const deployment of deployments) {
                        if (deployment.isEdited) {
                            return true
                        }
                    }

                    for (const service of services) {
                        if (service.isEdited) {
                            return true
                        }
                    }

                    for (const configmap of configmaps) {
                        if (configmap.isEdited) {
                            return true
                        }
                    }

                    for (const secret of secrets) {
                        if (secret.isEdited) {
                            return true
                        }
                    }

                    if (this.$store.state.mesosTemplate.canTemplateBindVersion) {
                        return true
                    }

                    return false
                } else {
                    return true
                }
            },
            curTemplateId () {
                return this.$store.state.mesosTemplate.curTemplateId || this.newTemplateId || this.$route.params.templateId
            },
            templateLockStatus () {
                const userInfo = window.$userInfo
                const status = {
                    isLocked: false,
                    isCurLocker: false,
                    locker: ''
                }
                // 模块集已经加锁
                if (this.curTemplate && this.curTemplate.is_locked) {
                    status.isLocked = true
                    status.locker = this.curTemplate.locker
                    // 如果是当前用户加锁
                    if (this.curTemplate.locker && this.curTemplate.locker === userInfo.username) {
                        status.isCurLocker = true
                    } else {
                        status.isCurLocker = false
                    }
                }
                return status
            },
            curVersion () {
                return this.$store.state.mesosTemplate.curVersion
            },
            curShowVersionId () {
                return this.$store.state.mesosTemplate.curShowVersionId
            },
            isVersionIsDraf () {
                if (this.curShowVersionId === '-1' || this.curShowVersionId === -1) {
                    return true
                } else {
                    return false
                }
            },
            isNewTemplate () {
                const templateId = this.$route.params.templateId
                if (String(templateId) === '0') {
                    return true
                } else {
                    return false
                }
            },
            curTemplate () {
                return this.$store.state.mesosTemplate.curTemplate
            },
            canTemplateEdit () {
                return this.curTemplate.permissions && this.curTemplate.permissions.edit
            },
            applications () {
                return this.$store.state.mesosTemplate.applications
            },
            deployments () {
                return this.$store.state.mesosTemplate.deployments
            },
            services () {
                return this.$store.state.mesosTemplate.services
            },
            configmaps () {
                return this.$store.state.mesosTemplate.configmaps
            },
            secrets () {
                return this.$store.state.mesosTemplate.secrets
            },
            projectId () {
                return this.$route.params.projectId
            },
            versionList () {
                const list = this.$store.state.mesosTemplate.versionList
                if (list.length === 0) {
                    this.canCreateInstance = false
                } else if (list.length === 1 && list[0].show_version_id === -1) {
                    this.canCreateInstance = false
                } else {
                    this.canCreateInstance = true
                }
                return list
            },
            allVersionList () {
                return this.$store.state.mesosTemplate.versionList
            },
            withoutCurVersionList () {
                // 去掉草稿和当前版本
                return this.$store.state.mesosTemplate.versionList.filter(item => {
                    return item.show_version_id !== -1 && item.show_version_id !== this.curShowVersionId
                })
            },
            imageList () {
                return this.$store.state.mesosTemplate.imageList
            }
        },
        watch: {
            'versionDialogConf.isShow' () {
                if (!this.versionDialogConf.isShow) {
                    this.versionKeyword = ''
                }
            },
            '$route' () {
                this.getVersionList()
            }
        },
        mounted () {
            this.getVersionList()
        },
        methods: {
            beforeLeave () {
                const self = this
                let isEdited = false
                this.applications.forEach(item => {
                    if (item.isEdited) {
                        isEdited = true
                    }
                })
                this.deployments.forEach(item => {
                    if (item.isEdited) {
                        isEdited = true
                    }
                })
                this.services.forEach(item => {
                    if (item.isEdited) {
                        isEdited = true
                    }
                })
                this.configmaps.forEach(item => {
                    if (item.isEdited) {
                        isEdited = true
                    }
                })
                this.secrets.forEach(item => {
                    if (item.isEdited) {
                        isEdited = true
                    }
                })
                if (isEdited || this.$store.state.mesosTemplate.canTemplateBindVersion) {
                    this.$bkInfo({
                        title: '确认',
                        content: '确定要离开？数据未保存，离开后将会丢失',
                        confirmFn () {
                            self.goTemplatePage()
                        }
                    })
                } else {
                    this.goTemplatePage()
                }
            },
            removeVersion (data) {
                const self = this
                this.$bkInfo({
                    title: `确认`,
                    content: this.$createElement('p', { style: { 'text-align': 'center' } }, `删除版本：“${data.name}”`),
                    confirmFn () {
                        const projectId = self.projectId
                        const templateId = self.curTemplateId
                        const versionId = data.show_version_id
                        self.$store.dispatch('mesosTemplate/removeVersion', { projectId, templateId, versionId }).then(res => {
                            self.$bkMessage({
                                theme: 'success',
                                message: '操作成功！'
                            })

                            self.getVersionList().then(versionList => {
                                // 如果是删除当前版本
                                if (versionId === self.curShowVersionId || String(versionId) === self.curShowVersionId) {
                                    // 加载第一项，优先选择非草稿
                                    if (self.versionList.length) {
                                        let versionData = self.versionList[0]
                                        if (versionData.show_version_id === -1 && self.versionList.length > 1) {
                                            versionData = self.versionList[1]
                                        }
                                        self.getTemplateByVersion(versionData.show_version_id, true)
                                    } else {
                                        self.getTemplateByVersion(-1)
                                    }
                                }
                            })
                        }, res => {
                            const message = res.message
                            this.$bkMessage({
                                theme: 'error',
                                message: message,
                                delay: '3000'
                            })
                        })
                    }
                })
            },

            goTemplatePage () {
                // 清空数据
                this.$store.commit('mesosTemplate/clearCurTemplateData')
                this.$router.push({
                    name: 'templateset',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
            },
            removeTemplate () {
                const self = this
                const projectId = this.projectId
                const templateId = this.curTemplateId
                this.$bkInfo({
                    title: '确定要删除此模板集？',
                    confirmFn () {
                        self.$store.dispatch('mesosTemplate/removeTemplate', { templateId, projectId }).then(res => {
                            this.$bkMessage({
                                theme: 'success',
                                message: '删除成功！'
                            })
                            self.goTemplatePage()
                        }, res => {
                            const message = res.message
                            this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                            this.$bkMessage({
                                theme: 'error',
                                message: message,
                                hasCloseIcon: true,
                                delay: '3000'
                            })
                        })
                    }
                })
            },
            createInstance () {
                if (this.canCreateInstance) {
                    this.$router.push({
                        name: 'instantiation',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode,
                            templateId: this.curTemplate.id,
                            curTemplate: this.curTemplate,
                            curShowVersionId: this.curShowVersionId
                        }
                    })
                }
            },
            editTemplateName () {
                this.isEditName = true
                this.editTemplate = Object.assign({}, this.curTemplate)
            },
            cancelEditName () {
                setTimeout(() => {
                    this.isEditName = false
                }, 200)
            },
            editTemplateDesc () {
                this.isEditDesc = true
                this.editTemplate = Object.assign({}, this.curTemplate)
            },
            cancelEditDesc () {
                setTimeout(() => {
                    this.isEditDesc = false
                }, 200)
            },
            updateTemplateLockStatus () {
                if (this.isTemplateLocking) {
                    return false
                }

                if (this.templateLockStatus.isLocked) {
                    this.unlockTemplateset()
                } else {
                    this.lockTemplateset()
                }
            },
            async lockTemplateset () {
                const projectId = this.projectId
                const templateId = this.curTemplateId
                this.isTemplateLocking = true
                try {
                    await this.$store.dispatch('mesosTemplate/lockTemplateset', { projectId, templateId })
                    this.$bkMessage({
                        theme: 'success',
                        message: '加锁成功！'
                    })
                    this.reloadTemplateLockStatus()
                } catch (res) {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '3000'
                    })
                } finally {
                    setTimeout(() => {
                        this.isTemplateLocking = false
                    }, 1000)
                }
            },
            async unlockTemplateset () {
                const projectId = this.projectId
                const templateId = this.curTemplateId
                // 不是当前加锁者不能解锁
                if (!this.templateLockStatus.isCurLocker) {
                    this.$bkMessage({
                        theme: 'error',
                        message: `${this.templateLockStatus.locker}正在操作，您如需编辑请联系${this.templateLockStatus.locker}解锁！`
                    })
                    return false
                }
                this.isTemplateLocking = true
                try {
                    await this.$store.dispatch('mesosTemplate/unlockTemplateset', { projectId, templateId })
                    this.$bkMessage({
                        theme: 'success',
                        message: '解锁成功！'
                    })
                    this.reloadTemplateLockStatus()
                } catch (res) {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '3000'
                    })
                } finally {
                    setTimeout(() => {
                        this.isTemplateLocking = false
                    }, 1000)
                }
            },
            saveTemplateDraft () {
                const projectId = this.projectId
                const projectCode = this.projectCode
                const templateId = this.curTemplateId

                const data = {
                    draft: {
                        application: this.applications,
                        deployment: this.deployments,
                        service: this.services,
                        configmap: this.configmaps,
                        secret: this.secrets
                    }
                }

                // 如果没有模板（template_id）
                if (this.isNewTemplate) {
                    data.template = {
                        name: this.curTemplate.name,
                        desc: this.curTemplate.desc
                    }
                    data.real_version_id = 0
                } else {
                    data.real_version_id = this.curVersion
                }

                if (projectId) {
                    this.$store.dispatch('mesosTemplate/updateTemplateDraft', { projectId, templateId, data }).then(res => {
                        this.$bkMessage({
                            theme: 'success',
                            message: '保存成功！'
                        })
                        // 新创建则跳转
                        if (this.isNewTemplate) {
                            this.$router.push({
                                name: this.$route.name,
                                params: {
                                    projectId: projectId,
                                    projectCode: projectCode,
                                    templateId: res.data.template_id
                                }
                            })
                        }
                    }, res => {
                        const message = res.message
                        this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                        this.$bkMessage({
                            theme: 'error',
                            message: message,
                            hasCloseIcon: true,
                            delay: '3000'
                        })
                    })
                }
            },
            showVersionPanel () {
                this.versionSidePanel.isShow = true
                this.getVersionList()
            },
            async getVersionList () {
                const projectId = this.projectId
                const templateId = this.curTemplateId
                this.isVersionListLoading = true
                if (templateId !== '0' && templateId !== 0) {
                    await this.$store.dispatch('mesosTemplate/getVersionList', { projectId, templateId }).then(res => {
                        let versionList = []
                        if (res && res.data) {
                            versionList = res.data
                            versionList.forEach(item => {
                                if (item.show_version_id === Number(this.curShowVersionId) || item.show_version_id === this.curShowVersionId) {
                                    this.versionMetadata = {
                                        show_version_id: item.show_version_id,
                                        name: item.name,
                                        real_version_id: item.real_version_id
                                    }
                                }
                            })
                        }

                        this.isVersionListLoading = false
                        return versionList
                    })
                } else {
                    this.$store.commit('mesosTemplate/updateVersionList', [])
                    this.isVersionListLoading = false
                    return []
                }
            },
            getTemplateByVersion (versionId, isVersionRemove) {
                const projectId = this.projectId
                const templateId = this.curTemplateId
                this.$store.dispatch('mesosTemplate/getTemplateByVersion', { projectId, templateId, versionId }).then(res => {
                    this.$emit('switchVersion', res.data)
                    // 如果不是操作删除版本，则可隐藏
                    if (!isVersionRemove) {
                        this.versionSidePanel.isShow = false
                    }
                })
            },
            async autoSaveResource (type) {
                // 没编辑权限不保存
                if (!this.curTemplate.permissions.edit) {
                    return false
                }

                switch (type) {
                    case 'mesosTemplatesetApplication':
                        const applications = this.applications
                        // 对application资源数据检测
                        for (const application of applications) {
                            if (application.isEdited) {
                                const isValid = await this.checkApplicationData(application)
                                if (isValid) {
                                    const result = await this.saveApplication(application)
                                    if (result) {
                                        this.$store.commit('mesosTemplate/updateBindVersion', true)
                                        if (result.template_id) {
                                            this.newTemplateId = result.template_id
                                            this.$store.commit('mesosTemplate/updateCurTemplateId', result.template_id)
                                        }
                                    }
                                    return false
                                }
                            }
                        }
                        break

                    case 'mesosTemplatesetDeployment':
                        const deployments = this.deployments
                        // 对deployment资源数据检测
                        for (const deployment of deployments) {
                            if (deployment.isEdited) {
                                const isValid = await this.checkDeploymentData(deployment)
                                if (isValid) {
                                    const result = await this.saveDeployment(deployment)
                                    if (result) {
                                        this.$store.commit('mesosTemplate/updateBindVersion', true)
                                        if (result.template_id) {
                                            this.newTemplateId = result.template_id
                                            this.$store.commit('mesosTemplate/updateCurTemplateId', result.template_id)
                                        }
                                    }
                                    return false
                                }
                            }
                        }
                        break

                    case 'mesosTemplatesetService':
                        const services = this.services
                        // 对service资源数据检测
                        for (const service of services) {
                            if (service.isEdited) {
                                const isValid = await this.checkServiceData(service)
                                if (isValid) {
                                    const result = await this.saveService(service)
                                    if (result) {
                                        this.$store.commit('mesosTemplate/updateBindVersion', true)
                                        if (result.template_id) {
                                            this.newTemplateId = result.template_id
                                            this.$store.commit('mesosTemplate/updateCurTemplateId', result.template_id)
                                        }
                                    }
                                    return false
                                }
                            }
                        }
                        break

                    case 'mesosTemplatesetConfigmap':
                        const configmaps = this.configmaps
                        // 对configmap资源数据检测
                        for (const configmap of configmaps) {
                            if (configmap.isEdited) {
                                const isValid = await this.checkConfigmapData(configmap)
                                if (isValid) {
                                    const result = await this.saveConfigmap(configmap)
                                    if (result) {
                                        this.$store.commit('mesosTemplate/updateBindVersion', true)
                                        if (result.template_id) {
                                            this.newTemplateId = result.template_id
                                            this.$store.commit('mesosTemplate/updateCurTemplateId', result.template_id)
                                        }
                                    }
                                    return false
                                }
                            }
                        }
                        break

                    case 'mesosTemplatesetSecret':
                        const secrets = this.secrets
                        // 对secret资源数据检测
                        for (const secret of secrets) {
                            if (secret.isEdited) {
                                const isValid = await this.checkSecretData(secret)
                                if (isValid) {
                                    const result = await this.saveSecret(secret)
                                    if (result) {
                                        this.$store.commit('mesosTemplate/updateBindVersion', true)
                                        if (result.template_id) {
                                            this.newTemplateId = result.template_id
                                            this.$store.commit('mesosTemplate/updateCurTemplateId', result.template_id)
                                        }
                                    }
                                    return false
                                }
                            }
                        }
                        break
                }
            },
            saveTemplate (event) {
                const projectId = this.projectId
                const templateId = this.curTemplateId
                const data = this.editTemplate
                // 用户填空数据，用原数据
                if (!data.name) {
                    data.name = this.curTemplate.name
                }
                if (!data.desc) {
                    data.desc = this.curTemplate.desc
                }

                // 没有修改，不处理
                if (data.name === this.curTemplate.name && data.desc === this.curTemplate.desc) {
                    console.log('noedit')
                    this.isEditName = false
                    this.isEditDesc = false
                    return false
                }

                if (templateId) {
                    this.$store.dispatch('mesosTemplate/updateTemplate', { projectId, templateId, data }).then(res => {
                        const data = res.data
                        if (event) {
                            this.$bkMessage({
                                theme: 'success',
                                message: '模板集基础信息保存成功！'
                            })
                        }
                        this.curTemplate = data
                        this.$store.commit('mesosTemplate/updateCurTemplate', data)
                        this.isEditName = false
                        this.isEditDesc = false
                    }, res => {
                        const message = res.message
                        this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                        this.$bkMessage({
                            theme: 'error',
                            message: message,
                            hasCloseIcon: true,
                            delay: '3000'
                        })
                    })
                } else {
                    this.curTemplate = data
                    this.$store.commit('mesosTemplate/updateCurTemplate', data)
                    this.isEditName = false
                    this.isEditDesc = false
                }
            },
            reloadTemplateLockStatus () {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                this.isTemplateLocking = true
                this.$store.dispatch('mesosTemplate/getTemplateById', { projectId, templateId }).then(res => {
                    const data = res.data
                    this.$store.commit('mesosTemplate/updateCurTemplate', data)
                }).finally(res => {
                    setTimeout(() => {
                        this.isTemplateLocking = false
                    }, 1000)
                })
            },
            reloadTemplateset () {
                this.$store.commit('mesosTemplate/clearCurTemplateData')
                this.$parent.$parent.reloadTemplateset()
            },
            initTemplate (callback) {
                if (this.curTemplate.id) {
                    const data = {
                        latest_version_id: this.curTemplate.latest_version_id,
                        applications: this.applications,
                        deployments: this.deployments,
                        services: this.services,
                        configmaps: this.configmaps,
                        secrets: this.secrets
                    }
                    this.isTemplateLoading = false
                    callback(data)
                } else if (this.curTemplateId === 0 || this.curTemplateId === '0') {
                    const templateParams = {
                        id: 0,
                        name: '模板集_' + (+new Date()),
                        desc: '模板集描述',
                        permissions: {
                            create: true,
                            delete: true,
                            list: true,
                            view: true,
                            edit: true,
                            use: true
                        }
                    }
                    this.isTemplateLoading = false
                    this.$store.commit('mesosTemplate/updateCurTemplate', templateParams)
                    this.initResources(callback)
                } else {
                    const templateId = this.curTemplateId
                    const projectId = this.projectId
                    this.$store.dispatch('mesosTemplate/getTemplateById', { projectId, templateId }).then(res => {
                        const data = res.data
                        this.$store.commit('mesosTemplate/updateCurTemplate', data)
                        this.initResources(callback)
                    }, res => {
                        const data = res.data
                        if (data) {
                            if (!data.code || data.code === 400 || data.code === 404) {
                                this.exceptionCode = {
                                    code: '404',
                                    msg: '当前访问的模板集不存在'
                                }
                            } else if (data.code === 403) {
                                this.exceptionCode = {
                                    code: '403',
                                    msg: 'Sorry，您的权限不足!'
                                }
                            } else {
                                this.exceptionCode = {
                                    code: '403',
                                    msg: '异常!'
                                }
                            }
                        } else {
                            this.exceptionCode = {
                                code: '403',
                                msg: '异常!'
                            }
                        }
                        this.$emit('exception', this.exceptionCode)
                    }).finally(res => {
                        this.isTemplateLoading = false
                    })
                }
            },
            initResources (callback) {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                const version = this.curTemplate.latest_show_version_id
                if (version) {
                    this.$store.dispatch('mesosTemplate/getTemplateResource', { projectId, templateId, version }).then(res => {
                        const data = res.data
                        if (data.version) {
                            this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                        }

                        this.$store.commit('mesosTemplate/updateResources', data)

                        const resources = {
                            latest_version_id: this.curTemplate.latest_version_id,
                            applications: data.application,
                            deployments: data.deployment,
                            services: data.service,
                            configmaps: data.configmap,
                            secrets: data.secret
                        }
                        callback(resources)
                    }, res => {
                        const message = res.message
                        this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                        this.$bkMessage({
                            theme: 'error',
                            message: message,
                            hasCloseIcon: true,
                            delay: '10000'
                        })
                    })
                } else {
                    const resources = {
                        latest_version_id: null,
                        applications: this.applications,
                        deployments: this.deployments,
                        services: this.services,
                        configmaps: this.configmaps,
                        secrets: this.secrets
                    }
                    callback(resources)
                }
            },
            updateLocalApplicationData (application, data) {
                application.isEdited = false
                const appId = application.id
                if (data.id) {
                    application.id = data.id
                }
                if (data.version) {
                    this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                }
                this.$store.commit('mesosTemplate/updateApplicationById', { application, appId })
            },
            async createFirstApplication (data, application) {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addFirstApplication', { projectId, templateId, data }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, application, 'application')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async updateApplication (data, application) {
                const version = this.curVersion
                const projectId = this.projectId
                const applicationId = data.id
                const result = await this.$store.dispatch('mesosTemplate/updateApplication', { projectId, version, data, applicationId }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, application, 'application')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async createApplication (data, application) {
                const version = this.curVersion
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addApplication', { projectId, version, data }).then(res => {
                    const responseData = res.data

                    this.updateLocalData(responseData, application, 'application')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async checkApplicationData (application) {
                const appName = application.config.metadata.name
                const instance = application.config.spec.instance
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,29}$/
                const portNameReg = /^[a-z]{1}[a-z0-9-]{0,255}$/
                const nameReg2 = /^[a-zA-Z]{1}[a-zA-Z0-9-_]{0,29}$/
                const pathReg = /\/((?!\.)[\w\d\-./~]+)+/
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                const chineseReg = /[\u4e00-\u9fa5]+/
                let megPrefix = `"${appName}"中`

                if (appName === '') {
                    megPrefix += `名称：`
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '请输入应用名称！'
                    })
                    return false
                }
                if (!nameReg1.test(appName)) {
                    megPrefix += `名称：`
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '应用名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                        delay: 8000
                    })
                    return false
                }

                if (instance === '') {
                    megPrefix += `实例数量：`
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '请输入实例数量！'
                    })
                    return false
                }

                if (application.config.spec.template.spec.networkMode === 'CUSTOM' && !application.config.spec.template.spec.custom_value) {
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '网络模式的自定义值不能为空！',
                        delay: 5000
                    })
                    return false
                }

                if (application.config.webCache && application.config.webCache.metricIdList) {
                    const result = application.config.webCache.metricIdList.filter(item => {
                        return this.metricList.includes(item)
                    })
                    application.config.webCache.metricIdList = result
                }

                const containers = application.config.spec.template.spec.containers

                for (const container of containers) {
                    // 检查container name
                    if (!container.name) {
                        megPrefix += `容器名称：`
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + `名称不能为空！`
                        })
                        return false
                    }

                    if (!nameReg1.test(container.name)) {
                        megPrefix += `容器名称：`
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + '名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                            delay: 8000
                        })
                        return false
                    }

                    // 检查container镜像设置
                    if (!container.image) {
                        this.$bkMessage({
                            theme: 'error',
                            delay: 5000,
                            message: megPrefix + `容器"${container.name}"的镜像及版本配置：请设置所属的镜像及版本！`
                        })
                        return false
                    } else if (container.imageName && !container.imageName.startsWith('{{')) {
                        const matchs = this.imageList.filter(item => {
                            return item.value === container.imageName
                        })
                        if (!matchs.length) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的镜像及版本配置：原镜像已经删除，请重新选择！`,
                                delay: 8000
                            })
                            return false
                        }
                    }

                    // 端口映射检查
                    const portNameCache = {}
                    for (const item of container.ports) {
                        if (item.name || item.protocol || item.containerPort || (item.hostPort !== '')) {
                            if (!item.name) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + `容器"${container.name}"的端口映射配置：名称不能为空！`
                                })
                                return false
                            }
                            if (!portNameReg.test(item.name.replace(varReg, 'name'))) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: megPrefix + `容器"${container.name}"的端口映射配置：名称错误，以字母开头，只能含小写字母、数字、连字符(-)，首字母必须是字母，长度小于256个字符`,
                                    delay: 8000
                                })
                                return false
                            }
                            if (portNameCache[item.name]) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: megPrefix + `容器"${container.name}"的端口映射配置：端口名称不可重复！`,
                                    delay: 8000
                                })
                                return false
                            } else {
                                portNameCache[item.name] = true
                            }
                            if (!item.protocol) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + `容器"${container.name}"的端口映射配置：协议不能为空！`
                                })
                                return false
                            }
                            if (!item.containerPort) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + `容器"${container.name}"的端口映射配置：容器端口不能为空！`
                                })
                                return false
                            }
                            if (parseInt(item.containerPort) < 1 || parseInt(item.containerPort) > 65535) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + `容器"${container.name}"的端口映射配置：容器端口范围为1-65535！`
                                })
                                return false
                            }
                            if (item.hostPort === '') {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + `容器"${container.name}"的端口映射配置：主机端口不能为空！`
                                })
                                return false
                            }
                            if (parseInt(item.hostPort) < -1 || parseInt(item.hostPort) > 65535) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + `容器"${container.name}"的端口映射配置：主机端口范围为0-65535！`
                                })
                                return false
                            }
                        }
                    }

                    // 命令
                    if (container.command && chineseReg.test(container.command)) {
                        this.$bkMessage({
                            theme: 'error',
                            delay: 5000,
                            message: megPrefix + `容器"${container.name}"的命令：启动命令不能含有中文字符！`
                        })
                        return false
                    }

                    if (container.args_text && chineseReg.test(container.args_text)) {
                        this.$bkMessage({
                            theme: 'error',
                            delay: 5000,
                            message: megPrefix + `容器"${container.name}"的命令：命令参数不能含有中文字符！`
                        })
                        return false
                    }

                    // 检查container volumes
                    if (container.volumes.length) {
                        for (const item of container.volumes) {
                            if (item.name || item.volume.hostname || item.volume.mountPath || item.volume.subPath) {
                                if (!item.name) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: megPrefix + `容器"${container.name}"的挂载卷配置：挂载名不能为空！`
                                    })
                                    return false
                                }

                                const name = item.name.replace(varReg, 'name')
                                if (!nameReg2.test(name)) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: megPrefix + `容器"${container.name}"的挂载卷配置：挂载名错误，只能包含：字母、数字、连字符(-)、下划线(_)，首字母必须是字母，长度小于30个字符`,
                                        delay: 8000
                                    })
                                    return false
                                }
                                if (item.type !== 'custom' && !item.volume.hostPath) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: megPrefix + `容器"${container.name}"的挂载卷配置：挂载源不能为空！`,
                                        delay: 5000
                                    })
                                    return false
                                }
                                if (!item.volume.mountPath) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: megPrefix + `容器"${container.name}"的挂载卷配置：容器目录不能为空！`,
                                        delay: 5000
                                    })
                                    return false
                                }
                                const mountPath = item.volume.mountPath.replace(varReg, '/path')
                                if (!pathReg.test(mountPath)) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: megPrefix + `容器"${container.name}"的挂载卷配置：容器目录不正确！`
                                    })
                                    return false
                                }
                            }
                        }
                    }

                    // 环境变量检查
                    const envList = container.env_list
                    for (const env of envList) {
                        if (env.key || env.value) {
                            if (!env.key) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: megPrefix + `容器"${container.name}"的环境变量配置：键不能为空！`,
                                    delay: 5000
                                })
                                return false
                            }

                            if (env.type !== 'custom' && !env.value) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: megPrefix + `容器"${container.name}"的环境变量配置：值不能为空！`,
                                    delay: 5000
                                })
                                return false
                            }
                        }
                    }

                    /**
                     * 资源限制
                     * 0、cpu和mem上下限对应，填了一个，另一个就必须填
                     * 1、request、limit都填
                     * 2、request不填、limit填，后端将limit给request
                     * 3、request填、limit不填，limit不限制
                     */
                    // cpu上限
                    if (container.resources.limits.cpu === '' && container.resources.requests.cpu === '' && container.resources.limits.memory === '' && container.resources.requests.memory === '') {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + `容器"${container.name}"的资源限制配置：CPU和内存限制必须配置！`,
                            delay: 5000
                        })
                        return false
                    }
                    if (container.resources.limits.cpu !== '') {
                        if (container.resources.limits.cpu < 0.001) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：CPU上限不能少于0.001！`,
                                delay: 5000
                            })
                            return false
                        }
                        if (container.resources.limits.cpu > 128) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：CPU上限不能大于128！`,
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.limits.memory === '') {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：内存上限不能为空！`,
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.requests.cpu && (container.resources.limits.cpu < container.resources.requests.cpu)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：CPU上限不能小于下限！`,
                                delay: 5000
                            })
                            return false
                        }
                    }

                    // cpu下限
                    if (container.resources.requests.cpu !== '') {
                        if (container.resources.requests.cpu < 0.001) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：CPU下限不能少于0.001！`,
                                delay: 5000
                            })
                            return false
                        }
                        if (container.resources.requests.cpu > 128) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：CPU下限不能大于128！`,
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.requests.memory === '') {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：内存下限不能为空！`,
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.limits.cpu && (container.resources.limits.cpu < container.resources.requests.cpu)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：CPU上限不能小于下限！`,
                                delay: 5000
                            })
                            return false
                        }
                    }

                    // 内存上限
                    if (container.resources.limits.memory !== '') {
                        if (container.resources.limits.cpu === '') {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：CPU上限不能为空！`,
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.requests.memory && (container.resources.limits.memory < container.resources.requests.memory)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：内存上限不能小于下限！`,
                                delay: 5000
                            })
                            return false
                        }
                    }

                    // 内存下限
                    if (container.resources.requests.memory !== '') {
                        if (container.resources.requests.cpu === '') {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：CPU下限不能为空！`,
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.limits.memory && (container.resources.limits.memory < container.resources.requests.memory)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `容器"${container.name}"的资源限制配置：内存上限不能小于下限！`,
                                delay: 5000
                            })
                            return false
                        }
                    }

                    // 健康检查
                    const healthChecks = container.healthChecks[0]
                    if (healthChecks.type) {
                        switch (healthChecks.type) {
                            case 'HTTP':
                            case 'REMOTE_HTTP':
                                if (!healthChecks.http.portName) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: megPrefix + `容器"${container.name}"的健康检查配置：端口名称不能为空！`
                                    })
                                    return false
                                }
                                break
                            case 'TCP':
                            case 'REMOTE_TCP':
                                if (!healthChecks.tcp.portName) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: megPrefix + `容器"${container.name}"的健康检查配置：端口名称不能为空！`
                                    })
                                    return false
                                }
                                break
                            case 'COMMAND':
                                if (!healthChecks.command.portName) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: megPrefix + `-容器"${container.name}"的健康检查配置：端口名称不能为空！`
                                    })
                                    return false
                                }
                                if (!healthChecks.command.value) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: megPrefix + `容器"${container.name}"的健康检查配置：检查命令不能为空！`
                                    })
                                    return false
                                }
                                break
                        }
                    }

                    if (container.logListCache.length) {
                        for (const log of container.logListCache) {
                            log.value = log.value.trim()
                            if (log.value && !pathReg.test(log.value.replace(varReg, '/path'))) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + `容器"${container.name}"的非标准日志采集配置：日志绝对路径不正确！`
                                })
                                return false
                            }
                        }
                    }
                }

                return true
            },
            async formatApplicationData (application) {
                const params = JSON.parse(JSON.stringify(application))
                params.template = {
                    name: this.curTemplate.name,
                    desc: this.curTemplate.desc
                }
                delete params.isEdited
                // 键值转换
                const webCache = application.config.webCache
                if (webCache && webCache.remarkListCache) {
                    const remarkKeyList = this.tranListToObject(webCache.remarkListCache)
                    params.config.metadata.annotations = remarkKeyList
                }

                if (webCache && webCache.labelListCache) {
                    const labelKeyList = this.tranListToObject(webCache.labelListCache)
                    params.config.metadata.labels = labelKeyList
                }

                if (webCache && webCache.logLabelListCache) {
                    const logLabelKeyList = this.tranListToObject(webCache.logLabelListCache)
                    params.config.customLogLabel = logLabelKeyList
                }

                // 转换调度约束
                const constraint = params.config.constraint.intersectionItem
                constraint.forEach(item => {
                    const data = item.unionData[0]
                    const operate = data.operate
                    switch (operate) {
                        case 'UNIQUE':
                            delete data.type
                            delete data.set
                            delete data.text
                            break
                        case 'MAXPER':
                            data.type = 3
                            data.text = {
                                'value': data.arg_value
                            }
                            delete data.set
                            break
                        case 'GREATER':
                            data.type = 1
                            delete data.set
                            delete data.text
                            data.scalar = {
                                'value': data.arg_value
                            }
                            break
                        case 'CLUSTER':
                            data.type = 4
                            if (data.arg_value.trim().length) {
                                data.set = {
                                    'item': data.arg_value.split('|')
                                }
                            } else {
                                data.set = {
                                    'item': []
                                }
                            }

                            delete data.text
                            break
                        case 'GROUPBY':
                            data.type = 4
                            if (data.arg_value.trim().length) {
                                data.set = {
                                    'item': data.arg_value.split('|')
                                }
                            } else {
                                data.set = {
                                    'item': []
                                }
                            }
                            delete data.text
                            break
                        case 'LIKE':
                            if (data.arg_value.indexOf('|') > -1) {
                                data.type = 4
                                if (data.arg_value.trim().length) {
                                    data.set = {
                                        'item': data.arg_value.split('|')
                                    }
                                } else {
                                    data.set = {
                                        'item': []
                                    }
                                }
                                delete data.text
                            } else {
                                data.type = 3
                                data.text = {
                                    'value': data.arg_value
                                }
                                delete data.set
                            }
                            break
                        case 'UNLIKE':
                            if (data.arg_value.indexOf('|') > -1) {
                                data.type = 4
                                if (data.arg_value.trim().length) {
                                    data.set = {
                                        'item': data.arg_value.split('|')
                                    }
                                } else {
                                    data.set = {
                                        'item': []
                                    }
                                }
                                delete data.text
                            } else {
                                data.type = 3
                                data.text = {
                                    'value': data.arg_value
                                }
                                delete data.set
                            }
                            break
                    }
                })

                // 转换命令参数和环境变量
                const containers = params.config.spec.template.spec.containers
                containers.forEach(container => {
                    if (container.args_text && container.args_text.trim().length) {
                        container.args = container.args_text.split(' ')
                    } else {
                        container.args = []
                    }

                    // docker参数
                    const parameterList = container.parameter_list
                    container.parameters = []
                    parameterList.forEach(param => {
                        if (param.key && param.value) {
                            container.parameters.push(param)
                        }
                    })

                    // 端口
                    const ports = container.ports
                    const validatePorts = []
                    ports.forEach(item => {
                        if (item.containerPort && (item.hostPort !== undefined) && item.name && item.protocol) {
                            validatePorts.push({
                                id: item.id,
                                containerPort: item.containerPort,
                                hostPort: item.hostPort,
                                protocol: item.protocol,
                                name: item.name
                            })
                        }
                    })

                    // volumes
                    const volumes = container.volumes
                    let validateVolumes = []
                    validateVolumes = volumes.filter(item => {
                        return item.volume.mountPath && item.name
                    })
                    container.volumes = validateVolumes

                    // logpath
                    const paths = []
                    const logList = container.logListCache
                    logList.forEach(item => {
                        if (item.value) {
                            paths.push(item.value)
                        }
                    })
                    container.logPathList = paths
                })
                return params
            },
            async saveTemplateData () {
                if (!this.isTemplateCanSave) {
                    return false
                }
                const applications = this.applications
                const deployments = this.deployments
                const services = this.services
                const configmaps = this.configmaps
                const secrets = this.secrets

                // 如果当前版本是草稿或者资源已经编辑过都需求检测和保存
                // 对application资源数据检测
                for (const application of applications) {
                    if (application.isEdited) {
                        const isValid = await this.checkApplicationData(application)
                        if (!isValid) {
                            return false
                        }
                    }
                }

                // 对deployment资源数据检测
                for (const deployment of deployments) {
                    if (deployment.isEdited) {
                        const isValid = await this.checkDeploymentData(deployment)
                        if (!isValid) {
                            return false
                        }
                    }
                }

                // 对service资源数据检测
                for (const service of services) {
                    if (service.isEdited) {
                        const isValid = await this.checkServiceData(service)
                        if (!isValid) {
                            return false
                        }
                    }
                }

                // 对configmap资源数据检测
                for (const configmap of configmaps) {
                    if (configmap.isEdited) {
                        const isValid = await this.checkConfigmapData(configmap)
                        if (!isValid) {
                            return false
                        }
                    }
                }

                // 对secret资源数据检测
                for (const secret of secrets) {
                    if (secret.isEdited) {
                        const isValid = await this.checkSecretData(secret)
                        if (!isValid) {
                            return false
                        }
                    }
                }

                if (this.isDataSaveing) {
                    return false
                } else {
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', true)
                    this.isDataSaveing = true
                }

                // 保存applicatoins
                for (const application of applications) {
                    if (!application.isEdited) {
                        continue
                    }
                    const preId = application.id
                    const result = await this.saveApplication(application)
                    if (!result) {
                        return false
                    } else {
                        this.$emit('saveApplicationSuccess', { responseData: result, resource: application, preId: preId })
                    }
                }

                // // // 保存deployments
                for (const deployment of deployments) {
                    if (!deployment.isEdited) {
                        continue
                    }
                    const preId = deployment.id
                    const result = await this.saveDeployment(deployment)
                    if (!result) {
                        return false
                    } else {
                        this.$emit('saveDeploymentSuccess', { responseData: result, resource: deployment, preId: preId })
                    }
                }

                // // 保存services
                for (const service of services) {
                    if (!service.isEdited) {
                        continue
                    }
                    const preId = service.id
                    const result = await this.saveService(service)
                    if (!result) {
                        return false
                    } else {
                        this.$emit('saveServiceSuccess', { responseData: result, resource: service, preId: preId })
                    }
                }

                // // 保存configmaps
                for (const configmap of configmaps) {
                    if (!configmap.isEdited) {
                        continue
                    }
                    const preId = configmap.id
                    const result = await this.saveConfigmap(configmap)
                    if (!result) {
                        return false
                    } else {
                        this.$emit('saveConfigmapSuccess', { responseData: result, resource: configmap, preId: preId })
                    }
                }

                // // 保存secrets
                for (const secret of secrets) {
                    if (!secret.isEdited) {
                        continue
                    }
                    const preId = secret.id
                    const result = await this.saveSecret(secret)
                    if (!result) {
                        return false
                    } else {
                        this.$emit('saveSecretSuccess', { responseData: result, resource: secret, preId: preId })
                    }
                }

                this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                await this.getVersionList()
                this.versionSidePanel.isShow = false
                this.versionDialogConf.isShow = true
                this.isDataSaveing = false
                // messager.close()
            },
            hideVersionBox () {
                if (this.isNewTemplate) {
                    if (this.newTemplateId) {
                        this.$router.push({
                            name: 'mesosTemplatesetApplication',
                            params: {
                                projectId: this.projectId,
                                projectCode: this.projectCode,
                                templateId: this.newTemplateId
                            }
                        })
                    }
                }
                this.versionDialogConf.isShow = false
                this.selectedVersion = ''
            },
            checkVersionData () {
                const nameReg = /^[a-zA-Z0-9-_.]{1,45}$/

                if (!nameReg.test(this.versionKeyword)) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请填写1至45个字符（由字母、数字、下划线以及 - 或 . 组成）'
                    })
                    return false
                }

                for (const item of this.versionList) {
                    if (item.name === this.versionKeyword) {
                        this.$bkMessage({
                            theme: 'error',
                            message: `版本${this.versionKeyword}已经存在！`
                        })
                        return false
                    }
                }
                return true
            },
            async saveVersion (version) {
                const projectId = this.projectId
                const templateId = this.curTemplateId

                // 根据不同方式组装数据
                this.versionMetadata.real_version_id = this.curVersion
                if (this.saveVersionWay === 'cur') {
                    this.versionMetadata.show_version_id = this.curShowVersionId
                } else if (this.saveVersionWay === 'old' && this.selectedVersion) {
                    this.versionMetadata.show_version_id = this.selectedVersion
                } else if (this.saveVersionWay === 'new') {
                    if (this.checkVersionData()) {
                        this.versionMetadata.name = this.versionKeyword
                        this.versionMetadata.show_version_id = 0
                    } else {
                        return false
                    }
                }

                // 匹配name
                if (this.versionList) {
                    // 如果有版本，自动默认选中原来版本号
                    this.versionList.forEach(item => {
                        if (String(item.show_version_id) === String(this.versionMetadata.show_version_id)) {
                            this.versionMetadata.name = item.name
                        }
                    })
                }

                const params = this.versionMetadata
                await this.$store.dispatch('mesosTemplate/saveVersion', { projectId, templateId, params }).then(res => {
                    this.$bkMessage({
                        theme: 'success',
                        message: '保存成功！',
                        delay: 3000
                    })

                    this.$store.commit('mesosTemplate/updateBindVersion', false)

                    if (res.data.show_version_id) {
                        this.$store.commit('mesosTemplate/updateCurShowVersionId', res.data.show_version_id)
                    }
                    if (this.isNewTemplate && this.curTemplateId) {
                        this.$router.push({
                            name: this.$route.name,
                            params: {
                                projectId: this.projectId,
                                projectCode: this.projectCode,
                                templateId: this.curTemplateId
                            }
                        })
                    }

                    this.curTemplate.latest_show_version = this.versionMetadata.name
                    this.curTemplate.latest_show_version_id = res.data.show_version_id
                    this.curTemplate.latest_version_id = res.data.real_version_id

                    this.saveVersionWay = 'cur'
                    this.versionKeyword = ''
                    this.selectedVersion = ''
                    this.versionDialogConf.isShow = false
                    this.getVersionList()
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                })
            },
            async saveApplication (application) {
                let result
                const data = await this.formatApplicationData(application)
                if (this.curVersion) {
                    if (application.id.indexOf && application.id.indexOf('local') > -1) {
                        result = await this.createApplication(data, application)
                    } else {
                        result = await this.updateApplication(data, application)
                    }
                } else {
                    result = await this.createFirstApplication(data, application)
                }
                return result
            },
            getKeyList (list) {
                let results = []
                results = list.filter(item => {
                    return item.key && item.value
                })
                return results
            },
            tranListToObject (list) {
                const results = this.getKeyList(list)
                if (results.length === 0) {
                    return {}
                } else {
                    const obj = {}
                    results.forEach(item => {
                        if (item.key) {
                            obj[item.key] = item.value
                        }
                    })
                    return obj
                }
            },
            async saveDeployment (deployment) {
                let result
                const data = JSON.parse(JSON.stringify(deployment))
                if (this.curVersion) {
                    if (deployment.id.indexOf && (deployment.id.indexOf('local') > -1)) {
                        result = await this.createDeployment(data, deployment)
                    } else {
                        result = await this.updateDeployment(data, deployment)
                    }
                } else {
                    result = await this.createFirstDeployment(data, deployment)
                }
                return result
            },
            async checkDeploymentData (deployment) {
                const deploymentName = deployment.name
                const appId = deployment.app_id
                const deploymentNameReg = /^[a-z]{1}[a-z0-9-]{0,29}$/
                let megPrefix = `"${deploymentName}"中`

                if (deploymentName === '') {
                    megPrefix += '名称：'
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入名称！'
                    })
                    return false
                }
                if (!deploymentNameReg.test(deploymentName)) {
                    megPrefix += '名称：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                        delay: 8000
                    })
                    return false
                }
                if (!appId) {
                    megPrefix += '关联：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '请关联相应的Application！'
                    })
                    return false
                }
                return true
            },
            updateLocalData (responseData, targetData, resourceType) {
                targetData.isEdited = false
                if (targetData.id) {
                    const preId = targetData.id
                    switch (resourceType) {
                        case 'application':
                            this.$store.commit('mesosTemplate/updateApplicationById', { application: responseData, preId: preId })
                            break
                        case 'deployment':
                            this.$store.commit('mesosTemplate/updateDeploymentById', { deployment: responseData, preId: preId })
                            break
                        case 'service':
                            this.$store.commit('mesosTemplate/updateServiceById', { service: responseData, preId: preId })
                            break
                        case 'configmap':
                            this.$store.commit('mesosTemplate/updateConfigmapById', { configmap: responseData, targetData: targetData, preId: preId })
                            break
                        case 'secret':
                            this.$store.commit('mesosTemplate/updateSecretById', { secret: responseData, targetData: targetData, preId: preId })
                            break
                    }
                }
                if (responseData.template_id) {
                    this.newTemplateId = responseData.template_id
                    this.$store.commit('mesosTemplate/updateCurTemplateId', responseData.template_id)
                }
                if (responseData.version) {
                    this.$store.commit('mesosTemplate/updateCurVersion', responseData.version)
                }
                // this.$store.commit('mesosTemplate/updateDeployments', this.deployments)
                // clearInterval(this.compareTimer)
                // deployment.isEdited = false
                // setTimeout(() => {
                //     deploymentCache = JSON.parse(JSON.stringify(deployment))
                //     this.watchChange()
                // }, 500)
            },
            async createDeployment (data, deployment) {
                const version = this.curVersion
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addDeployment', { projectId, version, data }).then(res => {
                    const responseData = res.data

                    this.updateLocalData(responseData, deployment, 'deployment')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async createFirstDeployment (data, deployment) {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addFirstDeployment', { projectId, templateId, data }).then(res => {
                    const responseData = res.data

                    this.updateLocalData(responseData, deployment, 'deployment')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async updateDeployment (data, deployment) {
                const version = this.curVersion
                const projectId = this.projectId
                const deploymentId = data.id
                const result = await this.$store.dispatch('mesosTemplate/updateDeployment', { projectId, version, data, deploymentId }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, deployment, 'deployment')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })

                return result
            },
            async saveService (service) {
                let result
                const data = await this.formatServiceData(service)

                if (this.curVersion) {
                    if (service.id.indexOf && (service.id.indexOf('local') > -1)) {
                        result = await this.createService(data, service)
                    } else {
                        result = await this.updateService(data, service)
                    }
                } else {
                    result = await this.createFirstService(data, service)
                }
                return result
            },
            async formatServiceData (service) {
                const params = JSON.parse(JSON.stringify(service))
                const webCache = params.config.webCache
                // 键值转换
                if (webCache && webCache.labelListCache) {
                    const labelKeyList = this.tranListToObject(webCache.labelListCache)
                    params.config.metadata.labels = labelKeyList
                }

                // ips
                const ips = service.serviceIPs.trim().split(',')
                params.config.spec.clusterIP = ips

                if (params.config.spec.type === 'None') {
                    params.config.spec.clusterIP = []
                }

                params.app_id = {}
                params.config.webCache.link_app_weight.forEach(item => {
                    params.app_id[item.id] = item.weight
                })
                return params
            },
            checkTotalPercent (service) {
                let total = 0
                service.config.webCache.link_app_weight.forEach(item => {
                    total += item.weight
                })
                if (total !== 100) {
                    // this.isWeightError = true
                    return false
                }
                // this.isWeightError = false
                return true
            },
            async checkServiceData (service) {
                const serviceName = service.config.metadata.name
                const appId = service.config.webCache.link_app

                const serviceNameReg = /^[a-z]{1}[a-z0-9-]{0,29}$/
                const serviceIPReg = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)($|(?!\.$)\.)){4}$/
                const pathReg = /\/((?!\.)[\w\d\-./~]+)+/
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                let megPrefix = `"${serviceName}"中`
                // if (serviceName) {
                //     megPrefix += `[${serviceName}]：`
                // } else {
                //     megPrefix += `[未命名]：`
                // }

                if (serviceName === '') {
                    megPrefix += '名称：'
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入名称！'
                    })
                    return false
                }

                if (!serviceNameReg.test(serviceName.replace(varReg, 'service'))) {
                    megPrefix += '名称：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                        delay: 8000
                    })
                    return false
                }

                if (!appId.length) {
                    megPrefix += '关联应用：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '请关联相应的Application！'
                    })
                    return false
                }

                if (!this.checkTotalPercent(service)) {
                    megPrefix += '权重设置：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '权重的值为大于等于0的整数，且所有权重相加为100！'
                    })
                    return false
                }

                const serviceIPs = service.serviceIPs.trim().split(',')
                for (const ip of serviceIPs) {
                    if (ip && !serviceIPReg.test(ip)) {
                        megPrefix += 'IP：'
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + '请输入正确IP地址！',
                            delay: 3000
                        })
                        return false
                    }
                }
                const ports = service.config.spec.ports
                // 端口映射检查
                for (const item of ports) {
                    if (item.name) {
                        if (!item.servicePort) {
                            megPrefix += '端口映射：'
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: megPrefix + '服务端口不能为空！'
                            })
                            return false
                        }
                        if (parseInt(item.servicePort) < 1 || parseInt(item.servicePort) > 65535) {
                            megPrefix += '端口映射：'
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: megPrefix + '服务端口范围为1-65535！'
                            })
                            return false
                        }
                        // if (item.protocol.toLowerCase() === 'http' && !item.domainName) {
                        //     megPrefix += '端口映射：'
                        //     this.$bkMessage({
                        //         theme: 'error',
                        //         delay: 5000,
                        //         message: megPrefix + '域名不能为空！'
                        //     })
                        //     return false
                        // }
                        const path = item.path.replace(varReg, '/a/b')
                        if (item.path && !pathReg.test(path)) {
                            megPrefix += '端口映射：'
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: megPrefix + `请填写正确的路径！`
                            })
                            return false
                        }
                    }
                }

                return true
            },
            async createService (data, service) {
                const version = this.curVersion
                const projectId = this.projectId
                const result = this.$store.dispatch('mesosTemplate/addService', { projectId, version, data }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, service, 'service')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async createFirstService (data, service) {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addFirstService', { projectId, templateId, data }).then(res => {
                    this.updateLocalData(data, service, 'service')
                    this.isDataSaveing = false
                    return data
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async updateService (data, service) {
                const version = this.curVersion
                const projectId = this.projectId
                const serviceId = data.id
                const result = this.$store.dispatch('mesosTemplate/updateService', { projectId, version, data, serviceId }).then(res => {
                    const data = res.data
                    this.updateLocalData(data, service, 'service')
                    this.isDataSaveing = false
                    return data
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async createConfigmap (data, configmap) {
                const version = this.curVersion
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addConfigmap', { projectId, version, data }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, configmap, 'configmap')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async createFirstConfigmap (data, configmap) {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addFirstConfigmap', { projectId, templateId, data }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, configmap, 'configmap')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async updateConfigmap (data, configmap) {
                const version = this.curVersion
                const projectId = this.projectId
                const configmapId = data.id
                const result = await this.$store.dispatch('mesosTemplate/updateConfigmap', { projectId, version, data, configmapId }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, configmap, 'configmap')
                    return responseData
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async checkConfigmapData (configmap) {
                const configmapName = configmap.config.metadata.name
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,29}$/
                const nameReg2 = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,29}$/
                const keys = configmap.configmapKeyList
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                let megPrefix = `"${configmapName}"中`

                if (configmapName === '') {
                    megPrefix += '名称：'
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入名称！'
                    })
                    return false
                }
                if (!nameReg1.test(configmapName)) {
                    megPrefix += '名称：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                        delay: 8000
                    })
                    return false
                }
                if (keys && keys.length) {
                    for (const item of keys) {
                        const key = item.key.replace(varReg, 'key')
                        if (!nameReg2.test(key)) {
                            megPrefix += '键：'
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + '键名错误，只能包含：字母、数字、连字符(-)、点(.)、下划线(_)，必须是字母开头，长度小于30个字符',
                                delay: 8000
                            })
                            return false
                        }
                        if (!item.content) {
                            megPrefix += '值：'
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `请输入键${item.key}的值！`
                            })
                            return false
                        }
                    }
                } else {
                    megPrefix += '键：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + `请先添加键！`
                    })
                    return false
                }
                return true
            },
            // updateConfigmapDatas (configmap) {
            //     let keyObj = {}
            //     let keys = configmap.configmapKeyList
            //     keys.forEach(item => {
            //         keyObj[item.key] = {
            //             type: item.type,
            //             content: item.content
            //         }
            //     })
            //     configmap.config.datas = keyObj
            // },
            async formatConfigmapData (configmap) {
                const params = JSON.parse(JSON.stringify(configmap))

                const keyObj = {}
                const keys = params.configmapKeyList
                if (keys && keys.length) {
                    keys.forEach(item => {
                        keyObj[item.key] = {
                            type: item.type,
                            content: item.content
                        }
                    })
                    params.config.datas = keyObj
                    configmap.config.datas = keyObj
                }

                params.template = {
                    name: this.curTemplate.name,
                    desc: this.curTemplate.desc
                }
                return params
            },
            async saveConfigmap (configmap) {
                const data = await this.formatConfigmapData(configmap)
                let result
                if (this.curVersion) {
                    if (configmap.id.indexOf && (configmap.id.indexOf('local') > -1)) {
                        result = this.createConfigmap(data, configmap)
                    } else {
                        result = this.updateConfigmap(data, configmap)
                    }
                } else {
                    result = this.createFirstConfigmap(data, configmap)
                }
                return result
            },
            async createSecret (data, secret) {
                const version = this.curVersion
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addSecret', { projectId, version, data }).then(res => {
                    const data = res.data
                    this.updateLocalData(data, secret, 'secret')
                    return data
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async createFirstSecret (data, secret) {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addFirstSecret', { projectId, templateId, data }).then(res => {
                    const data = res.data
                    this.updateLocalData(data, secret, 'secret')
                    return data
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async updateSecret (data, secret) {
                const version = this.curVersion
                const projectId = this.projectId
                const secretId = secret.id
                const result = await this.$store.dispatch('mesosTemplate/updateSecret', { projectId, version, data, secretId }).then(res => {
                    const data = res.data
                    this.updateLocalData(data, secret, 'secret')
                    return data
                }, res => {
                    const message = res.message
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async checkSecretData (secret) {
                const secretName = secret.config.metadata.name
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,29}$/
                const nameReg2 = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,29}$/
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                const keys = secret.secretKeyList
                let megPrefix = `"${secretName}"中`

                if (secretName === '') {
                    megPrefix += '名称：'
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入名称！'
                    })
                    return false
                }
                if (!nameReg1.test(secretName)) {
                    megPrefix += '名称：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                        delay: 8000
                    })
                    return false
                }

                if (keys && keys.length) {
                    for (const item of keys) {
                        const key = item.key.replace(varReg, 'key')
                        if (!nameReg2.test(key)) {
                            megPrefix += '键：'
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + '键名错误，只能包含：字母、数字、连字符(-)、点(.)、下划线(_)，必须是字母开头，长度小于30个字符',
                                delay: 8000
                            })
                            return false
                        }
                        if (!item.content) {
                            megPrefix += '值：'
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `请输入键${item.key}的值！`
                            })
                            return false
                        }
                    }
                } else {
                    megPrefix += '键：'
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + `请先添加键！`
                    })
                    return false
                }

                return true
            },
            // updateSecretDatas () {
            //     let keyObj = {}
            //     let keys = this.secretKeyList
            //     for (let item of keys) {
            //         keyObj[item.key] = {
            //             content: item.content
            //         }
            //     }
            //     this.curSecret.config.datas = keyObj
            // },
            async formatSecretData (secret) {
                const params = JSON.parse(JSON.stringify(secret))
                const keyObj = {}
                const keys = params.secretKeyList
                if (keys && keys.length) {
                    keys.forEach(item => {
                        keyObj[item.key] = {
                            type: item.type,
                            content: item.content
                        }
                    })
                    params.config.datas = keyObj
                    secret.config.datas = keyObj
                }

                params.template = {
                    name: this.curTemplate.name,
                    desc: this.curTemplate.desc
                }
                return params
            },
            async saveSecret (secret) {
                const data = await this.formatSecretData(secret)
                let result
                if (this.curVersion) {
                    if (secret.id.indexOf && (secret.id.indexOf('local') > -1)) {
                        result = this.createSecret(data, secret)
                    } else {
                        result = this.updateSecret(data, secret)
                    }
                } else {
                    result = this.createFirstSecret(data, secret)
                }
                return result
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '../../../css/mixins/scroller.css';
    @import '../../../css/mixins/ellipsis.css';

    .biz-templateset-action {
        font-size: 22px;
        color: #737987;
        float: right;
        margin: 12px 20px 0 0;

        >a {
            display: inline-block;
            color: #737987;
            margin-right: 5px;

            &:hover {
                color: #3c96ff;
            }

            &.is-disabled {
                color: #ccc;
                cursor: not-allowed;
            }
        }

    }

    .biz-lock-box {
        width: 100%;
        position: absolute;
        top: 60px;
        left: 0;
        text-align: left;

        .lock-wrapper {
            background-color: #F0F8FF;
            border: 1px solid #A3C5FD;
            border-radius: 2px;
            height: 36px;
            line-height: 34px;
            font-size: 12px;
            color: #63656E;
            padding: 0 12px;
            margin: 20px;

            &.warning {
                border-color: #FFB848;
                background-color: #FFF4E2;

                .bk-icon {
                    color: #FFB848;
                }
            }
        }

        .bk-icon {
            color: #3A84FF;
            font-size: 14px;
            margin-right: 3px;
        }

        .desc {
            font-weight: normal;
            color: #63656E;
        }

        .action {
            float: right;
        }
    }

    .biz-data-table {
        border: 1px solid #dde4eb;
        margin-bottom: 25px;
    }

    .biz-data-table>thead>tr>th {
        background: #fafbfd;
    }

    .biz-data-table>thead>tr>th,
    .biz-data-table>thead>tr>td,
    .biz-data-table>tbody>tr>th,
    .biz-data-table>tbody>tr>td {
        height: 42px;
        padding: 10px 20px;
    }

    .version-box {
        text-align: left;
        padding: 5px 15px;

        .title {
            text-align: left;
            font-size: 14px;
            margin: 0;
            font-weight: bold;
            color: #737987;
            margin-bottom: 10px;
        }

        .active {
            color: #c3cdd7;
        }

        ul {
            border: 1px solid #dde4eb;
            border-radius: 2px;
            background: #fafbfd;
            margin-top: 2px;
            padding: 10px;
            @mixin scroller;
        }

        .empty {
            line-height: 200px;
            color: #737987;
            font-size: 14px;
            text-align: center;

            .name {
                max-width: 100px;
                line-height: 1;
                @mixin ellipsis;
                display: inline-block;
            }
        }

        .create {
            font-size: 14px;
            color: #3c96ff;
            margin: 15px;
        }

        .item {
            line-height: 40px;
            padding: 0 15px;
            cursor: pointer;
            color: #737987;
            font-size: 14px;
            position: relative;

            .bk-icon {
                display: none;
            }

        }
    }

</style>
