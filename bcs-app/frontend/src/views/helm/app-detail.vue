<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-helm-title">
                <a class="bk-icon icon-arrows-left back" href="javascript:void(0);" @click="goToHelmIndex"></a>
                <span>{{curApp.name}}</span>
            </div>
        </div>

        <div class="biz-content-wrapper" v-bkloading="{ isLoading: updateInstanceLoading }">
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
                            <svg class="logo" @click="gotoHelmTplDetail" style="cursor: pointer;">
                                <use xlink:href="#biz-set-icon"></use>
                            </svg>
                            <div class="title">{{curApp.name}}</div>
                            <p>
                                <a class="bk-text-button f12" href="javascript:void(0);" @click="gotoHelmTplDetail">查看Chart详情</a>
                            </p>
                            <div class="desc" :title="curApp.description">
                                <span>简介：</span>
                                {{curApp.chart_info.description || '--'}}
                            </div>
                        </div>
                    </div>

                    <div class="right">
                        <div class="bk-collapse-item bk-collapse-item-active">
                            <div class="bk-collapse-item-header" style="cursor: default;">
                                配置选项
                            </div>
                            <div class="bk-collapse-item-content f13" style="padding: 15px;">
                                <div class="config-box">
                                    <div class="inner">
                                        <div class="inner-item">
                                            <label class="title">名称</label>
                                            <input type="text" class="bk-form-input" :value="curApp.name" readonly="readonly">
                                        </div>

                                        <div class="inner-item">
                                            <label class="title">版本</label>

                                            <div>
                                                <bk-selector
                                                    style="width: 225px; display: inline-block; vertical-align: middle;"
                                                    :placeholder="'请选择'"
                                                    :selected.sync="tplVersionId"
                                                    :list="curAppVersions"
                                                    :setting-key="'id'"
                                                    :is-loading="isAppVerLoading"
                                                    :display-key="'version'"
                                                    @item-selected="handlerVersionChange">
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
                                        <label class="title">
                                            命名空间
                                            <span class="ml10 biz-error-tip" v-if="!isNamespaceMatch && !isNamespaceLoading">
                                                （命名空间{{curApp.namespace}}不存在）
                                            </span>
                                        </label>
                                        <div>
                                            <bk-selector
                                                style="width: 557px;"
                                                :placeholder="'请选择'"
                                                :selected.sync="curApp.namespace_id"
                                                :disabled="true"
                                                :is-loading="isNamespaceLoading"
                                                :list="namespaceList"
                                                :setting-key="'id'"
                                                :display-key="'name'">
                                            </bk-selector>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="action-box">
                    <div class="title">
                        Helm参数
                    </div>
                </div>

                <div slot="content" class="mt10" style="min-height: 180px;">
                    <bk-tab
                        :type="'fill'"
                        :size="'small'"
                        :key="tplVersionId"
                        :active-name.sync="curEditMode"
                        @tab-changed="helmModeChangeHandler">
                        <bk-tabpanel name="yaml-mode" title="Yaml模式">
                            <span
                                slot="tag"
                                class="bk-icon icon-circle-shape biz-danger-text v-bk"
                                style="font-size: 10px;"
                                v-bktooltips.right="'Release参数与选中的Chart Version中values.yaml有区别'"
                                v-if="tplVersionId !== -1">
                            </span>
                            <div style="width: 100%; min-height: 600px;" v-bkloading="{ isLoading: isSyncYamlLoading }">
                                <p class="biz-tip m15" style="color: #63656E;">
                                    <i class="bk-icon icon-info-circle biz-warning-text mr5"></i>
                                    Yaml初始值为创建时Chart中values.yaml内容，后续更新部署以该Yaml内容为准，内容最终通过`--values`选项传递给`helm template`命令
                                </p>
                                <div v-if="tplVersionId !== -1" class="f14 mb15 ml15" style="color: #63656E;">
                                    <i class="bk-icon icon-eye biz-warning-text mr5"></i>
                                    您更改了Chart版本，<span class="bk-text-button" @click="showCodeDiffDialog">点击查看</span> Helm Release参数与选中的Chart Version中values.yaml区别
                                </div>
                                <ace
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
                                    <span>也可以通过<a href="javascript:void(0)" class="bk-text-button" @click="editYaml">Yaml模式</a>直接修改Helm Release参数
                                    </span>
                                </div>
                            </template>
                        </bk-tabpanel>
                    </bk-tab>
                </div>

                <div class="create-wrapper" v-if="!isNamespaceLoading && !isNamespaceMatch">
                    <bk-tooltip :content="'所属命名空间不存在，不可操作'" placement="top">
                        <bk-button type="primary" title="更新" :disabled="true">
                            更新
                        </bk-button>
                    </bk-tooltip>
                    <bk-tooltip :content="'所属命名空间不存在，不可操作'" placement="top">
                        <bk-button type="default" title="预览" :disabled="true">
                            预览
                        </bk-button>
                    </bk-tooltip>
                    <bk-button type="default" title="取消" @click="goToHelmIndex">
                        取消
                    </bk-button>
                </div>

                <div class="create-wrapper" v-else>
                    <bk-button type="primary" title="更新" @click="confirmUpdateApp" :disabled="isNamespaceLoading || !isNamespaceMatch">
                        更新
                    </bk-button>
                    <bk-button type="default" title="预览" @click="showPreview" :disabled="isNamespaceLoading || !isNamespaceMatch">
                        预览
                    </bk-button>
                    <bk-button type="default" title="取消" @click="goToHelmIndex">
                        取消
                    </bk-button>
                </div>
            </div>
        </div>

        <bk-sideslider
            :is-show.sync="previewEditorConfig.isShow"
            :title="previewEditorConfig.title"
            :quick-close="true"
            :width="900">
            <div slot="content" :style="{ height: `${winHeight - 70}px` }" v-bkloading="{ isLoading: previewLoading }">
                <template v-if="appPreviewList.length">
                    <div class="biz-resource-wrapper" style="height: 100%;">
                        <div class="tree-box" style="width: 250px;">
                            <bk-tree
                                :data="treeData"
                                :node-key="'name'"
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
                <p class="biz-no-data" style="padding: 100px 40px; text-align: center;" v-else>无数据</p>
            </div>
        </bk-sideslider>

        <bk-dialog
            width="900"
            :title="updateConfirmDialog.title"
            :close-icon="!updateInstanceLoading"
            :is-show.sync="updateConfirmDialog.isShow"
            @cancel="hideConfirmDialog">
            <template slot="content">
                <p class="biz-tip mb15 tl" style="color: #666;">Helm Release参数发生如下变化，请确认后再点击“确定”更新</p>
                <div class="difference-code" v-bkloading="{ isLoading: isDifferenceLoading }" v-if="isDifferenceLoading || difference">
                    <ace
                        :value="difference"
                        :width="updateConfirmDialog.width"
                        :height="updateConfirmDialog.height"
                        :lang="updateConfirmDialog.lang"
                        :read-only="updateConfirmDialog.readOnly"
                        :full-screen="updateConfirmDialog.fullScreen">
                    </ace>
                </div>
                <div class="difference-code" v-bkloading="{ isLoading: isDifferenceLoading }" v-else>
                    <ace
                        :value="'本次更新没有内容变化'"
                        :width="updateConfirmDialog.width"
                        :height="updateConfirmDialog.height"
                        :lang="updateConfirmDialog.lang"
                        :read-only="updateConfirmDialog.readOnly"
                        :full-screen="updateConfirmDialog.fullScreen">
                    </ace>
                </div>
                <p class="biz-tip mt15 tl biz-warning" v-if="isChartVersionChange">温馨提示：Helm Chart 版本已更改，请检查是否需要同步容器服务上Release 的参数</p>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template>
                        <button
                            :class="['bk-button bk-dialog-btn-confirm bk-primary', { 'is-disabled': isDifferenceLoading || updateInstanceLoading }]"
                            @click="updateApp">
                            {{updateInstanceLoading ? '更新中...' : '确定'}}
                        </button>
                        <button
                            :class="['bk-button bk-dialog-btn-cancel bk-default']"
                            @click="hideConfirmDialog">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

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
                <div class="biz-message" v-else>
                    <h3>您可以：</h3>
                    <p>1、更新Helm Chart，并推送到项目Chart仓库</p>
                    <p>2、重新更新</p>
                </div>
            </div>
            <template slot="footer">
                <div class="biz-footer">
                    <bk-button type="primary" @click="hideErrorDialog">知道了</bk-button>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="codeDialogConf.isShow"
            :width="1100"
            :has-header="false"
            :has-footet="false"
            :title="codeDialogConf.title"
            @cancel="hideCodeDiffDialog">
            <div slot="content">
                <div class="code-diff-header">
                    <h3>当前 Release 参数：</h3>
                    <h3>Chart 默认值：</h3>
                </div>
                <code-diff
                    :src-content="curEditYaml"
                    :target-content="curVersionYaml">
                </code-diff>
            </div>
            <template slot="footer">
                <div class="biz-footer">
                    <bk-button type="primary" @click="hideCodeDiffDialog" class="mr5">知道了</bk-button>
                </div>
            </template>
        </bk-dialog>
    </div>
</template>

<script>
    import yamljs from 'js-yaml'
    import path2tree from '@open/common/path2tree'
    import baseMixin from '@open/mixins/helm/mixin-base'
    import { catchErrorHandler } from '@open/common/util'
    import diff from '@open/components/diff'

    export default {
        components: {
            'code-diff': diff
        },
        mixins: [baseMixin],
        data () {
            return {
                tempProjectId: '',
                curTplReadme: '',
                curEditMode: 'yaml-mode',
                yamlEditor: null,
                yamlFile: '',
                curTplYaml: '',
                activeName: ['config'],
                collapseName: ['preview'],
                tplsetVerList: [],
                appPreviewList: [],
                isNamespaceLoading: true, // 命名空间加载中，如果没有命名空间，无法进行操作
                updateInstanceLoading: false,
                isDifferenceLoading: false,
                isQuestionsLoading: true,
                previewLoading: false,
                isNamespaceMatch: false, // 判断命名空间是否已经删除
                isRouterLeave: false,
                isTplSynLoading: false,
                isAppVerLoading: true,
                previewList: [],
                difference: '',
                isChartVersionChange: false,
                appName: '',
                tplVersionId: -1,
                formData: {},
                fieldset: [],
                winHeight: 0,
                editor: null,
                errorDialogConf: {
                    title: '',
                    isShow: false,
                    message: '',
                    errorCode: 0
                },
                codeDialogConf: {
                    title: '和当前版本对比',
                    isShow: false
                },
                curVersionYaml: '',
                curEditYaml: '',
                curReourceFile: {
                    name: '',
                    value: ''
                },
                updateConfirmDialog: {
                    title: '确认更新',
                    isShow: false,
                    width: '100%',
                    height: '100%',
                    lang: 'yaml',
                    closeIcon: true,
                    readOnly: true,
                    fullScreen: false,
                    values: [],
                    editors: []
                },
                curApp: {
                    created: '',
                    chart_info: {
                        description: ''
                    },
                    namespace_id: '',
                    release: {
                        id: '',
                        customs: [],
                        answers: {}
                    }
                },
                treeData: [],
                editorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'yaml',
                    readOnly: true,
                    fullScreen: false,
                    values: [],
                    editors: []
                },
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
                isSyncYamlLoading: false,
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
                curAppVersions: [],
                namespaceId: '',
                answers: {},
                namespaceList: [],
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
            },
            curLabelList () {
                const customs = this.curApp.release.customs
                const answers = {}
                const list = []
                customs.forEach(item => {
                    list.push({
                        key: item.name,
                        value: item.value
                    })
                    answers[item.name] = item.value
                })
                if (!list.length) {
                    list.push({
                        name: '',
                        value: ''
                    })
                }
                this.answers = answers
                return list
            }
        },
        async mounted () {
            const appId = this.$route.params.appId
            this.curApp = await this.getAppById(appId)
            this.getAppVersions(appId)
            this.getNamespaceList()
            this.winHeight = window.innerHeight
            this.editYaml()
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
             * 显示yaml对比
             */
            showCodeDiffDialog () {
                this.curEditYaml = this.yamlEditor.getValue()
                this.codeDialogConf.isShow = true
            },

            /**
             * 隐藏yaml对比
             */
            hideCodeDiffDialog () {
                this.codeDialogConf.isShow = false
            },

            /**
             * 访问模板详情
             */
            gotoHelmTplDetail () {
                const tplId = this.curApp.chart
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
             * 获取文件详情
             * @param  {object} file 文件
             */
            getFileDetail (file) {
                if (file.hasOwnProperty('value')) {
                    this.curReourceFile = file
                }
            },

            /**
             * 返回Helm应用首页
             */
            goToHelmIndex () {
                this.$router.push({
                    name: 'helms',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
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
                    this.editYaml()
                } else {
                    this.saveYaml()
                }
            },

            /**
             * 编辑yamml
             */
            async editYaml () {
                let formData = []

                this.curEditMode = 'yaml-mode'
                this.isSyncYamlLoading = true
                // 将数据配置的数据和yaml的数据进行合并同步
                if (this.$refs.bkFormCreater) {
                    formData = this.$refs.bkFormCreater.getFormData()
                }
                if (this.curTplYaml) {
                    yamljs.load(this.curTplYaml)
                }

                this.yamlConfig.isShow = true
                try {
                    const res = await this.$store.dispatch('helm/syncJsonToYaml', {
                        json: formData,
                        yaml: this.curTplYaml
                    })
                    this.curTplYaml = res.data.yaml
                    this.$nextTick(() => {
                        this.yamlEditor.gotoLine(0, 0)
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isSyncYamlLoading = false
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
                    // 通过load检测yaml是否合法
                    yamljs.load(yaml)
                } catch (err) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入合法的YAML!'
                    })
                    return false
                }

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
                let formData = []
                let yamlData = {}

                try {
                    // 通过load检测yaml是否合法
                    yamljs.load(yaml)
                } catch (err) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入合法的YAML!'
                    })
                    return false
                }

                // 同步到数据配置
                if (yaml) {
                    yamlData = yamljs.load(yaml)
                }
                if (this.$refs.bkFormCreater) {
                    formData = this.$refs.bkFormCreater.getFormData()
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
             * 获取应用
             * @param  {number} appId 应用ID
             * @return {object} result 应用
             */
            async getAppById (appId) {
                let result = {}
                const projectId = this.projectId

                this.isQuestionsLoading = true
                try {
                    const res = await this.$store.dispatch('helm/getAppById', { projectId, appId })
                    result = res.data
                    const files = result.release.chartVersionSnapshot.files
                    const tplName = result.release.chartVersionSnapshot.name
                    const questions = result.release.chartVersionSnapshot.questions

                    this.setPreviewList(files)
                    this.curTplReadme = files[`${tplName}/README.md`]
                    this.curTplYaml = result.valuefile
                    if (questions.questions) {
                        questions.questions.forEach(question => {
                            this.fieldset = result.release.answers
                            if (this.fieldset && this.fieldset.length) {
                                this.fieldset.forEach(item => {
                                    if (question.variable === item.name) {
                                        question.default = item.value
                                    }
                                })
                            }

                            if (question.subquestions) {
                                question.subquestions.forEach(subQuestion => {
                                    if (this.fieldset && this.fieldset.length) {
                                        this.fieldset.forEach(item => {
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
                    this.isQuestionsLoading = false
                } catch (e) {
                    if (e.status === 404) {
                        this.goToHelmIndex()
                    } else {
                        catchErrorHandler(e, this)
                    }
                    this.isQuestionsLoading = false
                }

                return result
            },

            /**
             * 切换应用版本号回调
             * @param  {number} index 索引
             * @param  {object} data 版本对象
             */
            async handlerVersionChange (index, data) {
                const projectId = this.projectId
                const appId = this.curApp.id
                const version = data.id
                const list = []

                this.curVersionYaml = ''
                try {
                    const res = await this.$store.dispatch('helm/getUpdateChartByVersion', {
                        projectId,
                        appId,
                        version
                    })

                    const files = res.data.data.files
                    const valueNames = [`${res.data.name}/values.yaml`, `${res.data.name}/values.yml`]
                    this.formData = res.data.data.questions

                    for (const key in files) {
                        list.push({
                            name: key,
                            value: files[key]
                        })
                        if (valueNames.includes(key)) {
                            this.curVersionYaml = files[key]
                        }
                    }
                    this.previewList.splice(0, this.previewList.length, ...list)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 设置预览文件
             * @param {array} files 文件
             */
            setPreviewList (files) {
                const list = []
                for (const key in files) {
                    list.push({
                        name: key,
                        value: files[key]
                    })
                }
                this.previewList.splice(0, this.previewList.length, ...list)
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
                    const appId = this.$route.params.appId
                    this.$bkMessage({
                        theme: 'success',
                        message: '同步成功！'
                    })

                    setTimeout(() => {
                        this.isAppVerLoading = true
                        this.getAppVersions(appId)
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
             * 获取应用版本列表
             * @param  {number} appId 应用ID
             */
            async getAppVersions (appId) {
                const projectId = this.projectId
                this.curAppVersions = []
                try {
                    const res = await this.$store.dispatch('helm/getUpdateVersions', { projectId, appId })
                    this.curAppVersions = res.data.results
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isAppVerLoading = false
                }
            },

            /**
             * 获取命名空间列表
             */
            async getNamespaceList () {
                const projectId = this.projectId
                this.isNamespaceLoading = true

                try {
                    const res = await this.$store.dispatch('helm/getNamespaceList', projectId)
                    const curNamespaceId = this.curApp.namespace_id
                    this.isNamespaceMatch = false
                    res.data.forEach(item => {
                        if (item.children) {
                            item.children.forEach(child => {
                                child.name = `${item.name} / ${child.name}`
                                if (child.id === curNamespaceId) {
                                    this.isNamespaceMatch = true
                                }
                            })
                        }
                    })
                    this.namespaceList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isNamespaceLoading = false
                }
            },

            /**
             * 显示确认更新弹窗
             */
            confirmUpdateApp () {
                if (this.curEditMode === 'yaml-mode' && !this.checkYaml()) {
                    return false
                }
                if (this.$refs.bkFormCreater && !(this.$refs.bkFormCreater.checkValid())) {
                    return false
                }
                this.isDifferenceLoading = true
                this.updateConfirmDialog.isShow = true
                this.getDifference()
            },

            /**
             * 获取应用参数
             * @return {object} params 应用参数
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
                    formData = this.$refs.bkFormCreater.getFormData()
                }

                const params = {
                    upgrade_verion: this.tplVersionId,
                    answers: formData,
                    customs: customs
                }

                params.valuefile = this.yamlFile || this.curTplYaml
                return params
            },

            /**
             * 隐藏确认更新弹窗
             */
            hideConfirmDialog () {
                if (this.updateInstanceLoading) {
                    return false
                }
                this.updateConfirmDialog.isShow = false
            },

            /**
             * 显示错误弹层
             * @param  {object} res ajax数据对象
             * @param  {string} title 错误提示
             * @param  {string} actionType 操作
             */
            showErrorDialog (res, title, actionType) {
                this.errorDialogConf.errorCode = res.code
                this.errorDialogConf.message = res.message || res.data.msg || res.statusText
                this.errorDialogConf.title = title
                this.errorDialogConf.isShow = true
                this.previewEditorConfig.isShow = false
                this.updateConfirmDialog.isShow = false
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
                            this.updateInstanceLoading = false
                            res.data.name = app.name || ''
                            this.showAppError(res.data)
                        }
                    }
                } catch (e) {
                    this.updateInstanceLoading = false
                    this.showErrorDialog(e, '操作失败', 'reback')
                }
            },

            /**
             * 更新应用
             */
            async updateApp () {
                if (this.isDifferenceLoading || this.updateInstanceLoading) {
                    return false
                }

                const params = this.getAppParams()
                const projectId = this.projectId
                const appId = this.$route.params.appId

                this.errorDialogConf.isShow = false
                this.errorDialogConf.message = ''
                this.errorDialogConf.errorCode = 0

                this.updateInstanceLoading = true
                this.updateConfirmDialog.isShow = false

                try {
                    const res = await this.$store.dispatch('helm/updateApp', {
                        projectId,
                        appId,
                        params
                    })
                    this.checkAppStatus(res.data)
                } catch (e) {
                    this.showErrorDialog(e, '更新失败', 'update')
                }
            },

            /**
             * 显示预览
             */
            async showPreview () {
                if (this.curEditMode === 'yaml-mode' && !this.checkYaml()) {
                    return false
                }
                if (this.$refs.bkFormCreater && !(this.$refs.bkFormCreater.checkValid())) {
                    return false
                }
                this.previewEditorConfig.isShow = true
                const params = this.getAppParams()
                const projectId = this.projectId
                const appId = this.$route.params.appId

                this.previewLoading = true
                this.appPreviewList = []
                this.difference = ''
                this.isChartVersionChange = false
                this.treeData = []

                try {
                    const res = await this.$store.dispatch('helm/previewApp', {
                        projectId,
                        appId,
                        params
                    })
                    for (const key in res.data.content) {
                        this.appPreviewList.push({
                            name: key,
                            value: res.data.content[key]
                        })
                    }
                    const tree = path2tree(this.appPreviewList)
                    this.treeData.push(tree)
                    this.difference = res.data.difference
                    this.isChartVersionChange = res.data.chart_version_changed
                    this.previewEditorConfig.value = res.data.notes
                    if (this.appPreviewList.length) {
                        this.curReourceFile = this.appPreviewList[0]
                    }
                } catch (e) {
                    this.showErrorDialog(e, '预览失败', 'preview')
                    this.previewEditorConfig.value = ''
                } finally {
                    this.previewLoading = false
                }
            },

            /**
             * 获取版本对比
             */
            async getDifference () {
                const params = this.getAppParams()
                const projectId = this.projectId
                const appId = this.$route.params.appId

                this.isDifferenceLoading = true
                this.difference = ''
                this.isChartVersionChange = ''

                try {
                    const res = await this.$store.dispatch('helm/previewApp', {
                        projectId,
                        appId,
                        params
                    })
                    this.difference = res.data.difference
                    this.isChartVersionChange = res.data.chart_version_changed
                } catch (e) {
                    this.showErrorDialog(e, 'Chart渲染失败', 'preUpdate')
                    this.updateConfirmDialog.value = ''
                } finally {
                    this.isDifferenceLoading = false
                }
            }
        }
    }
</script>

<style scoped>
    @import './app-detail.css';
</style>
