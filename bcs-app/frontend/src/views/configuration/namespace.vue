<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-config-namespace-title">
                {{$t('命名空间')}}
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper biz-namespace-loading" style="padding: 0;" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <app-exception
                v-if="exceptionCode && !isInitLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>
            <template v-if="!exceptionCode && !isInitLoading">
                <div class="biz-panel-header">
                    <div class="left">
                        <button class="bk-button bk-primary" @click.stop.prevent="showAddNamespace">
                            <i class="bk-icon icon-plus"></i>
                            <span>{{$t('新建')}}</span>
                        </button>
                        <bk-tooltip v-if="showSyncBtn" :content="$t('同步非本页面创建的命名空间数据')" placement="top">
                            <button class="bk-button" @click.stop.prevent="syncNamespace">
                                <span>{{$t('同步命名空间')}}</span>
                            </button>
                        </bk-tooltip>
                        <span class="biz-tip ml10" style="vertical-align: middle;">{{$t('命名空间创建后不可更改')}}</span>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            ref="dataSearcher"
                            :search-key.sync="search"
                            :scope-list="searchScopeList"
                            :search-scope.sync="searchScope"
                            @search="handleSearch"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>

                <div class="biz-namespace">
                    <div class="biz-table-wrapper">
                        <table class="bk-table has-table-hover biz-table biz-namespace-table" v-bkloading="{ isLoading: isPageLoading }">
                            <thead>
                                <tr>
                                    <th style="width: 200px;">{{$t('名称')}}</th>
                                    <th style="width: 200px;">{{$t('所属集群')}}</th>
                                    <th>{{$t('变量')}}</th>
                                    <th style="width: 220px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curPageData.length && !isInitLoading">
                                    <tr v-for="(ns, index) in curPageData" :class="ns.isEdit ? 'is-edit' : ''" :key="ns.id">
                                        <td style="white-space: nowrap;" class="biz-table-title">
                                            <span class="text">{{ns.name}}</span>
                                        </td>
                                        <td style="white-space: nowrap;line-height: 10px;">
                                            <bk-tooltip :content="ns.cluster_id" placement="top">
                                                <p class="biz-text-wrapper">{{ns.cluster_name}}</p>
                                            </bk-tooltip>
                                        </td>
                                        <td style="white-space: nowrap;line-height: 10px;">
                                            <template v-if="ns.ns_vars.length">
                                                <div style="position: relative;">
                                                    <div class="labels-wrapper" :class="ns.isExpandLabels ? 'expand' : ''" :ref="`${pageConf.curPage}-real${index}`">
                                                        <div class="labels-inner" v-for="(label, labelIndex) in ns.ns_vars" :key="labelIndex">
                                                            <bk-tooltip :delay="300" placement="top">
                                                                <span class="key">{{label.key}}</span>
                                                                <template slot="content">
                                                                    <p class="app-biz-node-label-tip-content">{{label.key}}</p>
                                                                </template>
                                                            </bk-tooltip>
                                                            <template v-if="label.value">
                                                                <bk-tooltip :delay="300" placement="top">
                                                                    <span class="value">{{label.value}}</span>
                                                                    <template slot="content">
                                                                        <p class="app-biz-node-label-tip-content">{{label.value}}</p>
                                                                    </template>
                                                                </bk-tooltip>
                                                            </template>
                                                            <template v-else>
                                                                <span class="value">{{label.value}}</span>
                                                            </template>
                                                        </div>
                                                        <a href="javascript:void(0);"
                                                            class="bk-text-button toggle-labels"
                                                            :class="ns.isExpandLabels ? 'expand' : ''"
                                                            v-if="ns.showExpand"
                                                            @click.stop="toggleLabel(ns, index)">
                                                            <template v-if="!ns.isExpandLabels">
                                                                {{$t('展开')}}<i class="bk-icon icon-angle-down"></i>
                                                            </template>
                                                            <template v-else>
                                                                {{$t('收起')}}<i class="bk-icon icon-angle-up"></i>
                                                            </template>
                                                        </a>
                                                    </div>
                                                    <div class="labels-wrapper fake" :ref="`${pageConf.curPage}-fake${index}`">
                                                        <div class="labels-inner" v-for="(label, labelIndex) in ns.ns_vars" :key="labelIndex">
                                                            <span class="key">{{label.key}}</span>
                                                            <span class="value">{{label.value}}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </template>
                                            <template v-else>--</template>
                                        </td>
                                        <td>
                                            <a href="javascript:void(0)" class="bk-text-button" @click="showEditNamespace(ns, index)">{{$t('设置变量值')}}</a>
                                            <a class="bk-text-button" v-if="!ns.permissions.use" @click="applyUsePermission(ns)">{{$t('申请使用权限')}}</a>
                                            <!-- <a href="javascript:void(0)" class="bk-text-button" @click="showDelNamespace(ns, index)" v-if="curProject.kind === 1 || curProject.kind === 3"> -->
                                            <a href="javascript:void(0)" class="bk-text-button" @click="showDelNamespace(ns, index)">
                                                {{$t('删除')}}
                                            </a>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else-if="!curPageData.length && !isInitLoading">
                                    <tr class="no-hover">
                                        <td colspan="4">
                                            <div class="bk-message-box">
                                                <p class="message empty-message">{{$t('无数据')}}</p>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr class="no-hover">
                                        <td colspan="4">
                                            <div class="bk-message-box">
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                    <div class="biz-page-wrapper" v-if="pageConf.total">
                        <bk-page-counter
                            :is-en="isEn"
                            :total="pageConf.total"
                            :page-size="pageConf.pageSize"
                            @change="changePageSize">
                        </bk-page-counter>
                        <bk-paging
                            :cur-page.sync="pageConf.curPage"
                            :total-page="pageConf.totalPage"
                            @page-change="pageChange">
                        </bk-paging>
                    </div>
                </div>
            </template>
        </div>

        <bk-sideslider
            :is-show.sync="addNamespaceConf.isShow"
            :title="addNamespaceConf.title"
            :width="addNamespaceConf.width"
            :quick-close="false"
            class="biz-cluster-set-variable-sideslider"
            @hidden="hideAddNamespace">
            <template slot="content">
                <div class="wrapper" style="position: relative;" v-bkloading="{ isLoading: addNamespaceConf.loading }">
                    <div class="bk-form bk-form-vertical set-label-form">
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <label class="bk-label label">{{$t('名称：')}}</label>
                            </div>
                            <div class="right" style="margin-left: 20px;">
                                <label class="bk-label label">{{$t('所属集群：')}}</label>
                            </div>
                        </div>
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <input type="text" class="bk-form-input" :placeholder="$t('请输入')" v-model="addNamespaceConf.namespaceName" maxlength="30">
                            </div>
                            <div class="right" style="margin-left: 20px;">
                                <div class="cluster-wrapper">
                                    <bk-selector
                                        :field-type="'cluster'"
                                        :placeholder="$t('请选择')"
                                        :setting-key="'cluster_id'"
                                        :display-key="'name'"
                                        :searchable="true"
                                        :search-key="'name'"
                                        :selected.sync="clusterId"
                                        :list="clusterList"
                                        @item-selected="chooseCluster">
                                    </bk-selector>
                                </div>
                            </div>
                        </div>
                        <template v-if="addNamespaceConf.variableList && addNamespaceConf.variableList.length">
                            <div class="bk-form-item flex-item">
                                <div class="left">
                                    <label class="bk-label label">{{$t('变量：')}}</label>
                                </div>
                            </div>
                            <div class="bk-form-item">
                                <div class="bk-form-content">
                                    <div class="biz-key-value-wrapper mb10">
                                        <div class="biz-key-value-item" v-for="(variable, index) in addNamespaceConf.variableList" :key="index">
                                            <bk-tooltip placement="top" :delay="500">
                                                <input type="text" class="bk-form-input" disabled v-model="variable.leftContent">
                                                <template slot="content">
                                                    <p style="text-align: left; white-space: normal;word-break: break-all;">{{variable.leftContent}}</p>
                                                </template>
                                            </bk-tooltip>
                                            <span class="equals-sign">=</span>
                                            <input type="text" class="bk-form-input right" :placeholder="$t('值')" v-model="variable.value">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <div class="action-inner">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="confirmAddNamespace">
                                {{$t('保存')}}
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideAddNamespace">
                                {{$t('取消')}}
                            </button>
                        </div>
                    </div>
                </div>
            </template>
        </bk-sideslider>

        <bk-sideslider
            :is-show.sync="editNamespaceConf.isShow"
            :title="editNamespaceConf.title"
            :width="editNamespaceConf.width"
            :quick-close="false"
            class="biz-cluster-set-variable-sideslider"
            @hidden="hideEditNamespace">
            <template slot="content">
                <div class="wrapper" style="position: relative;" v-bkloading="{ isLoading: editNamespaceConf.loading }">
                    <div class="bk-form bk-form-vertical set-label-form">
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <label class="bk-label label">{{$t('名称：')}}</label>
                            </div>
                            <div class="right" style="margin-left: 20px;">
                                <label class="bk-label label">{{$t('所属集群：')}}</label>
                            </div>
                        </div>
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <input type="text" class="bk-form-input" v-model="editNamespaceConf.namespaceName" v-if="editNamespaceConf.canEdit">
                                <input type="text" class="bk-form-input" disabled v-model="editNamespaceConf.namespaceName" v-else>
                            </div>
                            <div class="right" style="margin-left: 20px;">
                                <div class="cluster-wrapper">
                                    <bk-selector
                                        :field-type="'cluster'"
                                        :placeholder="$t('请选择')"
                                        :setting-key="'cluster_id'"
                                        :display-key="'name'"
                                        :searchable="true"
                                        :search-key="'name'"
                                        :selected.sync="clusterId"
                                        :list="clusterList"
                                        :disabled="!editNamespaceConf.canEdit"
                                        @item-selected="chooseCluster">
                                    </bk-selector>
                                </div>
                            </div>
                        </div>
                        <template v-if="editNamespaceConf.variableList && editNamespaceConf.variableList.length">
                            <div class="bk-form-item flex-item">
                                <div class="left">
                                    <label class="bk-label label" v-if="isEn">Variables: <span class="biz-tip f13 fn">(You can create more variables in the namespace through <router-link class="bk-text-button" :to="{ name: 'var', params: { projectCode: projectCode } }">Variables</router-link>)</span></label>
                                    <label class="bk-label label" v-else>变量：<span class="biz-tip f13 fn">（可通过 <router-link class="bk-text-button" :to="{ name: 'var', params: { projectCode: projectCode } }">变量管理</router-link> 创建更多作用在命名空间的变量）</span></label>
                                </div>
                            </div>
                            <div class="bk-form-item">
                                <div class="bk-form-content">
                                    <div class="biz-key-value-wrapper mb10">
                                        <div class="biz-key-value-item" v-for="(variable, index) in editNamespaceConf.variableList" :key="index">
                                            <bk-tooltip placement="top" :delay="500">
                                                <input type="text" class="bk-form-input" disabled v-model="variable.leftContent">
                                                <template slot="content">
                                                    <p style="text-align: left; white-space: normal;word-break: break-all;">{{variable.leftContent}}</p>
                                                </template>
                                            </bk-tooltip>
                                            <span class="equals-sign">=</span>
                                            <input type="text" class="bk-form-input right" :placeholder="$t('值')" v-model="variable.value">
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="action-inner">
                                <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="confirmEditNamespace">
                                    {{$t('保存')}}
                                </button>
                                <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideEditNamespace">
                                    {{$t('取消')}}
                                </button>
                            </div>
                        </template>
                        <template v-else>
                            <div class="biz-tip mt40">
                                <template v-if="isEn">The project does not set an environment variable that acts on the namespace. You cannot set the variable value. You can go to the <router-link class="bk-text-button" :to="{ name: 'var', params: { projectCode: projectCode } }">Variables</router-link> to set.</template>
                                <template v-else>该项目未设置作用在命名空间范围的环境变量，无法设置变量值，可前往 <router-link class="bk-text-button" :to="{ name: 'var', params: { projectCode: projectCode } }">变量管理</router-link> 设置</template>
                            </div>
                        </template>
                    </div>
                </div>
            </template>
        </bk-sideslider>

        <bk-dialog
            :is-show.sync="delNamespaceDialogConf.isShow"
            :width="delNamespaceDialogConf.width"
            :close-icon="delNamespaceDialogConf.closeIcon"
            :ext-cls="'biz-namespace-del-dialog'"
            :has-header="false"
            :quick-close="false">
            <div slot="content" style="padding: 0 20px;">
                <div class="title">
                    {{$t('删除命名空间')}}
                </div>
                <div class="info">
                    <template v-if="isEn">
                        Confirm want to delete the namespace: {{delNamespaceDialogConf.ns.name}}?
                    </template>
                    <template v-else>
                        您确定要删除Namespace: {{delNamespaceDialogConf.ns.name}}吗？
                    </template>
                </div>
                <div style="color: red;">
                    {{$t('删除Namespace将销毁Namespace下的所有资源，销毁后所有数据将被清除且不可恢复，请提前备份好数据。')}}
                </div>
            </div>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                        @click="delNamespaceConfirm">
                        {{$t('删除')}}
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="delNamespaceCancel">
                        {{$t('取消')}}
                    </button>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="delMesosNamespaceDialogConf.isShow"
            :width="delMesosNamespaceDialogConf.width"
            :close-icon="delMesosNamespaceDialogConf.closeIcon"
            :ext-cls="'biz-namespace-mesos-del-dialog'"
            :has-header="false"
            :has-footer="delMesosNamespaceDialogConf.hasFooter"
            :quick-close="false"
            @cancel="delMesosNamespaceCancel">
            <div slot="content" style="padding: 0 20px;">
                <div class="title">
                    {{$t('删除命名空间')}}
                </div>
                <div v-bkloading="{ isLoading: delMesosNamespaceDialogConf.loading, opacity: 1 }">
                    <div v-if="delMesosNamespaceDialogConf.list.length">
                        <div style="color: red; margin-top: 10px;">
                            {{$t('命名空间包含以下资源，请先删除资源，然后再删除命名空间')}}
                        </div>
                        <div class="res-list-container" :key="index" v-for="(item, index) in delMesosNamespaceDialogConf.list">
                            <div class="res-list-key">{{item.key}}</div>
                            <ul class="res-list">
                                <li :title="valItem" v-for="(valItem, valItemIndex) in item.val" :key="valItemIndex">{{valItem}}</li>
                            </ul>
                        </div>
                    </div>
                    <template v-else>
                        <div class="info">
                            <template v-if="isEn">
                                Confirm want to delete the namespace: {{delMesosNamespaceDialogConf.ns.name}}?
                            </template>
                            <template v-else>
                                您确定要删除Namespace: {{delMesosNamespaceDialogConf.ns.name}}吗？
                            </template>
                        </div>
                    </template>
                </div>
            </div>
            <template slot="footer">
                <div class="bk-dialog-outer" v-if="!delMesosNamespaceDialogConf.list.length">
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                        @click="delMesosNamespaceConfirm">
                        {{$t('删除')}}
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="delMesosNamespaceCancel">
                        {{$t('取消')}}
                    </button>
                </div>
                <div class="bk-dialog-outer" v-else></div>
            </template>
        </bk-dialog>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'

    export default {
        data () {
            // 环境类型 list
            const envList = [
                {
                    id: 'dev',
                    name: 'dev'
                },
                {
                    id: 'test',
                    name: 'test'
                },
                {
                    id: 'prod',
                    name: 'prod'
                }
            ]
            return {
                isNamespaceAdd: false,
                envList: envList,
                addEnvIndex: -1,
                editEnvIndex: -1,
                clusterList: [],
                clusterId: '',
                editClusterId: -1,
                isPageLoading: false,
                pageConf: {
                    total: 1,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                namespaceList: [],
                // 缓存，用于搜索
                namespaceListTmp: [],
                curPageData: [],
                newName: '',
                editName: '',
                isInitLoading: true,
                search: '',
                addNamespaceConf: {
                    isShow: false,
                    title: this.$t('新建命名空间'),
                    width: 680,
                    variableList: [],
                    namespaceName: '',
                    loading: false
                },
                editNamespaceConf: {
                    isShow: false,
                    title: '',
                    width: 680,
                    variableList: [],
                    namespaceName: '',
                    canEdit: false,
                    ns: {},
                    loading: false
                },
                permissions: {},
                exceptionCode: null,
                bkMessageInstance: null,
                delNamespaceDialogConf: {
                    isShow: false,
                    width: 650,
                    title: '',
                    closeIcon: false,
                    ns: {}
                },
                showSyncBtn: false,
                delMesosNamespaceDialogConf: {
                    isShow: false,
                    width: 650,
                    title: '',
                    closeIcon: true,
                    ns: {},
                    loading: false,
                    list: [],
                    hasFooter: false
                }
            }
        },
        computed: {
            projectId () {
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
            },
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            },
            isEn () {
                return this.$store.state.isEn
            },
            curProject () {
                return this.$store.state.curProject
            },
            isClusterDataReady () {
                return this.$store.state.cluster.isClusterDataReady
            }
        },
        watch: {
            isClusterDataReady: {
                immediate: true,
                handler (val) {
                    if (val) {
                        setTimeout(() => {
                            if (this.searchScopeList.length) {
                                const clusterIds = this.searchScopeList.map(item => item.id)
                                // 使用当前缓存
                                if (sessionStorage['bcs-cluster'] && clusterIds.includes(sessionStorage['bcs-cluster'])) {
                                    this.searchScope = sessionStorage['bcs-cluster']
                                } else {
                                    this.searchScope = this.searchScopeList[1].id
                                }
                            }
                            this.fetchNamespaceList()
                        }, 1000)
                    }
                }
            }
        },
        created () {
            this.getClusters()
        },
        destroyed () {
            this.bkMessageInstance && this.bkMessageInstance.close()
        },
        methods: {
            /**
             * 同步命名空间
             */
            async syncNamespace () {
                try {
                    await this.$store.dispatch('configuration/syncNamespace', {
                        projectId: this.projectId
                    })

                    // const me = this
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'success',
                        message: this.$t('同步命名空间任务已经启动，请稍后刷新'),
                        delay: 1000
                        // onClose: () => {
                        //     me.refresh()
                        // }
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.fetchNamespaceList()
            },

            /**
             * 分页大小更改
             *
             * @param {number} pageSize pageSize
             */
            changePageSize (pageSize) {
                this.pageConf.pageSize = pageSize
                this.pageConf.curPage = 1
                this.initPageConf()
                this.pageChange(this.pageConf.curPage)
            },

            /**
             * 搜索框清除事件
             */
            clearSearch () {
                this.search = ''
                this.handleSearch()
            },

            async applyUsePermission (ns) {
                this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'use',
                    resource_code: ns.id,
                    resource_name: ns.name,
                    resource_type: 'namespace',
                    is_raise: false
                }).then(res => {
                    if (res.data) {
                        const url = res.data.apply_url + `&project_code=${this.projectCode}`
                        window.open(url)
                    }
                })
            },
            /**
             * 获取所有的集群
             */
            async getClusters () {
                try {
                    const res = await this.$store.dispatch('cluster/getPermissionClusterList', this.projectId)
                    const list = res.data.results || []
                    list.forEach(item => {
                        item.name = `${item.name}(${item.cluster_id})`
                        this.clusterList.push(item)
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 加载命名空间列表
             */
            async fetchNamespaceList () {
                try {
                    const res = await this.$store.dispatch('configuration/getNamespaceList', {
                        projectId: this.projectId
                    })
                    this.permissions = JSON.parse(JSON.stringify(res.permissions || {}))

                    this.showSyncBtn = this.permissions.sync_namespace

                    const list = []
                    res.data.forEach(item => {
                        item.isExpandLabels = false
                        // 是否显示标签的展开按钮
                        item.showExpand = false
                        list.push(item)
                    })
                    this.namespaceList.splice(0, this.namespaceList.length, ...list)
                    this.namespaceListTmp.splice(0, this.namespaceListTmp.length, ...list)
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)

                    setTimeout(() => {
                        this.curPageData.forEach((item, index) => {
                            const fake = this.$refs[`${this.pageConf.curPage}-fake${index}`]
                            const real = this.$refs[`${this.pageConf.curPage}-real${index}`]
                            if (fake && real && fake[0] && real[0]) {
                                if (fake[0].offsetHeight > real[0].offsetHeight * 2) {
                                    item.showExpand = true
                                }
                            }
                        })
                    }, 0)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 初始化弹层翻页条
             */
            initPageConf () {
                const total = this.namespaceList.length
                this.pageConf.total = total
                this.pageConf.curPage = 1
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize) || 1
            },

            /**
             * 翻页回调
             *
             * @param {number} page 当前页
             */
            pageChange (page) {
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData.splice(0, this.curPageData.length, ...data)
                this.isPageLoading = true
                setTimeout(() => {
                    this.curPageData.forEach((item, index) => {
                        const fake = this.$refs[`${this.pageConf.curPage}-fake${index}`]
                        const real = this.$refs[`${this.pageConf.curPage}-real${index}`]
                        if (fake && real && fake[0] && real[0]) {
                            if (fake[0].offsetHeight > real[0].offsetHeight * 2) {
                                item.showExpand = true
                            }
                        }
                    })
                    this.isPageLoading = false
                }, 100)
            },

            /**
             * 展开或收起当前行的标签
             *
             * @param {Object} ns 当前行 ns 对象
             * @param {number} index 当前行 ns 对象索引
             */
            toggleLabel (ns, index) {
                ns.isExpandLabels = !ns.isExpandLabels
                this.$set(this.curPageData, index, ns)
            },

            /**
             * 获取当前这一页的数据
             *
             * @param {number} page 当前页
             *
             * @return {Array} 当前页数据
             */
            getDataByPage (page) {
                // 如果没有page，重置
                if (!page) {
                    this.pageConf.curPage = page = 1
                }
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                this.isPageLoading = true
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.namespaceList.length) {
                    endIndex = this.namespaceList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.namespaceList.slice(startIndex, endIndex)
            },

            /**
             * 下拉框选择所属集群
             */
            chooseCluster (index, data) {
                const len = this.clusterList.length
                for (let i = len - 1; i >= 0; i--) {
                    if (String(this.clusterList[i].cluster_id) === String(data.cluster_id)) {
                        this.clusterId = data.cluster_id
                        break
                    }
                }
            },

            /**
             * 显示添加命名空间的 sideslider
             */
            async showAddNamespace () {
                if (!this.permissions.create) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'create',
                        resource_type: 'namespace'
                    })
                }
                this.addNamespaceConf.isShow = true
                this.addNamespaceConf.loading = true
                try {
                    const res = await this.$store.dispatch('configuration/getNamespaceVariable', {
                        projectId: this.projectId,
                        namespaceId: 0
                    })
                    const variableList = []
                    ;(res.data || []).forEach(item => {
                        item.leftContent = `${item.name}(${item.key})`
                        variableList.push(item)
                    })

                    this.addNamespaceConf.variableList.splice(
                        0,
                        this.addNamespaceConf.variableList.length,
                        ...variableList
                    )
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    setTimeout(() => {
                        this.addNamespaceConf.loading = false
                    }, 300)
                }
            },

            /**
             * 添加命名空间 sideslder 取消按钮
             */
            hideAddNamespace () {
                this.addNamespaceConf.isShow = false
                this.addNamespaceConf.variableList.splice(0, this.addNamespaceConf.variableList.length, ...[])
                this.addNamespaceConf.namespaceName = ''
                this.clusterId = ''
            },

            /**
             * 添加命名空间确认按钮
             */
            async confirmAddNamespace () {
                const namespaceName = this.addNamespaceConf.namespaceName
                if (!namespaceName.trim()) {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请填写命名空间名称')
                    })
                    return
                }

                if (namespaceName.length < 2) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('命名空间名称不得小于2个字符')
                    })
                    return
                }

                if (!/^[a-z0-9]([-a-z0-9]*[a-z0-9])?$/g.test(namespaceName)) {
                    this.$bkMessage({
                        theme: 'error',
                        delay: 5000,
                        message: this.$t('命名空间名称只能包含小写字母、数字以及连字符(-)，不能以数字开头，且连字符（-）后面必须接英文或者数字')
                    })
                    return
                }

                if (!this.clusterId) {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        deplay: 5000,
                        message: this.$t('请选择所属集群')
                    })
                    return
                }

                const variableList = []
                const len = this.addNamespaceConf.variableList.length
                for (let i = 0; i < len; i++) {
                    const variable = this.addNamespaceConf.variableList[i]
                    variableList.push({
                        id: variable.id,
                        key: variable.key,
                        name: variable.name,
                        value: variable.value
                    })
                }

                try {
                    this.addNamespaceConf.loading = true
                    await this.$store.dispatch('configuration/addNamespace', {
                        projectId: this.projectId,
                        name: namespaceName,
                        cluster_id: this.clusterId,
                        ns_vars: variableList
                    })

                    this.hideAddNamespace()
                    setTimeout(() => {
                        this.fetchNamespaceList()
                    }, 300)
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.addNamespaceConf.loading = false
                }
            },

            /**
             * 显示修改命名空间的 sideslider
             *
             * @param {Object} ns 当前 namespace 对象
             * @param {number} index 当前 namespace 对象的索引
             */
            async showEditNamespace (ns, index) {
                if (!ns.permissions.edit) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'edit',
                        resource_code: ns.id,
                        resource_name: ns.name,
                        resource_type: 'namespace'
                    })
                }
                this.editNamespaceConf.isShow = true
                this.editNamespaceConf.loading = true
                this.editNamespaceConf.namespaceName = ns.name
                this.editNamespaceConf.title = this.$t('修改命名空间：{nsName}', {
                    nsName: ns.name
                })
                this.editNamespaceConf.ns = Object.assign({}, ns)
                this.clusterId = ns.cluster_id

                // mesos 可以修改命名空间名称和所属集群
                this.editNamespaceConf.canEdit = false

                try {
                    const res = await this.$store.dispatch('configuration/getNamespaceVariable', {
                        projectId: this.projectId,
                        namespaceId: ns.id
                    })
                    const variableList = []
                    ;(res.data || []).forEach(item => {
                        item.leftContent = `${item.name}(${item.key})`
                        variableList.push(item)
                    })

                    this.editNamespaceConf.variableList.splice(
                        0,
                        this.editNamespaceConf.variableList.length,
                        ...variableList
                    )
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    setTimeout(() => {
                        this.editNamespaceConf.loading = false
                    }, 300)
                }
            },

            /**
             * 修改命名空间 sideslder 取消按钮
             */
            hideEditNamespace () {
                this.editNamespaceConf.isShow = false
                this.editNamespaceConf.variableList.splice(0, this.editNamespaceConf.variableList.length, ...[])
                this.editNamespaceConf.namespaceName = ''
                this.editNamespaceConf.title = ''
                this.editNamespaceConf.canEdit = false
                this.editNamespaceConf.ns = Object.assign({}, {})
                this.clusterId = ''
            },

            /**
             * 修改命名空间确认按钮
             */
            async confirmEditNamespace () {
                const namespaceName = this.editNamespaceConf.namespaceName
                if (!namespaceName.trim()) {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请填写命名空间名称')
                    })
                    return
                }

                if (namespaceName.length < 2) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('命名空间名称不得小于2个字符')
                    })
                    return
                }
                if (!/^[a-z0-9]([-a-z0-9]*[a-z0-9])?$/g.test(namespaceName)) {
                    this.$bkMessage({
                        theme: 'error',
                        delay: 5000,
                        message: this.$t('命名空间名称只能包含小写字母、数字以及连字符(-)，不能以数字开头，且连字符（-）后面必须接英文或者数字')
                    })
                    return
                }

                if (!this.clusterId) {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择所属集群')
                    })
                    return
                }

                const variableList = []
                const len = this.editNamespaceConf.variableList.length
                for (let i = 0; i < len; i++) {
                    const variable = this.editNamespaceConf.variableList[i]
                    variableList.push({
                        id: variable.id,
                        key: variable.key,
                        name: variable.name,
                        value: variable.value
                    })
                }

                try {
                    this.editNamespaceConf.loading = true
                    await this.$store.dispatch('configuration/editNamespace', {
                        projectId: this.projectId,
                        cluster_id: this.clusterId,
                        name: namespaceName,
                        namespaceId: this.editNamespaceConf.ns.id,
                        ns_vars: variableList
                    })

                    this.hideEditNamespace()
                    setTimeout(() => {
                        this.fetchNamespaceList()
                    }, 300)
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.editNamespaceConf.loading = false
                }
            },

            /**
             * 显示删除 namespace 确认框
             *
             * @param {Object} ns 当前 namespace 对象
             * @param {number} index 当前 namespace 对象的索引
             */
            async showDelNamespace (ns, index) {
                if (this.curProject.kind === 1 || this.curProject.kind === 3) {
                    this.delNamespaceDialogConf.isShow = true
                    this.delNamespaceDialogConf.ns = Object.assign({}, ns)
                } else {
                    this.delMesosNamespaceDialogConf.isShow = true
                    this.delMesosNamespaceDialogConf.loading = true
                    this.delMesosNamespaceDialogConf.ns = Object.assign({}, ns)
                    await this.fetchMesosNamespaceRes()
                }
            },

            /**
             * 获取 mesos 命名空间里的资源
             */
            async fetchMesosNamespaceRes () {
                try {
                    const res = await this.$store.dispatch('configuration/getMesosNamespaceRes', {
                        projectId: this.projectId,
                        namespaceId: this.delMesosNamespaceDialogConf.ns.id
                    })
                    // const res = {
                    //     code: 0,
                    //     data: {
                    //         secret: [],
                    //         deployment: [],
                    //         application: [
                    //             // 'test323-test',
                    //             // 'test12312application-1'
                    //         ],
                    //         configmap: [
                    //             // 'configmap-1'
                    //         ],
                    //         service: []
                    //     },
                    //     request_id: 'ea80406250934f0ea6b70e61fce042ed'
                    // }

                    const data = res.data
                    const list = []
                    Object.keys(data).forEach(k => {
                        if (data[k].length) {
                            list.push({
                                key: k,
                                val: data[k],
                                str: data[k].join(';')
                            })
                        }
                    })
                    this.delMesosNamespaceDialogConf.list.splice(0, this.delMesosNamespaceDialogConf.list.length, ...list)
                    this.delMesosNamespaceDialogConf.hasFooter = !this.delMesosNamespaceDialogConf.list.length

                    setTimeout(() => {
                        this.delMesosNamespaceDialogConf.loading = false
                    }, 100)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 删除当前 namespace
             *
             * @param {Object} ns 当前 namespace 对象
             * @param {number} index 当前 namespace 对象的索引
             */
            async delNamespaceConfirm () {
                try {
                    this.isPageLoading = true
                    this.delNamespaceCancel()
                    await this.$store.dispatch('configuration/delNamespace', {
                        projectId: this.projectId,
                        namespaceId: this.delNamespaceDialogConf.ns.id
                    })
                    this.search = ''
                    this.searchScope = ''
                    // handleRefresh 会触发 refresh，refresh 触发 fetchNamespaceList
                    // fetchNamespaceList 里把 isPageLoading 设置为 false
                    this.$refs.dataSearcher.handleRefresh()
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除Namespace成功')
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 取消删除当前 namespace
             *
             * @param {Object} ns 当前 namespace 对象
             * @param {number} index 当前 namespace 对象的索引
             */
            delNamespaceCancel () {
                this.delNamespaceDialogConf.isShow = false
                setTimeout(() => {
                    this.delNamespaceDialogConf.ns = Object.assign({}, {})
                }, 300)
            },

            /**
             * 删除当前 namespace mesos
             *
             * @param {Object} ns 当前 namespace 对象
             * @param {number} index 当前 namespace 对象的索引
             */
            async delMesosNamespaceConfirm () {
                try {
                    this.isPageLoading = true
                    this.delMesosNamespaceCancel()
                    await this.$store.dispatch('configuration/deleteMesosNamespace', {
                        projectId: this.projectId,
                        namespaceId: this.delMesosNamespaceDialogConf.ns.id
                    })
                    this.search = ''
                    this.searchScope = ''
                    // handleRefresh 会触发 refresh，refresh 触发 fetchNamespaceList
                    // fetchNamespaceList 里把 isPageLoading 设置为 false
                    this.$refs.dataSearcher.handleRefresh()
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除Namespace成功')
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 取消删除当前 namespace mesos
             */
            delMesosNamespaceCancel () {
                this.delMesosNamespaceDialogConf.isShow = false
                setTimeout(() => {
                    this.delMesosNamespaceDialogConf.ns = Object.assign({}, {})
                    this.delMesosNamespaceDialogConf.list.splice(0, this.delMesosNamespaceDialogConf.list.length, ...[])
                    this.delMesosNamespaceDialogConf.hasFooter = false
                }, 300)
            },

            /**
             * 搜索事件
             */
            handleSearch () {
                const search = String(this.search || '').trim().toLowerCase()
                let list = JSON.parse(JSON.stringify(this.namespaceListTmp))

                if (this.searchScope) {
                    list = list.filter(item => {
                        return item.cluster_id === this.searchScope
                    })
                }

                const results = list.filter(ns => {
                    const name = String(ns.name || '').toLowerCase()
                    const envType = String(ns.env_type || '').toLowerCase()
                    const clusterName = String(ns.cluster_name || '').toLowerCase()

                    return name.indexOf(search) > -1
                        || envType.indexOf(search) > -1
                        || clusterName.indexOf(search) > -1
                })
                // const beforeLen = this.namespaceListTmp.length
                // const afterLen = results.length
                this.namespaceList.splice(0, this.namespaceList.length, ...results)
                // this.pageConf.curPage = beforeLen !== afterLen ? 1 : this.pageConf.curPage
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            }
        }
    }
</script>

<style scoped>
    @import './namespace.css';
</style>
