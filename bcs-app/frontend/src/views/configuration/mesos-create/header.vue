<template>
    <div class="biz-top-bar" :style="{ marginBottom: (isNewTemplate || !canTemplateEdit) ? '0px' : '55px' }">
        <i class="biz-back bk-icon icon-arrows-left" @click="beforeLeave"></i>
        <template v-if="exceptionCode">
            <div class="biz-templateset-title">
                <span>{{$t('返回模板集')}}</span>
            </div>
        </template>
        <template v-esle>
            <div class="biz-templateset-title">
                <span v-show="!isEditName">{{curTemplate.name}}</span>
                <input
                    type="text"
                    :placeholder="$t('30个以内的字符，Enter保存')" maxlength="30" class="bk-form-input"
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
                <input type="text" :placeholder="$t('50个以内的字符，Enter保存')" maxlength="50" class="bk-form-input" v-model="editTemplate.desc" v-bk-focus v-if="isEditDesc" @blur="saveTemplate" @keyup.enter="saveTemplate">
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
                                        {{$t('您已经对此模板集加锁，只有解锁后，其他用户才可操作此模板集。')}}
                                        <span v-if="lateShowVersionName">（{{$t('当前版本号')}}：{{lateShowVersionName}}）</span>
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
                                        {{$t('{locker}正在操作，您如需编辑请联系{locker}解锁。', templateLockStatus)}}
                                        <span v-if="lateShowVersionName">（{{$t('当前版本号')}}：{{lateShowVersionName}}）</span>
                                    </strong>
                                    <div class="action">
                                        <a href="javascript: void(0);" class="bk-text-button" @click="reloadTemplateset">{{$t('点击刷新')}}</a>
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
                                    {{$t('为避免多成员同时编辑，引起内容或版本冲突，建议在编辑时，开启保护功能。')}}
                                    <span v-if="lateShowVersionName">（{{$t('当前版本号')}}：{{lateShowVersionName}}）</span>
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
                        <button href="javascript:void(0)" class="bk-button bk-default" disabled>{{$t('保存草稿')}}</button>
                        <button href="javascript:void(0)" class="bk-button bk-primary" style="min-width: 70px;" disabled>{{$t('保存')}}</button>
                    </template>
                    <template v-else>
                        <button href="javascript:void(0)" class="bk-button bk-default" @click.stop.prevent="saveTemplateDraft">{{$t('保存草稿')}}</button>
                        <button href="javascript:void(0)" :class="['bk-button bk-primary', { 'is-loading': isDataSaveing, 'is-disabled': !isTemplateCanSave }]" style="min-width: 70px;" @click.stop.prevent="saveTemplateData">{{$t('保存')}}</button>
                    </template>
                </template>
                <template v-else>
                    <bk-tooltip :delay="300" placement="bottom">
                        <button href="javascript:void(0)" class="bk-button bk-default" disabled>{{$t('保存草稿')}}</button>
                        <template slot="content">
                            <p class="biz-permission-tip">
                                {{$t('无权限，请去')}}<a :href="createApplyPermUrl({
                                    policy: 'edit',
                                    projectCode: projectCode,
                                    idx: 'templates'
                                })" class="biz-link" target="_blank">{{$t('申请')}}</a>
                            </p>
                        </template>
                    </bk-tooltip>
                    <bk-tooltip :delay="300" placement="bottom">
                        <button href="javascript:void(0)" class="bk-button bk-success" disabled>{{$t('保存')}}</button>
                        <template slot="content">
                            <p class="biz-permission-tip">
                                {{$t('无权限，请去')}}<a :href="createApplyPermUrl({
                                    policy: 'edit',
                                    projectCode: projectCode,
                                    idx: 'templates'
                                })" class="biz-link" target="_blank">{{$t('申请')}}</a>
                            </p>
                        </template>
                    </bk-tooltip>
                </template>
                <!-- <button
                    href="javascript:void(0)"
                    style="min-width: 70px;"
                    v-bktooltips="zipTooltipText"
                    :key="fileImportIndex"
                    :class="['bk-button bk-default biz-import-btn']">
                    {{$t('导入')}}
                    <input
                        ref="fileInput"
                        type="file"
                        name="upload"
                        class="file-input"
                        accept="application/zip,application/x-zip,application/x-zip-compressed"
                        @change="handleFileInput()">
                </button> -->
                <button href="javascript:void(0)" style="min-width: 70px;" @click.stop.prevent="handleExport" :class="['bk-button bk-default', { 'is-disabled': !canCreateInstance }]">
                    {{$t('导出')}}
                </button>

                <template v-if="curTemplate.permissions.use">
                    <button href="javascript:void(0)" style="min-width: 70px;" @click.stop.prevent="createInstance" :class="['bk-button bk-default', { 'is-disabled': !canCreateInstance }]">
                        {{$t('实例化')}}
                    </button>
                </template>
                <template v-else>
                    <bk-tooltip :delay="300" placement="bottom">
                        <button href="javascript:void(0)" class="bk-button bk-default" disabled>{{$t('实例化')}}</button>
                        <template slot="content">
                            <p class="biz-permission-tip">
                                {{$t('无权限，请去')}}<a :href="createApplyPermUrl({
                                    policy: 'use',
                                    projectCode: projectCode,
                                    idx: 'templates'
                                })" class="biz-link" target="_blank">{{$t('申请')}}</a>
                            </p>
                        </template>
                    </bk-tooltip>
                </template>

                <template v-if="curTemplate.permissions.view">
                    <button href="javascript:void(0)" :class="['bk-button bk-default']" @click.stop.prevent="showVersionPanel">{{$t('版本列表')}}</button>
                </template>
                <template v-else>
                    <bk-tooltip :delay="300" placement="bottom">
                        <button href="javascript:void(0)" class="bk-button bk-default is-disabled" disabled>{{$t('版本列表')}}</button>
                        <template slot="content">
                            <p class="biz-permission-tip">
                                {{$t('无权限，请去')}}<a :href="createApplyPermUrl({
                                    policy: 'view',
                                    projectCode: projectCode,
                                    idx: 'templates'
                                })" class="biz-link" target="_blank">{{$t('申请')}}</a>
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
                    <p class="title">{{$t('保存修改到')}}：</p>
                    <ul class="version-list">
                        <template v-if="allVersionList.length && curShowVersionId !== -1">
                            <li class="item">
                                <label class="bk-form-radio">
                                    <input type="radio" name="save-version-way" value="cur" v-model="saveVersionWay">
                                    <i class="bk-radio-text" style="display: inline-block; min-width: 70px;">{{$t('当前版本号')}}：{{lateShowVersionName}}</i>
                                </label>
                            </li>

                            <li class="item">
                                <label class="bk-form-radio" style="margin-right: 0;">
                                    <input type="radio" name="save-version-way" value="new" v-model="saveVersionWay">
                                    <i class="bk-radio-text" style="display: inline-block; min-width: 70px;">{{$t('新版本')}}：</i>
                                    <input type="text" class="bk-form-input" :placeholder="$t('请输入版本号')" @focus="saveVersionWay = 'new'" style="display: inline-block; width: 176px;" v-model="versionKeyword" />
                                </label>
                            </li>

                            <li class="item" v-if="withoutCurVersionList.length">
                                <label class="bk-form-radio" style="margin-right: 0;">
                                    <input type="radio" name="save-version-way" value="old" v-model="saveVersionWay">
                                    <i class="bk-radio-text" style="display: inline-block; min-width: 70px;">{{$t('其它版本')}}：</i>
                                    <bk-selector
                                        style="width: 176px;"
                                        :placeholder="$t('请选择版本号')"
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
                                    <i class="bk-radio-text">{{$t('新版本')}}：</i>
                                    <input type="text" class="bk-form-input" :placeholder="$t('请输入版本号')" @focus="saveVersionWay = 'new'" style="display: inline-block; width: 217px;" v-model="versionKeyword" />
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
                            {{$t('保存中...')}}
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            {{$t('取消')}}
                        </button>
                    </template>
                    <template v-else>
                        <template v-if="!canVersionSave">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled" style="background-color: #fafafa; border-color: #e6e6e6; color: #ccc;">
                                {{$t('确定')}}
                            </button>
                        </template>
                        <template v-else>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="saveVersion(0)">
                                {{$t('确定')}}
                            </button>
                        </template>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideVersionBox">
                            {{$t('取消')}}
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
                            <th>{{$t('版本号')}}</th>
                            <th>{{$t('更新时间')}}</th>
                            <th>{{$t('最后更新人')}}</th>
                            <th style="width: 128px;">{{$t('操作')}}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-if="versionList.length">
                            <tr v-for="versionData in versionList" :key="versionData.show_version_id">
                                <td>
                                    <span>{{versionData.name}}</span>
                                    <span v-if="versionData.show_version_id === curShowVersionId">{{$t('(当前)')}}</span>
                                </td>
                                <td>{{versionData.updated}}</td>
                                <td>{{versionData.updator}}</td>
                                <td>
                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="getTemplateByVersion(versionData.show_version_id)">{{$t('加载')}}</a>
                                    <!-- 只有一个版本时不能删除 -->
                                    <template v-if="versionList.length <= 1">
                                        <bk-tooltip :delay="300" placement="right">
                                            <a href="javascript:void(0);" class="bk-text-button is-disabled ml5" disabled>{{$t('删除')}}</a>
                                            <template slot="content">
                                                <p class="biz-permission-tip">
                                                    {{$t('必须保留至少一个版本')}}
                                                </p>
                                            </template>
                                        </bk-tooltip>
                                    </template>
                                    <template v-else>
                                        <!-- 有编辑权限 -->
                                        <template v-if="curTemplate.permissions.edit">
                                            <template v-if="!templateLockStatus.isLocked || (templateLockStatus.isLocked && templateLockStatus.isCurLocker)">
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="removeVersion(versionData)">{{$t('删除')}}</a>
                                            </template>
                                            <template v-else>
                                                <bk-tooltip :delay="300" placement="right">
                                                    <a href="javascript:void(0);" class="bk-text-button is-disabled ml5" disabled>{{$t('删除')}}</a>
                                                    <template slot="content">
                                                        <p class="biz-permission-tip">
                                                            {{$t('{locker}正在操作，您如需编辑请联系{locker}解锁！', templateLockStatus)}}
                                                        </p>
                                                    </template>
                                                </bk-tooltip>
                                            </template>
                                        </template>
                                        <template v-else>
                                            <bk-tooltip :delay="300" placement="top">
                                                <a href="javascript:void(0);" class="bk-text-button is-disabled" disabled>{{$t('删除')}}</a>
                                                <template slot="content">
                                                    <p class="biz-permission-tip">
                                                        {{$t('无权限，请去')}}<a :href="createApplyPermUrl({
                                                            policy: 'edit',
                                                            projectCode: projectCode,
                                                            idx: 'templates'
                                                        })" class="biz-link" target="_blank">{{$t('申请')}}</a>
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
                                            <p class="message empty-message" style="margin: 30px;">{{$t('无数据')}}</p>
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
    import JSZip from 'jszip'
    import { saveAs } from 'file-saver'
    import { Archive } from 'libarchive.js/main.js'

    Archive.init({
        workerUrl: `${window.STATIC_URL}${window.VERSION_STATIC_URL}/archive-worker/worker-bundle.js`
    })

    export default {
        mixins: [applyPerm],
        data () {
            return {
                saveVersionWay: 'cur',
                isEditName: false,
                isEditDesc: false,
                isCreating: false,
                linkAppList: [],
                editTemplate: {
                    name: '',
                    desc: ''
                },
                isTemplateLocking: false,
                isVersionListLoading: true,
                exceptionCode: null,
                versionSidePanel: {
                    isShow: false,
                    title: this.$t('版本列表')
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
                selectedVersion: '',
                fileImportIndex: 0,
                zipTooltipText: this.$t('请选择zip压缩包导入，包中的文件名以.yaml结尾。其中的yaml文件(非"_常用Manifest"目录下的文件)将会统一导入到自定义Manifest分类下。注意：同名文件会被覆盖')
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
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
                    const ingresss = this.ingresss
                    const HPAs = this.HPAs

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

                    for (const ingress of ingresss) {
                        if (ingress.isEdited) {
                            return true
                        }
                    }

                    for (const HPA of HPAs) {
                        if (HPA.isEdited) {
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
            ingresss () {
                return this.$store.state.mesosTemplate.ingresss
            },
            HPAs () {
                return this.$store.state.mesosTemplate.HPAs
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
                this.ingresss.forEach(item => {
                    if (item.isEdited) {
                        isEdited = true
                    }
                })
                this.HPAs.forEach(item => {
                    if (item.isEdited) {
                        isEdited = true
                    }
                })
                if (isEdited || this.$store.state.mesosTemplate.canTemplateBindVersion) {
                    this.$bkInfo({
                        title: this.$t('确认'),
                        content: this.$createElement('p', {
                            style: {
                                textAlign: 'center'
                            }
                        }, this.$t('模板编辑的内容未保存，确认要离开？')),
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
                    title: this.$t('确认'),
                    content: this.$createElement('p', { style: { 'text-align': 'center' } }, `${this.$t('删除版本')}：“${data.name}”`),
                    confirmFn () {
                        const projectId = self.projectId
                        const templateId = self.curTemplateId
                        const versionId = data.show_version_id
                        self.$store.dispatch('mesosTemplate/removeVersion', { projectId, templateId, versionId }).then(res => {
                            self.$bkMessage({
                                theme: 'success',
                                message: this.$t('操作成功')
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
                    title: this.$t('确定要删除此模板集？'),
                    confirmFn () {
                        self.$store.dispatch('mesosTemplate/removeTemplate', { templateId, projectId }).then(res => {
                            this.$bkMessage({
                                theme: 'success',
                                message: this.$t('删除成功')
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
                // 判断curTemplate name为空防止返回时清空当前数据解发switcher change事件
                if (this.isTemplateLocking || this.curTemplate.name === '') {
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
                        message: this.$t('加锁成功')
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
                        message: this.$t('{locker}正在操作，您如需编辑请联系{locker}解锁！', this.templateLockStatus)
                    })
                    return false
                }
                this.isTemplateLocking = true
                try {
                    await this.$store.dispatch('mesosTemplate/unlockTemplateset', { projectId, templateId })
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('解锁成功')
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
                        secret: this.secrets,
                        ingress: this.ingresss,
                        HPAs: this.HPAs
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
                            message: this.$t('保存成功')
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
                    return true
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
                                    return true
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
                                    return true
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
                                    return true
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
                                    return true
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
                                    return true
                                }
                            }
                        }
                        break

                    case 'mesosTemplatesetIngress':
                        const ingresss = this.ingresss
                        // 对ingress资源数据检测
                        for (const ingress of ingresss) {
                            if (ingress.isEdited) {
                                const isValid = await this.checkIngressData(ingress)
                                if (isValid) {
                                    const result = await this.saveIngress(ingress)
                                    if (result) {
                                        this.$store.commit('mesosTemplate/updateBindVersion', true)
                                        if (result.template_id) {
                                            this.newTemplateId = result.template_id
                                            this.$store.commit('mesosTemplate/updateCurTemplateId', result.template_id)
                                        }
                                    }
                                    return true
                                }
                            }
                        }
                        break

                    case 'mesosTemplatesetHPA':
                        const HPAs = this.HPAs
                        // 对HPA资源数据检测
                        for (const HPA of HPAs) {
                            if (HPA.isEdited) {
                                const isValid = await this.checkHPAData(HPA)
                                if (isValid) {
                                    const result = await this.saveHPA(HPA)
                                    if (result) {
                                        this.$store.commit('mesosTemplate/updateBindVersion', true)
                                        if (result.template_id) {
                                            this.newTemplateId = result.template_id
                                            this.$store.commit('mesosTemplate/updateCurTemplateId', result.template_id)
                                        }
                                    }
                                    return true
                                }
                            }
                        }
                        break
                }
            },
            async saveTemplate (event) {
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
                    this.isEditName = false
                    this.isEditDesc = false
                    return true
                }

                if (templateId && String(templateId) !== '0') {
                    try {
                        await this.$store.dispatch('mesosTemplate/updateTemplate', { projectId, templateId, data })
                        // const params = res.data
                        if (event) {
                            this.$bkMessage({
                                theme: 'success',
                                message: this.$t('模板集基础信息保存成功')
                            })
                        }
                        // this.curTemplate = params
                        this.$store.commit('mesosTemplate/updateCurTemplate', data)
                        this.isEditName = false
                        this.isEditDesc = false
                    } catch (res) {
                        const message = res.message
                        this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                        this.$bkMessage({
                            theme: 'error',
                            message: message,
                            hasCloseIcon: true,
                            delay: '3000'
                        })
                    }
                } else {
                    this.curTemplate = data
                    this.$store.commit('mesosTemplate/updateCurTemplate', data)
                    this.isEditName = false
                    this.isEditDesc = false
                }
                return true
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
                        secrets: this.secrets,
                        ingresss: this.ingresss,
                        HPAs: this.HPAs
                    }
                    this.isTemplateLoading = false
                    callback(data)
                } else if (this.curTemplateId === 0 || this.curTemplateId === '0') {
                    if (!this.curTemplate.name) {
                        const templateParams = {
                            id: 0,
                            name: this.$t('模板集_') + (+new Date()),
                            desc: this.$t('模板集描述'),
                            permissions: {
                                create: true,
                                delete: true,
                                list: true,
                                view: true,
                                edit: true,
                                use: true
                            }
                        }
                        this.$store.commit('mesosTemplate/updateCurTemplate', templateParams)
                    }
                    
                    this.isTemplateLoading = false
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
                                    msg: this.$t('当前访问的模板集不存在')
                                }
                            } else if (data.code === 403) {
                                this.exceptionCode = {
                                    code: '403',
                                    msg: this.$t('Sorry，您的权限不足!')
                                }
                            } else {
                                this.exceptionCode = {
                                    code: '403',
                                    msg: this.$t('异常')
                                }
                            }
                        } else {
                            this.exceptionCode = {
                                code: '403',
                                msg: this.$t('异常')
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
                            secrets: data.secret,
                            ingresss: data.ingress,
                            HPAs: data.hpa
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
                        secrets: this.secrets,
                        ingresss: this.ingresss,
                        HPAs: this.HPAs
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
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,63}$/
                const portNameReg = /^[a-z]{1}[a-z0-9-]{0,255}$/
                const nameReg2 = /^[a-zA-Z]{1}[a-zA-Z0-9-_]{0,29}$/
                const pathReg = /\/((?!\.)[\w\d\-./~]+)*/
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                const chineseReg = /[\u4e00-\u9fa5]+/
                let megPrefix = `"${appName}"${this.$t('中')}`

                if (appName === '') {
                    megPrefix += `${this.$t('名称')}：`
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('请输入应用名称')
                    })
                    return false
                }
                if (!nameReg1.test(appName)) {
                    megPrefix += `${this.$t('名称')}：`
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('应用名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于64个字符'),
                        delay: 8000
                    })
                    return false
                }

                if (instance === '') {
                    megPrefix += `${this.$t('实例数量')}：`
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('请输入实例数量')
                    })
                    return false
                }

                if (application.config.spec.template.spec.networkMode === 'CUSTOM' && !application.config.spec.template.spec.custom_value) {
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('网络模式的自定义值不能为空'),
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
                        megPrefix += `${this.$t('容器名称')}：`
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('名称不能为空')
                        })
                        return false
                    }

                    if (!nameReg1.test(container.name)) {
                        megPrefix += `$t('容器名称')：`
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于64个字符'),
                            delay: 8000
                        })
                        return false
                    }

                    // 检查container镜像设置
                    if (!container.image) {
                        this.$bkMessage({
                            theme: 'error',
                            delay: 5000,
                            message: megPrefix + this.$t('容器"{name}"的镜像及版本配置：请设置所属的镜像及版本', container)
                        })
                        return false
                    }

                    // 镜像凭证
                    if (container.isAddImageSecrets) {
                        if (!container.imagePullUser) {
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: megPrefix + this.$t('容器"{name}"的镜像及版本配置：请设置imagePullUser值', container)
                            })
                            return false
                        }
                        if (!container.imagePullPasswd) {
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: megPrefix + this.$t('容器"{name}"的镜像及版本配置：请设置imagePullPasswd值', container)
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
                                    message: megPrefix + this.$t('容器"{name}"的端口映射配置：名称不能为空', container)
                                })
                                return false
                            }
                            if (!portNameReg.test(item.name.replace(varReg, 'name'))) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: megPrefix + this.$t('容器"{name}"的端口映射配置：名称错误，以字母开头，只能含小写字母、数字、连字符(-)，首字母必须是字母，长度小于256个字符', container),
                                    delay: 8000
                                })
                                return false
                            }
                            if (portNameCache[item.name]) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: megPrefix + this.$t('容器"{name}"的端口映射配置：端口名称不可重复', container),
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
                                    message: megPrefix + this.$t('容器"{name}"的端口映射配置：协议不能为空', container)
                                })
                                return false
                            }
                            if (!item.containerPort) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + this.$t('容器"{name}"的端口映射配置：容器端口不能为空', container)
                                })
                                return false
                            }
                            if (parseInt(item.containerPort) < 1 || parseInt(item.containerPort) > 65535) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + this.$t('容器"{name}"的端口映射配置：容器端口范围为1-65535', container)
                                })
                                return false
                            }
                            if (item.hostPort === '') {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + this.$t('容器"{name}"的端口映射配置：主机端口不能为空', container)
                                })
                                return false
                            }
                            if (parseInt(item.hostPort) < -1 || parseInt(item.hostPort) > 65535) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + this.$t('容器"{name}"的端口映射配置：主机端口范围为0-65535', container)
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
                            message: megPrefix + this.$t('容器"{name}"的命令：启动命令不能含有中文字符', container)
                        })
                        return false
                    }

                    if (container.args_text && chineseReg.test(container.args_text)) {
                        this.$bkMessage({
                            theme: 'error',
                            delay: 5000,
                            message: megPrefix + this.$t('容器"{name}"的命令：命令参数不能含有中文字符', container)
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
                                        message: megPrefix + this.$t('容器"{name}"的挂载卷配置：挂载名不能为空', container)
                                    })
                                    return false
                                }

                                const name = item.name.replace(varReg, 'name')
                                if (!nameReg2.test(name)) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: megPrefix + this.$t('容器"{name}"的挂载卷配置：挂载名错误，只能包含：字母、数字、连字符(-)、下划线(_)，首字母必须是字母，长度小于30个字符', container),
                                        delay: 8000
                                    })
                                    return false
                                }
                                if (item.type !== 'custom' && !item.volume.hostPath) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: megPrefix + this.$t('容器"{name}"的挂载卷配置：挂载源不能为空', container),
                                        delay: 5000
                                    })
                                    return false
                                }
                                if (!item.volume.mountPath) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: megPrefix + this.$t('容器"{name}"的挂载卷配置：容器目录不能为空'),
                                        delay: 5000
                                    })
                                    return false
                                }
                                const mountPath = item.volume.mountPath.replace(varReg, '/path')
                                if (!pathReg.test(mountPath)) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: megPrefix + this.$t('容器"{name}"的挂载卷配置：容器目录不正确', container)
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
                                    message: megPrefix + this.$t('容器"{name}"的环境变量配置：键不能为空', container),
                                    delay: 5000
                                })
                                return false
                            }

                            if (env.type !== 'custom' && !env.value) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: megPrefix + this.$t('容器"{name}"的环境变量配置：值不能为空', container),
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

                    if (container.resources.limits.cpu === '' && container.resources.requests.cpu === '' && container.resources.limits.memory === '' && container.resources.requests.memory === '') {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU和内存限制必须配置', container),
                            delay: 5000
                        })
                        return false
                    }
                    if (container.resources.limits.cpu !== '') {
                        if (container.resources.limits.cpu < 0.001) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU上限不能少于0.001', container),
                                delay: 5000
                            })
                            return false
                        }
                        if (container.resources.limits.cpu > 128) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU上限不能大于128', container),
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.limits.memory === '') {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：内存上限不能为空', container),
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.requests.cpu && (container.resources.limits.cpu < container.resources.requests.cpu)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU上限不能小于下限', container),
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
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU下限不能少于0.001', container),
                                delay: 5000
                            })
                            return false
                        }
                        if (container.resources.requests.cpu > 128) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU下限不能大于128', container),
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.requests.memory === '') {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：内存下限不能为空', container),
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.limits.cpu && (container.resources.limits.cpu < container.resources.requests.cpu)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU上限不能小于下限', container),
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
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU上限不能为空', container),
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.requests.memory && (container.resources.limits.memory < container.resources.requests.memory)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：内存上限不能小于下限', container),
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
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：CPU下限不能为空', container),
                                delay: 5000
                            })
                            return false
                        }

                        if (container.resources.limits.memory && (container.resources.limits.memory < container.resources.requests.memory)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('容器"{name}"的资源限制配置：内存上限不能小于下限', container),
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
                                        message: megPrefix + this.$t('容器"{name}"的健康检查配置：端口名称不能为空', container)
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
                                        message: megPrefix + this.$t('容器"{name}"的健康检查配置：端口名称不能为空', container)
                                    })
                                    return false
                                }
                                break
                            case 'COMMAND':
                                if (!healthChecks.command.value) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: megPrefix + this.$t('容器"{name}"的健康检查配置：检查命令不能为空', container)
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
                                    message: megPrefix + this.$t('容器"{name}"的非标准日志采集配置：日志绝对路径不正确', container)
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
                        case 'TOLERATION':
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
                const volumeUsers = {}

                const containers = params.config.spec.template.spec.containers
                containers.forEach(container => {
                    volumeUsers[container.name] = {}
                    if (container.args_text && container.args_text.trim().length) {
                        container.args = container.args_text.split(' ')
                    } else {
                        container.args = []
                    }

                    // 镜像凭证
                    if (!container.isAddImageSecrets) {
                        delete container.imagePullUser
                        delete container.imagePullPasswd
                    }
                    delete container.isAddImageSecrets

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
                    container.volumes.forEach(item => {
                        const volume = item.volume
                        if (item.type !== 'custom') {
                            const userKey = `${item.type}:${item.name}:${volume.hostPath}:${volume.mountPath}`
                            volumeUsers[container.name][userKey] = volume.user.trim()
                        }
                        delete volume.user
                    })
                    params.config.webCache.volumeUsers = volumeUsers

                    // logpath
                    const paths = []
                    const logList = container.logListCache
                    logList.forEach(item => {
                        if (item.value) {
                            paths.push(item.value)
                        }
                    })
                    container.logPathList = paths

                    // healCheck
                    container.healthChecks.forEach(healthCheck => {
                        if (healthCheck.http && typeof healthCheck.http.port !== 'number') {
                            delete healthCheck.http.port
                        }
                        if (healthCheck.tcp && typeof healthCheck.tcp.port !== 'number') {
                            delete healthCheck.tcp.port
                        }
                    })
                })
                return params
            },
            saveTemplateData () {
                setTimeout(() => {
                    this.updateTemplateData()
                }, 500)
            },
            async updateTemplateData () {
                if (!this.isTemplateCanSave) {
                    return false
                }
                const applications = this.applications
                const deployments = this.deployments
                const services = this.services
                const configmaps = this.configmaps
                const secrets = this.secrets
                const ingresss = this.ingresss
                const HPAs = this.HPAs

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

                // 对ingress资源数据检测
                for (const ingress of ingresss) {
                    if (ingress.isEdited) {
                        const isValid = await this.checkIngressData(ingress)
                        if (!isValid) {
                            return false
                        }
                    }
                }

                // 对HPA资源数据检测
                for (const HPA of HPAs) {
                    if (HPA.isEdited) {
                        const isValid = await this.checkHPAData(HPA)
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

                // // 保存ingresss
                for (const ingress of ingresss) {
                    if (!ingress.isEdited) {
                        continue
                    }
                    const preId = ingress.id
                    const result = await this.saveIngress(ingress)
                    if (!result) {
                        return false
                    } else {
                        this.$emit('saveIngressSuccess', { responseData: result, resource: ingress, preId: preId })
                    }
                }

                // // 保存HPAs
                for (const HPA of HPAs) {
                    if (!HPA.isEdited) {
                        continue
                    }
                    const preId = HPA.id
                    const result = await this.saveHPA(HPA)
                    if (!result) {
                        return false
                    } else {
                        this.$emit('saveHPASuccess', { responseData: result, resource: HPA, preId: preId })
                    }
                }

                this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                await this.getVersionList()
                this.versionSidePanel.isShow = false
                this.versionDialogConf.width = this.isEn ? 450 : 400
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
                        message: this.$t('请填写1至45个字符（由字母、数字、下划线以及 - 或 . 组成）')
                    })
                    return false
                }

                for (const item of this.versionList) {
                    if (item.name === this.versionKeyword) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('版本{versionKeyword}已经存在', { versionKeyword: this.versionKeyword })
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
                        message: this.$t('保存成功'),
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
                const deploymentNameReg = /^[a-z]{1}[a-z0-9-]{0,63}$/
                let megPrefix = `"${deploymentName}"${this.$t('中')}`

                if (deploymentName === '') {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }
                if (!deploymentNameReg.test(deploymentName)) {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于64个字符'),
                        delay: 8000
                    })
                    return false
                }
                if (!appId) {
                    megPrefix += this.$t('关联：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('请关联相应的Application')
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
                        case 'ingress':
                            this.$store.commit('mesosTemplate/updateIngressById', { ingress: responseData, targetData: targetData, preId: preId })
                            break
                        case 'HPA':
                            this.$store.commit('mesosTemplate/updateHPAById', { HPA: responseData, targetData: targetData, preId: preId })
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

                const serviceNameReg = /^[a-z]{1}[a-z0-9-]{0,63}$/
                const serviceIPReg = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)($|(?!\.$)\.)){4}$/
                const pathReg = /\/((?!\.)[\w\d\-./~]+)*/
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                let megPrefix = `"${serviceName}"${this.$t('中')}`
                // if (serviceName) {
                //     megPrefix += `[${serviceName}]：`
                // } else {
                //     megPrefix += `[未命名]：`
                // }

                if (serviceName === '') {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }

                if (!serviceNameReg.test(serviceName.replace(varReg, 'service'))) {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于64个字符'),
                        delay: 8000
                    })
                    return false
                }

                if (!appId.length) {
                    megPrefix += this.$t('关联应用：')
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
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,63}$/
                const nameReg2 = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,29}$/
                const keys = configmap.configmapKeyList
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                let megPrefix = `"${configmapName}"中`

                if (configmapName === '') {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }
                if (!nameReg1.test(configmapName)) {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于64个字符'),
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
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,63}$/
                const nameReg2 = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,29}$/
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                const keys = secret.secretKeyList
                let megPrefix = `"${secretName}"中`

                if (secretName === '') {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }
                if (!nameReg1.test(secretName)) {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于64个字符'),
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
            },

            // ingress
            async createIngress (data, ingress) {
                const version = this.curVersion
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addIngress', { projectId, version, data }).then(res => {
                    const data = res.data
                    this.updateLocalData(data, ingress, 'ingress')
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
            async createFirstIngress (data, ingress) {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addFirstIngress', { projectId, templateId, data }).then(res => {
                    const data = res.data
                    this.updateLocalData(data, ingress, 'ingress')
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
            async updateIngress (data, ingress) {
                const version = this.curVersion
                const projectId = this.projectId
                const ingressId = ingress.id
                const result = await this.$store.dispatch('mesosTemplate/updateIngress', { projectId, version, data, ingressId }).then(res => {
                    const data = res.data
                    this.updateLocalData(data, ingress, 'ingress')
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
            async checkIngressData (ingress) {
                const ingressName = ingress.config.metadata.name
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,63}$/
                // const nameReg2 = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,29}$/
                // const varReg = /\{\{([^\{\}]+)?\}\}/g
                // const keys = ingress.ingressKeyList
                let megPrefix = `"${ingressName}"中`

                if (ingressName === '') {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }

                if (!nameReg1.test(ingressName)) {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于64个字符'),
                        delay: 8000
                    })
                    return false
                }

                if (!ingress.config.metadata.labels['io.tencent.bcs.clb.region']) {
                    megPrefix += this.$t('区域：')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择区域')
                    })
                    return false
                }

                if (!ingress.config.metadata.labels['bmsf.tencent.com/clbname']) {
                    megPrefix += this.$t('CLB')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择CLB')
                    })
                    return false
                }
                
                const rules = ingress.config.webCache.rules
                for (const rule of rules) {
                    if (!rule.serviceName) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的Service名称：请选择Service名称', rule),
                            delay: 8000
                        })
                        return false
                    }

                    if (!rule.serviceType) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的协议：请选择协议', rule),
                            delay: 8000
                        })
                        return false
                    }

                    if (!rule.servicePort) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的端口：请选择端口', rule),
                            delay: 8000
                        })
                        return false
                    }

                    if (!rule.clbPort) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的监听CLB端口：请输入监听CLB端口', rule),
                            delay: 8000
                        })
                        return false
                    }

                    // if (rule.sessionTime) {
                    //     this.$bkMessage({
                    //         theme: 'error',
                    //         message: megPrefix + this.$t('规则"{name}"的会话保持时间：请输入会话保持时间', rule),
                    //         delay: 8000
                    //     })
                    //     return false
                    // }
                    if (rule.sessionTime && (rule.sessionTime < 30 || rule.sessionTime > 3600)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的会话保持时间：会话保持时间范围为30-3600', rule),
                            delay: 8000
                        })
                        return false
                    }
                    if (rule.httpsEnabled && rule.tls.mode === 'mutual' && !rule.tls.certCaId) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的开启Https：如果认证模式为mutual，客户端证书ID为必填项', rule),
                            delay: 8000
                        })
                        return false
                    }
                }

                return true
            },
            async formatIngressData (ingress) {
                const params = JSON.parse(JSON.stringify(ingress))
                const spec = params.config.spec
                spec.tcp = []
                spec.udp = []
                spec.http = []
                spec.https = []
                params.config.webCache.rules.forEach(data => {
                    const rule = JSON.parse(JSON.stringify(data))
                    if (rule.sessionTime === '') {
                        delete rule.sessionTime
                    }
                    switch (rule.serviceType) {
                        case 'TCP':
                            delete rule.serviceType
                            delete rule.tls
                            delete rule.host
                            delete rule.path
                            delete rule.healthCheck.httpCode
                            delete rule.healthCheck.httpCheckPath
                            delete rule.httpsEnabled
                            spec.tcp.push(rule)
                            break

                        case 'UDP':
                            delete rule.serviceType
                            delete rule.tls
                            delete rule.host
                            delete rule.path
                            delete rule.healthCheck.httpCode
                            delete rule.healthCheck.httpCheckPath
                            delete rule.httpsEnabled
                            spec.udp.push(rule)
                            break

                        case 'HTTP':
                            delete rule.serviceType
                            if (rule.httpsEnabled) {
                                delete rule.httpsEnabled
                                spec.https.push(rule)
                            } else {
                                delete rule.httpsEnabled
                                delete rule.tls
                                spec.http.push(rule)
                            }
                            break
                    }
                })

                // 添加versionId，用于后续的网络ingress编辑时获取
                params.config.metadata.labels['io.tencent.bcs.latest.version.id'] = String(this.curTemplate.latest_version_id)

                delete params.isEdited
                delete params.cache
                return params
            },
            async saveIngress (ingress) {
                const data = await this.formatIngressData(ingress)
                let result
                if (this.curVersion) {
                    if (ingress.id.indexOf && (ingress.id.indexOf('local') > -1)) {
                        result = this.createIngress(data, ingress)
                    } else {
                        result = this.updateIngress(data, ingress)
                    }
                } else {
                    result = this.createFirstIngress(data, ingress)
                }
                return result
            },
            // ingress

            async saveHPA (HPA) {
                let result
                const data = await this.formatHPAData(HPA)

                if (this.curVersion) {
                    if (HPA.id.indexOf && (HPA.id.indexOf('local') > -1)) {
                        result = await this.createHPA(data, HPA)
                    } else {
                        result = await this.updateHPA(data, HPA)
                    }
                } else {
                    result = await this.createFirstHPA(data, HPA)
                }
                return result
            },
            async checkHPAData (HPA) {
                const HPAName = HPA.config.metadata.name
                const nameReg = /^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$/
                let megPrefix = `"${HPAName}"中`

                if (HPAName === '') {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }

                if (!nameReg.test(HPAName)) {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '名称错误，以小写字母或数字开头和结尾，只能包含：小写字母、数字、连字符(-)、点(.)',
                        delay: 5000
                    })
                    return false
                }

                if (!HPA.config.spec.scaleTargetRef.name) {
                    megPrefix += this.$t('关联应用：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('请先关联应用'),
                        delay: 5000
                    })
                    return false
                }

                if (HPA.config.spec.minInstance === '') {
                    megPrefix += this.$t('实例数范围：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('最小实例数不能为空'),
                        delay: 5000
                    })
                    return false
                }

                if (HPA.config.spec.maxInstance === '') {
                    megPrefix += this.$t('实例数范围：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('最大实例数不能为空'),
                        delay: 5000
                    })
                    return false
                }

                if (HPA.config.spec.maxInstance < HPA.config.spec.minInstance) {
                    megPrefix += this.$t('实例数范围：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('最大实例数不能小于最小实例数'),
                        delay: 5000
                    })
                    return false
                }

                if (HPA.config.spec.metrics.length) {
                    for (const metric of HPA.config.spec.metrics) {
                        if (!metric.name) {
                            megPrefix += this.$t('扩缩容触发条件：')
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + '请选择资源类型！',
                                delay: 5000
                            })
                            return false
                        }

                        if (metric.name && !metric.target.averageUtilization) {
                            megPrefix += this.$t('扩缩容触发条件：')
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('资源目标不能为空'),
                                delay: 5000
                            })
                            return false
                        }
                    }
                }

                return true
            },
            async formatHPAData (HPA) {
                const params = JSON.parse(JSON.stringify(HPA))
                params.template = {
                    name: this.curTemplate.name,
                    desc: this.curTemplate.desc
                }
                delete params.isEdited
                delete params.cache
                return params
            },
            async createHPA (data, HPA) {
                const version = this.curVersion
                const projectId = this.projectId
                const result = this.$store.dispatch('mesosTemplate/addHPA', { projectId, version, data }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, HPA, 'HPA')
                    return responseData
                }, res => {
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: res.message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async updateHPA (data, HPA) {
                const version = this.curVersion
                const projectId = this.projectId
                const HPAId = data.id
                const result = this.$store.dispatch('mesosTemplate/updateHPA', { projectId, version, data, HPAId }).then(res => {
                    const data = res.data
                    this.updateLocalData(data, HPA, 'HPA')
                    this.isDataSaveing = false
                    return data
                }, res => {
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: res.message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },
            async createFirstHPA (data, HPA) {
                const templateId = this.curTemplateId
                const projectId = this.projectId
                const result = await this.$store.dispatch('mesosTemplate/addFirstHPA', { projectId, templateId, data }).then(res => {
                    const responseData = res.data
                    this.updateLocalData(responseData, HPA, 'HPA')
                    this.isDataSaveing = false
                    return data
                }, res => {
                    this.$store.commit('mesosTemplate/updateIsTemplateSaving', false)
                    this.$bkMessage({
                        theme: 'error',
                        message: res.message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
                return result
            },

            async handleFileInput () {
                const fileInput = this.$refs.fileInput
                if (fileInput.files && fileInput.files.length) {
                    try {
                        const file = fileInput.files[0]
                        const archive = await Archive.open(file)
                        const zipFile = await archive.extractFiles()
                        if (zipFile) {
                            this.importFileList = []
                            this.getImportFileList(zipFile)
                            this.renderJsonFile()
                            this.fileImportIndex++
                        }
                    } catch (e) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('请选择合适的压缩包')
                        })
                    }
                }
            },

            getImportFileList (zip, folderName = '') {
                for (const key in zip) {
                    const file = zip[key]
                    // 文件
                    if (file.name) {
                        this.importFileList.push(file)
                    } else {
                        this.getImportFileList(file, key)
                    }
                }
            },

            async renderJsonFile () {
                const promiseList = []
                const self = this
                this.importFileList.forEach(file => {
                    if (file.name.endsWith('.json')) {
                        promiseList.push(() => {
                            return new Promise((resolve, reject) => {
                                const reader = new FileReader()
                                reader.onloadend = async function (event) {
                                    if (event.target.readyState === FileReader.DONE) {
                                        const content = event.target.result
                                        const fileMetadata = file.name.split('--')
                                        const fileType = fileMetadata[0]
                                        const fileName = fileMetadata[1].replace('.json', '')
                                        self.importFile(fileName, fileType, content, resolve, reject)
                                    }
                                }
                                reader.readAsText(file)
                            })
                        })
                    }
                })

                // 上一个完成才可执行下一个
                let promiseIndex = 0
                while (promiseIndex >= 0 && promiseIndex < promiseList.length) {
                    await promiseList[promiseIndex]()
                    promiseIndex++
                }
                self.$bkMessage({
                    theme: 'success',
                    message: self.$t('导入成功')
                })
                // Promise.all(promiseList).then(() => {
                    
                // }).catch(() => {
                //     self.$bkMessage({
                //         theme: 'error',
                //         message: self.$t('请输入系统导出的包进行导入操作')
                //     })
                // })
            },

            async importFile (fileName, fileType, content, resolve, reject) {
                if (this[fileType]) {
                    let app = JSON.parse(content)
                    // 处理属性
                    const now = +new Date()
                    app.id = `local_${now}`
                    app.isEdited = true

                    // 处理关联
                    // 如果是application，需要先保存才可让deployment、service绑定
                    if (fileType === 'applications') {
                        await this.saveApplication(app)
                        const projectId = this.projectId
                        const version = this.curVersion
                        const res = await this.$store.dispatch('mesosTemplate/getApplicationsByVersion', { projectId, version })
                        this.linkAppList = res.data
                    } else if (fileType === 'deployments' || fileType === 'services') {
                        this.linkAppList.forEach(linkApp => {
                            const appName = linkApp.app_name
                            const reg = new RegExp(`<%${appName}%>`, 'g')
                            content = content.replace(reg, linkApp.app_id)
                        })
                        app = JSON.parse(content)
                    }

                    // 处理同名问题
                    const resources = this[fileType]
                    const matchIndex = resources.findIndex(item => {
                        return item.config.metadata.name === fileName
                    })
                    if (matchIndex > -1) {
                        resources.splice(matchIndex, 1, app)
                    } else {
                        resources.push(app)
                    }
                    resolve(true)
                    // 处理关联
                    // if (folderName === 'applications') {
                    //     await self.autoSaveResource('mesosTemplatesetApplication')
                    // }
                } else {
                    reject(false)
                }
            },

            formatDeploymentData (data) {
                return data
            },

            async formatExportData (data, type, linkAppList) {
                const formatMap = {
                    applications: 'formatApplicationData',
                    deployments: 'formatDeploymentData',
                    services: 'formatServiceData',
                    configmaps: 'formatConfigmapData',
                    secrets: 'formatSecretData',
                    ingresss: 'formatIngressData'
                }
                if (formatMap[type]) {
                    const resource = await this[formatMap[type]](data)
                    let content = JSON.stringify(resource, null, 4)
                    linkAppList.forEach(app => {
                        const appId = app.app_id
                        const reg = new RegExp(`${appId}`, 'g')
                        content = content.replace(reg, `<%${app.app_name}%>`)
                    })
                    return content
                }
                return ''
            },

            async handleExport () {
                const projectId = this.projectId
                const version = this.curVersion
                const res = await this.$store.dispatch('mesosTemplate/getApplicationsByVersion', { projectId, version })
                const linkAppList = res.data
                const zip = new JSZip()
                const resources = [
                    'applications',
                    'deployments',
                    'services',
                    'configmaps',
                    'secrets',
                    'ingresss'
                ]
                const rootFolderName = `${this.curTemplate.name || 'mesos'}_${this.curTemplate.latest_show_version}`
                const rootFolder = zip.folder(rootFolderName)
                resources.forEach(resourceKey => {
                    if (this[resourceKey] && this[resourceKey].length) {
                        this[resourceKey].forEach(resource => {
                            // 用_开头表示是通过内部导出的文件
                            const fileName = `${resourceKey}--${resource.name || resource.config.metadata.name || '未命名'}.json`
                            const fileContent = this.formatExportData(resource, resourceKey, linkAppList)
                            rootFolder.file(fileName, fileContent, { binary: false })
                        })
                    }
                })
                zip.generateAsync({ type: 'blob' }).then((content) => {
                    saveAs(content, `${rootFolderName}.zip`)
                })
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '@open/css/mixins/scroller.css';
    @import '@open/css/mixins/ellipsis.css';

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

    .biz-import-btn {
        position: relative;
        max-width: 90px;
        overflow: hidden;

        input[type=file] {
            position: absolute;
            width: 100%;
            height: 100%;
            left: 0;
            right: 0;
            top: 0;
            bottom: 0;
            margin: auto;
            cursor: pointer;
            opacity: 0;
        }
    }
</style>
