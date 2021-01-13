<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-helm-title">
                {{$t('Helm Release列表')}}
            </div>
            <bk-guide>
                <a class="bk-text-button" href="https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/helm/ServiceAccess.md" target="_blank">{{$t('如何使用Helm？')}}</a>
            </bk-guide>
        </div>
        <div class="biz-content-wrapper biz-helm-wrapper m0 p0" v-bkloading="{ isLoading: showLoading, opacity: 0.1 }">
            <template v-if="!showLoading">
                <app-exception
                    v-if="exceptionCode && !showLoading"
                    :type="exceptionCode.code"
                    :text="exceptionCode.msg">
                </app-exception>

                <div class="biz-panel-header p20">
                    <div class="left">
                        <router-link class="bk-button bk-primary" :to="{ name: 'helmTplList' }">
                            <i class="bk-icon icon-plus"></i>
                            <span>{{$t('部署Helm Chart')}}</span>
                        </router-link>
                    </div>
                    <div class="right">
                        <search
                            :width-refresh="false"
                            :scope-list="searchScopeList"
                            :namespace-list="namespaceList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            :search-namespace.sync="searchNamespace"
                            @cluster-change="handleClusterChange"
                            @search="handleSearch"
                            @refresh="handleRefresh">
                        </search>
                    </div>
                </div>

                <svg style="display: none;">
                    <title>{{$t('模板集默认图标')}}</title>
                    <symbol id="biz-set-icon" viewBox="0 0 60 60">
                        <path class="st0" d="M54.8,16.5L34,4.5C33.4,4.2,32.7,4,32,4s-1.4,0.2-2,0.5l-20.8,12c-1.2,0.7-2,2-2,3.5v24c0,1.4,0.8,2.7,2,3.5
                            l20.8,12c0.6,0.4,1.3,0.5,2,0.5s1.4-0.2,2-0.5l20.8-12c1.2-0.7,2-2,2-3.5V20C56.8,18.6,56,17.3,54.8,16.5z M11.2,20L11.2,20L11.2,20
                            L11.2,20z M30,54.8L11.2,44V22.3L30,33.2V54.8z M32,29.7L13.2,18.8L32,8l18.8,10.8L32,29.7z M52,28.1c-1.2,0.7-1.8,1.3-1.8,2v10.7
                            c0,0.6,0.6,0.6,1.8-0.1v1.1l-6.7,3.9v-1.1c1.3-0.7,1.9-1.4,1.9-2v-5l-6.8,3.9v5c0,0.6,0.6,0.6,1.9-0.2v1.1l-6.7,3.9v-1.1
                            c1.2-0.7,1.8-1.3,1.8-1.9V37.5c0-0.6-0.6-0.6-1.8,0.1v-1.2l6.7-3.9v1.2c-1.3,0.7-1.9,1.4-1.9,2V40l6.8-3.9v-4.2
                            c0-0.6-0.6-0.6-1.9,0.2v-1.2L52,27V28.1z M52.8,20L52.8,20L52.8,20L52.8,20z" />
                    </symbol>
                </svg>

                <div class="biz-namespace" style="margin-bottom: 150px;" v-bkloading="{ isLoading: isPageLoading }">
                    <table class="bk-table biz-templateset-table mb20">
                        <thead>
                            <tr>
                                <th class="logo-th center">{{$t('图标')}}</th>
                                <th class="data-th">{{$t('Release名称')}}</th>
                                <th class="namespace-th">{{$t('集群')}}/{{$t('命名空间')}}</th>
                                <th class="opera_record-th">{{$t('操作记录')}}</th>
                                <th class="action-th">{{$t('操作')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="appList.length">
                                <tr :key="appIndex" v-for="(app, appIndex) in appList">
                                    <td colspan="66">
                                        <table class="biz-inner-table">
                                            <tr>
                                                <td class="logo">
                                                    <svg class="biz-set-icon">
                                                        <use xlink:href="#biz-set-icon"></use>
                                                    </svg>
                                                </td>
                                                <td class="data">
                                                    <span v-if="app.transitioning_on" class="f14 fb app-name">
                                                        {{app.name}}
                                                    </span>
                                                    <a @click="showAppDetail(app)" href="javascript:void(0)" class="bk-text-button app-name f14 fb" v-else v-bktooltips="app.name">
                                                        {{app.name}}
                                                    </a>
                                                    <div class="mt5">
                                                        {{$t('版本')}}：
                                                        <bk-tooltip :content="app.current_version" placement="top">
                                                            <span class="app-version biz-text-wrapper">{{app.current_version}}</span>
                                                        </bk-tooltip>
                                                    </div>
                                                    <template v-if="app.transitioning_on">
                                                        <div class="bk-tag bk-warning">
                                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" style="margin-top: -3px;">
                                                                <div class="rotate rotate1"></div>
                                                                <div class="rotate rotate2"></div>
                                                                <div class="rotate rotate3"></div>
                                                                <div class="rotate rotate4"></div>
                                                                <div class="rotate rotate5"></div>
                                                                <div class="rotate rotate6"></div>
                                                                <div class="rotate rotate7"></div>
                                                                <div class="rotate rotate8"></div>
                                                            </div>
                                                            {{appAction[app.transitioning_action]}}中...
                                                        </div>
                                                    </template>
                                                    <template v-else-if="!app.transitioning_result && app.transitioning_action !== 'noop'">
                                                        <bk-tooltip :content="$t('点击查看原因')" placement="top">
                                                            <div class="bk-tag bk-danger biz-check-btn" @click="showAppError(app)">
                                                                <i class="bk-icon icon-order"></i>
                                                                {{appAction[app.transitioning_action]}}{{$t('失败')}}
                                                            </div>
                                                        </bk-tooltip>
                                                    </template>
                                                </td>
                                                <td class="namespace">
                                                    <div>
                                                        {{$t('所属集群')}}：
                                                        <bk-tooltip :content="app.cluster_id || '--'" placement="top">
                                                            <span class="biz-min-wrapper">{{app.cluster_name ? app.cluster_name : '--'}}</span>
                                                        </bk-tooltip>
                                                    </div>
                                                    <p>
                                                        {{$t('命名空间')}}：<span class="biz-text-wrapper ml5">{{app.namespace}}</span>
                                                    </p>
                                                </td>
                                                <td class="opera_record">
                                                    <p class="updator">{{$t('操作者')}}：{{app.updator}}</p>
                                                    <p class="updated">{{$t('更新时间')}}：{{app.updated}}</p>
                                                </td>
                                                <td class="action" style="width: 215px">
                                                    <template v-if="app.transitioning_on">
                                                        <button :class="['bk-button bk-default btn is-disabled']">
                                                            <span>{{$t('操作')}}</span>
                                                            <i class="bk-icon icon-angle-down dropdown-menu-angle-down ml0" style="font-size: 10px;"></i>
                                                        </button>
                                                        <button :class="['bk-button bk-default btn is-disabled']">
                                                            <span>{{$t('查看状态')}}</span>
                                                        </button>
                                                    </template>
                                                    <template v-else>
                                                        <bk-dropdown-menu
                                                            class="dropdown-menu"
                                                            :align="'left'"
                                                            ref="dropdown">
                                                            <button :class="['bk-button bk-default btn']" slot="dropdown-trigger" style="position: relative;">
                                                                <span>{{$t('操作')}}</span>
                                                                <i class="bk-icon icon-angle-down dropdown-menu-angle-down ml0" style="font-size: 10px;"></i>
                                                            </button>

                                                            <ul class="bk-dropdown-list" slot="dropdown-content">
                                                                <li>
                                                                    <a href="javascript:void(0)" @click="showAppDetail(app)">{{$t('更新')}}</a>
                                                                </li>
                                                                <li>
                                                                    <a href="javascript:void(0)" @click="showRebackDialog(app)">{{$t('回滚')}}</a>
                                                                </li>
                                                                <li>
                                                                    <a href="javascript:void(0)" @click="deleteApp(app)">{{$t('删除')}}</a>
                                                                </li>
                                                            </ul>
                                                        </bk-dropdown-menu>
                                                        <button :class="['bk-button bk-default btn']" @click="showAppInfoSlider(app)">
                                                            <span>{{$t('查看状态')}}</span>
                                                        </button>
                                                    </template>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="7">
                                        <div class="biz-guide-box" style="margin: 0 20px;">
                                            <p class="message empty-message">{{$t('无数据')}}</p>
                                        </div>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
            </template>
        </div>

        <bk-dialog
            width="800"
            :title="rebackDialogConf.title"
            :close-icon="!isRebackLoading"
            :quick-close="false"
            :is-show.sync="rebackDialogConf.isShow"
            @cancel="cancelReback">
            <template slot="content">
                <div class="flex" style="margin-top: -15px;">
                    <div class="bk-form bk-form-vertical" style="width: 760px;">
                        <div class="bk-form-item">
                            <label for="" class="bk-label">
                                {{$t('回滚到版本')}} <span class="error-tip" v-if="!isRebackListLoading && !rebackList.length">{{$t('（Release当前没有可切换的版本，无法回滚）')}}</span>
                            </label>
                            <div class="bk-form-content mb10">
                                <bk-selector
                                    :placeholder="$t('请选择')"
                                    :selected.sync="versionId"
                                    :list="rebackList"
                                    :setting-key="'id'"
                                    :disabled="isRebackLoading"
                                    :display-key="'version'"
                                    @item-selected="showRebackPreview">
                                </bk-selector>
                            </div>

                            <div style="height: 370px;" v-bkloading="{ isLoading: isRebackVersionLoading }" v-if="versionId">
                                <bk-tab
                                    :type="'fill'"
                                    :size="'small'"
                                    :active-name="'Difference'"
                                    :key="rebackPreviewList.length">
                                    <bk-tabpanel :name="'Difference'" :title="$t('版本对比')">
                                        <div style="height: 320px;">
                                            <ace
                                                :value="difference"
                                                :width="rebackEditorConfig.width"
                                                :height="rebackEditorConfig.height"
                                                :lang="rebackEditorConfig.lang"
                                                :read-only="rebackEditorConfig.readOnly"
                                                :full-screen="rebackEditorConfig.fullScreen">
                                            </ace>
                                        </div>
                                    </bk-tabpanel>
                                    <bk-tabpanel :key="index" :name="item.name" :title="item.name" v-for="(item, index) in rebackPreviewList">
                                        <div style="height: 320px;">
                                            <ace
                                                :value="item.value"
                                                :width="rebackEditorConfig.width"
                                                :height="rebackEditorConfig.height"
                                                :lang="rebackEditorConfig.lang"
                                                :read-only="rebackEditorConfig.readOnly"
                                                :full-screen="rebackEditorConfig.fullScreen">
                                            </ace>
                                        </div>
                                    </bk-tabpanel>
                                </bk-tab>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template>
                        <button :class="['bk-button bk-dialog-btn-confirm bk-primary', { 'is-disabled': isRebackVersionLoading || isRebackLoading || !versionId }]" @click="submitRebackData">
                            {{isRebackLoading ? $t('更新中...') : $t('确定')}}
                        </button>
                        <button :class="['bk-button bk-dialog-btn-cancel bk-default', { 'is-disabled': isRebackLoading }]" :disabled="isRebackLoading" @click="cancelReback">
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
            </div>
            <template slot="footer">
                <div class="biz-footer">
                    <bk-button type="primary" @click="hideErrorDialog">{{$t('知道了')}}</bk-button>
                </div>
            </template>
        </bk-dialog>

        <bk-sideslider
            :is-show.sync="appInfoConf.isShow"
            :title="appInfoConf.title"
            :quick-close="true"
            :width="800"
            @hidden="hideAppInfoSlider">
            <div slot="content" :style="{ height: `${winHeight - 100}px`, padding: '20px' }" v-bkloading="{ isLoading: isAppInfoLoading }">
                <div class="biz-search-input" style="width: 240px; float: right; margin-top: -68px;" v-if="!isAppInfoLoading">
                    <input
                        type="text"
                        class="bk-form-input"
                        :placeholder="$t('输入关键字，按Enter搜索')"
                        v-model="resourceSearchKey"
                        @keyup.enter="searchResource" />
                    <span href="javascript:void(0)" class="biz-search-btn" v-if="!resourceSearchKey">
                        <i class="bk-icon icon-search"></i>
                    </span>
                    <a href="javascript:void(0)" class="biz-search-btn" v-else @click.stop.prevent="clearResoureceSearch">
                        <i class="bk-icon icon-close-circle-shape"></i>
                    </a>
                </div>
                <table class="bk-table has-table-hover biz-data-table" v-if="!isAppInfoLoading">
                    <thead>
                        <tr>
                            <th style="width: 10px; padding: 0;"></th>
                            <th>{{$t('名称')}}</th>
                            <th style="width: 130px;">{{$t('类型')}}</th>
                            <th style="width: 100px;">
                                Pods
                                <bk-tooltip :content="$t('实际实例数/期望数')" placement="right">
                                    <i class="bk-icon icon-info-circle tip-trigger"></i>
                                </bk-tooltip>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-if="curAppResources.length">
                            <template v-for="resource of curAppResources">
                                <tr
                                    @click="showErrorInfo(resource)"
                                    :class="{ 'has-error': resource.pods.warnings }"
                                    :key="resource.id">
                                    <td style="padding: 0;">
                                        <template v-if="resource.pods.warnings">
                                            <bk-tooltip content="点击查看原因" placement="left">
                                                <i class="biz-status-icon bk-icon icon-info-circle tip-trigger biz-danger-text f13"></i>
                                            </bk-tooltip>
                                        </template>
                                        <i class="biz-status-icon bk-icon icon-check-circle biz-success-text f13" v-else></i>
                                    </td>
                                    <td>
                                        <template v-if="resource.link">
                                            <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="goResourceInfo(resource.link)">{{resource.name}}</a>
                                        </template>
                                        <template v-else>
                                            {{resource.name}}
                                        </template>
                                    </td>
                                    <td>
                                        <span class="bk-tag bk-primary">{{resource.kind}}</span>
                                    </td>
                                    <td>
                                        <template v-if="resource.pods.running !== 0 || resource.pods.desired !== 0">
                                            {{resource.pods.running}}/{{resource.pods.desired}}
                                        </template>
                                        <template v-else>
                                            --
                                        </template>
                                    </td>
                                </tr>
                                <tr v-if="resource.isOpened && resource.pods.warnings" :key="resource.id">
                                    <td colspan="4">
                                        <pre class="bk-intro bk-danger biz-error-message mb0">
                                            {{resource.pods.warnings}}
                                        </pre>
                                    </td>
                                </tr>
                            </template>
                        </template>
                        <template v-if="curAppResources.length === 0">
                            <tr>
                                <td colspan="4">
                                    <div class="biz-empty-message p50">{{$t('无数据')}}</div>
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
    import ace from '@open/components/ace-editor'
    import { catchErrorHandler } from '@open/common/util'
    import Clipboard from 'clipboard'
    import search from './search.vue'

    const FAST_TIME = 3000
    const SLOW_TIME = 10000

    export default {
        components: {
            ace,
            search
        },
        data () {
            return {
                curApp: {},
                allNamespaces: [],
                curAppResources: [],
                curAppResourcesCache: [],
                namespaceList: [],
                statusTimer: 0,
                isRebackLoading: false,
                isRebackListLoading: false,
                isRebackVersionLoading: false,
                isRouterLeave: false,
                isAppInfoLoading: false,
                appList: [],
                appListCache: [],
                showLoading: true,
                isPageLoading: false,
                exceptionCode: null,
                versionId: '',
                difference: '',
                versionList: [],
                rebackPreviewList: [],
                rebackList: [],
                editor: null,
                searchKeyword: '',
                searchScope: '',
                searchNamespace: '',
                previewLoading: true,
                rebackDialogConf: {
                    title: '',
                    isShow: false
                },
                appInfoConf: {
                    isShow: false,
                    title: ''
                },
                curAppDetail: {
                    created: '',
                    namespace_id: '',
                    release: {
                        id: '',
                        customs: [],
                        answers: {}
                    }
                },
                errorDialogConf: {
                    title: '',
                    isShow: false,
                    message: '',
                    errorCode: 0
                },
                curProjectId: '',
                winHeight: 0,
                editorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'json',
                    readOnly: true,
                    fullScreen: false,
                    value: '',
                    editors: []
                },
                resourceSearchKey: '',
                rebackEditorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'yaml',
                    readOnly: true,
                    fullScreen: false,
                    value: '',
                    editors: []
                },
                operaRunningApp: {}, // 缓存操作更新中的app状态信息
                appAction: {
                    create: this.$t('部署'),
                    noop: '',
                    update: this.$t('更新'),
                    rollback: this.$t('回滚'),
                    delete: this.$t('删除'),
                    destroy: this.$t('删除')
                },
                isOperaLayerShow: false, // 操作弹层显示，包括删除和回滚
                appCheckTime: FAST_TIME
            }
        },
        computed: {
            curProject () {
                const project = this.$store.state.curProject
                return project
            },
            projectId () {
                this.curProjectId = this.$route.params.projectId
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            searchScopeList () {
                const clusterList = this.$store.state.cluster.clusterList
                let results = []
                if (clusterList.length) {
                    results = [{
                        id: '',
                        name: this.$t('全部集群')
                    }]
                    clusterList.forEach(item => {
                        results.push({
                            id: item.cluster_id,
                            name: item.name
                        })
                    })
                }

                return results
            }
        },
        watch: {
            curProjectId () {
                // 如果不是k8s类型的项目，无法访问些页面，重定向回集群首页
                if (this.curProject && (this.curProject.kind !== PROJECT_K8S && this.curProject.kind !== PROJECT_TKE)) {
                    this.$router.push({
                        name: 'clusterMain',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode
                        }
                    })
                }
            }
        },
        mounted () {
            this.isRouterLeave = false
            this.winHeight = window.innerHeight
            if (window.sessionStorage && window.sessionStorage['bcs-cluster']) {
                this.searchScope = window.sessionStorage['bcs-cluster']
            }
            if (window.sessionStorage && window.sessionStorage['bcs-helm-namespace']) {
                this.searchNamespace = window.sessionStorage['bcs-helm-namespace']
            }

            this.getAppList()
            this.getAllNamespaces()
        },
        beforeRouteLeave (to, from, next) {
            this.isRouterLeave = true
            // 如果不是到详情内页，清空搜索条件
            // if (to.name !== 'helmAppDetail') {
            //     window.sessionStorage['bcs-helm-cluster'] = ''
            //     window.sessionStorage['bcs-helm-namespace'] = ''
            // }
            clearTimeout(this.statusTimer)
            next()
        },
        beforeDestroy () {
            this.isRouterLeave = true
            clearTimeout(this.statusTimer)
            // window.sessionStorage['bcs-helm-cluster'] = ''
            // window.sessionStorage['bcs-helm-namespace'] = ''
        },
        methods: {
            /**
             * 刷新列表
             */
            handleRefresh () {
                this.getAppList()
            },

            /**
             * 搜索列表
             */
            handleSearch () {
                window.sessionStorage['bcs-cluster'] = this.searchScope
                window.sessionStorage['bcs-helm-namespace'] = this.searchNamespace
                this.getAppList()
            },

            /**
             * 查看资源详情
             * @param  {string} link 资源链接
             */
            goResourceInfo (link) {
                const clusterId = this.curApp.cluster_id
                const url = `${DEVOPS_HOST}${link}&cluster_id=${clusterId}`
                window.open(url)
            },

            /**
             * 显示资源异常信息
             * @param  {object} resource 资源
             */
            showErrorInfo (resource) {
                resource.isOpened = !resource.isOpened
            },

            /**
             * 显示应用状态信息
             * @params {object} app 应用对象
             */
            async showAppInfoSlider (app) {
                const params = {
                    project_id: this.projectId,
                    policy_code: 'use',
                    resource_code: app.namespace_id,
                    resource_name: app.namespace,
                    resource_type: 'namespace'
                }
                await this.$store.dispatch('getResourcePermissions', params)
                this.curAppResources = []
                this.appInfoConf.isShow = true
                this.isOperaLayerShow = true
                this.appInfoConf.title = app.name
                this.curApp = app

                const projectId = this.projectId
                const appId = app.id

                this.isAppInfoLoading = true
                try {
                    const res = await this.$store.dispatch('helm/getAppInfo', { projectId, appId })
                    const resources = []
                    const appResources = res.data.status
                    for (const key in appResources) {
                        const resource = appResources[key]
                        const metedata = {
                            name: resource.name,
                            kind: resource.kind,
                            link: resource.link,
                            isOpened: false,
                            pods: {
                                desired: resource.status_sumary.desired_pods, // 期望数
                                running: resource.status_sumary.ready_pods, // 实例实例数
                                warnings: resource.status_sumary.messages
                            }
                        }
                        resources.push(metedata)
                    }
                    this.curAppResources = this.sortResource(resources)
                    this.curAppResourcesCache = JSON.parse(JSON.stringify(this.curAppResources))
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isAppInfoLoading = false
                }
            },

            /**
             * 按顺序对资源进行靠近排序（相同类型临近一起）
             * @param  {array} resources 资源
             * @return {array} arrayCache 排序结果
             */
            sortResource (resources) {
                let sortCache = []
                const sortKey = {
                    'Deployment': [],
                    'DaemonSet': [],
                    'Job': [],
                    'StatefulSet': [],
                    'Service': [],
                    'Ingress': [],
                    'ConfigMap': [],
                    'Secret': [],
                    'other': []
                }

                resources.forEach(resource => {
                    const kind = resource.kind
                    if (sortKey[kind]) {
                        sortKey[kind].push(resource)
                    } else {
                        sortKey['other'].push(resource)
                    }
                })

                sortKey['other'].sort((a, b) => {
                    return a.kind.toLowerCase() < b.kind.toLowerCase()
                })

                for (const key in sortKey) {
                    sortCache = sortCache.concat(...sortKey[key])
                }
                return sortCache
            },

            /**
             * 显示应用详情
             * @param {object} app 应用
             */
            async showAppDetail (app) {
                const params = {
                    project_id: this.projectId,
                    policy_code: 'use',
                    resource_code: app.namespace_id,
                    resource_name: app.namespace,
                    resource_type: 'namespace'
                }
                await this.$store.dispatch('getResourcePermissions', params)

                this.$router.push({
                    name: 'helmAppDetail',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        appId: app.id
                    }
                })
            },

            /**
             * 隐藏错误提示弹层
             */
            hideErrorDialog () {
                this.errorDialogConf.isShow = false
                this.isOperaLayerShow = false
                this.appCheckTime = FAST_TIME
                this.getAppsStatus()
            },

            /**
             * 确认删除应用
             * @param {object} app 应用
             */
            async deleteApp (app) {
                const params = {
                    project_id: this.projectId,
                    policy_code: 'use',
                    resource_code: app.namespace_id,
                    resource_name: app.namespace,
                    resource_type: 'namespace'
                }
                await this.$store.dispatch('getResourcePermissions', params)

                const projectId = this.projectId
                const appId = app.id
                const me = this
                const boxStyle = {
                    'margin-top': '-20px',
                    'margin-bottom': '-20px'
                }
                const titleStyle = {
                    style: {
                        'text-align': 'left',
                        'font-size': '20px',
                        'margin-bottom': '15px',
                        'color': '#313238'
                    }
                }
                const itemStyle = {
                    style: {
                        'text-align': 'left',
                        'font-size': '14px',
                        'margin-bottom': '3px',
                        'color': '#71747c'
                    }
                }

                clearTimeout(this.statusTimer)
                this.isOperaLayerShow = true
                this.$bkInfo({
                    title: '',
                    clsName: 'biz-remove-dialog',
                    // content: me.$createElement('p', {
                    //     class: 'biz-confirm-desc'
                    // }, `确定要删除Release【${app.name}】？`),
                    content: me.$createElement('div', { class: 'biz-confirm-desc', style: boxStyle }, [
                        me.$createElement('h5', titleStyle, this.$t('确定要删除Release？')),
                        me.$createElement('p', itemStyle, `${this.$t('名称')}：${app.name}`),
                        me.$createElement('p', itemStyle, `${this.$t('所属集群')}：${app.cluster_name}`),
                        me.$createElement('p', itemStyle, `${this.$t('命名空间')}：${app.namespace}`)
                    ]),
                    async confirmFn () {
                        app.transitioning_action = 'delete'
                        app.transitioning_on = true
                        try {
                            await me.$store.dispatch('helm/deleteApp', { projectId, appId }, { cancelPrevious: true })
                            me.checkingAppStatus(app, 'delete')
                        } catch (e) {
                            catchErrorHandler(e, this)
                        } finally {
                            me.isOperaLayerShow = false
                            me.showLoading = false
                        }
                    },
                    cancelFn (close) {
                        me.appCheckTime = FAST_TIME
                        me.isOperaLayerShow = false
                        me.getAppsStatus()
                        close()
                    }
                })
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
             * 显示错误弹层
             * @param  {object} res ajax数据对象
             * @param  {string} title 错误提示
             * @param  {string} actionType 操作
             */
            showErrorDialog (res, title, actionType) {
                // 先检查集群是否注册到 BKE server。未注册则返回 code: 40031
                this.errorDialogConf.errorCode = res.code
                this.errorDialogConf.message = res.message || res.data.msg || res.statusText
                this.errorDialogConf.isShow = true
                this.isOperaLayerShow = true
                this.errorDialogConf.title = title
                this.rebackDialogConf.isShow = false
                this.errorDialogConf.actionType = actionType

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
             * 搜索Helm app
             */
            search () {
                const keyword = this.searchKeyword
                const keyList = ['name', 'namespace', 'cluster_name']
                const list = JSON.parse(JSON.stringify(this.appListCache))
                
                if (keyword) {
                    const results = list.filter(item => {
                        for (const key of keyList) {
                            if (item[key].indexOf(keyword) > -1) {
                                return true
                            }
                        }
                        return false
                    })
                    this.appList.splice(0, this.appList.length, ...results)
                } else {
                    // 没有搜索关键字，直接从缓存返回列表
                    this.appList.splice(0, this.appList.length, ...list)
                }
            },

            /**
             * 搜索resource
             */
            searchResource () {
                const keyword = this.resourceSearchKey
                if (keyword) {
                    const results = this.curAppResourcesCache.filter(item => {
                        if (item.name.indexOf(keyword) > -1 || item.kind.indexOf(keyword) > -1) {
                            return true
                        } else {
                            return false
                        }
                    })
                    this.curAppResources.splice(0, this.curAppResources.length, ...results)
                } else {
                    // 没有搜索关键字，直接从缓存返回列表
                    this.curAppResources.splice(0, this.curAppResources.length, ...this.curAppResourcesCache)
                }
            },

            /**
             * 清除Helm app搜索
             */
            clearSearch () {
                this.searchKeyword = ''
                this.search()
            },

            /**
             * 清空资源搜索
             */
            clearResoureceSearch () {
                this.resourceSearchKey = ''
                this.searchResource()
            },

            /**
             * ace编辑器初始化成功回调
             * @param  {object} editor ace
             */
            handlerEditorInit (editor) {
                this.editor = editor
            },

            /**
             *  显示回滚弹层
             * @param  {object} app 应用
             */
            async showRebackDialog (app) {
                const params = {
                    project_id: this.projectId,
                    policy_code: 'use',
                    resource_code: app.namespace_id,
                    resource_name: app.namespace,
                    resource_type: 'namespace'
                }
                await this.$store.dispatch('getResourcePermissions', params)
                clearTimeout(this.statusTimer)

                this.curApp = app
                this.versionId = ''
                this.isRebackVersionLoading = false
                this.rebackDialogConf.isShow = true
                this.isOperaLayerShow = true
                this.rebackDialogConf.title = `${this.$t('回滚')} ${app.name}`
                this.rebackPreviewList = []
                this.rebackList = []
                this.isRebackListLoading = true
                this.getRebackList(app.id)
            },

            /**
             * 获取回滚版本列表
             * @param  {number} appId 应用ID
             */
            async getRebackList (appId) {
                const projectId = this.projectId
                this.isRebackListLoading = true

                try {
                    const res = await this.$store.dispatch('helm/getRebackList', { projectId, appId })

                    if (res.data.results) {
                        res.data.results.forEach(item => {
                            item.version = `${this.$t('版本')}：${item.version} （${this.$t('部署时间')}：${item.created_at}） `
                        })
                        this.rebackList = res.data.results
                    } else {
                        this.rebackList = []
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isRebackListLoading = false
                }
            },

            getParams () {
                const data = {
                    projectId: this.projectId,
                    params: {
                        limit: 1000000,
                        offset: 0,
                        cluster_id: this.searchScope,
                        namespace: ''
                    }
                }
                if (this.searchNamespace) {
                    const args = this.searchNamespace.split(':')
                    data.params.cluster_id = args[0]
                    data.params.namespace = args[1]
                }

                return data
            },

            /**
             * 获取应用列表
             */
            async getAppList (reload) {
                if (reload) {
                    this.searchKeyword = ''
                }
                this.isPageLoading = true
                try {
                    clearTimeout(this.statusTimer)
                    const data = this.getParams()
                    const res = await this.$store.dispatch('helm/getAppList', data)
                    this.searchScope = data.params.cluster_id
                    this.appList = res.data.results
                    this.appListCache = JSON.parse(JSON.stringify(res.data.results))

                    this.getAppsStatus()

                    // 按原关键字再搜索
                    if (this.searchKeyword) {
                        this.search()
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.showLoading = false
                    this.isPageLoading = false
                }
            },

            /**
             * 获取所有命名空间列表
             */
            async getAllNamespaces (reload) {
                this.allNamespaces = []
                try {
                    clearTimeout(this.statusTimer)
                    const res = await this.$store.dispatch('helm/getNamespaceList', {
                        projectId: this.projectId,
                        params: {
                            filter_use_perm: false
                        }
                    })
                    res.data.forEach(item => {
                        item.id = item.name
                        item.name = item.name.split('(')[0]
                        let clusterId = ''
                        const matcher = item.id.match(/^[\S|\s]*\((\S+)\)$/)
                        if (matcher && matcher.length > 1) {
                            clusterId = matcher[1]
                        }
                        item.children.forEach(child => {
                            child.namespace_id = `${clusterId}:${child.name}`
                        })
                    })
                    this.allNamespaces = res.data
                    this.namespaceList = res.data
                    this.setNamespaceList()
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            handleClusterChange () {
                this.searchNamespace = ''
                this.setNamespaceList()
            },

            setNamespaceList () {
                if (this.searchScope) {
                    const match = this.allNamespaces.find(item => {
                        return item.id.indexOf(this.searchScope) > -1
                    })

                    if (match) {
                        this.namespaceList = match.children
                    } else {
                        this.namespaceList = []
                    }
                } else {
                    this.namespaceList = this.allNamespaces
                }
            },

            /**
             * 提交回滚数据
             * @return {[type]} [description]
             */
            async submitRebackData () {
                const projectId = this.projectId
                const appId = this.curApp.id
                const params = {
                    release: this.versionId
                }

                if (this.isRebackLoading || !this.versionId) {
                    return false
                } else {
                    this.isRebackLoading = true
                }

                try {
                    await this.$store.dispatch('helm/reback', { projectId, appId, params })
                    this.rebackDialogConf.isShow = false
                    this.isOperaLayerShow = false
                    this.checkingAppStatus(this.curApp, 'rollback')
                } catch (e) {
                    this.showErrorDialog(e, this.$t('回滚失败'), 'reback')
                } finally {
                    this.isRebackLoading = false
                }
            },

            updateApp (appId, status) {
                this.appList.forEach((app, index) => {
                    if (app.id === appId) {
                        app.transitioning_action = status.transitioning_action
                        app.transitioning_message = status.transitioning_message
                        app.transitioning_on = status.transitioning_on
                        app.transitioning_result = status.transitioning_result
                    }
                })
                this.appListCache.forEach((app, index) => {
                    if (app.id === appId) {
                        app.transitioning_action = status.transitioning_action
                        app.transitioning_message = status.transitioning_message
                        app.transitioning_on = status.transitioning_on
                        app.transitioning_result = status.transitioning_result
                    }
                })
            },

            /**
             * 查询应用的状态
             * @param  {object} app 应用对象
             */
            checkingAppStatus (app, action) {
                if (app) {
                    const status = {
                        name: app.name,
                        transitioning_on: true,
                        transitioning_action: action,
                        transitioning_result: false,
                        transitioning_message: ''
                    }
                    this.operaRunningApp[app.id] = status
                    this.updateApp(app.id, status)
                }

                this.appCheckTime = FAST_TIME
                this.getAppsStatus()
            },

            /**
             * 查看app状态，包括创建、更新、回滚、删除
             * @param  {object} app 应用对象
             */
            getAppsStatus () {
                clearTimeout(this.statusTimer)
                this.statusTimer = setTimeout(async () => {
                    if (this.isOperaLayerShow) {
                        return false
                    }
                    try {
                        const data = this.getParams()
                        const res = await this.$store.dispatch('helm/getAppList', data)

                        this.appList = res.data.results
                        this.appListCache = JSON.parse(JSON.stringify(res.data.results))

                        this.appCheckTime = SLOW_TIME
                        this.appList.forEach(app => {
                            if (app.transitioning_on) {
                                this.appCheckTime = FAST_TIME // 如果有更新中的app，继续快速轮询
                            }
                        })

                        // 按原关键字再搜索
                        if (this.searchKeyword) {
                            this.search()
                        }

                        this.diffAppStatus()
                        this.getAppsStatus()
                    } catch (e) {
                        catchErrorHandler(e, this)
                    } finally {
                        this.showLoading = false
                    }
                }, this.appCheckTime)
            },

            /**
             * 遍历appList 获取应用状态
             * @param {number} appId appId
             * @return {object} app状态数据
             */
            getAppStatusById (appId) {
                let result = null
                this.appList.forEach(item => {
                    if (String(item.id) === appId) {
                        result = {
                            name: item.name,
                            transitioning_on: item.transitioning_on,
                            transitioning_action: item.transitioning_action,
                            transitioning_result: item.transitioning_result,
                            transitioning_message: item.transitioning_message
                        }
                    }
                })
                return result
            },

            /**
             * 对比各个应用发生变化的状态
             */
            diffAppStatus () {
                const continueRunningApps = {}

                this.appList.forEach(app => {
                    if (app.transitioning_on) {
                        continueRunningApps[app.id] = {
                            name: app.name,
                            transitioning_on: app.transitioning_on,
                            transitioning_action: app.transitioning_action,
                            transitioning_result: app.transitioning_result,
                            transitioning_message: app.transitioning_message
                        }
                    }
                })

                for (const appId in this.operaRunningApp) {
                    const appStatus = this.getAppStatusById(appId)

                    // 和上次对比，如果应用不存在，则已经删除成功
                    if (!appStatus) {
                        const app = this.operaRunningApp[appId]
                        this.$bkMessage({
                            theme: 'success',
                            message: `${app.name}${this.$t('删除成功')}`
                        })
                        delete this.operaRunningApp[appId]
                        return true
                    }

                    // 如果操作状态结束
                    if (!appStatus.transitioning_on) {
                        const action = this.appAction[appStatus.transitioning_action]

                        if (appStatus.transitioning_result) {
                            this.$bkMessage({
                                theme: 'success',
                                message: `${appStatus.name}${action}${this.$t('成功')}`
                            })
                        } else {
                            this.$bkMessage({
                                theme: 'error',
                                message: `${appStatus.name}${action}${this.$t('失败')}`
                            })
                        }
                        delete this.operaRunningApp[appId]
                    }
                }

                this.operaRunningApp = continueRunningApps // 保存当前更新中的应用
            },

            /**
             * 显示回滚相应的预览对比列表
             * @param  {object} app 应用
             */
            async showRebackPreview (app) {
                const projectId = this.projectId
                const appId = this.curApp.id
                const params = {
                    release: this.versionId
                }

                this.isRebackVersionLoading = true
                this.difference = ''
                this.rebackPreviewList = []

                try {
                    const res = await this.$store.dispatch('helm/previewReback', {
                        projectId,
                        appId,
                        params
                    })

                    this.rebackEditorConfig.value = res.data.notes

                    for (const key in res.data.content) {
                        this.rebackPreviewList.push({
                            name: key,
                            value: res.data.content[key]
                        })
                    }
                    if (res.data.difference) {
                        this.difference = res.data.difference
                    } else {
                        this.difference = this.$t('与当前线上版本没有内容差异')
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isRebackVersionLoading = false
                }
            },

            /**
             *  获取应用
             * @param  {number} appId 应用ID
             */
            async getAppById (appId) {
                let result = {}
                const projectId = this.projectId

                this.previewLoading = true
                try {
                    const res = await this.$store.dispatch('helm/getAppById', { projectId, appId })
                    result = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.previewLoading = false
                }

                return result
            },

            /**
             * 取消回滚操作
             */
            cancelReback () {
                this.appCheckTime = FAST_TIME
                this.rebackDialogConf.isShow = false
                this.isOperaLayerShow = false
                this.getAppsStatus()
            },

            /**
             * 隐藏应用详情面板回调
             */
            hideAppInfoSlider () {
                this.isOperaLayerShow = false
                this.appCheckTime = FAST_TIME
                this.getAppsStatus()
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
