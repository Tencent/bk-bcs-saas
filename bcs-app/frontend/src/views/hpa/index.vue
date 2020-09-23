<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-app-title">
                {{$t('HPA管理')}}
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
                        <button class="bk-button bk-default" @click.stop.prevent="removeHPAs">
                            <span>{{$t('批量删除')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="searchHPA"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>
                <div class="biz-hpa">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table biz-hpa-table has-table-hover">
                            <thead>
                                <tr>
                                    <th style="width: 50px;">
                                        <label class="bk-form-checkbox">
                                            <label class="bk-form-checkbox">
                                                <input
                                                    type="checkbox"
                                                    name="check-all-user"
                                                    :checked="isCheckCurPageAll"
                                                    :disabled="!HPAList.length"
                                                    @click="toogleCheckCurPage">
                                            </label>
                                        </label>
                                    </th>
                                    <th style="min-width: 100px;">
                                        {{$t('名称')}}
                                    </th>
                                    <th style="min-width: 100px;">{{$t('集群')}}</th>
                                    <th style="min-width: 100px;">{{$t('命名空间')}}</th>
                                    <th style="min-width: 135px;">Metric({{$t('当前')}}/{{$t('目标')}})</th>
                                    <th style="min-width: 135px;">{{$t('实例数')}}({{$t('当前')}}/{{$t('范围')}})</th>
                                    <th style="min-width: 90px;">{{$t('关联资源')}}</th>
                                    <th style="min-width: 70px;">{{$t('来源')}}</th>
                                    <th style="min-width: 100px;">{{$t('创建时间')}}</th>
                                    <th style="min-width: 70px;">{{$t('创建人')}}</th>
                                    <th style="min-width: 60px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curPageData.length">
                                    <tr v-for="(HPA, index) of curPageData" :key="index">
                                        <td>
                                            <label class="bk-form-checkbox">
                                                <input
                                                    type="checkbox"
                                                    name="check-variable"
                                                    v-model="HPA.isChecked"
                                                    @click="rowClick" />
                                            </label>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="HPA.name" placement="top">
                                                <span class="biz-text-wrapper">{{HPA.name}}</span>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="HPA.cluster_name" placement="top">
                                                <span class="biz-text-wrapper">{{HPA.cluster_name}}</span>
                                            </bk-tooltip>
                                        </td>
                                        <td>{{HPA.namespace}}</td>
                                        <td>{{HPA.current_metrics_display}}</td>
                                        <td>{{HPA.current_replicas}} / {{HPA.min_replicas}}-{{HPA.max_replicas}}</td>
                                        <td>
                                            <bk-tooltip :content="HPA.deployment_name" placement="top">
                                                <a class="bk-text-button biz-text-wrapper" target="_blank" :href="HPA.deployment_link">{{HPA.deployment_name}}</a>
                                            </bk-tooltip>
                                        </td>
                                        <td>{{HPA.source_type || '--'}}</td>
                                        <td>{{HPA.create_time || '--'}}</td>
                                        <td>{{HPA.creator || '--'}}</td>
                                        <td>
                                            <template v-if="HPA.permissions.use">
                                                <a href="javascript:void(0);" :class="['bk-text-button']" @click="removeHPA(HPA)">{{$t('删除')}}</a>
                                            </template>
                                            <template v-else>
                                                <bk-tooltip :content="HPA.permissions.use_msg" placement="left">
                                                    <a href="javascript:void(0);" :class="['bk-text-button is-disabled']">{{$t('删除')}}</a>
                                                </bk-tooltip>
                                            </template>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="11">
                                            <div class="bk-message-box">
                                                <p class="message empty-message" v-if="!isInitLoading">{{$t('无数据')}}</p>
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
                            @page-change="pageChangeHandler">
                        </bk-paging>
                        <div class="already-selected-nums" v-if="alreadySelectedNums">{{$t('已选')}} {{alreadySelectedNums}} {{$t('条')}}</div>
                    </div>
                </div>
            </template>

            <bk-dialog
                :is-show="batchDialogConfig.isShow"
                :width="400"
                :has-header="false"
                :quick-close="false"
                @confirm="deleteHPAs(batchDialogConfig.data)"
                @cancel="batchDialogConfig.isShow = false">
                <div slot="content">
                    <div class="biz-batch-wrapper">
                        <p class="batch-title">{{$t('确定要删除以下')}} HPA？</p>
                        <ul class="batch-list">
                            <li v-for="(item, index) of batchDialogConfig.list" :key="index">{{item}}</li>
                        </ul>
                    </div>
                </div>
            </bk-dialog>
        </div>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'
    export default {
        data () {
            return {
                exceptionCode: null,
                isInitLoading: true,
                isPageLoading: false,
                curPageData: [],
                searchKeyword: '',
                searchScope: '',
                pageConf: {
                    total: 1,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                alreadySelectedNums: 0,
                isBatchRemoving: false,
                curSelectedData: [],
                batchDialogConfig: {
                    isShow: false,
                    list: [],
                    data: []
                }
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            projectId () {
                return this.$route.params.projectId
            },
            HPAList () {
                const list = this.$store.state.hpa.HPAList
                return JSON.parse(JSON.stringify(list))
            },
            searchScopeList () {
                const clusterList = this.$store.state.cluster.clusterList
                const results = clusterList.map(item => {
                    return {
                        id: item.cluster_id,
                        name: item.name
                    }
                })

                results.length && results.unshift({
                    id: '',
                    name: this.$t('全部集群')
                })

                return results
            },
            isCheckCurPageAll () {
                if (this.curPageData.length) {
                    const list = this.curPageData
                    const selectList = list.filter((item) => {
                        return item.isChecked === true
                    })
                    const canSelectList = list.filter((item) => {
                        return item.permissions.use
                    })
                    if (selectList.length && (selectList.length === canSelectList.length)) {
                        return true
                    } else {
                        return false
                    }
                } else {
                    return false
                }
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
                                    const clusterId = this.searchScopeList[1].id
                                    this.searchScope = clusterId
                                }
                            }
                            this.getServiceList()
                        }, 1000)
                    }
                }
            }
        },
        mounted () {
            this.init()
        },
        methods: {
            /**
             * 初始化入口
             */
            init () {
                this.initPageConf()
                this.getHPAList()
            },

            /**
             * 获取HPA 列表
             */
            async getHPAList () {
                try {
                    await this.$store.dispatch('hpa/getHPAList', this.projectId)

                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)

                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchScope || this.searchKeyword) {
                        this.searchHPA()
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                        this.isPageLoading = false
                    }, 200)
                }
            },

            /**
             * Toogle当前页面全选
             * @return {[type]} [description]
             */
            toogleCheckCurPage () {
                const isChecked = this.isCheckCurPageAll
                this.$nextTick(() => {
                    this.curPageData.forEach((item) => {
                        // 能删除且有权限才可操作
                        if (item.permissions.use) {
                            item.isChecked = !isChecked
                        }
                    })
                    // this.selectHPAs()
                    this.curPageData.splice(0, this.curPageData.length, ...this.curPageData)
                    this.alreadySelectedNums = this.HPAList.filter(item => item.isChecked).length
                })
            },

            /**
             * 每行的多选框点击事件
             */
            rowClick () {
                this.$nextTick(() => {
                    this.alreadySelectedNums = this.HPAList.filter(item => item.isChecked).length
                })
            },

            /**
             * 选择当前页数据
             */
            selectHPAs () {
                const list = this.curPageData
                const selectList = list.filter((item) => {
                    return item.isChecked === true
                })
                this.curSelectedData.splice(0, this.curSelectedData.length, ...selectList)
            },

            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.getHPAList()
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
                this.pageChangeHandler()
            },

            /**
             * 搜索HPA
             */
            searchHPA () {
                const keyword = this.searchKeyword.trim()
                const keyList = ['name', 'cluster_name', 'creator']
                let list = JSON.parse(JSON.stringify(this.$store.state.hpa.HPAList))
                const results = []

                if (this.searchScope) {
                    list = list.filter(item => {
                        return item.cluster_id === this.searchScope
                    })
                }

                list.forEach(item => {
                    item.isChecked = false
                    for (const key of keyList) {
                        if (item[key].indexOf(keyword) > -1) {
                            results.push(item)
                            return true
                        }
                    }
                })

                this.HPAList.splice(0, this.HPAList.length, ...results)
                this.pageConf.curPage = 1
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.HPAList.length
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
            },

            /**
             * 获取分页数据
             * @param  {number} page 第几页
             * @return {object} data 数据
             */
            getDataByPage (page) {
                if (page < 1) {
                    this.pageConf.curPage = page = 1
                }
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                this.isPageLoading = true
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.HPAList.length) {
                    endIndex = this.HPAList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.HPAList.slice(startIndex, endIndex)
            },

            /**
             * 页数改变回调
             * @param  {number} page 第几页
             */
            pageChangeHandler (page = 1) {
                this.pageConf.curPage = page

                const data = this.getDataByPage(page)
                this.curPageData = data
            },

            /**
             * 重新加载当面页数据
             */
            reloadCurPage () {
                this.initPageConf()
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 清空当前页选择
             */
            clearSelectHPAs () {
                this.HPAList.forEach((item) => {
                    item.isChecked = false
                })
            },

            /**
             * 确认批量删除HPA
             */
            async removeHPAs () {
                const data = []
                const names = []

                this.HPAList.forEach(item => {
                    if (item.isChecked) {
                        data.push({
                            cluster_id: item.cluster_id,
                            namespace: item.namespace,
                            name: item.name
                        })
                        names.push(item.name)
                    }
                })
                if (!data.length) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择要删除的HPA！')
                    })
                    return false
                }

                this.batchDialogConfig.list = names
                this.batchDialogConfig.data = data
                this.batchDialogConfig.isShow = true
            },

            /**
             * 确认删除HPA
             * @param  {object} HPA HPA
             */
            async removeHPA (HPA) {
                const self = this
                // if (!HPA.permissions.use) {
                //     const params = {
                //         project_id: this.projectId,
                //         policy_code: 'use',
                //         resource_code: HPA.namespace_id,
                //         resource_name: HPA.namespace,
                //         resource_type: 'namespace'
                //     }
                //     await this.$store.dispatch('getResourcePermissions', params)
                // }

                this.$bkInfo({
                    title: ``,
                    clsName: 'biz-remove-dialog',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除HPA')}【${HPA.name}】？`),
                    async confirmFn () {
                        self.deleteHPA(HPA)
                    }
                })
            },

            /**
             * 批量删除HPA
             * @param  {object} data HPAs
             */
            async deleteHPAs (data) {
                this.batchDialogConfig.isShow = false
                this.isPageLoading = true
                const projectId = this.projectId

                try {
                    await this.$store.dispatch('hpa/batchDeleteHPA', {
                        projectId,
                        params: { data }
                    })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除成功')
                    })
                    this.initPageConf()
                    this.getHPAList()
                } catch (e) {
                    // 4004，已经被删除过，但接口不能立即清除，防止重复删除
                    if (e.code === 4004) {
                        this.initPageConf()
                        this.getHPAList()
                    }
                    this.$bkMessage({
                        theme: 'error',
                        delay: 8000,
                        hasCloseIcon: true,
                        message: e.message
                    })
                    this.isPageLoading = false
                }
            },

            /**
             * 删除HPA
             * @param {object} HPA HPA
             */
            async deleteHPA (HPA) {
                const projectId = this.projectId
                const namespace = HPA.namespace
                const clusterId = HPA.cluster_id
                const name = HPA.name
                this.isPageLoading = true
                try {
                    await this.$store.dispatch('hpa/deleteHPA', {
                        projectId,
                        clusterId,
                        namespace,
                        name
                    })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除成功')
                    })
                    this.initPageConf()
                    this.getHPAList()
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.isPageLoading = false
                }
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
