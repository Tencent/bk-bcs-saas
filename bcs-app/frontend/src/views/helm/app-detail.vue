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
                            <title>{{$t('模板集默认图标')}}</title>
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
                            <!-- <p>
                                <a class="bk-text-button f12" href="javascript:void(0);" @click="gotoHelmTplDetail">{{$t('查看Chart详情')}}</a>
                            </p> -->
                            <div class="desc" :title="curApp.description">
                                <span>Chart：</span>
                                <a class="bk-text-button f12 ml5" href="javascript:void(0);" @click="gotoHelmTplDetail">{{curApp.chart_info.name || '--'}}</a>
                            </div>
                            <div class="desc" :title="curApp.description">
                                <span>{{$t('简介')}}：</span>
                                {{curApp.chart_info.description || '--'}}
                            </div>
                        </div>
                    </div>

                    <div class="right">
                        <div class="bk-collapse-item bk-collapse-item-active">
                            <div class="bk-collapse-item-header" style="cursor: default;">
                                {{$t('配置选项')}}
                            </div>
                            <div class="bk-collapse-item-content f12" style="padding: 15px;">
                                <div class="config-box">
                                    <div class="inner">
                                        <div class="inner-item">
                                            <label class="title">{{$t('名称')}}</label>
                                            <input type="text" class="bk-form-input" :value="curApp.name" readonly="readonly">
                                        </div>

                                        <div class="inner-item">
                                            <label class="title">{{$t('版本')}}</label>

                                            <div>
                                                <bk-input
                                                    style="width: 225px;"
                                                    type="text"
                                                    :placeholder="$t('请选择')"
                                                    :value.sync="tplVersionId"
                                                    :is-select-mode="true"
                                                    :default-list="curAppVersions"
                                                    :setting-key="'id'"
                                                    :disabled="isTplSynLoading"
                                                    :display-key="'version'"
                                                    :search-key="'version'"
                                                    @item-selected="handlerVersionChange">
                                                </bk-input>

                                                <button class="bk-button bk-default is-outline is-icon" v-bktooltips.top="$t('同步仓库')" @click="syncHelmTpl">
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
                                        <div class="inner-item">
                                            <label class="title">{{$t('所属集群')}}</label>
                                            <input type="text" class="bk-form-input" :value="curClusterName" readonly="readonly">
                                        </div>
                                        <div class="inner-item">
                                            <label class="title">
                                                {{$t('命名空间')}}
                                                <span class="ml10 biz-error-tip" v-if="!isNamespaceMatch && !isNamespaceLoading">
                                                    （{{$t('此命名空间不存在')}}）
                                                </span>
                                            </label>
                                            <div>
                                                <input type="text" class="bk-form-input" :value="curApp.namespace" readonly="readonly">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="biz-expand-panel mt20 mb10">
                    <div class="header" @click="isShowCommandParams = !isShowCommandParams" style="line-height: 40px;">
                        {{$t('Helm命令行参数')}}
                        <div class="expand">
                            <i class="bk-icon icon-angle-down" v-if="isShowCommandParams"></i>
                            <i class="bk-icon icon-angle-up" v-else></i>
                        </div>
                    </div>
                    <div class="content p0 m0 biz-table-wrapper" style="border: none;">
                        <table class="bk-table has-table-hover has-table-bordered" style="border: none;" v-if="isShowCommandParams">
                            <thead>
                                <tr>
                                    <th class="pl20 f12" style="width: 400px; height: auto;">{{$t('参数')}}</th>
                                    <th class="pl25 f12" style="height: auto;">{{$t('是否启用')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="command of commandList" :key="command.id" v-if="!command.disabled">
                                    <td class="pl20 pt5 pb5" style="height: auto;">
                                        {{command.id}}
                                        <bk-tooltip placement="top" :content="command.desc">
                                            <span style="font-size: 12px;cursor: pointer;">
                                                <i class="bk-icon icon-info-circle"></i>
                                            </span>
                                        </bk-tooltip>
                                    </td>
                                    <td class="pl25 pt5 pb5" style="height: auto;">
                                        <label class="bk-form-checkbox">
                                            <input type="checkbox" v-model="helmCommandParams[command.id]">
                                        </label>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="action-box">
                    <div class="title">
                        Chart Values
                    </div>
                </div>

                <div slot="content" class="mt10" style="min-height: 180px;">
                    <section class="value-file-wrapper">
                        {{$t('Values文件：')}}
                        <bk-selector
                            style="width: 200px;"
                            :placeholder="$t('请选择')"
                            :searchable="true"
                            :selected.sync="curValueFile"
                            :list="curValueFileList"
                            :setting-key="'name'"
                            :display-key="'name'"
                            :disabled="isLocked"
                            @item-selected="changeValueFile">
                        </bk-selector>

                        <bk-tooltip placement="top" :content="$t('Values文件命名规范是以values.yaml结尾，例如xxx-values.yaml')">
                            <span class="bk-badge" style="margin-left: 3px;">
                                <i class="f12 bk-icon icon-question"></i>
                            </span>
                        </bk-tooltip>

                        <div style="display: inline-block;">
                            <label class="bk-form-checkbox ml10 mr5">
                                <input type="checkbox" v-model="isLocked">
                                <i class="bk-checkbox-text">{{isLocked ? '已锁定' : '已解锁'}}</i>
                            </label>
                        </div>
                        <!-- <span class="f12 vm">{{isLocked ? '已锁定' : '已解锁'}}</span> -->
                        <span class="biz-tip f12 vm">(默认锁定values内容为当前release(版本：<span v-bktooltips.top="curApp.chart_info.version" class="release-version">{{curApp.chart_info.version}}</span>)的内容，解除锁定后，加载为对应Chart中的values内容)</span>
                    </section>
                    <bk-tab
                        :type="'fill'"
                        :size="'small'"
                        :key="tabChangeIndex"
                        :active-name.sync="curEditMode"
                        @tab-changed="helmModeChangeHandler">
                        <bk-tabpanel name="yaml-mode" :title="$t('YAML模式')">
                            <template slot="tag">
                                <span
                                    class="bk-icon icon-circle-shape biz-danger-text v-bk"
                                    style="font-size: 10px;"
                                    v-bktooltips.top="$t('Release参数与选中的Chart Version中values.yaml有区别')"
                                    v-if="String(tplVersionId) !== '-1' && !isLocked">
                                </span>
                            </template>
                            <div style="width: 100%; min-height: 600px;" v-bkloading="{ isLoading: isSyncYamlLoading }">
                                <p class="biz-tip m15" style="color: #63656E;">
                                    <i class="bk-icon icon-info-circle biz-warning-text mr5"></i>
                                    {{$t('YAML初始值为创建时Chart中values.yaml内容，后续更新部署以该YAML内容为准，内容最终通过`--values`选项传递给`helm template`命令')}}
                                </p>
                                <div v-if="String(tplVersionId) !== '-1' && !isLocked" class="f14 mb15 ml15" style="color: #63656E;">
                                    <i class="bk-icon icon-eye biz-warning-text mr5"></i>
                                    {{$t('您更改了Chart版本，')}}<span class="bk-text-button" @click="showCodeDiffDialog">{{$t('点击查看')}}</span> Helm Release参数与选中的Chart Version中values.yaml区别
                                </div>
                                <ace
                                    ref="codeViewer"
                                    :value="curTplYaml"
                                    :width="yamlConfig.width"
                                    :height="yamlConfig.height"
                                    :lang="yamlConfig.lang"
                                    :read-only="yamlConfig.readOnly"
                                    :full-screen="yamlConfig.fullScreen"
                                    :key="curValueFile"
                                    @init="editorInit">
                                </ace>
                            </div>
                        </bk-tabpanel>
                        <bk-tabpanel name="form-mode" :title="$t('表单模式')">
                            <p class="biz-tip p15" style="color: #63656E;">
                                <i class="bk-icon icon-info-circle biz-warning-text mr5"></i>{{$t('表单根据Chart中questions.yaml生成，表单修改后的数据会自动同步给YAML模式')}}
                            </p>
                            <template v-if="formData.questions">
                                <bk-form-creater :form-data="formData" ref="bkFormCreater"></bk-form-creater>
                            </template>
                            <template v-else>
                                <div class="biz-guard-box" v-if="!isQuestionsLoading">
                                    <span>{{$t('您可以参考')}}
                                        <a class="bk-text-button" href="https://docs.bk.tencent.com/bcs/Container/helm/WriteQuestionsYaml.html" target="_blank">{{$t('指引')}}</a>
                                        {{$t('通过表单模式配置您的Helm Release 参数')}}，
                                    </span>
                                    <span>{{$t('也可以通过')}}<a href="javascript:void(0)" class="bk-text-button" @click="editYaml">{{$t('YAML模式')}}</a>{{$t('直接修改Helm Release参数')}}
                                    </span>
                                </div>
                            </template>
                        </bk-tabpanel>
                    </bk-tab>
                </div>

                <div class="create-wrapper" v-if="!isNamespaceLoading && !isNamespaceMatch">
                    <bk-tooltip :content="$t('所属命名空间不存在，不可操作')" placement="top">
                        <bk-button type="primary" :title="$t('更新')" :disabled="true">
                            {{$t('更新')}}
                        </bk-button>
                    </bk-tooltip>
                    <bk-tooltip :content="$t('所属命名空间不存在，不可操作')" placement="top">
                        <bk-button type="default" :title="$t('预览')" :disabled="true">
                            {{$t('预览')}}
                        </bk-button>
                    </bk-tooltip>
                    <bk-button type="default" :title="$t('取消')" @click="goToHelmIndex">
                        {{$t('取消')}}
                    </bk-button>
                </div>

                <div class="create-wrapper" v-else>
                    <bk-button type="primary" :title="$t('更新')" @click="confirmUpdateApp" :disabled="isNamespaceLoading || !isNamespaceMatch">
                        {{$t('更新')}}
                    </bk-button>
                    <bk-button type="default" :title="$t('预览')" @click="showPreview" :disabled="isNamespaceLoading || !isNamespaceMatch">
                        {{$t('预览')}}
                    </bk-button>
                    <bk-button type="default" :title="$t('取消')" @click="goToHelmIndex">
                        {{$t('取消')}}
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
                        <resizer :class="['resize-layout fl']"
                            direction="right"
                            :handler-offset="3"
                            :min="250"
                            :max="400">
                            <div class="tree-box">
                                <bk-tree
                                    :data="treeData"
                                    :node-key="'name'"
                                    :has-border="true"
                                    @on-click="getFileDetail">
                                </bk-tree>
                            </div>
                        </resizer>
                        
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
                <p class="biz-no-data" style="padding: 100px 40px; text-align: center;" v-else>{{$t('无数据')}}</p>
            </div>
        </bk-sideslider>
        <bk-dialog
            :width="1100"
            :title="updateConfirmDialog.title"
            :close-icon="!updateInstanceLoading"
            :is-show.sync="updateConfirmDialog.isShow"
            @cancel="hideConfirmDialog">
            <template slot="content">
                <p class="biz-tip mb5 tl" style="color: #666;">{{$t('Helm Release参数发生如下变化，请确认后再点击“确定”更新')}}</p>
                <div class="difference-code" v-bkloading="{ isLoading: isDifferenceLoading }" v-if="isDifferenceLoading || difference">
                    <div class="editor-header">
                        <div>当前版本</div>
                        <div>更新版本</div>
                    </div>
                    
                    <div :class="['diff-editor-box', { 'editor-fullscreen': yamlDiffEditorOptions.fullScreen }]" style="position: relative;">
                        <!-- <div title="关闭全屏" class="fullscreen-close" v-if="yamlDiffEditorOptions.fullScreen" @click="cancelFullScreen">
                            <i class="bk-icon icon-close"></i>
                        </div>
                        <div title="全屏" class="fullscreen-use" v-else @click="setFullScreen">
                            <i class="bk-icon icon-full-screen"></i>
                        </div> -->
                        <monaco-editor
                            ref="yamlEditor"
                            class="editor"
                            theme="monokai"
                            language="yaml"
                            :style="{ height: `${diffEditorHeight}px`, width: '100%' }"
                            v-model="curAppDifference.content"
                            :diff-editor="true"
                            :key="differenceKey"
                            :options="yamlDiffEditorOptions"
                            :original="curAppDifference.originContent">
                        </monaco-editor>
                    </div>
                </div>
                <div class="difference-code" v-bkloading="{ isLoading: isDifferenceLoading }" v-else>
                    <ace
                        :value="$t('本次更新没有内容变化')"
                        :width="updateConfirmDialog.width"
                        :height="updateConfirmDialog.height"
                        :lang="updateConfirmDialog.lang"
                        :read-only="updateConfirmDialog.readOnly"
                        :full-screen="updateConfirmDialog.fullScreen">
                    </ace>
                </div>
                <p class="biz-tip mt15 tl biz-warning" v-if="isChartVersionChange">{{$t('温馨提示：Helm Chart 版本已更改，请检查是否需要同步容器服务上Release 的参数')}}</p>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template>
                        <button
                            :class="['bk-button bk-dialog-btn-confirm bk-primary', { 'is-disabled': isDifferenceLoading || updateInstanceLoading }]"
                            @click="updateApp">
                            {{updateInstanceLoading ? $t('更新中...') : $t('确定')}}
                        </button>
                        <button
                            :class="['bk-button bk-dialog-btn-cancel bk-default']"
                            @click="hideConfirmDialog">
                            {{$t('取消')}}
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
                <div class="bk-intro bk-danger pb30 mb15" v-if="errorDialogConf.message" style="position: relative;">
                    <pre class="biz-error-message">
                        {{errorDialogConf.message}}
                    </pre>
                    <bk-button size="mini" type="default" id="error-copy-btn" :data-clipboard-text="errorDialogConf.message"><i class="bk-icon icon-clipboard mr5"></i>{{$t('复制')}}</bk-button>
                </div>
                <div class="biz-message" v-if="errorDialogConf.errorCode === 40031">
                    <h3>{{$t('您需要')}}：</h3>
                    <p>{{$t('在集群页面，启用Helm')}}</p>
                </div>
                <div class="biz-message" v-else>
                    <h3>{{$t('您可以')}}：</h3>
                    <p>1、{{$t('更新Helm Chart，并推送到项目Chart仓库')}}</p>
                    <p>2、{{$t('重新更新')}}</p>
                </div>
            </div>
            <template slot="footer">
                <div class="biz-footer">
                    <bk-button type="primary" @click="hideErrorDialog">{{$t('知道了')}}</bk-button>
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
                    <h3>{{$t('当前 Release 参数')}}：</h3>
                    <h3>{{$t('Chart 默认值')}}：</h3>
                </div>
                <div style="max-height: 500px; overflow: auto; position: relative; border: 1px solid #ddd; border-radius: 2px;">
                    <div :class="['diff-editor-box', { 'editor-fullscreen': yamlDiffEditorOptions.fullScreen }]" style="position: relative;">
                        <div title="关闭全屏" class="fullscreen-close" v-if="yamlDiffEditorOptions.fullScreen" @click="cancelFullScreen">
                            <i class="bk-icon icon-close"></i>
                        </div>
                        <div title="全屏" class="fullscreen-use" v-else @click="setFullScreen">
                            <i class="bk-icon icon-full-screen"></i>
                        </div>
                        <monaco-editor
                            ref="yamlEditor"
                            class="editor"
                            theme="monokai"
                            language="yaml"
                            :style="{ height: `${diffEditorHeight}px`, width: '100%' }"
                            v-model="curEditYaml"
                            :diff-editor="true"
                            :key="differenceKey"
                            :options="yamlDiffEditorOptions"
                            :original="instanceYamlValue">
                        </monaco-editor>
                    </div>
                </div>
            </div>
            <template slot="footer">
                <div class="biz-footer">
                    <bk-button type="primary" @click="hideCodeDiffDialog" class="mr5">{{$t('知道了')}}</bk-button>
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
    import Clipboard from 'clipboard'
    import MonacoEditor from '@open/components/monaco-editor/editor.vue'
    import resizer from '@open/components/resize'

    export default {
        components: {
            MonacoEditor,
            resizer
        },
        mixins: [baseMixin],
        data () {
            return {
                tabChangeIndex: 0,
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
                instanceYamlValue: '', // 当前应用实例化后的配置
                instanceValueFileName: '', // 用户实例化选择的value文件名
                yamlDiffEditorOptions: {
                    readOnly: true,
                    fontSize: 14,
                    fullScreen: false
                },
                // previewList: [],
                difference: '',
                differenceKey: 0,
                curAppDifference: {
                    content: '',
                    originContent: ''
                },
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
                    title: this.$t('和当前版本对比'),
                    isShow: false
                },
                curVersionYaml: '',
                curEditYaml: '',
                curReourceFile: {
                    name: '',
                    value: ''
                },
                updateConfirmDialog: {
                    title: this.$t('确认更新'),
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
                    title: this.$t('预览'),
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
                    title: this.$t('预览'),
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
                clusterList: [],
                namespaceList: [],
                appAction: {
                    create: this.$t('部署'),
                    noop: '',
                    update: this.$t('更新'),
                    rollback: this.$t('回滚'),
                    delete: this.$t('删除'),
                    destroy: this.$t('删除')
                },
                curValueFileList: [],
                curValueFile: 'values.yaml',
                isLocked: true,
                isShowCommandParams: false,
                commandList: [
                    {
                        id: 'disable-openapi-validation',
                        disabled: true,
                        desc: '如果选择，部署时，不会通过Kubernetes OpenAPI Schema校验渲染的模板'
                    },
                    {
                        id: 'no-hooks',
                        disabled: false,
                        desc: '如果选择，部署或更新时，忽略hooks'
                    },
                    {
                        id: 'skip-crds',
                        disabled: false,
                        desc: '如果选择，部署或更新时，跳过crds'
                    }
                ],
                helmCommandParams: {
                    'disable-openapi-validation': false,
                    'no-hooks': false,
                    'skip-crds': false
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
            diffEditorHeight () {
                return this.yamlDiffEditorOptions.fullScreen ? window.innerHeight : 315
            },
            curClusterName () {
                if (this.curApp.cluster_id !== undefined) {
                    const match = this.clusterList.find(item => item.id === this.curApp.cluster_id)
                    return match ? match.name : this.curApp.cluster_id
                }
                return ''
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
        watch: {
            tplVersionId () {
                this.tabChangeIndex++
            },
            isLocked () {
                this.initValuesFileData(this.curTplName, this.curTplFiles)
                this.tabChangeIndex++
            }
        },
        async mounted () {
            const appId = this.$route.params.appId
            this.curApp = await this.getAppById(appId)
            this.getAppVersions(appId)
            this.getNamespaceList()
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
             * 显示yaml对比
             */
            showCodeDiffDialog () {
                this.differenceKey++
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
                    // this.curTplYaml = res.data.yaml.replace(/\'/ig, '\"')
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
                        message: this.$t('请输入YAML')
                    })
                    return false
                }

                try {
                    // 通过load检测yaml是否合法
                    yamljs.load(yaml)
                } catch (err) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入合法的YAML')
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
                        message: this.$t('请输入合法的YAML')
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
                    this.curTplReadme = files[`${tplName}/README.md`]
                    this.curValueFile = result.valuefile_name || 'values.file'
                    this.curTplYaml = result.valuefile
                    this.instanceYamlValue = result.valuefile // 保存当前应用实例化后的配置
                    this.instanceValueFileName = result.valuefile_name // 保存用户实例化时选择的文件名
                    this.curTplName = tplName
                    this.curTplFiles = files
                    this.initValuesFileData(tplName, files, result.valuefile_name)

                    this.$nextTick(() => {
                        this.$refs.codeViewer.$ace.scrollToLine(1, true, true)
                    })

                    if (result.cmd_flags && result.cmd_flags.length) {
                        result.cmd_flags.forEach(key => {
                            this.helmCommandParams[key] = true
                        })
                    }
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

                this.curVersionYaml = ''
                try {
                    const res = await this.$store.dispatch('helm/getUpdateChartByVersion', {
                        projectId,
                        appId,
                        version
                    })

                    const files = res.data.data.files
                    const tplName = res.data.name
                    this.formData = res.data.data.questions

                    this.curTplName = tplName
                    this.curTplFiles = files
                    this.initValuesFileData(tplName, files)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            initValuesFileData (tplName, files, valueFileName) {
                const list = []
                const regex = new RegExp(`^${tplName}\\/[\\w-]*values.(yaml|yml)$`)
                const valueNames = [`${tplName}/values.yaml`, `${tplName}/values.yml`]

                this.yamlFile = ''

                // 根据valueFileName判断是否第一次展示, curTplYaml显示实例化配置的内容
                if (valueFileName) {
                    this.curValueFile = valueFileName
                    this.curVersionYaml = files[valueFileName]
                }

                for (const key in files) {
                    if (regex.test(key)) {
                        const catalog = key.split('/')
                        const fileName = catalog[catalog.length - 1]
                        list.push({
                            name: fileName,
                            content: files[key]
                        })
                    }

                    // 选择版本后
                    if (!valueFileName && valueNames.includes(key)) {
                        // 如果锁定则用release values
                        if (this.isLocked) {
                            this.curTplYaml = this.instanceYamlValue
                            this.curValueFile = this.instanceValueFileName
                            console.log('locked usedefault')
                        } else {
                            this.curVersionYaml = files[key]

                            // 选择版本后依然是原来的, 显示原来实例化时的配置内容
                            if (String(this.tplVersionId) === '-1') {
                                this.curTplYaml = this.instanceYamlValue
                                this.curValueFile = this.instanceValueFileName
                                console.log('unlocked but no change usedefault')
                            } else {
                                // curTplYaml以返回的files为默认值
                                this.curTplYaml = files[key]
                                this.curValueFile = key.split('/')[1]
                                console.log('unlocked and change usenew')
                            }
                        }
                    }
                }
                this.curValueFileList = list
            },

            /**
             * 修改value file
             */
            changeValueFile (index, data) {
                this.curValueFile = index
                this.curVersionYaml = data.content
                this.curTplYaml = data.content
                this.yamlFile = ''

                // 没有选择过版本时, 如果切换为原来实例化的文件名，显示原来实例化时的配置内容
                if (String(this.tplVersionId) === '-1' && index === this.instanceValueFileName) {
                    this.curTplYaml = this.instanceYamlValue
                    console.log('unlocked && nochange use default')
                } else {
                    console.log('unlocked && valsuechange')
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
                // this.previewList.splice(0, this.previewList.length, ...list)
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
                        message: this.$t('同步成功')
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
                    const res = await this.$store.dispatch('helm/getNamespaceList', {
                        projectId: projectId
                    })
                    const curNamespaceId = this.curApp.namespace_id
                    this.isNamespaceMatch = false

                    this.clusterList = []
                    res.data.forEach(item => {
                        const obj = {}
                        const match = item.name.match(/^([\s\S]*)\(([\w-]*)\)/)
                        if (match && match.length > 2) {
                            obj.name = match[1]
                            obj.id = match[2]
                            item.id = match[2]
                        } else {
                            obj.name = item.name
                            obj.id = item.name
                        }
                        this.clusterList.push(obj)

                        if (item.children) {
                            item.children.forEach(child => {
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
                const commands = []
                for (const key in this.answers) {
                    customs.push({
                        name: key,
                        value: this.answers[key],
                        type: 'string'
                    })
                }

                for (const key in this.helmCommandParams) {
                    if (this.helmCommandParams[key] && key !== 'disable-openapi-validation') {
                        commands.push(key)
                    }
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
                    customs: customs,
                    cmd_flags: commands,
                    valuefile_name: this.curValueFile
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

                if (this.clipboardInstance && this.clipboardInstance.off) {
                    this.clipboardInstance.off('success')
                }
                if (this.errorDialogConf.message) {
                    this.$nextTick(() => {
                        this.clipboardInstance = new Clipboard('#error-copy-btn')
                        this.clipboardInstance.on('success', e => {
                            this.$bkMessage({
                                theme: 'success',
                                message: '复制成功'
                            })
                            this.isVarPanelShow = false
                        })
                    })
                }
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
                const title = `${app.name}${this.appAction[app.transitioning_action]}${this.$t('失败')}`
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
                                message: `${app.name}${action}${this.$t('成功')}`
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
                    this.showErrorDialog(e, this.$t('操作失败'), 'reback')
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
                    this.showErrorDialog(e, this.$t('更新失败'), 'update')
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
                    this.curAppDifference.content = res.data.new_content
                    this.curAppDifference.originContent = res.data.old_content
                    this.isChartVersionChange = res.data.chart_version_changed
                    this.previewEditorConfig.value = res.data.notes
                    if (this.appPreviewList.length) {
                        this.curReourceFile = this.appPreviewList[0]
                    }
                } catch (e) {
                    this.showErrorDialog(e, this.$t('预览失败'), 'preview')
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
                    // for (const key in res.data.content) {
                    //     this.curAppDifference.content += res.data.content[key]
                    // }
                    this.curAppDifference.content = res.data.new_content
                    this.curAppDifference.originContent = res.data.old_content
                    this.differenceKey++
                    this.isChartVersionChange = res.data.chart_version_changed
                } catch (e) {
                    this.showErrorDialog(e, this.$t('Chart渲染失败'), 'preUpdate')
                    this.updateConfirmDialog.value = ''
                } finally {
                    this.isDifferenceLoading = false
                }
            },

            /**
             * 全屏
             */
            setFullScreen (index) {
                this.yamlDiffEditorOptions.fullScreen = true
                this.differenceKey++
            },

            /**
             * 取消全屏
             */
            cancelFullScreen () {
                this.yamlDiffEditorOptions.fullScreen = false
                this.differenceKey++
            },

            handleToggleLock () {
                this.isLocked = !this.isLocked
                this.initValuesFileData(this.curTplName, this.curTplFiles)
            }
        }
    }
</script>

<style scoped>
    @import './app-detail.css';
</style>
