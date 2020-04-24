<template>
    <div class="biz-content">
        <section class="biz-top-bar" :style="{ marginBottom: isNewTemplate ? '0px' : '70px' }">
            <i class="biz-back bk-icon icon-arrows-left" @click="handleBeforeLeave"></i>
            <div class="biz-templateset-title">
                <span v-show="!isEditName">{{curTemplate.name}}</span>
                <input
                    type="text"
                    :placeholder="$t('30个以内的字符')"
                    maxlength="30"
                    class="bk-form-input"
                    v-model="editTemplate.name"
                    v-if="isEditName"
                    ref="templateNameInput"
                    @blur="saveTemplate"
                    @keyup.enter="saveTemplate" />
                <a href="javascript:void(0)" class="bk-text-button bk-default" v-show="!isEditName" @click="editTemplateName">
                    <i class="bk-icon icon-edit"></i>
                </a>
            </div>
            <div class="biz-templateset-desc">
                <span v-show="!isEditDesc">{{curTemplate.desc}}</span>
                <input
                    type="text"
                    :placeholder="$t('50个以内的字符')"
                    maxlength="50"
                    class="bk-form-input"
                    v-model="editTemplate.desc"
                    v-if="isEditDesc"
                    ref="templateDescInput"
                    @blur="saveTemplate"
                    @keyup.enter="saveTemplate" />
                <a href="javascript:void(0)" class="bk-text-button bk-default" v-show="!isEditDesc" @click="editTemplateDesc" @keyup.enter="saveTemplate">
                    <i class="bk-icon icon-edit"></i>
                </a>
            </div>
            <div class="biz-templateset-action">
                <!-- 如果不是新增状态的模板集并且有权限编辑才可查看加锁状态 -->
                <template v-if="String(templateId) !== '0'">
                    <template v-if="templateLockStatus.isLocked">
                        <template v-if="templateLockStatus.isCurLocker">
                            <div class="biz-lock-box">
                                <div class="lock-wrapper warning">
                                    <i class="bk-icon icon-info-circle-shape"></i>
                                    <strong class="desc">
                                        {{$t('您已经对此模板集加锁，只有解锁后，其他用户才可操作此模板集。')}}
                                        <span v-if="lateShowVersionName">（{{$t('当前版本号')}}：{{lateShowVersionName}}）</span>
                                    </strong>
                                    <div class="action" @click="updateTemplateLockStatus">
                                        <bk-switcher
                                            :selected="templateLockStatus.isLocked"
                                            size="small">
                                        </bk-switcher>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <div class="biz-lock-box">
                                <div class="lock-wrapper warning">
                                    <i class="bk-icon icon-info-circle-shape"></i>
                                    <strong class="desc">
                                        {{$t('{locker}正在操作，您如需编辑请联系{locker}解锁。', templateLockStatus)}}
                                        <span v-if="lateShowVersionName">（{{$t('当前版本号')}}：{{lateShowVersionName}}）</span>
                                    </strong>
                                    <div class="action">
                                        <a href="javascript: void(0);" class="bk-text-button" @click="reloadTemplateLockStatus">{{$t('点击刷新')}}</a>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </template>
                    <template v-else>
                        <div class="biz-lock-box">
                            <div class="lock-wrapper">
                                <i class="bk-icon icon-info-circle-shape"></i>
                                <strong class="desc">
                                    {{$t('为避免多成员同时编辑，引起内容或版本冲突，建议在编辑时，开启保护功能。')}}
                                    <span v-if="lateShowVersionName">（{{$t('当前版本号')}}：{{lateShowVersionName}}）</span>
                                </strong>
                                <div class="action" @click="updateTemplateLockStatus">
                                    <bk-switcher
                                        :selected="templateLockStatus.isLocked"
                                        size="small">
                                    </bk-switcher>
                                </div>
                            </div>
                        </div>
                    </template>
                </template>

                <!-- 如果模板集没有加锁或者当前用户是加锁者才可以操作 -->
                <template v-if="templateLockStatus.isLocked && !templateLockStatus.isCurLocker">
                    <button href="javascript:void(0)" class="bk-button bk-primary" disabled>{{$t('保存')}}</button>
                </template>
                <template v-else>
                    <button class="bk-button bk-primary" :disabled="!canTemplateSave" @click="handleSaveTemplate">{{$t('保存')}}</button>
                </template>
                
                <button class="bk-button bk-default" :disabled="templateId === 0" @click="createInstance">
                    {{$t('实例化')}}
                </button>

                <button class="bk-button bk-default" :disabled="!allVersionList.length" @click="showVersionPanel">{{$t('版本列表')}}</button>
            </div>
        </section>

        <p class="biz-tip m20 mb15">
            {{$t('YAML中资源所属的命名空间不需要用户指定，由平台根据用户实例化时的选择自动生成')}}
        </p>

        <section class="biz-yaml-content" v-bkloading="{ isLoading: isYamlTemplateLoading || isTemplateLocking, opacity: 0.3 }">
            <div class="biz-yaml-resources">
                <ul class="yaml-tab">
                    <li :class="{ 'active': tabName === 'default' }" @click="handleToggleTab('default')">
                        {{$t('常用Manifest')}}
                    </li>
                    <li :class="{ 'active': tabName === 'custom' }" @click="handleToggleTab('custom')">
                        {{$t('自定义Manifest')}}
                    </li>
                </ul>
                <ul class="resources-tree">
                    <li class="group" v-for="resource of curTemplateFiles" :key="resource.resource_name">
                        <div :class="['group-header', { 'has-file': resource.files.filter(file => file.action !== 'delete').length }]" @click="handleToggleResource(resource)">
                            <strong class="title">
                                {{resource.resource_name}}
                                <span class="badge">({{resource.files.filter(file => file.action !== 'delete').length}})</span>
                            </strong>
                            <i class="bk-icon icon-plus" @click.stop.prevent="handleAddFile(resource)"></i>
                        </div>

                        <collapse-transition :key="resource.files.length">
                            <ul class="group-content" v-show="resource.actived">
                                <template v-for="(file, index) of resource.files">
                                    <template v-if="file.action !== 'delete'">
                                        <li :class="{ 'active': curResourceFile.id === file.id }" :key="file.id" v-if="!file.isEdited" @click="handleSelectFile(resource, file)">
                                            <span class="title" :title="file.name">{{file.name}}</span>
                                            <i class="edit-dot" v-bktooltips.top="'文件有更新'" v-show="file.content !== file.originContent"></i>
                                            <i class="bk-icon icon-close" @click.stop.prevent="handleRemoveFile(resource, file, index)"></i>
                                        </li>
                                        <li :key="file.id" v-else>
                                            <input
                                                type="text"
                                                v-model="addFileNameTmp"
                                                ref="fileNameInput"
                                                class="bk-form-input"
                                                maxlength="64"
                                                :placeholder="$t('请输入')"
                                                @blur="handleFileBlur(resource, file)"
                                                @keyup.enter="handleFileEnter(resource, file)">
                                        </li>
                                    </template>
                                </template>
                            </ul>
                        </collapse-transition>
                    </li>
                </ul>
            </div>
            <div class="biz-yaml-editor">
                <div class="yaml-header">
                    <template v-if="isEditFileName">
                        <input
                            type="text"
                            v-model="editFileNameTmp"
                            style="width: 300px;"
                            ref="resourceFileNameInput"
                            maxlength="64"
                            class="bk-form-input resource-file-input"
                            :placeholder="$t('请输入')"
                            @blur="handleEditNameBlur"
                            @keyup.enter="handleEditNameEnter">
                        <a href="javascript: void(0);" class="bk-text-button f12 ml10">确定</a>
                        <a href="javascript: void(0);" class="bk-text-button f12 ml5" @click="isEditFileName = false">取消</a>
                    </template>
                    <template v-else>
                        <strong class="title" v-show="curResourceFile.name">
                            {{curResourceFile.name}}
                            <a href="javascript:void(0)" class="bk-text-button bk-default ml5" @click="handleEditFileName">
                                <i class="bk-icon icon-edit"></i>
                            </a>
                        </strong>
                    </template>
                    
                    <div class="yaml-header-action">
                        <button
                            v-if="curResourceFile.content !== curResourceFile.originContent || useEditorDiff"
                            class="biz-template-btn"
                            @click="toggleCompare">
                            {{ useEditorDiff ? $t('返回编辑') : $t('修改对比') }}
                        </button>
                        <button class="biz-template-btn" @click.stop.prevent="handleToggleVarPanel">{{$t('变量列表')}}</button>
                        <button class="biz-template-btn" @click.stop.prevent="handleToggleImagePanel">{{$t('镜像查询')}}</button>
                    </div>
                </div>
                <div class="yaml-content">
                    <template v-if="curResourceFile.id">
                        <monaco-editor
                            ref="yamlEditor"
                            class="editor"
                            theme="monokai"
                            language="yaml"
                            :style="{ height: `${editorHeight}px`, width: '100%' }"
                            v-model="curResourceFile.content"
                            :diff-editor="useEditorDiff"
                            :options="yamlEditorOptions"
                            :key="reRenderEditor"
                            :original="curResourceFile.originContent"
                            @mounted="handleEditorMount">
                        </monaco-editor>
                    </template>
                    <template v-else>
                        <div class="biz-editor-tip" v-if="!isYamlTemplateLoading">
                            <i class="bk-icon icon-edit2"></i>
                            <p>{{$t('请选择需要编辑的资源文件')}}</p>
                        </div>
                    </template>

                    <div :class="['biz-var-panel', { 'show': isVarPanelShow }]" v-clickoutside="hideVarPanel">
                        <div class="var-panel-header">
                            <strong class="var-panel-title">{{$t('可用变量')}}<span class="f12">（{{$t('模板集中引入方式')}}：{{varUserWay}}）</span></strong>
                        </div>
                        <div class="var-panel-list">
                            <table class="bk-table biz-var-table">
                                <thead>
                                    <tr>
                                        <th>{{$t('变量名')}}</th>
                                        <th style="width: 230px;">KEY</th>
                                        <th style="width: 43px;"></th>
                                    </tr>
                                </thead>
                            </table>
                            <div class="var-list">
                                <table class="bk-table biz-var-table">
                                    <tbody>
                                        <template v-if="varList.length">
                                            <tr v-for="item of varList" :key="item.name">
                                                <td>
                                                    <bk-tooltip :content="item.name" placement="right">
                                                        <span class="var-name">{{item.name}}</span>
                                                    </bk-tooltip>
                                                </td>
                                                <td style="width: 230px;">
                                                    <bk-tooltip :content="item.key" placement="right">
                                                        <span class="var-key">{{item.key}}</span>
                                                    </bk-tooltip>
                                                </td>
                                                <td style="width: 43px;">
                                                    <button class="var-copy-btn" :data-clipboard-text="`{{${item.key}}}`" type="default">
                                                        <i class="bk-icon icon-clipboard"></i>
                                                    </button>
                                                </td>
                                            </tr>
                                        </template>
                                        <template v-else>
                                            <tr>
                                                <td colspan="3">
                                                    <p class="message empty-message">{{$t('无数据')}}</p>
                                                </td>
                                            </tr>
                                        </template>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <div :class="['biz-image-content', { 'show': isImagePanelShow }]" v-clickoutside="hideImagePanel">
                        <div class="biz-image-list" style="width: 600px;">
                            <div class="bk-dropdown-box ml20 mb20" style="width: 300px;">
                                <bk-input
                                    style="width: 250px;"
                                    type="text"
                                    :placeholder="$t('选择镜像')"
                                    :display-key="'_name'"
                                    :setting-key="'_id'"
                                    :search-key="'_name'"
                                    :value.sync="imageName"
                                    :list="varList"
                                    :is-link="true"
                                    :is-select-mode="true"
                                    :default-list="imageList"
                                    @item-selected="changeImage(...arguments)">
                                </bk-input>
                                <button class="bk-button bk-default is-outline is-icon" @click="initImageList">
                                    <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-default" style="margin-top: -3px;" v-if="isLoadingImageList">
                                        <div class="rotate rotate1"></div>
                                        <div class="rotate rotate2"></div>
                                        <div class="rotate rotate3"></div>
                                        <div class="rotate rotate4"></div>
                                        <div class="rotate rotate5"></div>
                                        <div class="rotate rotate6"></div>
                                        <div class="rotate rotate7"></div>
                                        <div class="rotate rotate8"></div>
                                    </div>
                                    <i class="bk-icon icon-refresh" v-else></i>
                                </button>
                            </div>

                            <div class="bk-dropdown-box mb20" style="width: 250px;">
                                <bk-input
                                    type="text"
                                    :placeholder="$t('版本号1')"
                                    :display-key="'_name'"
                                    :setting-key="'_id'"
                                    :search-key="'_name'"
                                    :value.sync="imageVersion"
                                    :list="varList"
                                    :is-select-mode="true"
                                    :default-list="imageVersionList"
                                    :disabled="!imageName"
                                    @item-selected="setImageVersion"
                                >
                                </bk-input>
                            </div>

                            <div class="image-box" v-show="image">
                                <input type="text" class="bk-form-input" readonly :value="image" style="width: 482px;">
                                <button class="bk-button bk-primary image-copy-btn" :data-clipboard-text="`${image}`">{{$t('复制')}}</button>
                            </div>
                        </div>
                        <p class="biz-tip">
                            {{$t('使用指南：请将镜像复制后填入所使用的YAML中')}}
                        </p>
                    </div>
                </div>
            </div>
        </section>
        <bk-dialog
            :is-show.sync="versionDialogConf.isShow"
            :width="isEn ? 450 : 400"
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
                                    <i class="bk-radio-text" style="display: inline-block; min-width: 70px;">{{$t('当前版本：')}}{{curShowVersionName}}</i>
                                </label>
                            </li>

                            <li class="item">
                                <label class="bk-form-radio" style="margin-right: 0;">
                                    <input type="radio" name="save-version-way" value="new" v-model="saveVersionWay">
                                    <i class="bk-radio-text" style="display: inline-block; min-width: 70px;">{{$t('新建版本')}}：</i>
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
                                        :list="withoutCurVersionList">
                                    </bk-selector>
                                </label>
                            </li>
                        </template>
                        <template v-else>
                            <li class="item">
                                <label class="bk-form-radio" style="margin-right: 0;">
                                    <i class="bk-radio-text">{{$t('新版本')}}：</i>
                                    <input type="text"
                                        class="bk-form-input"
                                        ref="versionInput"
                                        maxlength="45"
                                        :placeholder="$t('请输入版本号')"
                                        @focus="saveVersionWay = 'new'"
                                        style="display: inline-block; width: 217px;"
                                        v-model="versionKeyword" />
                                </label>
                            </li>
                        </template>
                    </ul>
                </div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isTemplateSaving">
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
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="saveYamlTemplate">
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
                        <template v-if="allVersionList.length">
                            <tr v-for="(versionData, index) in allVersionList" :key="index">
                                <td>
                                    <span>{{versionData.name}}</span>
                                    <span v-if="versionData.show_version_id === curShowVersionId">{{$t('(当前)')}}</span>
                                </td>
                                <td>{{versionData.updated}}</td>
                                <td>{{versionData.updator}}</td>
                                <td>
                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="getTemplateByVersion(versionData.show_version_id)">{{$t('加载')}}</a>
                                    <!-- 只有一个版本时不能删除 -->
                                    <!-- <template v-if="allVersionList.length <= 1">
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
                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="removeVersion(versionData)">删除</a>
                                    </template> -->
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
    import yamljs from 'js-yaml'
    import MonacoEditor from './editor.js'
    import CollapseTransition from '@open/components/menu/collapse-transition'
    import { catchErrorHandler } from '@open/common/util'
    import Clipboard from 'clipboard'
    import clickoutside from '@open/directives/clickoutside'
    // import FileInputer from './inputer.vue'

    export default {
        components: {
            MonacoEditor,
            CollapseTransition
            // FileInputer
        },
        directives: {
            clickoutside
        },
        data () {
            return {
                isEditName: false,
                isEditDesc: false,
                isTemplateSaving: false,
                isVersionListLoading: true,
                isLoadingImageList: false,
                isTemplateLocking: false,
                isVarPanelShow: false,
                isImagePanelShow: false,
                isEditFileName: false,
                // canTemplateSave: false,
                useEditorDiff: false,
                winHeight: 500,
                isYamlTemplateLoading: true,
                reRenderEditor: 0,
                curTemplate: {
                    name: '',
                    desc: '',
                    show_version: {
                        name: ''
                    },
                    template_files: []
                },
                saveVersionWay: 'cur',
                selectedVersion: '',
                versionSidePanel: {
                    isShow: false,
                    title: this.$t('版本列表')
                },
                imageList: [],
                imageVersionList: [],
                curImageData: {},
                imageName: '',
                imageVersion: '',
                image: '',
                varUserWay: this.$t('{{变量KEY}}'),
                editorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'yaml',
                    readOnly: false,
                    fullScreen: false,
                    value: '',
                    editor: null
                },
                addFileNameTmp: '',
                editFileNameTmp: '',
                curResource: {
                    files: []
                },
                curResourceFile: {
                    id: 0,
                    name: '',
                    content: '',
                    originContent: ''
                },
                editTemplate: {
                    name: '',
                    desc: ''
                },
                versionDialogConf: {
                    isShow: false,
                    closeIcon: false
                },
                versionKeyword: '',
                yamlEditorOptions: {
                    readOnly: true,
                    fontSize: 14
                },
                yamlResourceConf: null,
                yamlTemplateJson: null,
                tabName: 'default'
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            curProject () {
                return this.$store.state.curProject
            },
            templateId () {
                return Number(this.$route.params.templateId)
            },
            isNewTemplate () {
                return this.templateId === 0
            },
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            editorHeight () {
                // 由于则导航的高度最小为630，导致整个页面的高度最不为630
                const height = this.winHeight - 260
                return height < 630 ? 630 : height
            },
            varList () {
                const list = this.$store.state.variable.varList
                list.forEach(item => {
                    item._id = item.key
                    item._name = item.key
                })
                return list
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
            canVersionSave () {
                if (this.saveVersionWay === 'cur' && this.curShowVersionId) {
                    return true
                } else if (this.saveVersionWay === 'old' && this.selectedVersion) {
                    return true
                } else if (this.saveVersionWay === 'new' && this.versionKeyword) {
                    return true
                }
                return false
            },
            curShowVersionId () {
                return this.curTemplate.show_version.show_version_id
            },
            curShowVersionName () {
                return this.curTemplate.show_version.name
            },
            allVersionList () {
                return this.$store.state.k8sTemplate.versionList
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
            withoutCurVersionList () {
                // 去掉当前版本
                return this.$store.state.k8sTemplate.versionList.filter(item => {
                    return item.show_version_id !== this.curShowVersionId
                })
            },
            defaultTemplateFiles () {
                return this.curTemplate.template_files.filter(item => {
                    return item.resource_name !== 'CustomManifest'
                })
            },
            customTemplateFiles () {
                return this.curTemplate.template_files.filter(item => {
                    return item.resource_name === 'CustomManifest'
                })
            },
            canTemplateSave () {
                if (!this.curTemplate.id) {
                    const resource = this.curTemplate.template_files.find(item => {
                        return item.files.length
                    })
                    return resource
                }
                return true
            },
            curTemplateFiles () {
                if (this.tabName === 'default') {
                    return this.defaultTemplateFiles
                } else {
                    return this.customTemplateFiles
                }
            }
        },

        watch: {
            useEditorDiff () {
                this.reRenderEditor++
            },
            editorHeight () {
                this.reRenderEditor++
            },
            'curResourceFile.id' () {
                this.reRenderEditor++
            },
            varList () {
                if (this.clipboardVarInstance && this.clipboardVarInstance.off) {
                    this.clipboardVarInstance.off('success')
                }
                this.clipboardVarInstance = new Clipboard('.var-copy-btn')
                this.clipboardVarInstance.on('success', e => {
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('复制成功')
                    })
                    this.isVarPanelShow = false
                })
            },
            image () {
                if (this.clipboardImageInstance && this.clipboardImageInstance.off) {
                    this.clipboardImageInstance.off('success')
                }

                this.clipboardImageInstance = new Clipboard('.image-copy-btn')
                this.clipboardImageInstance.on('success', e => {
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('复制成功')
                    })
                    this.isImagePanelShow = false
                })
            }
        },

        async created () {
            this.isYamlTemplateLoading = true
            await this.initYamlResources()
            this.initVarList()
            this.initTemplate()
            this.initImageList()
        },

        mounted () {
            if (this.curProject.kind === PROJECT_MESOS) {
                this.$router.push({
                    name: 'templateset',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
                return false
            }
            this.winHeight = window.innerHeight

            const debounce = this.debounce(() => {
                this.winHeight = window.innerHeight
                this.reRenderEditor++
            }, 200)

            window.addEventListener('resize', () => {
                debounce()
            })
            // window.addEventListener('change::$currentProjectId', async e => {
            //     this.isProjectChange = true
            //     this.goTemplateIndex()
            // })
        },

        beforeRouteLeave (to, from, next) {
            let isEdited = false
            const changeActions = ['create', 'delete', 'update']
            this.curTemplate.template_files.forEach(resource => {
                resource.files.forEach(file => {
                    if (changeActions.includes(file.action)) {
                        isEdited = true
                    } else if (file.content !== file.originContent) {
                        isEdited = true
                    }
                })
            })
            
            if (isEdited) {
                this.$bkInfo({
                    title: this.$t('确认'),
                    content: this.$createElement('p', {
                        style: {
                            textAlign: 'center'
                        }
                    }, this.$t('模板编辑的内容未保存，确认要离开？')),
                    confirmFn () {
                        next(true)
                    }
                })
            } else {
                next(true)
            }
        },

        beforeDestroy () {
            if (this.clipboardVarInstance && this.clipboardVarInstance.off) {
                this.clipboardVarInstance.off('success')
            }

            if (this.clipboardImageInstance && this.clipboardImageInstance.off) {
                this.clipboardImageInstance.off('success')
            }
        },
        
        methods: {
            /**
             * 初始化入口
             */
            initTemplate () {
                if (this.templateId === 0) {
                    this.createNewTemplate()
                } else {
                    this.getYamlTemplateDetail()
                }
                this.getVersionList()
            },

            /**
             * 初始化资源列表
             */
            async initYamlResources () {
                this.yamlTemplateJson = {
                    name: '',
                    desc: '',
                    show_version: {
                        name: ''
                    },
                    template_files: []
                }

                const projectId = this.projectId
                try {
                    const res = await this.$store.dispatch('k8sTemplate/getYamlResources', { projectId })
                    this.yamlResourceConf = res.data

                    this.yamlResourceConf.resource_names.forEach(resource => {
                        this.yamlTemplateJson.template_files.push({
                            resource_name: resource,
                            actived: true,
                            files: []
                        })
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.isYamlTemplateLoading = false
                }
            },
            
            /**
             * 镜像列表初始化
             */
            async initImageList () {
                if (this.isLoadingImageList) return false

                this.isLoadingImageList = true

                const projectId = this.projectId
                try {
                    const res = await this.$store.dispatch('k8sTemplate/getImageList', { projectId })
                    const data = res.data
                    setTimeout(() => {
                        data.forEach(item => {
                            item._id = item.value
                            item._name = item.name
                        })
                        this.imageList.splice(0, this.imageList.length, ...data)
                        this.$store.commit('k8sTemplate/updateImageList', this.imageList)
                        this.isLoadingImageList = false
                    }, 1500)
                } catch (e) {
                    this.isLoadingImageList = false
                    catchErrorHandler(e, this)
                }
            },

            changeImage (value, data) {
                const projectId = this.projectId
                const imageId = data.value
                const isPub = data.is_pub

                this.curImageData = data
                // 如果不是输入变量
                if (isPub !== undefined) {
                    this.$store.dispatch('k8sTemplate/getImageVertionList', { projectId, imageId, isPub }).then(res => {
                        const data = res.data
                        data.forEach(item => {
                            item._id = item.text
                            item._name = item.text
                        })

                        this.imageVersionList.splice(0, this.imageVersionList.length, ...data)
                        if (this.imageVersionList.length) {
                            const imageInfo = this.imageVersionList[0]

                            this.imageVersion = imageInfo.text
                            this.setImageVersion(imageInfo.value, imageInfo)
                        } else {
                            this.image = ''
                        }
                    }, res => {
                        const message = res.message
                        this.$bkMessage({
                            theme: 'error',
                            message: message
                        })
                    })
                } else {
                    this.image = ''
                    this.imageVersion = ''
                    this.imageVersionList = []
                }
            },

            /**
             * 设置镜像版本
             */
            setImageVersion (value, data) {
                // 镜像和版本都是通过下拉选择
                const projectCode = this.projectCode
                // curImageData不是空对象
                if (JSON.stringify(this.curImageData) !== '{}') {
                    if (data.text && data.value) {
                        this.imageVersion = data.text
                        const items = data.value.split('/')
                        items.splice(0, 1, '{{SYS_JFROG_DOMAIN}}')
                        this.image = `'${items.join('/')}'`
                    } else if (this.curImageData.is_pub !== undefined) {
                        // 镜像是下拉，版本是变量
                        // image = imageBase + imageName + ':' + imageVersion
                        const imageName = this.imageName
                        this.imageVersion = value
                        this.image = `'{{SYS_JFROG_DOMAIN}}/${imageName}:${value}'`
                    } else {
                        // 镜像和版本是变量
                        // image = imageBase +  'paas/' + projectCode + '/' + imageName + ':' + imageVersion
                        const imageName = this.imageName
                        this.imageVersion = value
                        this.image = `'{{SYS_JFROG_DOMAIN}}/${projectCode}/${imageName}:${value}'`
                    }
                }
            },

            /**
             * 创建新的模板
             */
            createNewTemplate () {
                const params = JSON.parse(JSON.stringify(this.yamlTemplateJson))
                params.name = this.$t('模板集_') + (+new Date())
                params.desc = this.$t('模板集描述')
                this.curTemplate = params

                // 默认第一个资源添加文件
                this.handleAddFile(this.curTemplate.template_files[0], true)
                this.isYamlTemplateLoading = false
            },

            handleEditorMount (editorInstance, monacoEditor) {
                this.monacoEditor = monacoEditor
            },

            handleSelectFile (resource, file) {
                this.setCurResourceFile(resource, file)
            },

            editTemplateName () {
                this.isEditName = true
                this.editTemplate.name = this.curTemplate.name

                this.$nextTick(() => {
                    const inputer = this.$refs.templateNameInput
                    inputer.focus()
                    inputer.select()
                })
            },

            cancelEditName () {
                setTimeout(() => {
                    this.isEditName = false
                }, 200)
            },

            editTemplateDesc () {
                this.isEditDesc = true
                this.editTemplate.desc = this.curTemplate.desc

                this.$nextTick(() => {
                    const inputer = this.$refs.templateDescInput
                    inputer.focus()
                    inputer.select()
                })
            },

            cancelEditDesc () {
                setTimeout(() => {
                    this.isEditDesc = false
                }, 200)
            },

            /**
             * 保存模板集名称和描述
             */
            async saveTemplate () {
                const data = this.editTemplate
                const projectId = this.projectId
                const templateId = this.templateId

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

                if (templateId && templateId !== 0) {
                    try {
                        await this.$store.dispatch('k8sTemplate/updateYamlTemplate', {
                            projectId,
                            templateId,
                            data
                        })

                        this.updateTemplateBaseInfo(data)
                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('模板集基础信息保存成功')
                        })
                    } catch (e) {
                        catchErrorHandler(e, this)
                    }
                } else {
                    this.updateTemplateBaseInfo(data)
                }
            },

            updateTemplateBaseInfo (data) {
                this.isEditName = false
                this.isEditDesc = false
                this.curTemplate.name = data.name
                this.curTemplate.desc = data.desc
            },

            /**
             * 展开、折叠
             *
             * @param {Object} resource 资源
             */
            handleToggleResource (resource) {
                resource.actived = !resource.actived
            },

            focusAddNameInput () {
                this.$nextTick(() => {
                    const inputer = this.$refs.fileNameInput[0]
                    if (inputer) {
                        inputer.focus()
                        inputer.select()
                    }
                })
            },

            /**
             * 添加相应的资源文件
             *
             * @param {Object} resource 资源
             * action 'create' 创建
             * action 'update' 更新
             * action 'delete' 删除
             * action 'unchange' 没改变
             */
            handleAddFile (resource, isImmediate) {
                if (this.addFileNameTmp) {
                    this.focusAddNameInput()
                    return false
                }

                const type = resource.resource_name
                const index = resource.files.length + 1
                const content = this.yamlResourceConf.initial_templates[type] || ''
                const name = `${type.toLowerCase()}-${index}.yaml`
                const id = `local_${+new Date()}`

                const file = {
                    id: id,
                    name: name,
                    content: content,
                    originContent: content,
                    isEdited: true,
                    action: 'create'
                }

                resource.actived = true
                resource.files.push(file)
                this.addFileNameTmp = file.name

                if (isImmediate) {
                    file.isEdited = false
                    this.addFileNameTmp = ''
                    this.setCurResourceFile(resource, file)
                } else {
                    this.focusAddNameInput()
                }
            },

            checkFileName (resource, file, name, action) {
                const nameReg = /^[a-z]{1}[a-z0-9-.]{0,63}$/
                if (!name) {
                    // 如果是刚新建，直接删除
                    if (file.action === 'create' && action === 'addFileBlur') {
                        // 把新建的删除
                        resource.files = resource.files.filter(item => {
                            return item.id !== file.id
                        })
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('请输入资源文件名称')
                        })
                    }
                    return false
                }

                if (!nameReg.test(name)) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('文件名称错误，只能包含：小写字母、数字、点(.)、连字符(-)，必须是字母开头，长度小于64个字符'),
                        delay: 8000
                    })
                    return false
                }

                // 判断是否已经重复命名(存在两个)
                const repeatFile = resource.files.find(resourceFile => {
                    return resourceFile.name === name && resourceFile.id !== file.id
                })
                
                if (repeatFile) {
                    // const deleteFile = files.find(file => file.action === 'delete')
                    // 如果新建和已经删除的重命名，把已经删除的重新启用
                    if (repeatFile.action === 'delete') {
                        repeatFile.action = 'update'
                        repeatFile.content = file.content
                        repeatFile.originContent = file.originContent

                        // 把新建的删除
                        resource.files = resource.files.filter(item => {
                            return item.id !== file.id
                        })

                        this.setCurResourceFile(resource, repeatFile)
                        return false
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('文件名称不能重复'),
                            delay: 8000
                        })
                        return false
                    }
                } else {
                    return true
                }
            },
            /**
             * 编辑当前资源文件名称失焦点
             *
             * @param {Object} resource 资源
             * @param {Object} file 资源文件
             */
            handleFileEnter (resource, file) {
                this.isEnterTrigger = true
                const name = this.addFileNameTmp
                if (!this.checkFileName(resource, file, name)) return false
                
                file.isEdited = false
                file.name = name
                this.setCurResourceFile(resource, file)
                this.addFileNameTmp = ''
            },
            handleFileBlur (resource, file) {
                const name = this.addFileNameTmp

                if (this.isEnterTrigger) {
                    this.isEnterTrigger = false
                    return false
                }
                if (!this.checkFileName(resource, file, name, 'addFileBlur')) return false
                
                file.isEdited = false
                file.name = name
                this.setCurResourceFile(resource, file)
                this.addFileNameTmp = ''
            },

            /**
             * 设置当前要编辑的资源文件
             * @param {Object} file 资源文件
             */
            setCurResourceFile (resource, file) {
                this.addFileNameTmp = ''
                this.useEditorDiff = false
                this.curResource = resource
                this.curResourceFile = file
                this.yamlEditorOptions.readOnly = false
            },

            /**
             * 清空当前资源文件
             */
            clearCurResourfeFile () {
                this.curResourceFile = {
                    id: 0,
                    name: '',
                    yamlValue: ''
                }
            },

            /**
             * 删除资源文件
             *
             * @param {Object} resource 资源
             * @param {Object} file 文件
             * @param {Number} index 索引
             */
            handleRemoveFile (resource, file, index) {
                const self = this
                this.$bkInfo({
                    title: this.$t('确认'),
                    content: this.$createElement('p', { style: { 'text-align': 'center' } }, `${this.$t('删除')} ${resource.resource_name}：${file.name}`),
                    confirmFn () {
                        self.removeLocalFile(resource, file, index)
                    }
                })
            },

            /**
             * 删除本地资源文件
             * @param  {object} application application
             * @param  {number} index 索引
             */
            removeLocalFile (resource, file, index) {
                // 如果是新建直接删除，否则设置action为delete
                if (String(file.id).startsWith('local_')) {
                    resource.files.splice(index, 1)
                } else {
                    file.action = 'delete'
                }
                // 如果删除的为当前编辑文件，则重新设置编辑文件
                if (this.curResourceFile.id === file.id) {
                    this.clearCurResourfeFile()

                    // 找到第一个不为delete状态的文件
                    const activeFile = resource.files.find(file => file.action !== 'delete')
                    if (activeFile) {
                        this.setCurResourceFile(resource, activeFile)
                    } else {
                        this.yamlEditorOptions.readOnly = true
                    }
                }

                this.useEditorDiff = false
            },

            toggleCompare () {
                this.useEditorDiff = !this.useEditorDiff
            },

            debounce (func, wait) {
                let timer
                const that = this
                return function () {
                    const context = that
                    const args = arguments
                    if (timer) {
                        clearTimeout(timer)
                    }

                    timer = setTimeout(() => {
                        func.apply(context, args)
                    }, wait)
                }
            },

            /**
             * 校验版本名称
             */
            checkVersionData (versionName) {
                const nameReg = /^[a-zA-Z0-9-_.]{1,45}$/

                if (!nameReg.test(versionName)) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请填写1至45个字符（由字母、数字、下划线以及 - 或 . 组成）')
                    })
                    return false
                }

                for (const item of this.allVersionList) {
                    if (item.name === versionName) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('版本{versionKeyword}已经存在', {
                                versionKeyword: this.versionKeyword
                            })
                        })
                        return false
                    }
                }
                return true
            },

            /**
             * 保存模板集
             */
            handleSaveTemplate () {
                // 验证模板集信息
                if (!this.curTemplate.name) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入模板集名称')
                    })
                    return false
                }

                if (!this.curTemplate.desc) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入模板集描述')
                    })
                    return false
                }

                const resources = this.curTemplate.template_files
                for (const resource of resources) {
                    const files = resource.files.filter(file => file.action !== 'delete')
                    for (const file of files) {
                        if (!file.name) {
                            this.$bkMessage({
                                theme: 'error',
                                message: this.$t('请输入资源文件名称')
                            })
                            return false
                        }

                        if (!file.content) {
                            this.$bkMessage({
                                theme: 'error',
                                message: `${file.name}：${this.$t('请输入资源文件内容')}`
                            })
                            return false
                        }
                        if (resource.resource_name !== 'CustomManifest') {
                            try {
                                yamljs.load(file.content)
                            } catch (err) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: `${file.name}：${this.$t('请输入合法的YAML')}`
                                })
                                return false
                            }
                        }
                    }
                }

                this.showVersionBox()
            },

            saveYamlTemplate () {
                if (this.saveVersionWay === 'new' && this.versionKeyword && !this.checkVersionData(this.versionKeyword)) {
                    return false
                }
                if (this.isTemplateSaving) {
                    return false
                }

                if (this.templateId === 0) {
                    this.createYamlTemplate()
                } else {
                    this.updateYamlTemplate()
                }
            },

            /**
             * 组装数据
             */
            getYamlParams () {
                const params = JSON.parse(JSON.stringify(this.curTemplate))
                params.template_files = params.template_files.filter(resource => {
                    return resource.files.length
                })

                params.template_files.forEach(resource => {
                    delete resource.actived

                    if (resource.files.length) {
                        resource.files.forEach(file => {
                            // action 'create' 创建
                            // action 'update' 更新
                            // action 'delete' 删除
                            // action 'unchange' 没改变
                            
                            if (String(file.id).startsWith('local_')) {
                                delete file.id
                                file.action = 'create'
                            } else if (file.action === 'unchange') {
                                file.action = (file.content !== file.originContent) ? 'update' : 'unchange'
                            }

                            delete file.originContent
                            delete file.isEdited
                        })
                    } else {
                        delete resource.files
                    }
                })

                // 选择旧版或者创建新版本
                if (this.saveVersionWay === 'old') {
                    const versionData = this.withoutCurVersionList.find(version => {
                        return version.show_version_id === this.selectedVersion
                    })
                    if (versionData) {
                        params.show_version = {
                            name: versionData.name
                        }
                    }
                } else if (this.saveVersionWay === 'new') {
                    params.show_version.name = this.versionKeyword
                }
                params.show_version.old_show_version_id = this.curShowVersionId
                delete params.show_version.show_version_id
                return params
            },

            /**
             * 创建yaml模板集
             */
            async createYamlTemplate () {
                const params = this.getYamlParams()

                this.isTemplateSaving = true
                try {
                    const res = await this.$store.dispatch('k8sTemplate/createYamlTemplate', {
                        projectId: this.projectId,
                        data: params
                    })
                    
                    this.$router.push({
                        name: 'K8sYamlTemplateset',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode,
                            templateId: res.data.template_id
                        }
                    })
                    this.hideVersionBox()
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 更新yaml模板集
             */
            async updateYamlTemplate () {
                const params = this.getYamlParams()

                this.isTemplateSaving = true
                try {
                    await this.$store.dispatch('k8sTemplate/updateYamlTemplate', {
                        projectId: this.projectId,
                        templateId: this.templateId,
                        data: params
                    })
                    // this.updateLocalYamlTemplate(res.data)
                    this.getYamlTemplateDetail()
                    this.getVersionList()
                    this.hideVersionBox()

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('保存成功')
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 更新当前模板数据
             */
            // updateLocalYamlTemplate (data) {
            //     this.curTemplate.template_files.forEach(resource => {
            //         // 重置
            //         resource.files.forEach(file => {

            //         })
            //     })
            // },

            /**
             * 获取模板集详情
             */
            async getYamlTemplateDetail () {
                const originYamlParams = JSON.parse(JSON.stringify(this.yamlTemplateJson))

                try {
                    const res = await this.$store.dispatch('k8sTemplate/getYamlTemplateDetail', {
                        projectId: this.projectId,
                        templateId: this.templateId
                    })
                    this.setCurTemplte(res.data)
                } catch (e) {
                    this.curTemplate = originYamlParams
                    catchErrorHandler(e, this)
                } finally {
                    this.isYamlTemplateLoading = false
                    this.isTemplateSaving = false
                }
            },

            setCurTemplte (template) {
                const originYamlParams = JSON.parse(JSON.stringify(this.yamlTemplateJson))
                const resourceList = originYamlParams.template_files
                let hasDefaultList = false
                let hasCustomList = false
                template.template_files.forEach(resource => {
                    resource.files.forEach(file => {
                        file.action = 'unchange'
                        file.originContent = file.content
                        file.isEdited = false
                    })
                    if (resource.files.length) {
                        if (resource.resource_name === 'CustomManifest') {
                            hasCustomList = true
                        } else {
                            hasDefaultList = true
                        }
                    }
                })
                if (hasCustomList && !hasDefaultList) {
                    this.tabName = 'custom'
                } else {
                    this.tabName = 'default'
                }

                resourceList.forEach(resource => {
                    const targetResource = template.template_files.find(serverResource => serverResource.resource_name === resource.resource_name)
                    if (targetResource) {
                        resource.files = targetResource.files
                    }
                })

                template.template_files = resourceList
                this.curTemplate = template
                this.setDefaultEditFile()
            },

            /**
             * 设置默认要编辑的资源文件
             */
            setDefaultEditFile () {
                // 如果已经存在当前编辑中的文件
                // if (this.curResourceFile.id) {
                //     this.curTemplate.template_files.find(resource => {
                //         resource.files.forEach()
                //     })
                //     return false
                // }
                const activeResource = this.curTemplate.template_files.find(resource => {
                    return resource.files.length
                })

                if (activeResource) {
                    this.setCurResourceFile(activeResource, activeResource.files[0])
                }
            },

            showVersionBox () {
                this.versionDialogConf.isShow = true

                if (this.isNewTemplate) {
                    this.$nextTick(() => {
                        this.$refs.versionInput.focus()
                    })
                }
            },

            hideVersionBox () {
                this.saveVersionWay = 'cur'
                this.versionKeyword = ''
                this.selectedVersion = ''
                this.versionDialogConf.isShow = false
            },

            /**
             * 获取版本列表
             */
            async getVersionList () {
                const projectId = this.projectId
                const templateId = this.templateId
                
                if (templateId !== 0) {
                    this.isVersionListLoading = true
                    try {
                        const res = await this.$store.dispatch('k8sTemplate/getVersionList', { projectId, templateId })
                        if (res && res.data) {
                            const versionList = res.data
                            if (versionList) {
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
                        }
                    } catch (e) {
                        this.$store.commit('k8sTemplate/updateVersionList', [])
                        catchErrorHandler(e, this)
                    } finally {
                        this.isVersionListLoading = false
                    }
                } else {
                    this.$store.commit('k8sTemplate/updateVersionList', [])
                }
            },

            /**
             * 离开当前编辑页面
             */
            handleBeforeLeave (callback) {
                this.goTemplateIndex()
            },

            goTemplateIndex () {
                // 清空数据
                this.$router.push({
                    name: 'templateset',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
            },

            /**
             * 实例化
             */
            createInstance () {
                this.curTemplate.edit_mode = 'yaml'
                this.$router.push({
                    name: 'instantiation',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        templateId: this.templateId,
                        curTemplate: this.curTemplate,
                        curShowVersionId: this.curShowVersionId
                    }
                })
            },

            showVersionPanel () {
                this.versionSidePanel.isShow = true
                this.getVersionList()
            },

            /**
             * 获取相应版本的资源详情
             *
             * @param {Number} versionId 版本id
             * @param {Object} [varname] [description]
             */
            async getTemplateByVersion (versionId, isVersionRemove) {
                const projectId = this.projectId
                const templateId = this.templateId
                
                this.isEditFileName = false
                try {
                    const res = await this.$store.dispatch('k8sTemplate/getYamlTemplateDetailByVersion', { projectId, templateId, versionId })
                    this.setCurTemplte(res.data)
                    // 如果不是操作删除版本，则可隐藏
                    if (!isVersionRemove) {
                        this.versionSidePanel.isShow = false
                    }
                } catch (e) {
                    this.$store.commit('k8sTemplate/updateVersionList', [])
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 展示/隐藏变量面板
             */
            handleToggleVarPanel () {
                this.isVarPanelShow = !this.isVarPanelShow
                this.isImagePanelShow = false
            },

            /**
             * 展示/隐藏变量面板
             */
            handleToggleImagePanel () {
                this.isImagePanelShow = !this.isImagePanelShow
                this.isVarPanelShow = false
            },

            hideVarPanel () {
                this.isVarPanelShow = false
            },

            hideImagePanel () {
                this.isImagePanelShow = false
            },

            /**
             * 获取变量数据
             */
            async initVarList () {
                try {
                    await this.$store.dispatch('variable/getBaseVarList', this.projectId)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 编辑当前资源文件名
             */
            handleEditFileName () {
                this.isEditFileName = true
                this.editFileNameTmp = this.curResourceFile.name

                this.$nextTick(() => {
                    const inputer = this.$refs.resourceFileNameInput
                    inputer.focus()
                    inputer.select()
                })
            },

            handleEditNameEnter () {
                const name = this.editFileNameTmp
                if (!this.checkFileName(this.curResource, this.curResourceFile, name)) {
                    this.$nextTick(() => {
                        const inputer = this.$refs.resourceFileNameInput
                        inputer.focus()
                        inputer.select()
                    })
                    return false
                }
                this.isEditFileName = false
                this.curResourceFile.name = name
                this.curResourceFile.action = 'update'
                this.isEnterTrigger = true
                this.editFileNameTmp = ''
            },

            handleEditNameBlur () {
                // 用setTimeout主要是考虑tab切换时，放弃编辑操作
                setTimeout(() => {
                    if (this.isEditFileName) {
                        const name = this.editFileNameTmp
                        if (this.isEnterTrigger) {
                            this.isEnterTrigger = false
                            return false
                        }
                        if (!this.checkFileName(this.curResource, this.curResourceFile, name)) {
                            this.$nextTick(() => {
                                const inputer = this.$refs.resourceFileNameInput
                                inputer.focus()
                                inputer.select()
                            })
                            return false
                        }

                        this.isEditFileName = false
                        this.curResourceFile.name = name
                        this.curResourceFile.action = 'update'
                        this.editFileNameTmp = ''
                    }
                }, 500)
            },
            handleImagePanel () {
                return false
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

            async reloadTemplateLockStatus () {
                this.isTemplateLocking = true
                try {
                    const res = await this.$store.dispatch('k8sTemplate/getYamlTemplateDetail', {
                        projectId: this.projectId,
                        templateId: this.templateId
                    })
                    this.curTemplate.is_locked = res.data.is_locked
                    this.curTemplate.locker = res.data.locker
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isTemplateLocking = false
                }
            },

            async lockTemplateset () {
                const projectId = this.projectId
                const templateId = this.templateId
                this.isTemplateLocking = true
                try {
                    await this.$store.dispatch('k8sTemplate/lockTemplateset', { projectId, templateId })
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('加锁成功')
                    })
                    this.reloadTemplateLockStatus()
                } catch (res) {
                    this.$bkMessage({
                        theme: 'error',
                        message: res.message,
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
                const templateId = this.templateId
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
                    await this.$store.dispatch('k8sTemplate/unlockTemplateset', { projectId, templateId })
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('解锁成功')
                    })
                    this.reloadTemplateLockStatus()
                } catch (res) {
                    this.$bkMessage({
                        theme: 'error',
                        message: res.message,
                        hasCloseIcon: true,
                        delay: '3000'
                    })
                } finally {
                    setTimeout(() => {
                        this.isTemplateLocking = false
                    }, 1000)
                }
            },

            handleToggleTab (name) {
                this.tabName = name
                this.isEditFileName = false
                this.$nextTick(() => {
                    this.clearCurResourfeFile()
                })
            }
            // removeVersion (data) {
            //     const self = this
            //     this.$bkInfo({
            //         title: `确认`,
            //         content: this.$createElement('p', { style: { 'text-align': 'center' } }, `删除版本：“${data.name}”`),
            //         confirmFn () {
            //             const projectId = self.projectId
            //             const templateId = self.templateId
            //             const versionId = data.show_version_id
            //             self.$store.dispatch('k8sTemplate/removeVersion', { projectId, templateId, versionId }).then(res => {
            //                 self.$bkMessage({
            //                     theme: 'success',
            //                     message: '操作成功！'
            //                 })

            //                 self.getVersionList().then(versionList => {
            //                     // 如果是删除当前版本
            //                     if (versionId === self.curShowVersionId || String(versionId) === self.curShowVersionId) {
            //                         // 加载第一项，优先选择非草稿
            //                         if (self.versionList.length) {
            //                             let versionData = self.versionList[0]
            //                             if (versionData.show_version_id === -1 && self.versionList.length > 1) {
            //                                 versionData = self.versionList[1]
            //                             }
            //                             self.getTemplateByVersion(versionData.show_version_id, true)
            //                         } else {
            //                             self.getTemplateByVersion(-1)
            //                         }
            //                     }
            //                 })
            //             }, res => {
            //                 this.$bkMessage({
            //                     theme: 'error',
            //                     message: res.message,
            //                     delay: '3000'
            //                 })
            //             })
            //         }
            //     })
            // }
        }
    }
</script>

<style lang="postcss" scoped>
    @import './index.css';
    @import '../header.css';
</style>
