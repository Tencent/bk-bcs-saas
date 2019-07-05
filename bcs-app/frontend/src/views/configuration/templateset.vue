<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-config-templateset-title">
                模板集
            </div>
            <bk-guide></bk-guide>
        </div>

        <div class="biz-content-wrapper" style="margin: 0; padding: 0;" v-bkloading="{ isLoading: isLoading, opacity: 0.1 }">
            <template v-if="!isLoading">
                <div class="biz-panel-header" style="padding: 20px;">
                    <div class="left">
                        <button class="bk-button bk-primary" @click.stop.prevent="addTemplate">
                            <i class="bk-icon icon-plus"></i>
                            <span>添加模板集</span>
                        </button>
                    </div>
                    <div class="right">
                        <div class="biz-search-input" style="width: 300px;">
                            <input
                                type="text"
                                class="bk-form-input"
                                placeholder="输入关键字，按Enter搜索"
                                v-model="searchKeyword"
                                @keyup.enter="search" />
                            <a href="javascript:void(0)" class="biz-search-btn" v-if="!searchKeyword">
                                <i class="bk-icon icon-search" style="color: #c3cdd7;"></i>
                            </a>
                            <a href="javascript:void(0)" class="biz-search-btn" v-else @click.stop.prevent="clearSearch">
                                <i class="bk-icon icon-close-circle-shape"></i>
                            </a>
                        </div>
                    </div>
                </div>
                <svg style="display: none;">
                    <title>模板集默认图标</title>
                    <symbol id="biz-set-icon" viewBox="0 0 32 32">
                        <path d="M6 3v3h-3v23h23v-3h3v-23h-23zM24 24v3h-19v-19h19v16zM27 24h-1v-18h-18v-1h19v19z"></path>
                        <path d="M13.688 18.313h-6v6h6v-6z"></path>
                        <path d="M21.313 10.688h-6v13.625h6v-13.625z"></path>
                        <path d="M13.688 10.688h-6v6h6v-6z"></path>
                    </symbol>
                </svg>

                <div class="biz-namespace">
                    <table class="bk-table biz-templateset-table" id="templateset-table">
                        <thead>
                            <tr>
                                <!-- <th class="template-logo center">图标</th> -->
                                <th class="template-name">模板集名称</th>
                                <th class="template-type">类型</th>
                                <th class="template-container">容器 / 镜像</th>
                                <!-- <th style="padding-left: 0;">镜像</th> -->
                                <th class="template-action">操作</th>
                            </tr>
                        </thead>
                    </table>

                    <div id="templateset-container" ref="templatesetContainer">
                        <table class="bk-table biz-templateset-table">
                            <tbody>
                                <template v-if="templateList.length">
                                    <tr :key="templateIndex" v-for="(template, templateIndex) in templateList">
                                        <td colspan="6">
                                            <table class="biz-inner-table">
                                                <tr>
                                                    <!-- <td class="logo">
                                                        <div class="logo-wrapper">
                                                            <svg class="biz-set-icon"><use xlink:href="#biz-set-icon"></use></svg>
                                                        </div>
                                                    </td> -->
                                                    <td class="data">
                                                        <div class="data-wrapper">
                                                            <a href="javascript:void(0);" class="title" @click.stop.prevent="goTemplateIndex(template)">
                                                                {{template.name}}
                                                            </a>

                                                            <p class="vertion">最新版本：{{template.latest_show_version || '--'}}</p>
                                                        </div>
                                                    </td>
                                                    <td class="type">
                                                        <div class="type-wrapper">
                                                            <strong class="type-name">{{template.category_name}}</strong>
                                                        </div>
                                                    </td>
                                                    <td class="service">
                                                        <div class="service-wrapper">
                                                            <template v-if="template.containers.length">
                                                                <div :key="serviceIndex" v-for="(service, serviceIndex) in template.containers">
                                                                    <bk-tooltip :content="service.name || '--'" placement="top">
                                                                        <span class="biz-text-wrapper">{{service.name || '--'}}</span>
                                                                    </bk-tooltip>
                                                                    /
                                                                    <bk-tooltip :content="service.image || '--'" placement="top">
                                                                        <span class="biz-text-wrapper">{{service.image || '--'}}</span>
                                                                    </bk-tooltip>
                                                                </div>
                                                            </template>
                                                            <template v-else>
                                                                -- / --
                                                            </template>
                                                        </div>
                                                    </td>
                                                    <!-- <td class="image">
                                                        <template v-if="template.containers.length">
                                                            <div class="biz-image-wrapper" :key="serviceIndex" v-for="(service, serviceIndex) in template.containers">
                                                                <bk-tooltip :content="service.image" placement="top">
                                                                    {{service.image || '--'}}
                                                                </bk-tooltip>
                                                            </div>
                                                        </template>
                                                        <template v-else>
                                                            --
                                                        </template>
                                                    </td> -->
                                                    <td class="operate">
                                                        <div class="operate-wrapper">
                                                            <template v-if="!template.permissions.use">
                                                                <button class="bk-button bk-default btn" @click="goApplyPermission(template)">
                                                                    申请使用权限
                                                                </button>
                                                            </template>
                                                            <template v-else>
                                                                <template v-if="template.latest_show_version_id === -1">
                                                                    <bk-tooltip content="模板集为草稿状态，不能实例化" placement="top">
                                                                        <button class="bk-button bk-default btn" disabled="disabled" style="width: 124px;">
                                                                            实例化
                                                                        </button>
                                                                    </bk-tooltip>
                                                                </template>
                                                                <template v-else>
                                                                    <button class="bk-button bk-default btn" @click="goCreateInstance(template)" style="width: 124px;">
                                                                        实例化
                                                                    </button>
                                                                </template>
                                                            </template>

                                                            <bk-dropdown-menu class="dropdown-menu" :align="'left'" ref="dropdown">
                                                                <button class="bk-button bk-default btn" slot="dropdown-trigger" style="width: 82px; position: relative;">
                                                                    <span>更多</span>
                                                                    <i class="bk-icon icon-angle-down dropdown-menu-angle-down ml0" style="font-size: 10px;"></i>
                                                                </button>
                                                                <ul class="bk-dropdown-list" slot="dropdown-content">
                                                                    <li>
                                                                        <a href="javascript:void(0)" @click="showCopy(template)">复制模板集</a>
                                                                    </li>
                                                                    <li>
                                                                        <a href="javascript:void(0)" @click="removeTemplate(template)">删除模板集</a>
                                                                    </li>
                                                                    <li>
                                                                        <a href="javascript:void(0)" @click="showChooseDialog(template)">删除实例</a>
                                                                    </li>
                                                                </ul>
                                                            </bk-dropdown-menu>
                                                        </div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr>
                                        <td colspan="6">
                                            <div class="biz-guide-box" style="margin: 0 20px;">
                                                <p class="message empty-message">无数据</p>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                </div>
            </template>
            <div class="scroll-loading" v-bkloading="{ isLoading: isScrollLoading }" v-if="isScrollLoading && !isListReload">
            </div>
            <p class="biz-no-data" v-if="!pageConf.hasNext && templateList.length">全部数据加载完成</p>
        </div>
        <bk-dialog
            :is-show.sync="copyDialogConf.isShow"
            :width="copyDialogConf.width"
            :close-icon="copyDialogConf.closeIcon"
            :ext-cls="'biz-config-templateset-copy-dialog'"
            :has-header="false"
            :quick-close="false">
            <div slot="content" v-bkloading="{ isLoading: isCopying }">
                <div class="bk-form bk-form-vertical biz-instance-num-form">
                    <div class="bk-form-item">
                        <label class="bk-label">
                            模板集【{{copyDialogConf.title}}】复制为：
                        </label>
                        <div class="bk-form-content">
                            <input type="text" class="bk-form-input" maxlength="30" placeholder="新模板集名称" v-model="copyName" />
                        </div>
                    </div>
                </div>
            </div>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isCopying">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            复制中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="confirmCopyTemplate">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideCopy">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="delInstanceDialogConf.isShow"
            :width="delInstanceDialogConf.width"
            :title="delInstanceDialogConf.title"
            :close-icon="delInstanceDialogConf.closeIcon"
            :quick-close="false"
            :ext-cls="'biz-config-templateset-del-instance-dialog'"
            @cancel="delInstanceDialogConf.isShow = false">
            <div slot="content" v-bkloading="{ isLoading: isDeleting }">
                <div class="content-inner">
                    <div class="bk-form bk-form-vertical" style="margin-bottom: 20px;">
                        <div class="bk-form-item">
                            <label class="bk-label">
                                模板集版本
                            </label>
                            <div class="bk-form-content">
                                <div class="bk-dropdown-box" style="width: 240px;" @click="fetchTemplatesetVerList">
                                    <bk-selector
                                        :placeholder="'请选择'"
                                        :selected.sync="tplsetVerIndex"
                                        :list="tplsetVerList"
                                        @item-selected="changeTplset"
                                        :is-loading="isLoadingTplsetVer"
                                        :ext-cls="'ver-selector'">
                                    </bk-selector>
                                </div>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">
                                模板
                            </label>
                            <div class="bk-form-content">
                                <bk-dropdown :placeholder="'请选择'"
                                    :selected.sync="tplIndex"
                                    :list="tplList"
                                    @item-selected="changeTpl"
                                    :ext-cls="'ver-selector'">
                                </bk-dropdown>
                            </div>
                        </div>
                    </div>
                    <template v-if="showNamespaceContainer && !candidateNamespaceList.length">
                        <transition name="fadeDown">
                            <div class="content-trigger-wrapper" style="text-align: center;">
                                没有命名空间数据
                            </div>
                        </transition>
                    </template>
                    <template v-else>
                        <div tag="div" name="fadeDown">
                            <div
                                :key="index" class="content-trigger-wrapper"
                                :class="item.isOpen ? 'open' : ''"
                                v-for="(item, index) in candidateNamespaceList">
                                <div class="content-trigger" @click="triggerHandler(item, index)">
                                    <div class="left-area">
                                        <div class="label">
                                            {{item.cluster_name}}
                                        </div>
                                        <div class="checker-inner">
                                            <a href="javascript:;" class="bk-text-button" @click.stop="selectAll(item, index)">全选</a>
                                            <a href="javascript:;" class="bk-text-button" @click.stop="selectInvert(item, index)">反选</a>
                                        </div>
                                    </div>
                                    <i v-if="item.isOpen" class="bk-icon icon-angle-up trigger active"></i>
                                    <i v-else class="bk-icon icon-angle-down trigger"></i>
                                </div>
                                <div class="biz-namespace-wrapper" v-if="item.results.length" :style="{ display: item.isOpen ? '' : 'none' }">
                                    <div class="namespace-inner">
                                        <template v-for="(namespace, i) in item.results">
                                            <div :key="i" v-if="namespace.isExist" class="candidate-namespace exist" style="position: relative;">
                                                <bk-tooltip :content="namespace.name" :delay="500" placement="bottom">
                                                    <div class="candidate-namespace-name">
                                                        <span>{{namespace.name}}</span>
                                                        <span class="icon" v-if="namespace.isExist"><i class="bk-icon icon-check-1"></i></span>
                                                    </div>
                                                </bk-tooltip>
                                            </div>
                                            <div
                                                :key="i" v-else class="candidate-namespace"
                                                :class="namespace.isChoose ? 'active' : ''"
                                                @click="selectNamespaceInDialog(index, namespace, i)" style="position: relative;">
                                                <bk-tooltip :content="namespace.name" :delay="500" placement="bottom">
                                                    <div class="candidate-namespace-name">
                                                        <span>{{namespace.name}}</span>
                                                        <span class="icon" v-if="namespace.isChoose"><i class="bk-icon icon-check-1"></i></span>
                                                    </div>
                                                </bk-tooltip>
                                            </div>
                                        </template>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isDeleting">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            删除中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="confirmDelInstance">
                            提交
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="cancelDelInstance">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="delTemplateDialogConf.isShow"
            :width="delTemplateDialogConf.width"
            :close-icon="delTemplateDialogConf.closeIcon"
            :ext-cls="'biz-config-templateset-copy-dialog'"
            :has-header="false"
            :quick-close="false">
            <div slot="content" style="padding: 0 20px;">
                <div style="color: #333; font-size: 20px">
                    模板集【{{delTemplateDialogConf.title}}】版本：
                </div>
                <ul style="margin: 10px 0; font-size: 14px; color: #333;">
                    <li v-for="(key, index) in Object.keys(delTemplateDialogConf.existVersion)" :key="index">
                        <span>{{key}}：</span>
                        <span>有{{delTemplateDialogConf.existVersion[key]}}个实例</span>
                    </li>
                </ul>
                <div>
                    您需要先删除所有实例，再进行模板集删除操作
                </div>
            </div>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <button type="button" style="width: 96px;" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                        @click="delTemplateConfirm">
                        删除实例
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="delTemplateCancel">
                        取消
                    </button>
                </div>
            </template>
        </bk-dialog>
    </div>
</template>

<script>
    import applyPerm from '@open/mixins/apply-perm'
    import { catchErrorHandler } from '@open/common/util'

    export default {
        mixins: [applyPerm],
        data () {
            return {
                permissions: {},
                isLoading: true,
                searchKeyword: '',
                templateList: [],
                templateListCache: [],
                resourceList: [
                    {
                        id: 'application',
                        name: 'Application'
                    },
                    {
                        id: 'deployment',
                        name: 'Deployment'
                    },
                    {
                        id: 'service',
                        name: 'Service'
                    },
                    {
                        id: 'configmap',
                        name: 'Configmap'
                    },
                    {
                        id: 'secret',
                        name: 'Secret'
                    }
                ],
                resourceIndex: -1,
                pageConf: {
                    totalPage: 1,
                    pageSize: 10,
                    hasNext: true,
                    curPage: 1
                },
                copyDialogConf: {
                    isShow: false,
                    width: 400,
                    title: '',
                    closeIcon: false
                },
                copyName: '',
                curCopyTemplate: null,
                isCopying: false,
                delInstanceDialogConf: {
                    isShow: false,
                    width: 912,
                    title: '',
                    closeIcon: false
                },
                candidateNamespaceList: [], // 弹层中的 namespace 集合
                namespaceListTmp: {}, // 在弹层中选择的 namespace 缓存
                showNamespaceContainer: false,
                curDelInstanceTemplate: null,
                tplsetVerList: [],
                tplsetVerIndex: -1,
                tplsetVerId: '',
                tplList: [],
                tplIndex: -1,
                tplId: '',
                tplCategory: '',
                isDeleting: false,
                delTemplateDialogConf: {
                    isShow: false,
                    width: 650,
                    title: '',
                    closeIcon: false,
                    existVersion: {},
                    template: {}
                },
                isLoadingTplsetVer: false,
                isScrollLoading: false,
                isListReload: false
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            curProject () {
                return this.$store.state.curProject
            },
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            }
        },
        watch: {
            searchKeyword (newVal, oldVal) {
                // 如果删除，为空时触发搜索
                if (oldVal && !newVal) {
                    this.search()
                }
            }
        },
        mounted () {
            this.getTemplateList()
            this.$nextTick(() => {
                window.scrollTo(0, 0)
                window.onscroll = () => {
                    if (this.isLoading) {
                        return false
                    }
                    this.loadNextPage()
                }
            })
        },
        beforeRouteLeave (to, from, next) {
            window.onscroll = null
            next()
        },
        beforeDestroy (to, from, next) {
            window.onscroll = null
        },
        methods: {
            /**
             * 加载下一页数据
             */
            loadNextPage () {
                if (this.isScrollLoading || !this.pageConf.hasNext || this.isListReload) {
                    return false
                }
                if (this.scrollBottom()) {
                    this.isScrollLoading = true

                    this.pageConf.curPage++
                    this.getTemplateList()
                }
            },

            /**
             * 申请权限
             * @param  {object} template 当前模板集对象
             */
            goApplyPermission (template) {
                const url = this.createApplyPermUrl({
                    policy: 'use',
                    projectCode: this.projectCode,
                    idx: `templates:${template.id}`
                })
                window.open(url)
            },

            scrollBottom () {
                return document.documentElement.clientHeight + window.scrollY >= (document.documentElement.scrollHeight || document.documentElement.clientHeight)
            },

            /**
             * 确认删除模板集
             * @param {Object} template 当前模板集对象
             */
            async removeTemplate (template) {
                if (!template.permissions.delete) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'delete',
                        resource_code: template.id,
                        resource_name: template.name,
                        resource_type: 'templates'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                try {
                    // 先检测当前模板集是否存在实例
                    const res = await this.$store.dispatch('templateset/getExistVersion', {
                        projectId: this.projectId,
                        templateId: template.id
                    })

                    // 如果没有实例，可删除模板集，否则调用删除实例
                    if (!Object.keys(res.data.exist_version || {}).length) {
                        const me = this
                        me.$bkInfo({
                            title: ``,
                            clsName: 'biz-remove-dialog',
                            content: me.$createElement('p', {
                                class: 'biz-confirm-desc'
                            }, `确定要删除模板集【${template.name}】?`),
                            async confirmFn () {
                                me.deleteTemplate(template)
                            }
                        })
                    } else {
                        this.delTemplateDialogConf.isShow = true
                        this.delTemplateDialogConf.title = template.name
                        this.delTemplateDialogConf.template = Object.assign({}, template)
                        this.delTemplateDialogConf.existVersion = Object.assign({}, res.data.exist_version)
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 确认删除模板集
             * @param {Object} template 当前模板集对象
             */
            async deleteTemplate (template) {
                const backup = []
                backup.splice(0, backup.length, ...this.templateList)

                this.isLoading = true
                this.templateList.splice(0, this.templateList.length, ...[])
                this.templateListCache.splice(0, this.templateListCache.length, ...[])

                try {
                    await this.$store.dispatch('templateset/removeTemplate', {
                        projectId: this.projectId,
                        templateId: template.id
                    })

                    this.$bkMessage({
                        theme: 'success',
                        message: '删除成功！'
                    })
                    this.getTemplateList(true)
                } catch (e) {
                    this.isLoading = false
                    this.templateList.splice(0, this.templateList.length, ...backup)
                    this.templateListCache.splice(0, this.templateListCache.length, ...backup)
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 创建实例
             * @param  {object} template 当前模板集对象
             */
            async goCreateInstance (template) {
                if (!template.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: template.id,
                        resource_name: template.name,
                        resource_type: 'templates'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.$router.push({
                    name: 'instantiation',
                    params: {
                        projectId: this.projectId,
                        templateId: template.id,
                        curTemplate: template,
                        projectCode: this.projectCode
                    }
                })
            },

            /**
             * 关闭 delTemplateDialog
             */
            delTemplateCancel () {
                this.delTemplateDialogConf.isShow = false
                this.delTemplateDialogConf.title = ''
                this.delTemplateDialogConf.template = Object.assign({}, {})
                this.delTemplateDialogConf.existVersion = Object.assign({}, {})
            },

            /**
             * delTemplateDialog confirm
             */
            delTemplateConfirm () {
                const template = Object.assign({}, this.delTemplateDialogConf.template)
                this.delTemplateDialogConf.isShow = false
                this.delTemplateDialogConf.title = ''
                this.delTemplateDialogConf.template = Object.assign({}, {})
                this.delTemplateDialogConf.existVersion = Object.assign({}, {})
                this.showChooseDialog(template)
            },

            /**
             * 显示复制弹层
             * @param {Object} template 当前 template
             */
            async showCopy (template) {
                if (!template.permissions.edit) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'edit',
                        resource_code: template.id,
                        resource_name: template.name,
                        resource_type: 'templates'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.curCopyTemplate = Object.assign({}, template)
                this.copyDialogConf.isShow = true
                this.copyDialogConf.title = template.name
            },

            /**
             * 模板集复制提交前检测
             */
            confirmCopyTemplate () {
                const me = this

                const copyName = me.copyName.trim()

                if (!copyName) {
                    me.$bkMessage({
                        theme: 'error',
                        message: '请填写要复制的名称'
                    })
                    return
                }

                if (copyName.toLowerCase() === me.curCopyTemplate.name.trim().toLowerCase()) {
                    me.$bkMessage({
                        theme: 'error',
                        message: '复制的名称不能与之前的名称相同'
                    })
                    return
                }

                if (copyName.length > 30) {
                    me.$bkMessage({
                        theme: 'error',
                        message: '名称不得大于三十个字符'
                    })
                    return
                }

                this.copyTemplate()
            },

            /**
             * 提交模板集复制
             */
            async copyTemplate () {
                const backup = []
                backup.splice(0, backup.length, ...this.templateList)

                this.isCopying = true
                try {
                    await this.$store.dispatch('templateset/copyTemplate', {
                        projectId: this.projectId,
                        templateId: this.curCopyTemplate.id,
                        name: this.copyName
                    })

                    this.$bkMessage({
                        theme: 'success',
                        message: '复制成功！'
                    })

                    this.templateList.splice(0, this.templateList.length, ...[])
                    this.templateListCache.splice(0, this.templateListCache.length, ...[])
                    this.isLoading = true
                    this.getTemplateList(true)
                } catch (e) {
                    this.isLoading = false
                    this.templateList.splice(0, this.templateList.length, ...backup)
                    this.templateListCache.splice(0, this.templateListCache.length, ...backup)
                    catchErrorHandler(e, this)
                } finally {
                    this.hideCopy()
                    this.isCopying = false
                }
            },

            /**
             * 关闭复制弹层
             */
            hideCopy () {
                this.curCopyTemplate = Object.assign({}, {})
                this.copyName = ''
                this.copyDialogConf.isShow = false
            },

            /**
             * 显示选择命名空间弹层
             *
             * @param {Object} template 当前 template
             */
            async showChooseDialog (template) {
                if (!template.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: template.id,
                        resource_name: template.name,
                        resource_type: 'templates'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                // 清除弹层中的选中状态，不需要清除已选择的 ns 的状态
                this.clearCandidateNamespaceStatus()

                // 之前没选择过，那么展开第一个
                this.delInstanceDialogConf.title = `删除【${template.name}】模板集的实例`
                this.delInstanceDialogConf.isShow = true
                this.curDelInstanceTemplate = Object.assign({}, template)

                this.fetchTemplatesetVerList()
            },

            /**
             * 关闭选择命名空间弹层
             */
            cancelDelInstance () {
                this.tplsetVerList.splice(0, this.tplsetVerList.length, ...[])
                this.tplsetVerIndex = -1
                this.tplsetVerId = ''
                this.tplList.splice(0, this.tplList.length, ...[])
                this.tplIndex = -1
                this.tplId = ''
                this.tplCategory = ''
                this.candidateNamespaceList.splice(0, this.candidateNamespaceList.length, ...[])
                this.showNamespaceContainer = false
                this.delInstanceDialogConf.isShow = false
                this.namespaceListTmp = Object.assign({}, {})
            },

            /**
             * 获取模板集版本
             */
            async fetchTemplatesetVerList () {
                try {
                    this.isLoadingTplsetVer = true
                    this.tplsetVerList.splice(0, this.tplsetVerList.length, ...[])
                    const res = await this.$store.dispatch('templateset/getTemplatesetVerList', {
                        projectId: this.projectId,
                        templateId: this.curDelInstanceTemplate.id,
                        hasFilter: true
                    })

                    const list = res.data.results || []
                    list.forEach(item => {
                        this.tplsetVerList.push({
                            id: item.id,
                            name: item.version,
                            version: item.version,
                            template_id: item.template_id
                        })
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    setTimeout(() => {
                        this.isLoadingTplsetVer = false
                    }, 600)
                }
            },

            /**
             * 访问模板集首页
             * @param  {object} template 当前模板集对象
             */
            async goTemplateIndex (template) {
                if (!template.permissions.view) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: template.id,
                        resource_name: template.name,
                        resource_type: 'templates'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                const projectKind = await this.getProjectKind(this.projectId)

                if (projectKind === PROJECT_K8S) {
                    this.$router.push({
                        name: 'k8sTemplatesetDeployment',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode,
                            templateId: template.id
                        }
                    })
                } else if (projectKind === PROJECT_MESOS) {
                    this.$router.push({
                        name: 'mesosTemplatesetApplication',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode,
                            templateId: template.id
                        }
                    })
                } else {
                    this.$bkMessage({
                        theme: 'error',
                        message: '获取项目信息失败！'
                    })
                }
            },

            /**
             * 切换模板集下拉框
             * @param {number} index 索引
             * @param {Object} data 当前下拉框数据
             */
            async changeTplset (index, data) {
                try {
                    const res = await this.$store.dispatch('templateset/getTemplateInsResourceById', {
                        projectId: this.projectId,
                        templateId: data.template_id,
                        showVerName: data.name
                    })

                    const list = []
                    Object.keys(res.data.data || {}).forEach(key => {
                        res.data.data[key].forEach(item => {
                            list.push({
                                id: item.id,
                                name: `${key}:${item.name}`
                            })
                        })
                    })

                    if (list.length) {
                        list.unshift({
                            id: 0,
                            name: '全部'
                        })
                    }

                    this.tplsetVerId = data.id
                    this.tplList.splice(0, this.tplList.length, ...list)
                    this.tplIndex = -1
                    this.tplId = ''
                    this.tplCategory = ''
                    this.showNamespaceContainer = false
                    this.candidateNamespaceList.splice(0, this.candidateNamespaceList.length, ...[])
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 切换模板下拉框
             * @param {number} index 索引
             * @param {Object} data 当前下拉框数据
             */
            async changeTpl (index, data) {
                if (this.tplId === data.id) {
                    return
                }

                if (data.id === 0) {
                    this.tplId = 0
                    this.tplCategory = 'ALL'
                } else {
                    this.tplId = data.id
                    this.tplCategory = data.name.split(':')[0]
                }

                try {
                    const res = await this.$store.dispatch('templateset/getNamespaceList4DelInstance', {
                        projectId: this.projectId,
                        tplMusterId: this.curDelInstanceTemplate.id,
                        tplsetVerId: this.tplsetVerId,
                        tplId: this.tplId === 0 ? this.tplList[1].id : this.tplId,
                        category: this.tplCategory
                    })

                    this.candidateNamespaceList.splice(0, this.candidateNamespaceList.length, ...[])
                    this.namespaceListTmp = Object.assign({}, {})

                    const list = res.data
                    list.forEach((item, index) => {
                        // 展开第一个
                        this.candidateNamespaceList.push({ ...item, isOpen: index === 0 })
                    })
                    this.showNamespaceContainer = true
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 清除弹层中 namespace trigger 的展开以及 namespace 的选中
             */
            clearCandidateNamespaceStatus () {
                const list = this.candidateNamespaceList
                list.forEach(item => {
                    item.isOpen = false
                    item.results.forEach(ns => {
                        ns.isChoose = false
                    })
                })

                this.candidateNamespaceList.splice(0, this.candidateNamespaceList.length, ...list)
                this.namespaceListTmp = Object.assign({}, {})
            },

            /**
             * 在弹层中选择命名空间
             * @param {number} index candidateNamespaceList 的索引
             * @param {Object} namespace 当前点击的这个 namespace
             * @param {number} i 当前点击的这个 namespace 在 item.results 的索引
             */
            selectNamespaceInDialog (index, namespace, i) {
                namespace.isChoose = !namespace.isChoose
                this.$set(this.candidateNamespaceList[index].results, i, namespace)
                if (this.namespaceListTmp[`${namespace.env_type}_${namespace.id}`]) {
                    delete this.namespaceListTmp[`${namespace.env_type}_${namespace.id}`]
                } else {
                    this.namespaceListTmp[`${namespace.env_type}_${namespace.id}`] = {
                        ...namespace,
                        candidateIndex: index,
                        index: i
                    }
                }
            },

            /**
             * 在弹层中全选命名空间
             * @param {Object} item 当前的 candidateNamespace 对象
             * @param {number} index 当前的 candidateNamespace 对象在 candidateNamespaceList 中的索引
             */
            selectAll (item, index) {
                this.collapseTrigger()
                item.results.forEach((ns, i) => {
                    ns.isChoose = true
                    this.namespaceListTmp[`${ns.env_type}_${ns.id}`] = {
                        ...ns,
                        candidateIndex: index,
                        index: i
                    }
                })
                item.isOpen = true
                this.$set(this.candidateNamespaceList, index, item)
            },

            /**
             * 在弹层中反选命名空间
             * @param {Object} item 当前的 candidateNamespace 对象
             * @param {number} index 当前的 candidateNamespace 对象在 candidateNamespaceList 中的索引
             */
            selectInvert (item, index) {
                this.collapseTrigger()
                item.results.forEach((ns, i) => {
                    ns.isChoose = !ns.isChoose
                    if (this.namespaceListTmp[`${ns.env_type}_${ns.id}`]) {
                        delete this.namespaceListTmp[`${ns.env_type}_${ns.id}`]
                    } else {
                        this.namespaceListTmp[`${ns.env_type}_${ns.id}`] = {
                            ...ns,
                            candidateIndex: index,
                            index: i
                        }
                    }
                })
                item.isOpen = true
                this.$set(this.candidateNamespaceList, index, item)
            },

            /**
             * 收起所有的 trigger
             */
            collapseTrigger () {
                const list = this.candidateNamespaceList
                list.forEach(item => {
                    item.isOpen = false
                })
                this.candidateNamespaceList.splice(0, this.candidateNamespaceList.length, ...list)
            },

            /**
             * 选择命名空间弹层 trigger 点击事件
             * @param {Object} item 当前 namespace 对象
             * @param {number} index 当前 namespace 对象的索引
             */
            triggerHandler (item, index) {
                this.collapseTrigger()
                item.isOpen = !item.isOpen
                this.$set(this.candidateNamespaceList, index, item)
            },

            /**
             * 删除命名空间弹层确认
             */
            async confirmDelInstance () {
                const me = this
                const list = Object.keys(this.namespaceListTmp)

                if (this.tplsetVerIndex === -1) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择模板集版本'
                    })
                    return
                }
                if (this.tplIndex === -1) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择模板'
                    })
                    return
                }
                if (list.length === 0) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择命名空间'
                    })
                    return
                }

                this.$bkInfo({
                    title: '确定删除实例？',
                    async confirmFn () {
                        me.deleteInstance()
                    }
                })
            },

            /**
             * 删除实例
             */
            async deleteInstance () {
                const list = Object.keys(this.namespaceListTmp)
                const projectKind = await this.getProjectKind(this.projectId)
                const params = {
                    projectId: this.projectId,
                    tplMusterId: this.curDelInstanceTemplate.id,
                    tplsetVerId: this.tplsetVerId,
                    tplId: this.tplId,
                    namespace_list: [],
                    category: this.tplCategory
                }

                list.forEach(key => {
                    params.namespace_list.push(this.namespaceListTmp[key].id)
                })

                let isRedirect = false

                if (this.tplId === 0) {
                    const idList = []
                    this.tplList.forEach((item, index) => {
                        // 第 0 个是 all
                        if (index !== 0) {
                            const prefix = item.name.split(':')[0]
                            idList.push({
                                id: item.id,
                                category: prefix
                            })
                            if (prefix === 'application' || prefix === 'deployment') {
                                isRedirect = true
                            }
                        }
                    })
                    params.id_list = idList
                    params.category = 'all'
                }

                this.isDeleting = true

                try {
                    await this.$store.dispatch('templateset/delNamespaceInDelInstance', params)

                    this.$bkMessage({
                        theme: 'success',
                        message: '删除成功！'
                    })

                    if (this.tplCategory === 'application' || this.tplCategory === 'deployment' || isRedirect) {
                        this.$router.push({
                            name: projectKind === 1 ? 'deployments' : 'mesos',
                            params: {
                                projectId: this.projectId,
                                projectCode: this.projectCode,
                                tplsetId: this.curDelInstanceTemplate.id
                            }
                        })
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDeleting = false
                    if (!isRedirect) {
                        this.isLoading = true
                        this.templateList.splice(0, this.templateList.length, ...[])
                        this.templateListCache.splice(0, this.templateListCache.length, ...[])
                        this.cancelDelInstance()
                        this.getTemplateList(true)
                    }
                }
            },

            /**
             * 重置分页配置数据
             */
            resetPageConf () {
                this.pageConf.curPage = 1
                this.pageConf.pageSize = 10
                this.pageConf.hasNext = false
            },

            /**
             * 搜索列表
             */
            search () {
                this.resetPageConf()
                this.getTemplateList(true)
            },

            // 获取模板集列表搜索参数
            getQueryString () {
                const offset = (this.pageConf.curPage - 1) * this.pageConf.pageSize
                if (!this.searchKeyword) {
                    return `offset=${offset}&limit=${this.pageConf.pageSize}`
                } else {
                    return `offset=${offset}&limit=${this.pageConf.pageSize}&search=${this.searchKeyword}`
                }
            },

            /**
             * 获取模板集列表
             * @params {boolean} isRelaod 是否重新加载数据
             */
            async getTemplateList (isReload) {
                const projectId = this.projectId
                const TEMPLATE_ITEM_HEIGHT = 111
                const SCROLL_PLACEHOLDER_HEIGHT = 60

                // 清空数据，重置分页配置信息
                if (isReload) {
                    this.resetPageConf()
                    this.isListReload = true
                    window.scrollTo(0, 0)
                }
                try {
                    const queryString = this.getQueryString()
                    const res = await this.$store.dispatch('templateset/getTemplateList', { projectId, queryString })
                    const data = res.data

                    // 清空数据，重置分页配置信息
                    if (isReload) {
                        this.templateList.splice(0, this.templateList.length)
                    }

                    data.results.forEach(item => {
                        this.templateList.push(item)
                    })

                    this.permissions = res.permissions || {}
                    this.pageConf.hasNext = data.has_next
                    this.$nextTick(() => {
                        if (!isReload) {
                            const pageContentHeight = (this.pageConf.pageSize + 1) * TEMPLATE_ITEM_HEIGHT
                            const scrollTop = document.documentElement.scrollHeight - pageContentHeight * 2 + SCROLL_PLACEHOLDER_HEIGHT
                            window.scrollTo(0, scrollTop) // 回滚到最上一页数据底部
                        }
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isLoading = false
                    setTimeout(() => {
                        this.isListReload = false
                        this.isScrollLoading = false
                    }, 500)
                }
            },

            /**
             * 清除搜索
             */
            clearSearch () {
                this.searchKeyword = ''
                this.search()
            },

            /**
             * 获取项目类型
             * @param  {number} id 项目ID
             * @return {number}  项目类型
             */
            async getProjectKind (id) {
                const curProject = this.curProject
                let kind = 0
                if (curProject && curProject.project_id === id) {
                    kind = curProject.kind
                } else {
                    const projects = this.onlineProjectList
                    for (const project of projects) {
                        if (project.project_id === id) {
                            kind = project.kind
                        }
                    }
                }
                return kind
            },

            /**
             * 创建模板集
             */
            async addTemplate () {
                if (!this.permissions.create) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'create',
                        resource_type: 'templates'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                const projectKind = await this.getProjectKind(this.projectId)
                if (projectKind === PROJECT_K8S) {
                    this.$router.push({
                        name: 'k8sTemplatesetDeployment',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode,
                            templateId: 0
                        }
                    })
                } else if (projectKind === PROJECT_MESOS) {
                    this.$router.push({
                        name: 'mesosTemplatesetApplication',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode,
                            templateId: 0
                        }
                    })
                } else {
                    this.$bkMessage({
                        theme: 'error',
                        message: '获取项目信息失败！'
                    })
                }
            }
        }
    }
</script>
<style scoped>
    @import './templateset.css';
</style>
