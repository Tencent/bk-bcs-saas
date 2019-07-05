<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-helm-title">
                <a class="bk-icon icon-arrows-left back" @click="goTplList"></a>
                <span>Chart部署</span>
            </div>
        </div>

        <div class="biz-content-wrapper" v-bkloading="{ isLoading: createInstanceLoading }">
            <div>
                <div class="biz-helm-header">
                    <div class="left">
                        <svg style="display: none;">
                            <title>模板集默认图标</title>
                            <symbol id="biz-set-icon" viewBox="0 0 32 32">
                                <path d="M6 3v3h-3v23h23v-3h3v-23h-23zM24 24v3h-19v-19h19v16zM27 24h-1v-18h-18v-1h19v19z"></path>
                                <path d="M13.688 18.313h-6v6h6v-6z"></path>
                                <path d="M21.313 10.688h-6v13.625h6v-13.625z"></path>
                                <path d="M13.688 10.688h-6v6h6v-6z"></path>
                            </symbol>
                        </svg>
                        <div class="info">
                            <div class="logo-wrapper" v-if="curTpl.icon && isImage(curTpl.icon)" @click="gotoHelmTplDetail">
                                <img :src="curTpl.icon" style="width: 100px;">
                            </div>
                            <svg class="logo" v-else>
                                <use xlink:href="#biz-set-icon"></use>
                            </svg>

                            <div class="title">{{curTpl.name}}</div>
                            <p>
                                <a class="bk-text-button f12" href="javascript:void(0);" @click="gotoHelmTplDetail">查看Chart详情</a>
                            </p>
                            <div class="desc" :title="curTpl.description">
                                <span>简介：</span>
                                {{curTpl.description || '--'}}
                            </div>
                        </div>
                    </div>

                    <div class="right">
                        <div class="bk-collapse biz-collapse" style="border-top: none;">
                            <div class="bk-collapse-item bk-collapse-item-active">
                                <div class="bk-collapse-item-header" style="cursor: default; color: #737987;">
                                    配置选项
                                </div>
                                <div class="bk-collapse-item-content" style="padding: 15px;">
                                    <div class="config-box">
                                        <div class="inner">
                                            <div class="inner-item">
                                                <label class="title">名称</label>
                                                <input type="text" class="bk-form-input" v-model="appName">
                                            </div>

                                            <div class="inner-item">
                                                <label class="title">版本</label>
                                                <div>
                                                    <bk-selector
                                                        style="width: 225px; display: inline-block; vertical-align: middle;"
                                                        :placeholder="'请选择'"
                                                        :selected.sync="tplsetVerIndex"
                                                        :list="curTplVersions"
                                                        :setting-key="'id'"
                                                        :is-loading="isTplVerLoading"
                                                        :display-key="'version'"
                                                        @item-selected="getTplDetail">
                                                    </bk-selector>
                                                    <button class="bk-button bk-default is-outline is-icon" v-bktooltips.top="'同步仓库'" @click="syncHelmTpl">
                                                        <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-default" style="margin-top: -3px;" v-if="isTplSynLoading">
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
                                            </div>
                                        </div>
                                        <div class="inner">
                                            <label class="title">命名空间</label>
                                            <div>
                                                <bk-selector
                                                    style="width: 557px;"
                                                    :placeholder="'请选择'"
                                                    :searchable="true"
                                                    :selected.sync="namespaceId"
                                                    :field-type="'namespace'"
                                                    :list="namespaceList"
                                                    :filter-list="initedList"
                                                    :setting-key="'id'"
                                                    :display-key="'name'"
                                                    @item-selected="getClusterInfo">
                                                </bk-selector>
                                            </div>
                                            <p class="biz-tip f13 mt5" id="cluster-info" v-if="clusterInfo" v-html="clusterInfo"></p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <template v-if="tplsetVerIndex">
                    <div class="action-box">
                        <div class="title">
                            Helm参数
                        </div>
                    </div>
                    <div slot="content" class="mt10" style="min-height: 180px;">
                        <bk-tab
                            :type="'fill'"
                            :size="'small'"
                            :active-name.sync="curEditMode"
                            @tab-changed="helmModeChangeHandler">
                            <bk-tabpanel name="yaml-mode" title="Yaml模式">
                                <div style="width: 100%; min-height: 600px;" v-bkloading="{ isLoading: isSyncYamlLoading }">
                                    <p class="biz-tip p15" style="color: #63656E; overflow: hidden;">
                                        <i class="bk-icon icon-info-circle biz-warning-text mr5"></i>
                                        Yaml初始值为创建时Chart中values.yaml内容，后续更新部署以该Yaml内容为准，Yaml内容最终通过`--values`选项传递给`helm template`命令
                                    </p>
                                    <ace
                                        v-if="curEditMode === 'yaml-mode'"
                                        :value="curTplYaml"
                                        :width="yamlConfig.width"
                                        :height="yamlConfig.height"
                                        :lang="yamlConfig.lang"
                                        :read-only="yamlConfig.readOnly"
                                        :full-screen="yamlConfig.fullScreen"
                                        @init="editorInit">
                                    </ace>
                                </div>
                            </bk-tabpanel>
                            <bk-tabpanel name="form-mode" title="表单模式">
                                <p class="biz-tip p15" style="color: #63656E;">
                                    <i class="bk-icon icon-info-circle biz-warning-text mr5"></i>表单根据Chart中questions.yaml生成，表单修改后的数据会自动同步给Yaml模式
                                </p>
                                <template v-if="formData.questions">
                                    <bk-form-creater :form-data="formData" ref="bkFormCreater"></bk-form-creater>
                                </template>
                                <template v-else>
                                    <div class="biz-guard-box" v-if="!isQuestionsLoading">
                                        <span>您可以参考
                                            <a class="bk-text-button" :href="PROJECT_CONFIG.doc.writeQuestionsYaml" target="_blank">指引</a>
                                            通过表单模式配置您的Helm Release 参数，
                                        </span>
                                        <span>也可以通过<a href="javascript:void(0)" class="bk-text-button" @click="editYaml">Yaml模式</a>直接修改Helm Release参数</span>
                                    </div>
                                </template>
                            </bk-tabpanel>
                        </bk-tab>
                    </div>
                </template>

                <div class="create-wrapper">
                    <bk-button type="primary" title="部署" @click="createApp">
                        部署
                    </bk-button>
                    <bk-button type="default" title="预览" @click="showPreview">
                        预览
                    </bk-button>
                    <bk-button type="default" title="取消" @click="goBack">
                        取消
                    </bk-button>
                </div>
            </div>
        </div>

        <bk-sideslider
            :is-show.sync="previewEditorConfig.isShow"
            :title="previewEditorConfig.title"
            :quick-close="true"
            :width="1000">
            <div slot="content" :style="{ height: `${winHeight - 70}px` }" v-bkloading="{ isLoading: previewInstanceLoading }">
                <template v-if="tplPreviewList.length">
                    <div class="biz-resource-wrapper" style="height: 100%;">
                        <div class="tree-box" style="width: 320px;">
                            <bk-tree
                                ref="tree1"
                                :data="treeData"
                                :node-key="'id'"
                                :has-border="true"
                                @on-click="getFileDetail">
                            </bk-tree>
                        </div>
                        <div class="resource-box">
                            <div class="biz-code-wrapper" style="height: 100%;">
                                <ace
                                    :value="curReourceFile.value"
                                    :width="editorConfig.width"
                                    :height="editorConfig.height"
                                    :lang="editorConfig.lang"
                                    :read-only="editorConfig.readOnly"
                                    :full-screen="editorConfig.fullScreen">
                                </ace>
                            </div>
                        </div>
                    </div>
                </template>
                <p class="biz-no-data" v-else>无数据</p>
            </div>
        </bk-sideslider>

        <bk-dialog
            :is-show.sync="errorDialogConf.isShow"
            :width="750"
            :has-footet="false"
            :title="errorDialogConf.title"
            @cancel="hideErrorDialog">
            <div slot="content">
                <pre class="bk-intro bk-danger biz-error-message" v-if="errorDialogConf.message">
                    {{errorDialogConf.message}}
                </pre>
                <div class="biz-message" v-if="errorDialogConf.errorCode === 40031">
                    <h3>您需要：</h3>
                    <p>在集群页面，启用Helm</p>
                </div>
                <div class="biz-message" v-else-if="errorDialogConf.actionType === 'previewApp'">
                    <h3>您可以：</h3>
                    <p>1、检查Helm Chart是否存在语法错误</p>
                    <p>2、前往Helm Release列表页面，更新Helm Release</p>
                </div>
                <div class="biz-message" v-else>
                    <h3>您可以：</h3>
                    <p>1、更新Helm Chart，并推送到项目Chart仓库</p>
                    <p>2、前往Helm Release列表页面，更新Helm Release</p>
                </div>
            </div>
            <template slot="footer">
                <div class="biz-footer">
                    <bk-button type="primary" @click="hideErrorDialog">知道了</bk-button>
                </div>
            </template>
        </bk-dialog>
    </div>
</template>

<script>
    import MarkdownIt from 'markdown-it'
    import yamljs from 'js-yaml'
    import path2tree from '@open/common/path2tree'
    import baseMixin from '@open/mixins/helm/mixin-base'
    import { catchErrorHandler } from '@open/common/util'
    import moment from 'moment'

    export default {
        mixins: [baseMixin],
        data () {
            return {
                clusterInfo: '',
                curEditMode: '',
                curTplReadme: '',
                yamlEditor: null,
                yamlFile: '',
                curTplYaml: '',
                activeName: ['config'],
                collapseName: ['var'],
                tplsetVerList: [],
                formData: {},
                createInstanceLoading: false,
                previewList: [],
                tplPreviewList: [],
                difference: '',
                previewInstanceLoading: true,
                isQuestionsLoading: false,
                isSyncYamlLoading: true,
                isTplVerLoading: false,
                isRouterLeave: false,
                appName: '',
                winHeight: 0,
                editor: null,
                curTpl: {
                    data: {
                        name: ''
                    }
                },
                errorDialogConf: {
                    title: '',
                    isShow: false,
                    message: '',
                    errorCode: 0
                },
                curProjectId: '',
                previewEditorConfig: {
                    isShow: false,
                    title: '预览',
                    width: '100%',
                    height: '100%',
                    lang: 'yaml',
                    readOnly: true,
                    fullScreen: false,
                    value: '',
                    editors: []
                },
                initedList: [],
                yamlConfig: {
                    isShow: false,
                    title: '预览',
                    width: '100%',
                    height: '700',
                    lang: 'yaml',
                    readOnly: false,
                    fullScreen: false,
                    value: '',
                    editors: []
                },
                curReourceFile: {
                    name: '',
                    value: ''
                },
                editorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'yaml',
                    readOnly: true,
                    fullScreen: false,
                    values: [],
                    editors: []
                },
                curTplVersions: [],
                tplsetVerIndex: '',
                namespaceId: '',
                answers: {},
                treeData: [],
                namespaceList: [],
                isTplSynLoading: false,
                curLabelList: [
                    {
                        key: '',
                        value: ''
                    }
                ],
                appAction: {
                    create: '部署',
                    noop: '',
                    update: '更新',
                    rollback: '回滚',
                    delete: '删除',
                    destroy: '删除'
                }
            }
        },
        computed: {
            curProject () {
                return this.$store.state.curProject
            },
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            tplList () {
                return this.$store.state.helm.tplList
            }
        },
        async mounted () {
            const tplId = this.$route.params.tplId
            const uid = moment().format('YYMMDDhhmm')

            this.isRouterLeave = false
            this.curTpl = await this.getTplById(tplId)
            this.appName = `${this.curTpl.name}-${uid}`
            this.getTplVersions(tplId)
            this.getNamespaceList(tplId)
            this.winHeight = window.innerHeight
        },
        beforeRouteLeave (to, from, next) {
            this.isRouterLeave = true
            next()
        },
        beforeDestroy () {
            this.isRouterLeave = true
        },
        methods: {
            /**
             * 返回chart 模版列表
             */
            goTplList () {
                const projectCode = this.$route.params.projectCode
                this.$router.push({
                    name: 'helmTplList',
                    params: {
                        projectCode: projectCode
                    }
                })
            },

            /**
             * 访问模板详情
             */
            gotoHelmTplDetail () {
                const tplId = this.$route.params.tplId
                const projectCode = this.projectCode
                const href = `${DEVOPS_HOST}/console/bcs/${projectCode}/helm/tpl/${tplId}`
                window.open(href, '_blank')
            },

            /**
             * 隐藏错误弹窗
             */
            hideErrorDialog () {
                this.errorDialogConf.isShow = false
            },

            /**
             * 获取集群信息
             * @param  {number} index 索引
             * @param  {object} data 集群
             */
            async getClusterInfo (index, data) {
                const clusterId = data.cluster_id
                const projectId = this.projectId

                this.clusterInfo = ''

                try {
                    const res = await this.$store.dispatch('helm/getClusterInfo', { projectId, clusterId })
                    const clusterInfo = res.data.note
                    const md = new MarkdownIt({
                        linkify: false
                    })

                    this.clusterInfo = md.render(clusterInfo)
                    this.$nextTick(() => {
                        // 处理链接情况
                        const markdownDom = document.getElementById('cluster-info')
                        markdownDom.querySelectorAll('a').forEach(item => {
                            item.target = '_blank'
                            item.className = 'bk-text-button'
                        })
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取文件详情
             * @param  {object} file 文件
             */
            getFileDetail (file) {
                if (file.hasOwnProperty('value')) {
                    this.curReourceFile = file
                }
            },

            /**
             * 从本地选择yaml文件
             */
            selectYaml (event) {
                const file = event.target.files[0]
                if (file) {
                    const fileReader = new FileReader()
                    fileReader.onload = (e) => {
                        this.curTplYaml = e.target.result
                        this.yamlConfig.isShow = true
                    }
                    fileReader.readAsText(file)
                }
            },

            /**
             * 编辑模式变化回调
             */
            helmModeChangeHandler (name) {
                if (name === 'yaml-mode') {
                    this.curTplYaml && this.editYaml()
                } else {
                    this.saveYaml()
                }
            },

            /**
             * 编辑yamml
             */
            async editYaml () {
                this.curEditMode = 'yaml-mode'
                let formData = []

                this.isSyncYamlLoading = true
                // 将数据配置的数据和yaml的数据进行合并同步
                if (this.$refs.bkFormCreater) {
                    formData = this.$refs.bkFormCreater.getFormData()
                }

                this.yamlConfig.isShow = true

                try {
                    const res = await this.$store.dispatch('helm/syncJsonToYaml', {
                        json: formData,
                        yaml: this.curTplYaml
                    })
                    this.curTplYaml = res.data.yaml
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    setTimeout(() => {
                        this.isSyncYamlLoading = false
                    }, 500)
                }
            },

            /**
             * 检查yaml
             */
            checkYaml () {
                const editor = this.yamlEditor
                const yaml = editor.getValue()

                if (!yaml) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入YAML!'
                    })
                    return false
                }

                try {
                    yamljs.load(yaml)
                } catch (err) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入合法的YAML!'
                    })
                    return false
                }

                // 显示错误提示
                const annot = editor.getSession().getAnnotations()
                if (annot && annot.length) {
                    editor.gotoLine(annot[0].row, annot[0].column, true)
                    return false
                }
                return true
            },

            /**
             * 保存yaml
             */
            saveYaml () {
                if (!this.checkYaml()) {
                    return false
                }
                const editor = this.yamlEditor
                const yaml = editor.getValue()
                let yamlData = {}

                try {
                    yamlData = yamljs.load(yaml)
                } catch (err) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入合法的YAML!'
                    })
                    return false
                }

                // 同步表单到yaml数据配置
                if (yaml) {
                    yamlData = yamljs.load(yaml)
                }
                if (this.$refs.bkFormCreater) {
                    const formData = this.$refs.bkFormCreater.getFormData()
                    formData.forEach(formItem => {
                        const path = formItem.name
                        if (this.hasProperty(yamlData, path)) {
                            formItem.value = this.getProperty(yamlData, path)
                        }
                    })
                    this.setFormData(formData)
                }
                this.yamlFile = yaml
                this.yamlConfig.isShow = false
            },

            /**
             * 设置formCreater的值
             * @param {array} fieldset 字段数据
             */
            setFormData (fieldset) {
                const questions = JSON.parse(JSON.stringify(this.formData))
                if (questions.questions) {
                    questions.questions.forEach(question => {
                        if (fieldset && fieldset.length) {
                            fieldset.forEach(item => {
                                if (question.variable === item.name) {
                                    question.default = item.value
                                }
                            })
                        }

                        if (question.subquestions) {
                            question.subquestions.forEach(subQuestion => {
                                if (fieldset && fieldset.length) {
                                    fieldset.forEach(item => {
                                        if (subQuestion.variable === item.name) {
                                            subQuestion.default = item.value
                                        }
                                    })
                                }
                            })
                        }
                    })
                }
                this.formData = questions
            },

            /**
             * 隐藏yaml编辑
             */
            hideYaml () {
                this.yamlConfig.isShow = false
            },

            /**
             * 编辑器初始化成功回调
             * @param  {object} editor ace
             */
            editorInit (editor) {
                this.yamlEditor = editor
            },

            /**
             * 获取模板
             * @param  {number} id 模板ID
             * @return {object} result 模板
             */
            async getTplById (id) {
                let list = this.tplList

                // 如果没有缓存，获取远程数据
                if (!list.length) {
                    try {
                        const projectId = this.projectId
                        const res = await this.$store.dispatch('helm/asyncGetTplList', projectId)
                        list = res.data
                    } catch (e) {
                        catchErrorHandler(e, this)
                    }
                }

                const result = list.find(item => item.id === Number(id))
                return result || {}
            },

            /**
             * 根据版本号获取模板详情
             * @param  {number} index 索引
             * @param  {object} data 数据
             */
            async getTplDetail (index, data) {
                const list = []
                const projectId = this.projectId
                const version = index
                const chartId = this.$route.params.tplId

                this.isQuestionsLoading = true

                try {
                    const res = await this.$store.dispatch('helm/getChartByVersion', { projectId, chartId, version })
                    const tplData = res.data
                    const files = res.data.data.files
                    const tplName = tplData.name
                    this.formData = res.data.data.questions

                    for (const key in files) {
                        list.push({
                            name: key,
                            value: files[key]
                        })
                    }

                    this.previewList.splice(0, this.previewList.length, ...list)
                    this.curTplReadme = files[`${tplName}/README.md`]
                    this.curTplYaml = files[`${tplName}/values.yaml`]
                    this.yamlFile = files[`${tplName}/values.yaml`]

                    this.editYaml()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isQuestionsLoading = false
                }
            },

            /**
             * 同步仓库
             */
            async syncHelmTpl () {
                if (this.isTplSynLoading) {
                    return false
                }

                this.isTplSynLoading = true
                try {
                    await this.$store.dispatch('helm/syncHelmTpl', { projectId: this.projectId })

                    const tplId = this.$route.params.tplId
                    this.$bkMessage({
                        theme: 'success',
                        message: '同步成功！'
                    })

                    setTimeout(() => {
                        this.isTplVerLoading = true
                        this.getTplVersions(tplId)
                        this.tplsetVerIndex = ''
                    }, 1000)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    setTimeout(() => {
                        this.isTplSynLoading = false
                    }, 1000)
                }
            },

            /**
             * 获取模板版本列表
             * @param  {number} tplId 模板ID
             */
            async getTplVersions (tplId) {
                const projectId = this.projectId
                try {
                    const res = await this.$store.dispatch('helm/getTplVersions', { projectId, tplId })
                    this.curTplVersions = res.data.results
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    setTimeout(() => {
                        this.isTplVerLoading = false
                    }, 1000)
                }
            },

            /**
             * 获取命名空间列表
             */
            async getNamespaceList (chartId) {
                const projectId = this.projectId

                try {
                    const res = await this.$store.dispatch('helm/getNamespaceListByChart', { projectId, chartId })

                    this.initedList = []
                    res.data.forEach(item => {
                        if (item.children) {
                            item.children.forEach(child => {
                                if (child.has_initialized) {
                                    child.name = `${child.name} （已部署）`
                                    this.initedList.push(child.id)
                                }
                            })
                        }
                    })
                    this.namespaceList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 检查数据
             * @param  {object} data 实例化数据
             * @return {boolean} true/false
             */
            checkFormData (data) {
                if (this.$refs.bkFormCreater) {
                    if (!this.$refs.bkFormCreater.checkValid()) {
                        return false
                    }
                }
                if (!data.name) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入名称！'
                    })
                    return false
                }

                if (!data.chart_version) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择版本！'
                    })
                    return false
                }

                if (!data.namespace_info) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择命名空间！'
                    })
                    return false
                }

                return true
            },

            /**
             * 获取实例化参数
             * @return {object} data 实例化参数
             */
            getAppParams () {
                let formData = []
                const customs = []
                for (const key in this.answers) {
                    customs.push({
                        name: key,
                        value: this.answers[key],
                        type: 'string'
                    })
                }
                if (this.curEditMode === 'yaml-mode') {
                    this.saveYaml()
                }

                if (this.$refs.bkFormCreater) {
                    if (this.$refs.bkFormCreater.checkValid()) {
                        formData = this.$refs.bkFormCreater.getFormData()
                    }
                }
                const data = {
                    name: this.appName,
                    namespace_info: this.namespaceId,
                    chart_version: this.tplsetVerIndex,
                    answers: formData,
                    customs: customs,
                    valuefile: this.yamlFile
                }
                return data
            },

            /**
             * 显示错误弹层
             * @param  {object} res ajax数据对象
             * @param  {string} title 错误提示
             * @param  {string} actionType 操作
             */
            showErrorDialog (res, title, actionType) {
                // 先检查集群是否注册到 BKE server。未注册则返回 code: 40031
                this.errorDialogConf.errorCode = res.code
                this.createInstanceLoading = false
                this.errorDialogConf.message = res.message || res.data.msg || res.statusText
                this.errorDialogConf.isShow = true
                this.previewEditorConfig.isShow = false
                this.errorDialogConf.title = title
                this.errorDialogConf.actionType = actionType
            },

            /**
             * 展示App异常信息
             * @param  {object} app 应用对象
             */
            showAppError (app) {
                let actionType = ''
                const res = {
                    code: 500,
                    message: ''
                }

                res.message = app.transitioning_message
                actionType = app.transitioning_action
                const title = `${app.name}${this.appAction[app.transitioning_action]}失败`
                this.showErrorDialog(res, title, actionType)
            },

            /**
             * 查看app状态，包括创建、更新、回滚、删除
             * @param  {object} app 应用对象
             */
            async checkAppStatus (app) {
                const projectId = this.projectId
                const appId = app.id

                if (this.isRouterLeave) {
                    return false
                }

                try {
                    const res = await this.$store.dispatch('helm/checkAppStatus', { projectId, appId })
                    const action = this.appAction[res.data.transitioning_action]

                    if (res.data.transitioning_on) {
                        setTimeout(() => {
                            this.checkAppStatus(app)
                        }, 2000)
                    } else {
                        if (res.data.transitioning_result) {
                            this.$bkMessage({
                                theme: 'success',
                                message: `${app.name}${action}成功`
                            })
                            // 返回helm首页
                            setTimeout(() => {
                                this.$router.push({
                                    name: 'helms'
                                })
                            }, 200)
                        } else {
                            this.createInstanceLoading = false
                            res.data.name = app.name || ''
                            this.showAppError(res.data)
                        }
                    }
                } catch (e) {
                    this.createInstanceLoading = false
                    this.showErrorDialog(e, '操作失败', 'reback')
                }
            },

            /**
             * 创建应用
             */
            async createApp () {
                if (this.curEditMode === 'yaml-mode' && !this.checkYaml()) {
                    return false
                }
                const projectId = this.projectId
                const data = this.getAppParams()
                if (!this.checkFormData(data)) {
                    return false
                }

                this.errorDialogConf.isShow = false
                this.errorDialogConf.message = ''
                this.errorDialogConf.errorCode = 0
                this.createInstanceLoading = true

                try {
                    const res = await this.$store.dispatch('helm/createApp', { projectId, data })
                    this.checkAppStatus(res.data)
                } catch (e) {
                    this.showErrorDialog(e, '部署失败', 'createApp')
                }
            },

            /**
             * 显示预览
             */
            async showPreview () {
                if (this.curEditMode === 'yaml-mode' && !this.checkYaml()) {
                    return false
                }
                const projectId = this.projectId
                const data = this.getAppParams()

                if (!this.checkFormData(data)) {
                    return false
                }

                this.previewEditorConfig.isShow = true
                this.previewInstanceLoading = true
                this.tplPreviewList = []
                this.difference = ''
                this.treeData = []

                try {
                    const res = await this.$store.dispatch('helm/previewCreateApp', { projectId, data })
                    this.previewEditorConfig.value = res.data.notes
                    for (const key in res.data.content) {
                        this.tplPreviewList.push({
                            name: key,
                            value: res.data.content[key]
                        })
                    }

                    const tree = path2tree(this.tplPreviewList)
                    this.treeData.push(tree)
                    this.difference = res.data.difference
                    if (this.tplPreviewList.length) {
                        this.curReourceFile = this.tplPreviewList[0]
                    }
                } catch (e) {
                    this.showErrorDialog(e, '预览失败', 'previewApp')
                } finally {
                    this.previewInstanceLoading = false
                }
            }
        }
    }
</script>

<style scoped>
    @import './common.css';
    @import './tpl-instance.css';
</style>
