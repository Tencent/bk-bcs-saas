<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-crd-instance-title">
                <a href="javascript:void(0);" class="bk-icon icon-arrows-left back" @click="goBack"></a>
                {{$t('DB授权配置管理')}}
                <span class="biz-tip f12 ml10">({{$t('集群名称')}}：{{clusterName}})</span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper" style="padding: 0;" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <app-exception
                v-if="exceptionCode && !isInitLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>

            <template v-if="!exceptionCode && !isInitLoading">
                <div class="biz-panel-header">
                    <div class="left">
                        <button class="bk-button bk-primary" @click.stop.prevent="createLoadBlance">
                            <i class="bk-icon icon-plus" style="top: -1px;"></i>
                            <span>{{$t('新建')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="$t('输入关键字，按Enter搜索')"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="clusterId"
                            :scope-disabled="true"
                            @search="searchCrdInstance"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>

                <div class="biz-crd-instance">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table has-table-hover biz-table biz-crd-instance-table">
                            <thead>
                                <tr>
                                    <th style="width: 200px; padding-left: 30px;">{{$t('名称')}}</th>
                                    <!-- <th>{{$t('所属集群')}}</th> -->
                                    <th>{{$t('命名空间')}}</th>
                                    <th style="width: 100px;">{{$t('状态')}}</th>
                                    <th>{{$t('更新时间')}}</th>
                                    <th>{{$t('更新人')}}</th>
                                    <th style="min-width: 120px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="crdInstanceList.length">
                                    <tr v-for="(crdInstance, index) in curPageData" :key="index">
                                        <td style="width: 200px; padding-left: 30px;">
                                            <a href="javascript: void(0)" class="bk-text-button biz-table-title biz-resource-title" @click.stop.prevent="editCrdInstance(crdInstance, true)">{{crdInstance.name || '--'}}</a>
                                        </td>
                                        <td>{{crdInstance.namespace || '--'}}</td>
                                        <td>{{crdInstance.status ? $t('正常') : $t('异常')}}</td>
                                        <td>{{crdInstance.updated || '--'}}</td>
                                        <td>{{crdInstance.operator || '--'}}</td>
                                        <td>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="editCrdInstance(crdInstance)">{{$t('更新')}}</a>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="removeCrdInstance(crdInstance)">{{$t('删除')}}</a>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="6">
                                            <div class="biz-app-list">
                                                <div class="bk-message-box">
                                                    <p class="message empty-message" v-if="!isInitLoading">{{$t('无数据')}}</p>
                                                </div>
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
                            @page-change="handlerPageChange">
                        </bk-paging>
                    </div>
                </div>
            </template>

            <bk-sideslider
                style="z-index: 150;"
                :quick-close="false"
                :is-show.sync="crdInstanceSlider.isShow"
                :title="crdInstanceSlider.title"
                :width="'660'">
                <div class="p30" slot="content">
                    <div class="bk-form bk-form-vertical">
                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 270px;">
                                    <label class="bk-label">{{$t('所属集群')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请输入')"
                                            :setting-key="'cluster_id'"
                                            :display-key="'name'"
                                            :selected.sync="clusterId"
                                            :list="clusterList"
                                            :disabled="true">
                                        </bk-selector>
                                    </div>
                                </div>

                                <div class="bk-form-inline-item is-required" style="width: 270px; margin-left: 35px;">
                                    <label class="bk-label">{{$t('命名空间')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :searchable="true"
                                            :placeholder="$t('请选择')"
                                            :selected.sync="curCrdInstance.namespace_id"
                                            :list="nameSpaceList"
                                            :disabled="curCrdInstance.crd_id"
                                            @item-selected="handleNamespaceSelect">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 270px;">
                                    <label class="bk-label">{{$t('名称')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            :placeholder="$t('请输入')"
                                            :value.sync="curCrdInstance.name"
                                            :disabled="curCrdInstance.crd_id">
                                        </bk-input>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 270px; margin-left: 35px;">
                                    <label class="bk-label">
                                        {{$t('业务名称')}}：
                                        <i class="bk-icon icon-question-circle label-icon" v-bktooltips.left="$t('必须与GCS权限模板中的“业务名”相同')"></i>
                                    </label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            :placeholder="$t('请输入')"
                                            :value.sync="curCrdInstance.app_name">
                                        </bk-input>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 270px;">
                                    <label class="bk-label">{{$t('DB访问地址')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            :placeholder="$t('请输入')"
                                            :value.sync="curCrdInstance.db_host">
                                        </bk-input>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 270px; margin-left: 35px;">
                                    <label class="bk-label">{{$t('DB类型')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请选择')"
                                            :selected.sync="curCrdInstance.db_type"
                                            :list="dbTypes">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 270px;">
                                    <label class="bk-label">
                                        {{$t('帐号')}}：
                                        <i class="bk-icon icon-question-circle label-icon" v-bktooltips.right="$t('必须与GCS权限模板中的“帐号”相同')"></i>
                                    </label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            :placeholder="$t('请输入')"
                                            :value.sync="curCrdInstance.call_user">
                                        </bk-input>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 270px; margin-left: 35px;">
                                    <label class="bk-label">
                                        {{$t('DB名称')}}：
                                        <i class="bk-icon icon-question-circle label-icon" v-bktooltips.left="$t('必须与GCS权限模板中的“数据库名称”相同')"></i>
                                    </label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            :placeholder="$t('请输入')"
                                            :value.sync="curCrdInstance.db_name">
                                        </bk-input>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item is-required">
                            <label class="bk-label">
                                {{$t('标签管理')}}：
                                <i class="bk-icon icon-question-circle label-icon" v-bktooltips.right="$t('bcs-webhook-server用labels过滤，相同labels的pod被选中注入用于DB授权的init-container')"></i>
                            </label>
                            <div class="bk-form-content">
                                <bk-keyer :key-list.sync="curLabelList" ref="labelKeyer" @change="changeLabels"></bk-keyer>
                            </div>
                        </div>

                        <div class="bk-form-item mt25">
                            <button :class="['bk-button bk-primary', { 'is-loading': isDataSaveing }]" @click.stop.prevent="saveCrdInstance">{{curCrdInstance.crd_id ? $t('更新') : $t('创建')}}</button>
                            <button class="bk-button bk-default" @click.stop.prevent="hideCrdInstanceSlider">{{$t('取消')}}</button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>

            <bk-sideslider
                :quick-close="true"
                :is-show.sync="detailSliderConf.isShow"
                :title="detailSliderConf.title"
                :width="'800'">
                <div class="p30" slot="content">
                    <p class="data-title">
                        {{$t('基础信息')}}
                    </p>
                    <div class="biz-metadata-box mb15">
                        <div class="data-item">
                            <p class="key">{{$t('所属集群')}}：</p>
                            <p class="value">{{clusterName || '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('命名空间')}}：</p>
                            <p class="value">{{curCrdInstance.namespace || '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('名称')}}：</p>
                            <p class="value">{{curCrdInstance.name || '--'}}</p>
                        </div>
                    </div>

                    <p class="data-title">
                        {{$t('DB信息')}}
                    </p>
                    <div class="biz-metadata-box">
                        <div class="data-item">
                            <p class="key">{{$t('业务名称')}}：</p>
                            <p class="value">{{curCrdInstance.app_name || '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('DB访问地址')}}：</p>
                            <p class="value">{{curCrdInstance.db_host || '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('DB类型')}}：</p>
                            <p class="value">{{curCrdInstance.db_type || '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('帐号')}}：</p>
                            <p class="value">{{curCrdInstance.call_user || '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('DB名称')}}：</p>
                            <p class="value">{{curCrdInstance.db_name || '--'}}</p>
                        </div>
                    </div>

                    <div class="actions">
                        <span class="show-labels-btn bk-button bk-button-small bk-primary">{{$t('标签')}}</span>
                    </div>
                    <div class="point-box">
                        <template v-if="curLabelList.length">
                            <ul class="key-list">
                                <li v-for="(label, index) in curLabelList" :key="index">
                                    <span class="key">{{label.key}}</span>
                                    <span class="value">{{label.value}}</span>
                                </li>
                            </ul>
                        </template>
                        <template v-else>
                            <div class="bk-message-box" style="min-height: auto;">
                                <p class="message empty-message" style="margin: 30px; font-size: 14px;">{{$t('无数据')}}</p>
                            </div>
                        </template>
                    </div>
                </div>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'
    import bkKeyer from '@open/components/keyer'

    export default {
        components: {
            bkKeyer
        },
        data () {
            return {
                isInitLoading: true,
                isPageLoading: false,
                exceptionCode: null,
                curPageData: [],
                isDataSaveing: false,
                prmissions: {},
                pageConf: {
                    total: 0,
                    totalPage: 1,
                    pageSize: 5,
                    curPage: 1,
                    show: true
                },
                crdInstanceSlider: {
                    title: this.$t('新建'),
                    isShow: false
                },
                clusterIndex: 0,
                searchKeyword: '',
                searchScope: '',
                nameSpaceList: [],
                curLabelList: [
                    {
                        key: '',
                        value: ''
                    }
                ],

                dbTypes: [
                    {
                        id: 'mysql',
                        name: 'mysql'
                    },
                    {
                        id: 'spider',
                        name: 'spider'
                    }
                ],

                curCrdInstance: {
                    'cluster_id': '',
                    'name': '',
                    'namespace': '',
                    'namespace_id': 0,
                    'pod_selector': {},
                    'app_name': '',
                    'db_host': '',
                    'db_type': 'mysql',
                    'call_user': '',
                    'db_name': '',
                    'crd_kind': '',
                    'labels': [
                        {
                            'key': '',
                            'value': ''
                        }
                    ]
                },
                detailSliderConf: {
                    isShow: false,
                    title: ''
                },
                crdKind: 'DbPrivilege'
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            varList () {
                return this.$store.state.variable.varList
            },
            projectId () {
                return this.$route.params.projectId
            },
            crdInstanceList () {
                return Object.assign([], this.$store.state.crdcontroller.crdInstanceList)
            },
            clusterList () {
                return this.$store.state.cluster.clusterList
            },
            curProject () {
                return this.$store.state.curProject
            },
            clusterId () {
                return this.$route.params.clusterId
            },
            clusterName () {
                const cluster = this.clusterList.find(item => {
                    return item.cluster_id === this.clusterId
                })
                return cluster ? cluster.name : ''
            },
            searchScopeList () {
                const clusterList = this.$store.state.cluster.clusterList
                let results = []
                if (clusterList.length) {
                    results = []
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
            crdInstanceList () {
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },
            curPageData () {
                this.curPageData.forEach(item => {
                    if (item.clb_status && item.clb_status !== 'Running') {
                        this.getCrdInstanceStatus(item)
                    }
                })
            }
        },
        created () {
            // 如果不是mesos类型的项目，无法访问页面，重定向回集群首页
            if (this.curProject && this.curProject.kind === PROJECT_MESOS) {
                this.$router.push({
                    name: 'clusterMain',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
                return false
            }

            this.getCrdInstanceList()
            this.getNameSpaceList()
        },
        methods: {
            goBack () {
                this.$router.push({
                    name: 'dbCrdcontroller',
                    params: {
                        projectId: this.projectId
                    }
                })
            },

            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.getCrdInstanceList()
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
                this.handlerPageChange()
            },

            /**
             * 新建
             */
            createLoadBlance () {
                this.curCrdInstance = {
                    'cluster_id': this.clusterId,
                    'name': '',
                    'namespace': '',
                    'namespace_id': 0,
                    'pod_selector': {},
                    'app_name': '',
                    'db_host': '',
                    'db_type': 'mysql',
                    'call_user': '',
                    'db_name': '',
                    'crd_kind': this.crdKind,
                    'labels': [
                        {
                            'key': '',
                            'value': ''
                        }
                    ]
                }

                this.curLabelList = [
                    {
                        'key': '',
                        'value': ''
                    }
                ]

                this.crdInstanceSlider.isShow = true
            },

            /**
             * 编辑
             * @param  {object} crdInstance crdInstance
             * @param  {number} index 索引
             */
            async editCrdInstance (crdInstance, isReadonly) {
                if (crdInstance.permissions && !crdInstance.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: crdInstance.namespace,
                        resource_name: crdInstance.namespace_name,
                        resource_type: 'namespace'
                    })
                }

                try {
                    const projectId = this.projectId
                    const clusterId = this.clusterId
                    const crdId = crdInstance.crd_id
                    const res = await this.$store.dispatch('crdcontroller/getCrdInstanceDetail', {
                        projectId,
                        clusterId,
                        crdId
                    })

                    res.data.labels = []
                    const selector = res.data.pod_selector
                    this.curLabelList = []
                    for (const key in selector) {
                        res.data.labels.push({
                            key: key,
                            value: selector[key]
                        })
                        this.curLabelList.push({
                            key: key,
                            value: selector[key]
                        })
                    }

                    if (!this.curLabelList) {
                        this.curLabelList = [
                            {
                                'key': '',
                                'value': ''
                            }
                        ]
                    }

                    this.curCrdInstance = res.data
                    this.curCrdInstance.crd_id = crdId

                    if (isReadonly) {
                        this.detailSliderConf.title = `${this.curCrdInstance.name}`
                        this.detailSliderConf.isShow = true
                    } else {
                        this.crdInstanceSlider.title = this.$t('编辑')
                        this.crdInstanceSlider.isShow = true
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 删除
             * @param  {object} crdInstance crdInstance
             * @param  {number} index 索引
             */
            async removeCrdInstance (crdInstance, index) {
                if (crdInstance.permissions && !crdInstance.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: crdInstance.namespace,
                        resource_name: crdInstance.namespace_name,
                        resource_type: 'namespace'
                    })
                }

                const self = this
                const projectId = this.projectId
                const clusterId = this.clusterId
                const crdId = crdInstance.crd_id

                this.$bkInfo({
                    title: '',
                    clsName: 'biz-remove-dialog',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除')}【${crdInstance.name}】？`),
                    async confirmFn () {
                        self.isPageLoading = true
                        try {
                            await self.$store.dispatch('crdcontroller/deleteCrdInstance', { projectId, clusterId, crdId })
                            self.$bkMessage({
                                theme: 'success',
                                message: self.$t('删除成功')
                            })
                            self.getCrdInstanceList()
                        } catch (e) {
                            catchErrorHandler(e, this)
                        } finally {
                            self.isPageLoading = false
                        }
                    }
                })
            },

            /**
             * 获取
             * @param  {number} crdInstanceId id
             * @return {object} crdInstance crdInstance
             */
            getCrdInstanceById (crdInstanceId) {
                return this.crdInstanceList.find(item => {
                    return item.id === crdInstanceId
                })
            },

            /**
             * 清空搜索
             */
            clearSearch () {
                this.searchKeyword = ''
                this.searchCrdInstance()
            },

            /**
             * 搜索
             */
            searchCrdInstance () {
                const keyword = this.searchKeyword.trim()
                const list = this.$store.state.crdcontroller.crdInstanceList
                let results = []

                results = list.filter(item => {
                    if (item.name.indexOf(keyword) > -1 || item.namespace.indexOf(keyword) > -1 || item.operator.indexOf(keyword) > -1) {
                        return true
                    } else {
                        return false
                    }
                })
                this.crdInstanceList.splice(0, this.crdInstanceList.length, ...results)
                this.pageConf.curPage = 1
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.crdInstanceList.length
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
            },

            /**
             * 重新加载当前页
             */
            reloadCurPage () {
                this.initPageConf()
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 获取页数据
             * @param  {number} page 页
             * @return {object} data lb
             */
            getDataByPage (page) {
                // 如果没有page，重置
                if (!page) {
                    this.pageConf.curPage = page = 1
                }
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                // this.isPageLoading = true
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.crdInstanceList.length) {
                    endIndex = this.crdInstanceList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.crdInstanceList.slice(startIndex, endIndex)
            },

            /**
             * 分页改变回调
             * @param  {number} page 页
             */
            handlerPageChange (page = 1) {
                this.isPageLoading = true
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData = JSON.parse(JSON.stringify(data))
            },

            /**
             * 隐藏lb侧面板
             */
            hideCrdInstanceSlider () {
                this.crdInstanceSlider.isShow = false
            },

            /**
             * 加载数据
             */
            async getCrdInstanceList () {
                try {
                    const projectId = this.projectId
                    const clusterId = this.clusterId
                    const params = {
                        crd_kind: this.crdKind
                    }

                    await this.$store.dispatch('crdcontroller/getCrdInstanceList', {
                        projectId,
                        clusterId,
                        params
                    })

                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)

                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchKeyword) {
                        this.searchCrdInstance()
                    }
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
             * 获取命名空间列表
             */
            async getNameSpaceList () {
                try {
                    const projectId = this.projectId
                    const clusterId = this.clusterId
                    const res = await this.$store.dispatch('crdcontroller/getNameSpaceListByCluster', { projectId, clusterId })
                    const list = res.data
                    list.forEach(item => {
                        item.isSelected = false
                    })
                    this.nameSpaceList.splice(0, this.nameSpaceList.length, ...list)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 选择/取消选择命名空间
             * @param  {object} nameSpace 命名空间
             * @param  {number} index 索引
             */
            toggleSelected (nameSpace, index) {
                nameSpace.isSelected = !nameSpace.isSelected
                this.nameSpaceList = JSON.parse(JSON.stringify(this.nameSpaceList))
            },

            /**
             * 检查提交的数据
             * @return {boolean} true/false 是否合法
             */
            checkData () {
                if (!this.curCrdInstance.namespace_id) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择命名空间'),
                        delay: 5000
                    })
                    return false
                }

                if (this.curCrdInstance.name === '') {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }

                if (!this.curCrdInstance.app_name) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入业务名称'),
                        delay: 5000
                    })
                    return false
                }

                if (!this.curCrdInstance.db_host) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入DB访问地址'),
                        delay: 5000
                    })
                    return false
                }

                if (!this.curCrdInstance.call_user) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入帐号'),
                        delay: 5000
                    })
                    return false
                }

                if (!this.curCrdInstance.db_name) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入DB名称'),
                        delay: 5000
                    })
                    return false
                }

                if (JSON.stringify(this.curCrdInstance.pod_selector) === '{}') {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入标签'),
                        delay: 5000
                    })
                    return false
                }

                return true
            },

            showCrdInstanceDetail (data) {
                data.labels = []
                for (const key in data.pod_selector) {
                    data.labels.push({
                        key: key,
                        value: data.pod_selector[key]
                    })
                }
                this.curCrdInstance = data

                this.detailSliderConf.title = `${data.name}`
                this.detailSliderConf.isShow = true
            },

            /**
             * 格式化数据，符合接口需要的格式
             */
            formatData () {
                const labels = this.curCrdInstance.labels
                this.curCrdInstance.pod_selector = {}
                labels.forEach(item => {
                    if (item.key) {
                        this.curCrdInstance.pod_selector[item.key] = item.value
                    }
                })
            },

            /**
             * 保存新建的
             */
            async createCrdInstance () {
                const projectId = this.projectId
                const data = this.curCrdInstance
                this.isDataSaveing = true

                try {
                    await this.$store.dispatch('crdcontroller/addCrdInstance', { projectId, data })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('数据保存成功')
                    })
                    this.getCrdInstanceList()
                    this.hideCrdInstanceSlider()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }
            },

            /**
             * 保存更新的
             */
            async updateCrdInstance () {
                const projectId = this.projectId
                const data = this.curCrdInstance
                this.isDataSaveing = true

                data.crd_kind = this.crdKind
                try {
                    await this.$store.dispatch('crdcontroller/updateCrdInstance', { projectId, data })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('数据保存成功')
                    })
                    this.getCrdInstanceList()
                    this.hideCrdInstanceSlider()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }
            },

            /**
             * 保存
             */
            saveCrdInstance () {
                this.formatData()
                if (this.checkData() && !this.isDataSaveing) {
                    if (this.curCrdInstance.crd_id > 0) {
                        this.updateCrdInstance()
                    } else {
                        this.createCrdInstance()
                    }
                }
            },

            handleNamespaceSelect (index, data) {
                this.curCrdInstance.namespace = data.name
            },

            changeLabels (labels, data) {
                // this.curCrdInstance.pod_selector = data
                this.curCrdInstance.labels = labels
            }
        }
    }
</script>

<style scoped>
    @import './db_list.css';
</style>
