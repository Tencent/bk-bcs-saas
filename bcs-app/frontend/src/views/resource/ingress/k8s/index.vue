<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-topbar-title">
                Ingress
                <span class="biz-tip f12 ml10">{{$t('请通过模板集或Helm创建Ingress')}}</span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper p0" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <template v-if="!isInitLoading">
                <div class="biz-panel-header">
                    <div class="left">
                        <button
                            class="bk-button bk-default"
                            v-if="curPageData.length"
                            @click.stop.prevent="removeIngresses">
                            <span>{{$t('批量删除')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="getIngressList"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>

                <div class="biz-resource">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table has-table-hover biz-table biz-resource-table">
                            <thead>
                                <tr>
                                    <th style="width: 80px;">
                                        <label class="bk-form-checkbox">
                                            <input
                                                type="checkbox"
                                                name="check-all-user"
                                                :checked="isCheckCurPageAll"
                                                :disabled="!ingressList.length"
                                                @click="toogleCheckCurPage" />
                                        </label>
                                    </th>
                                    <th style="width: 300px;">{{$t('名称')}}</th>
                                    <th style="width: 300px;">{{$t('所属集群')}}</th>
                                    <th style="width: 300px;">{{$t('命名空间')}}</th>
                                    <th style="min-width: 70px;">{{$t('来源')}}</th>
                                    <th style="width: 300px;">{{$t('创建时间')}}</th>
                                    <th style="width: 300px;">{{$t('更新时间')}}</th>
                                    <th style="width: 300px;">{{$t('更新人')}}</th>
                                    <th style="width: 100px">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="ingressList.length">
                                    <tr v-for="(ingress, index) in curPageData" :key="index">
                                        <td>
                                            <label class="bk-form-checkbox">
                                                <input
                                                    type="checkbox"
                                                    name="check-variable"
                                                    :disabled="!ingress.can_delete || !ingress.permissions.use"
                                                    v-model="ingress.isChecked"
                                                    @click="rowClick" />
                                            </label>
                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="ingress.status === 'updating'">
                                                <div class="rotate rotate1"></div>
                                                <div class="rotate rotate2"></div>
                                                <div class="rotate rotate3"></div>
                                                <div class="rotate rotate4"></div>
                                                <div class="rotate rotate5"></div>
                                                <div class="rotate rotate6"></div>
                                                <div class="rotate rotate7"></div>
                                                <div class="rotate rotate8"></div>
                                            </div>
                                        </td>
                                        <td>
                                            <a href="javascript: void(0)" class="bk-text-button biz-table-title biz-resource-title" @click.stop.prevent="showIngressDetail(ingress, index)">{{ingress.resourceName}}</a>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="ingress.cluster_id || '--'" placement="top">
                                                <p class="biz-text-wrapper">{{ingress.cluster_name ? ingress.cluster_name : '--'}}</p>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            {{ingress.namespace}}
                                        </td>
                                        <td>
                                            {{ingress.source_type ? ingress.source_type : '--'}}
                                        </td>
                                        <td>
                                            {{ingress.createTime ? formatDate(ingress.createTime) : '--'}}
                                        </td>
                                        <td>
                                            {{ingress.updateTime ? formatDate(ingress.updateTime) : '--'}}
                                        </td>
                                        <td>
                                            {{ingress.updator || '--'}}
                                        </td>
                                        <td>
                                            <li style="width: 100px;">
                                                <a @click.stop="showIngressDetail(ingress)" class="biz-operate">{{$t('查看')}}</a>
                                                <a v-if="ingress.can_delete" @click.stop="removeIngress(ingress)" class="biz-operate">{{$t('删除')}}</a>
                                                <bk-tooltip :content="ingress.can_delete_msg || $t('不可删除')" v-else placement="left">
                                                    <span class="biz-not-operate">{{$t('删除')}}</span>
                                                </bk-tooltip>
                                            </li>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="9">
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
                            @page-change="pageChangeHandler">
                        </bk-paging>
                        <div class="already-selected-nums" v-if="alreadySelectedNums">{{$t('已选')}} {{alreadySelectedNums}} {{$t('条')}}</div>
                    </div>
                </div>
            </template>

            <bk-sideslider
                v-if="curIngress"
                :quick-close="true"
                :is-show.sync="ingressSlider.isShow"
                :title="ingressSlider.title"
                :width="'800'">
                <div class="pt20 pr30 pb20 pl30" slot="content">
                    <label class="biz-title">{{$t('主机列表')}}（spec.tls）</label>
                    <table class="bk-table biz-data-table has-table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 270px;">{{$t('主机名')}}</th>
                                <th>SecretName</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curIngress.tls.length">
                                <tr v-for="(rule, index) in curIngress.tls" :key="index">
                                    <td>{{rule.host || '--'}}</td>
                                    <td>{{rule.secretName || '--'}}</td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="2"><p style="padding: 10px; text-align: center;">{{$t('无数据')}}</p></td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <label class="biz-title">{{$t('规则')}}（spec.rules）</label>
                    <table class="bk-table biz-data-table has-table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 200px;">{{$t('主机名')}}</th>
                                <th style="width: 150px;">{{$t('路径')}}</th>
                                <th>{{$t('服务名称')}}</th>
                                <th style="width: 100px;">{{$t('服务端口')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curIngress.rules.length">
                                <tr v-for="(rule, index) in curIngress.rules" :key="index">
                                    <td>{{rule.host || '--'}}</td>
                                    <td>{{rule.path || '--'}}</td>
                                    <td>{{rule.serviceName || '--'}}</td>
                                    <td>{{rule.servicePort || '--'}}</td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="4"><p style="padding: 10px; text-align: center;">{{$t('无数据')}}</p></td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <div class="actions">
                        <button class="show-labels-btn bk-button bk-button-small bk-primary">{{$t('显示标签')}}</button>
                    </div>

                    <div class="point-box">
                        <template v-if="curIngress.labels.length">
                            <ul class="key-list">
                                <li v-for="(label, index) in curIngress.labels" :key="index">
                                    <span class="key">{{label[0]}}</span>
                                    <span class="value">{{label[1] || '--'}}</span>
                                </li>
                            </ul>
                        </template>
                        <template v-else>
                            <p class="biz-no-data">{{$t('无数据')}}</p>
                        </template>
                    </div>
                </div>
            </bk-sideslider>

            <bk-dialog
                :is-show="batchDialogConfig.isShow"
                :width="550"
                :has-header="false"
                :quick-close="false"
                @confirm="deleteIngresses(batchDialogConfig.data)"
                @cancel="batchDialogConfig.isShow = false">
                <div slot="content">
                    <div class="biz-batch-wrapper">
                        <p class="batch-title">{{$t('确定要删除以下Ingress？')}}</p>
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
    import { catchErrorHandler, formatDate } from '@open/common/util'

    export default {
        data () {
            return {
                formatDate: formatDate,
                isInitLoading: true,
                isPageLoading: false,
                searchKeyword: '',
                searchScope: '',
                curPageData: [],
                curIngress: null,
                pageConf: {
                    total: 1,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                ingressSlider: {
                    title: '',
                    isShow: false
                },
                batchDialogConfig: {
                    isShow: false,
                    list: [],
                    data: []
                },
                curIngressName: '',
                alreadySelectedNums: 0
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            curProject () {
                return this.$store.state.curProject
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
                        return item.can_delete && item.permissions.use
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
            projectId () {
                return this.$route.params.projectId
            },
            ingressList () {
                const list = this.$store.state.resource.ingressList
                list.forEach(item => {
                    item.isChecked = false
                })
                return JSON.parse(JSON.stringify(list))
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
                                this.searchScope = this.searchScopeList[1].id
                            }
                            this.getIngressList()
                        }, 1000)
                    }
                }
            }
        },
        created () {
            this.initPageConf()
            // this.getIngressList()
        },
        methods: {
            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.getIngressList()
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
             * 全选/取消全选当前页数据
             */
            toogleCheckCurPage () {
                const isChecked = this.isCheckCurPageAll
                this.curPageData.forEach((item) => {
                    if (item.can_delete && item.permissions.use) {
                        item.isChecked = !isChecked
                    }
                })
                this.$nextTick(() => {
                    this.alreadySelectedNums = this.ingressList.filter(item => item.isChecked).length
                })
            },

            /**
             * 确认批量删除
             */
            async removeIngresses () {
                const data = []
                const names = []

                this.ingressList.forEach(item => {
                    if (item.isChecked) {
                        data.push({
                            cluster_id: item.cluster_id,
                            namespace: item.namespace,
                            name: item.name
                        })
                        names.push(`${item.cluster_name} / ${item.namespace} / ${item.resourceName}`)
                    }
                })

                if (!data.length) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择要删除的Ingress')
                    })
                    return false
                }

                this.batchDialogConfig.list = names
                this.batchDialogConfig.data = data
                this.batchDialogConfig.isShow = true
            },

            /**
             * 批量删除
             * @param  {object} data ingresses
             */
            async deleteIngresses (data) {
                const me = this
                const projectId = this.projectId

                this.batchDialogConfig.isShow = false
                this.isPageLoading = true
                try {
                    await this.$store.dispatch('resource/deleteIngresses', { projectId, data })
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除成功')
                    })
                    // 稍晚一点加载数据，接口不一定立即清除
                    setTimeout(() => {
                        me.getIngressList()
                    }, 500)
                } catch (e) {
                    // 4004，已经被删除过，但接口不能立即清除，再重新拉数据，防止重复删除
                    if (e.code === 4004) {
                        me.isPageLoading = true
                        setTimeout(() => {
                            me.getIngressList()
                        }, 500)
                    } else {
                        this.isPageLoading = false
                    }
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 确认删除ingress
             * @param  {object} ingress ingress
             */
            async removeIngress (ingress) {
                if (!ingress.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: ingress.namespace_id,
                        resource_name: ingress.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                const me = this
                me.$bkInfo({
                    title: ``,
                    clsName: 'biz-remove-dialog max-size',
                    content: me.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除Ingress')}【${ingress.cluster_name} / ${ingress.namespace} / ${ingress.name}】？`),
                    confirmFn () {
                        me.deleteIngress(ingress)
                    }
                })
            },

            /**
             * 删除ingress
             * @param  {object} ingress ingress
             */
            async deleteIngress (ingress) {
                const me = this
                const projectId = me.projectId
                const clusterId = ingress.cluster_id
                const namespace = ingress.namespace
                const name = ingress.name

                this.isPageLoading = true
                try {
                    await this.$store.dispatch('resource/deleteIngress', {
                        projectId,
                        clusterId,
                        namespace,
                        name
                    })
                    me.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除成功')
                    })
                    
                    // 稍晚一点加载数据，接口不一定立即清除
                    setTimeout(() => {
                        me.getIngressList()
                    }, 500)
                } catch (e) {
                    this.isPageLoading = false
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 显示ingress详情
             * @param  {object} ingress object
             * @param  {number} index 索引
             */
            showIngressDetail (ingress, index) {
                this.ingressSlider.title = ingress.resourceName
                this.curIngress = ingress
                this.ingressSlider.isShow = true
            },

            /**
             * 清除选择，在分页改变时触发
             */
            clearSelectIngress () {
                this.curPageData.forEach((item) => {
                    item.isChecked = false
                })
            },

            /**
             * 获取Ingresslist
             */
            async getIngressList () {
                const projectId = this.projectId
                const params = {
                    cluster_id: this.searchScope
                }
                try {
                    this.isPageLoading = true
                    await this.$store.dispatch('resource/getIngressList', {
                        projectId,
                        params
                    })

                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)

                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchKeyword) {
                        this.searchIngress()
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isPageLoading = false
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 清除搜索
             */
            clearSearch () {
                this.searchKeyword = ''
                this.searchIngress()
            },

            /**
             * 搜索Ingress
             */
            searchIngress () {
                const keyword = this.searchKeyword.trim()
                const keyList = ['resourceName', 'namespace', 'cluster_name']
                let list = JSON.parse(JSON.stringify(this.$store.state.resource.ingressList))
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

                this.ingressList.splice(0, this.ingressList.length, ...results)
                this.pageConf.curPage = 1
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.ingressList.length
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
            },

            /**
             * 重新加载当面页数据
             * @return {[type]} [description]
             */
            reloadCurPage () {
                this.initPageConf()
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
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
                if (endIndex > this.ingressList.length) {
                    endIndex = this.ingressList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.ingressList.slice(startIndex, endIndex)
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
             * 每行的多选框点击事件
             */
            rowClick () {
                this.$nextTick(() => {
                    this.alreadySelectedNums = this.ingressList.filter(item => item.isChecked).length
                })
            }
        }
    }
</script>

<style scoped>
    @import '../../ingress.css';
</style>
