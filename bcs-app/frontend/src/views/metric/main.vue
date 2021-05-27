<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-app-title">
                {{$t('Metric管理')}}
                <span class="biz-tip f13 ml10">
                    <template v-if="isEn">
                        Support for Metric in Prometheus format, View the <a href="https://iwiki.oa.tencent.com/pages/viewpage.action?pageId=10733511" target="_blank" class="bk-text-button">document</a> for details
                    </template>
                    <template v-else>
                        支持 Prometheus 格式的 Metric，详情<a href="https://iwiki.oa.tencent.com/pages/viewpage.action?pageId=10733511" target="_blank" class="bk-text-button">查看文档</a>
                    </template>
                </span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper" style="padding: 0;" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <app-exception
                v-if="exceptionCode && !isInitLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>
            <div v-show="!exceptionCode && !isInitLoading">
                <div class="biz-lock-box" v-if="updateMsg">
                    <div class="lock-wrapper warning">
                        <i class="bk-icon icon-info-circle-shape"></i>
                        <strong class="desc">{{updateMsg}}</strong>
                        <div class="action">
                            <a class="bk-text-button metric-query" href="javascript:void(0)" @click="doUpdate">{{$t('升级')}}</a>
                        </div>
                    </div>
                </div>
                <div class="biz-panel-header biz-metric-manage-create" style="padding: 27px 30px 22px 20px;">
                    <div class="left">
                        <bk-button type="primary" :title="$t('新建Metric')" @click="showCreateMetric">
                            <i class="bk-icon icon-plus"></i>
                            <span class="text">{{$t('新建Metric')}}</span>
                        </bk-button>
                        <button class="bk-button" @click="batchDel">
                            <span>{{$t('批量删除')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <searcher
                            ref="dSearcher"
                            :scope-list="clusterList"
                            :search-scope.sync="searchClusterId"
                            :placeholder="$t('输入名称，按Enter搜索')"
                            :search-key.sync="searchKeyWord"
                            @update:searchScope="searchMetricByCluster"
                            @update:searchKey="searchMetricByWord"
                            @refresh="refresh">
                        </searcher>
                    </div>
                </div>
                <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                    <table class="bk-table has-table-hover biz-table biz-metric-manage-table">
                        <thead>
                            <tr>
                                <th style="width: 20px; text-align: center; top: 0; position: relative; padding: 0;">
                                    <label class="bk-form-checkbox" v-if="curPageData.length">
                                        <bk-tooltip v-if="curPageData.filter(node => node.canDel).length === 0" :content="$t('当前页全是系统命名空间')" placement="left" :transfer="true" :delay="300">
                                            <input type="checkbox" name="check-strategy" :disabled="true" />
                                        </bk-tooltip>
                                        <input type="checkbox" v-else name="check-all-strategy" v-model="isCheckAll" @click="checkAllMetric">
                                    </label>
                                </th>
                                <th style="width: 20px;"></th>
                                <th style="">{{$t('名称')}}</th>
                                <th style="">Endpoints</th>
                                <th style="width: 90px;">{{$t('命名空间')}}</th>
                                <th style="">Service</th>
                                <th style="width: 100px;">{{$t('Metric路径')}}</th>
                                <th style="">{{$t('端口')}}</th>
                                <th style="width: 90px;">{{$t('周期(s)')}}</th>
                                <th style="width: 190px;text-align: right; padding-right: 100px;">{{$t('操作')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curPageData.length">
                                <template v-for="(item, index) in curPageData">
                                    <tr :key="index">
                                        <td style="width: 20px; text-align: center; position: relative;">
                                            <label class="bk-form-checkbox">
                                                <bk-tooltip v-if="!item.canDel" :content="item.delMsg" placement="left" :transfer="true" :delay="300">
                                                    <input type="checkbox" name="check-strategy" v-model="item.isChecked" :disabled="true" />
                                                </bk-tooltip>
                                                <input type="checkbox" v-else name="check-strategy" v-model="item.isChecked" @click.stop="checkMetric(item)" />
                                            </label>
                                        </td>
                                        <td style="text-align: left;">
                                            <i class="bk-icon" @click="toggleRow(item)" :class="item.expand ? 'icon-down-shape' : 'icon-right-shape'"></i>
                                        </td>
                                        <td>
                                            <bk-tooltip placement="top" :delay="500">
                                                <p class="item-name" @click="toggleRow(item)">{{item.name || '--'}}</p>
                                                <template slot="content">
                                                    <p style="text-align: left; white-space: normal;word-break: break-all;">{{item.name || '--'}}</p>
                                                </template>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            <template v-if="Object.keys(item.targetData).length">
                                                {{item.targetData.health_count}}/{{item.targetData.total_count}}
                                            </template>
                                            <template v-else>
                                                -/-
                                            </template>
                                        </td>
                                        <td>{{item.namespace || '--'}}</td>
                                        <td>
                                            <bk-tooltip placement="top" :delay="500">
                                                <p class="service-name">{{item.service_name || '--'}}</p>
                                                <template slot="content">
                                                    <p style="text-align: left; white-space: normal;word-break: break-all;">{{item.service_name || '--'}}</p>
                                                </template>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            <template v-for="(endpoint, endpointIndex) in item.spec.endpoints">
                                                <div :key="endpointIndex">{{endpoint.path || '--'}}</div>
                                            </template>
                                        </td>
                                        <td>
                                            <template v-for="(endpoint, endpointIndex) in item.spec.endpoints">
                                                <div :key="endpointIndex">{{endpoint.port || '80'}}</div>
                                            </template>
                                        </td>
                                        <td>
                                            <template v-for="(endpoint, endpointIndex) in item.spec.endpoints">
                                                <div :key="endpointIndex">{{endpoint.interval || '--'}}</div>
                                            </template>
                                        </td>
                                        <td class="act">
                                            <a href="javascript:void(0);" class="bk-text-button" @click="showEditMetric(item)" v-if="item.canEdit">{{$t('更新')}}</a>
                                            <template v-else>
                                                <bk-tooltip :delay="300" placement="left">
                                                    <a href="javascript:void(0);" class="bk-text-button disabled">{{$t('更新')}}</a>
                                                    <template slot="content">
                                                        <p class="app-biz-node-label-tip-content">{{item.editMsg}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </template>
                                            <a class="bk-text-button metric-query" href="javascript:void(0)" @click="go(item)" v-if="item.targetData.graph_url">{{$t('指标查询')}}</a>
                                            <a class="bk-text-button metric-query disabled" href="javascript:void(0)" v-else>{{$t('指标查询')}}</a>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="deleteMetric(item)" v-if="item.canDel">{{$t('删除')}}</a>
                                            <template v-else>
                                                <bk-tooltip :delay="300" placement="left">
                                                    <a href="javascript:void(0);" class="bk-text-button disabled metric-del">{{$t('删除')}}</a>
                                                    <template slot="content">
                                                        <p class="app-biz-node-label-tip-content">{{item.delMsg}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </template>
                                        </td>
                                    </tr>
                                    <tr :key="'expand-' + index" v-if="item.expand">
                                        <td colspan="9" style="padding: 0 30px 0 42px;background-color: #fff;">
                                            <div class="sub-table-wrapper" v-bkloading="{ isLoading: item.expanding }">
                                                <table class="bk-table has-table-hover biz-table biz-metric-manage-sub-table">
                                                    <thead>
                                                        <tr>
                                                            <th style="width: 200px;">Endpoints</th>
                                                            <th style="width: 230px;">{{$t('状态')}}</th>
                                                            <th style="width: 400px;">Labels</th>
                                                            <th style="width: 300px;">{{$t('最后请求时间')}}</th>
                                                            <th style="width: 300px;">{{$t('请求耗时')}}</th>
                                                            <th style="width: 300px;">{{$t('错误信息')}}</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        <template v-if="item.targetData.targets && item.targetData.targets.length && !item.expanding">
                                                            <template v-for="(targetItem, targetItemIndex) in item.targetData.targets">
                                                                <tr :key="targetItemIndex">
                                                                    <td>
                                                                        <bk-tooltip placement="top" :delay="500">
                                                                            <p class="sub-item-name">{{targetItem.scrapeUrl || '--'}}</p>
                                                                            <template slot="content">
                                                                                <p style="text-align: left; white-space: normal;word-break: break-all;">{{targetItem.scrapeUrl || '--'}}</p>
                                                                            </template>
                                                                        </bk-tooltip>
                                                                    </td>
                                                                    <td>
                                                                        <span class="health up" v-if="targetItem.health === 'up'">{{$t('正常')}}</span>
                                                                        <span class="health down" v-else>{{$t('异常')}}</span>
                                                                    </td>
                                                                    <td>
                                                                        <div class="labels-wrapper">
                                                                            <div class="labels-inner" v-for="(labelKey, labelKeyIndex) in Object.keys(targetItem.labels)" :key="labelKeyIndex">
                                                                                <!-- <span class="key">{{labelKey}}</span>
                                                                                <span class="value">{{targetItem.labels[labelKey]}}</span> -->
                                                                                <bk-tooltip :delay="300" placement="top">
                                                                                    <span class="key">{{labelKey}}</span>
                                                                                    <template slot="content">
                                                                                        <p class="app-biz-node-label-tip-content">{{labelKey}}</p>
                                                                                    </template>
                                                                                </bk-tooltip>
                                                                                <bk-tooltip :delay="300" placement="top">
                                                                                    <span class="value">{{targetItem.labels[labelKey]}}</span>
                                                                                    <template slot="content">
                                                                                        <p class="app-biz-node-label-tip-content">{{targetItem.labels[labelKey]}}</p>
                                                                                    </template>
                                                                                </bk-tooltip>
                                                                            </div>
                                                                        </div>
                                                                        <!-- <template v-for="(labelStr, labelStrIndex) in targetItem.labelArr">
                                                                            <div :key="labelStrIndex">{{labelStr}}</div>
                                                                        </template> -->
                                                                    </td>
                                                                    <td>
                                                                        <template v-if="targetItem.lastScrapeDiffStr === '--'">
                                                                            {{targetItem.lastScrapeDiffStr}}
                                                                        </template>
                                                                        <template v-else>
                                                                            {{targetItem.lastScrapeDiffStr}}{{$t('前')}}
                                                                        </template>
                                                                    </td>
                                                                    <td>{{targetItem.lastScrapeDuration * 1000}}ms</td>
                                                                    <td>{{targetItem.lastError || '--'}}</td>
                                                                </tr>
                                                            </template>
                                                        </template>
                                                        <template v-else-if="(!item.targetData.targets || !item.targetData.targets.length) && !item.expanding">
                                                            <tr class="no-hover">
                                                                <td colspan="6">
                                                                    <div class="bk-message-box">
                                                                        <!-- <p class="message empty-message">{{$t('无数据')}}</p> -->
                                                                        <p class="message empty-message">{{item.emptyMsg}}</p>
                                                                    </div>
                                                                </td>
                                                            </tr>
                                                        </template>
                                                        <template v-else>
                                                            <tr class="no-hover">
                                                                <td colspan="6">
                                                                    <div class="bk-message-box">
                                                                    </div>
                                                                </td>
                                                            </tr>
                                                        </template>
                                                    </tbody>
                                                </table>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </template>
                            <template v-else-if="!curPageData.length && !isInitLoading">
                                <tr class="no-hover">
                                    <td colspan="10">
                                        <div class="bk-message-box">
                                            <p class="message empty-message">{{$t('无数据')}}</p>
                                        </div>
                                    </td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr class="no-hover">
                                    <td colspan="10">
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
        </div>

        <create-metric ref="createMetricComp"
            :is-show="isShowCreateMetric"
            :cluster-id="searchClusterId"
            :cluster-name="searchClusterName"
            @hide-create-metric="hideCreateMetric"
            @create-success="createMetricSuccess">
        </create-metric>

        <edit-metric ref="editMetricComp"
            :data="curEditMetric"
            :is-show="isShowEditMetric"
            :cluster-id="searchClusterId"
            :cluster-name="searchClusterName"
            :service-list="serviceList"
            @hide-edit-metric="hideEditMetric"
            @edit-success="editMetricSuccess">
        </edit-metric>

        <bk-dialog
            :is-show.sync="updateDialogConf.isShow"
            :width="updateDialogConf.width"
            :close-icon="updateDialogConf.closeIcon"
            :ext-cls="'biz-metric-update-dialog'"
            :has-header="false"
            :quick-close="false">
            <div slot="content" style="padding: 0 20px;">
                <div class="title">
                    {{$t('升级')}}
                </div>
                <div class="info">
                    &nbsp;
                </div>
                <div style="color: red;">
                    {{$t('升级大约需要 1~2 分钟，请勿重复提交；升级过程中 Prometheus 服务将会重启，数据无损失')}}
                </div>
            </div>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                        @click="updateConfirm">
                        {{$t('确定')}}
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="updateCancel">
                        {{$t('取消')}}
                    </button>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="batchDelDialogConf.isShow"
            :width="360"
            :close-icon="false"
            :ext-cls="'export-strategy-dialog'"
            :has-header="false"
            :quick-close="false">
            <div slot="content" style="font-size: 18px; text-align: center;">
                {{batchDelDialogConf.content}}
            </div>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="batchDelDialogConf.isDeleting">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary is-disabled">
                            {{$t('删除中...')}}
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel is-disabled">
                            {{$t('取消')}}
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="batchDelConfirm">
                            {{$t('确定')}}
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideBatchDelDialog">
                            {{$t('取消')}}
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>
    </div>
</template>

<script>
    import moment from 'moment'

    import CreateMetric from './create'
    import EditMetric from './edit'
    import Searcher from './searcher'

    export default {
        components: {
            CreateMetric,
            EditMetric,
            Searcher
        },
        data () {
            return {
                isInitLoading: true,
                isPageLoading: false,
                bkMessageInstance: null,
                exceptionCode: null,
                dataList: [],
                dataListTmp: [],
                curPageData: [],
                pageConf: {
                    // 总数
                    total: 0,
                    // 总页数
                    totalPage: 1,
                    // 每页多少条
                    pageSize: 10,
                    // 当前页
                    curPage: 1,
                    // 是否显示翻页条
                    show: false
                },
                isShowCreateMetric: false,
                searchClusterId: '',
                searchClusterName: '',
                searchKeyWord: '',
                clusterList: [],
                serviceList: [],
                targets: {},
                isShowEditMetric: false,
                curEditMetric: {},
                updateMsg: '',
                updateDialogConf: {
                    isShow: false,
                    width: 650,
                    title: '',
                    closeIcon: false
                },
                urlClusterId: '',
                isCheckAll: false,
                // 已选择的 nodeList
                checkedNodeList: [],
                batchDelDialogConf: {
                    isShow: false,
                    content: '',
                    isDeleting: false
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
            isEn () {
                return this.$store.state.isEn
            }
        },
        async created () {
            this.urlClusterId = this.$route.query.cluster_id
            await this.getClusters()
        },
        destroyed () {
            this.bkMessageInstance && this.bkMessageInstance.close()
        },
        methods: {
            /**
             * 设置 router query 参数，如果同名，那么会被覆盖（router 不会刷新）
             *
             * @param {Object} params 要设置的 url 参数
             */
            addParamsToRouter (params) {
                this.$router.push({
                    query: Object.assign(JSON.parse(JSON.stringify(this.$route.query)), params)
                })
            },

            /**
             * 查看是否需要升级版本
             */
            async fetchPrometheusUpdate () {
                try {
                    const res = await this.$store.dispatch('metric/getPrometheusUpdate', {
                        projectId: this.projectId,
                        clusterId: this.searchClusterId
                    })
                    const data = res.data || {}
                    this.updateMsg = data.update_tooltip || ''
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 获取所有的集群
             */
            async getClusters () {
                try {
                    const res = await this.$store.dispatch('cluster/getClusterList', this.projectId)
                    const list = res.data.results || []
                    const clusterList = []
                    list.forEach(item => {
                        clusterList.push({
                            id: item.cluster_id,
                            cluster_id: item.cluster_id,
                            cluster_name: item.name,
                            name: item.name
                        })
                    })
                    this.clusterList.splice(0, this.clusterList.length, ...clusterList)
                    if (this.clusterList.length) {
                        const clusterIds = this.clusterList.map(item => item.cluster_id)
                        if (this.urlClusterId === null || this.urlClusterId === undefined || this.urlClusterId === '') {
                            // 使用当前缓存
                            if (sessionStorage['bcs-cluster'] && clusterIds.includes(sessionStorage['bcs-cluster'])) {
                                this.urlClusterId = sessionStorage['bcs-cluster']
                            } else {
                                this.urlClusterId = this.clusterList[0].cluster_id
                                sessionStorage['bcs-cluster'] = this.urlClusterId
                            }
                        } else {
                            sessionStorage['bcs-cluster'] = this.urlClusterId
                        }

                        const cluster = this.clusterList.find(cl => cl.cluster_id === this.urlClusterId)
                        if (cluster) {
                            this.searchClusterId = cluster.cluster_id
                            this.searchClusterName = cluster.cluster_name
                            this.addParamsToRouter({ cluster_id: this.searchClusterId })

                            await this.fetchService()
                            await this.fetchTarget()
                            await this.fetchData()
                            this.fetchPrometheusUpdate()
                        } else {
                            this.bkMessageInstance = this.$bkMessage({
                                theme: 'error',
                                message: `集群 ${this.urlClusterId} 不存在`
                            })
                            setTimeout(() => {
                                this.isInitLoading = false
                            }, 200)
                        }
                    } else {
                        // 没有集群时，这里就终止了，不会执行 fetchData，所以这里关闭 loading，不能在 finally 里面关闭
                        // 因为如果集群存在时，还需要 loading fetchData
                        setTimeout(() => {
                            this.isInitLoading = false
                        }, 200)
                    }
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 切换集群搜索
             */
            async searchMetricByCluster () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.addParamsToRouter({ cluster_id: this.searchClusterId })
                await this.fetchService()
                await this.fetchTarget()
                await this.fetchData()
                this.fetchPrometheusUpdate()
            },

            /**
             * 获取 service 数据
             */
            async fetchService () {
                try {
                    const res = await this.$store.dispatch('metric/listServices', {
                        projectId: this.projectId,
                        clusterId: this.searchClusterId
                    })
                    const list = res.data || []
                    list.forEach(item => {
                        item.displayName = `${item.namespace}/${item.resourceName}`
                    })
                    this.serviceList.splice(0, this.serviceList.length, ...list)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 获取 targets 数据
             */
            async fetchTarget () {
                try {
                    const res = await this.$store.dispatch('metric/listTargets', {
                        projectId: this.projectId,
                        clusterId: this.searchClusterId
                    })
                    this.targets = Object.assign({}, res.data || {})
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 获取 metric 列表数据
             */
            async fetchData () {
                this.searchClusterName = this.clusterList.find(
                    cluster => cluster.cluster_id === this.searchClusterId
                ).cluster_name
                try {
                    this.isPageLoading = true
                    const res = await this.$store.dispatch('metric/listServiceMonitor', {
                        projectId: this.projectId,
                        clusterId: this.searchClusterId
                    })
                    const list = res.data || []
                    list.forEach(item => {
                        item.expand = false
                        item.expanding = false
                        item.canEdit = item.permissions.edit && !!this.serviceList.find(service =>
                            service.clusterId === item.cluster_id
                            && service.namespace === item.namespace
                            && service.resourceName === item.metadata.service_name
                        )
                        item.editMsg = item.permissions.edit_msg
                        item.canDel = item.permissions.delete
                        item.delMsg = item.permissions.delete_msg
                        item.targetData = Object.assign({}, this.targets[item.instance_id] || {})
                        item.isChecked = false
                    })
                    this.dataListTmp.splice(0, this.dataListTmp.length, ...list)
                    this.dataList.splice(0, this.dataList.length, ...list)
                    this.pageConf.curPage = 1
                    this.searchMetricByWord()
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                        this.isPageLoading = false
                    }, 200)
                }
            },

            /**
             * 根据关键字搜索
             */
            searchMetricByWord () {
                const search = String(this.searchKeyWord || '').trim().toLowerCase()
                let results = []
                if (search === '') {
                    this.dataList.splice(0, this.dataList.length, ...this.dataListTmp)
                } else {
                    results = this.dataListTmp.filter(m => {
                        return m.name.toLowerCase().indexOf(search) > -1
                    })
                    this.dataList.splice(0, this.dataList.length, ...results)
                }
                this.initPageConf()
                this.curPageData = this.getDataByPage()
            },

            /**
             * 初始化翻页条
             */
            initPageConf () {
                const total = this.dataList.length
                if (total <= this.pageConf.pageSize) {
                    this.pageConf.show = false
                } else {
                    this.pageConf.show = true
                }
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize) || 1
            },

            /**
             * 翻页回调
             *
             * @param {number} page 当前页
             */
            pageChange (page = 1) {
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData.splice(0, this.curPageData.length, ...data)

                // 当前页选中的
                const selectedNodeList = this.curPageData.filter(item => item.isChecked === true)
                // 当前页合法的
                const validList = this.curPageData.filter(item => item.canDel)
                this.isCheckAll = selectedNodeList.length === validList.length
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
                this.pageChange()
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
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.dataList.length) {
                    endIndex = this.dataList.length
                }
                return this.dataList.slice(startIndex, endIndex)
            },

            /**
             * 手动刷新表格数据
             */
            async refresh () {
                this.pageConf.curPage = 1
                this.searchKeyWord = ''
                this.isPageLoading = true
                await this.fetchService()
                await this.fetchTarget()
                await this.fetchData()
                this.fetchPrometheusUpdate()
            },

            /**
             * 列表全选
             */
            checkAllMetric (e) {
                const isChecked = e.target.checked
                this.curPageData.forEach(item => {
                    if (item.canDel) {
                        item.isChecked = isChecked
                    }
                })

                const checkedNodeList = []
                checkedNodeList.splice(0, 0, ...this.checkedNodeList)
                // 用于区分是否已经选择过
                const hasCheckedList = checkedNodeList.map(item => item.name + item.instance_id + item.cluster_id + item.namespace_id)
                if (isChecked) {
                    const checkedList = this.curPageData.filter(
                        item => item.canDel && !hasCheckedList.includes(item.name + item.instance_id + item.cluster_id + item.namespace_id)
                    )
                    checkedNodeList.push(...checkedList)
                    this.checkedNodeList.splice(0, this.checkedNodeList.length, ...checkedNodeList)
                } else {
                    // 当前页所有合法的 node id 集合
                    const validIdList = this.curPageData.filter(
                        item => item.canDel
                    ).map(item => item.name + item.instance_id + item.cluster_id + item.namespace_id)

                    const newCheckedNodeList = []
                    this.checkedNodeList.forEach(checkedNode => {
                        if (validIdList.indexOf(checkedNode.name + checkedNode.instance_id + checkedNode.cluster_id + checkedNode.namespace_id) < 0) {
                            newCheckedNodeList.push(JSON.parse(JSON.stringify(checkedNode)))
                        }
                    })
                    this.checkedNodeList.splice(0, this.checkedNodeList.length, ...newCheckedNodeList)
                }
            },

            /**
             * 列表每一行的 checkbox 点击
             *
             * @param {Object} row 当前策略对象
             */
            checkMetric (row) {
                this.$nextTick(() => {
                    // 当前页选中的
                    const selectedNodeList = this.curPageData.filter(item => item.isChecked === true)
                    // 当前页合法的
                    const validList = this.curPageData.filter(item => item.canDel)
                    this.isCheckAll = selectedNodeList.length === validList.length

                    const checkedNodeList = []
                    if (row.isChecked) {
                        checkedNodeList.splice(0, checkedNodeList.length, ...this.checkedNodeList)
                        if (!this.checkedNodeList.filter(
                            checkedNode => checkedNode.name + checkedNode.instance_id + checkedNode.cluster_id + checkedNode.namespace_id === row.name + row.instance_id + row.cluster_id + row.namespace_id
                        ).length) {
                            checkedNodeList.push(row)
                        }
                    } else {
                        this.checkedNodeList.forEach(checkedNode => {
                            if (checkedNode.name + checkedNode.instance_id + checkedNode.cluster_id + checkedNode.namespace_id !== row.name + row.instance_id + row.cluster_id + row.namespace_id) {
                                checkedNodeList.push(JSON.parse(JSON.stringify(checkedNode)))
                            }
                        })
                    }
                    this.checkedNodeList.splice(0, this.checkedNodeList.length, ...checkedNodeList)
                })
            },

            /**
             * 批量删除
             */
            batchDel () {
                if (!this.checkedNodeList.length) {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: this.$t('还未选择Metric')
                    })
                    return
                }

                this.batchDelDialogConf.content = this.$t('确定删除所选的{len}个Metric？', { len: this.checkedNodeList.length })
                this.batchDelDialogConf.isShow = true
            },

            /**
             * 批量删除弹框取消按钮
             */
            hideBatchDelDialog () {
                this.batchDelDialogConf.isShow = false
                setTimeout(() => {
                    this.batchDelDialogConf.content = ''
                    this.batchDelDialogConf.isDeleting = false
                }, 300)
            },

            /**
             * 批量删除弹框确定按钮
             */
            async batchDelConfirm () {
                try {
                    this.batchDelDialogConf.isDeleting = true

                    await this.$store.dispatch('metric/batchDeleteServiceMonitor', {
                        projectId: this.projectId,
                        clusterId: this.searchClusterId,
                        data: {
                            servicemonitors: this.checkedNodeList.map(item => {
                                return {
                                    namespace: item.namespace,
                                    name: item.name
                                }
                            })
                        }
                    })
                    this.hideBatchDelDialog()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'success',
                        delay: 1000,
                        message: this.$t('删除Metric成功')
                    })
                    this.checkedNodeList.splice(0, this.checkedNodeList.length, ...[])

                    await this.refresh()
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.batchDelDialogConf.isDeleting = false
                }
            },

            /**
             * 展开/收起当前行
             *
             * @param {Object} row 当前行数据
             */
            async toggleRow (row) {
                if (row.expand) {
                    row.expand = false
                    return
                }
                row.expand = true
                row.expanding = true

                setTimeout(() => {
                    if (row.targetData.targets && row.targetData.targets.length) {
                        row.targetData.targets.forEach(item => {
                            item.labelArr = []
                            Object.keys(item.labels).forEach(k => {
                                item.labelArr.push(`${k}="${item.labels[k]}"`)
                            })

                            if (item.lastScrape.substr(0, 10) === '0001-01-01') {
                                item.lastScrapeDiffStr = '--'
                            } else {
                                const timeDiff = moment.duration(
                                    moment().diff(moment(Date.parse(item.lastScrape)).format('YYYY-MM-DD HH:mm:ss'))
                                )
                                const arr = [
                                    moment().diff(moment(Date.parse(item.lastScrape)), 'days'),
                                    timeDiff.get('hour'),
                                    timeDiff.get('minute'),
                                    timeDiff.get('second')
                                ]
                                item.lastScrapeDiffStr = (arr[0] !== 0 ? (arr[0] + this.$t('天1')) : '')
                                    + (arr[1] !== 0 ? (arr[1] + this.$t('小时1')) : '')
                                    + (arr[2] !== 0 ? (arr[2] + this.$t('分1')) : '')
                                    + (arr[3] !== 0 ? (arr[3] + this.$t('秒1')) : '')
                            }
                        })
                    } else {
                        const curTimestamp = new Date().getTime()
                        const createTimestamp = new Date(Date.parse(row.metadata.creationTimestamp)).getTime()
                        if (curTimestamp - createTimestamp > 120000) {
                            row.emptyMsg = this.$t('无数据（请检查 Service 是否有关联的 Endpoints)')
                        } else {
                            row.emptyMsg = this.$t('无数据（新建 Metric 需要1~2分钟生效，请刷新），通过计算创建时间和当前时间判断')
                        }
                    }
                    row.expanding = false
                }, 500)
            },

            /**
             * 显示创建 metric sideslider
             */
            async showCreateMetric () {
                this.$refs.createMetricComp.resetParams()
                this.isShowCreateMetric = true
            },

            /**
             * 隐藏创建 metric sideslider
             */
            hideCreateMetric () {
                this.isShowCreateMetric = false
            },

            /**
             * 创建 metric 成功回调函数
             */
            async createMetricSuccess () {
                this.hideCreateMetric()
                setTimeout(async () => {
                    await this.refresh()
                }, 300)
            },

            /**
             * 显示编辑 metric sideslider
             *
             * @param {Object} metric 当前行数据
             */
            async showEditMetric (metric) {
                this.curEditMetric = Object.assign({}, metric)
                this.$refs.editMetricComp.resetParams()
                this.isShowEditMetric = true
            },

            /**
             * 隐藏编辑 metric sideslider
             */
            hideEditMetric () {
                this.isShowEditMetric = false
            },

            /**
             * 编辑 metric 成功回调函数
             */
            async editMetricSuccess () {
                this.hideEditMetric()
                setTimeout(async () => {
                    await this.refresh()
                }, 300)
            },

            /**
             * 删除 metric
             *
             * @param {Object} metric 当前 metric 对象
             */
            async deleteMetric (metric) {
                const me = this
                me.$bkInfo({
                    title: ``,
                    clsName: 'biz-remove-dialog',
                    content: me.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除Metric')}【${metric.name}】？`),
                    async confirmFn () {
                        try {
                            me.$bkLoading({
                                title: me.$createElement('span', me.$t('删除Metric中，请稍候'))
                            })

                            await me.$store.dispatch('metric/deleteServiceMonitor', {
                                projectId: me.projectId,
                                clusterId: metric.cluster_id,
                                namespace: metric.namespace,
                                name: metric.name
                            })

                            await me.refresh()
                            me.$bkLoading.hide()
                        } catch (e) {
                            console.error(e)
                            me.$bkLoading.hide()
                            me.bkMessageInstance = me.$bkMessage({
                                theme: 'error',
                                message: e.message || e.data.msg || e.statusText
                            })
                        }
                    }
                })
            },

            /**
             * prometheus_update
             */
            async doUpdate () {
                this.updateDialogConf.isShow = true
            },

            /**
             * 确定更新
             */
            async updateConfirm () {
                try {
                    await this.$store.dispatch('metric/startPrometheusUpdate', {
                        projectId: this.projectId,
                        clusterId: this.searchClusterId
                    })
                    this.updateCancel()
                    await this.refresh()
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 取消更新
             *
             * @param {Object} ns 当前 namespace 对象
             * @param {number} index 当前 namespace 对象的索引
             */
            updateCancel () {
                this.updateDialogConf.isShow = false
            },

            /**
             * 跳转到 指标查询 页面
             *
             * @param {Object} metric 当前 metric 对象
             */
            async go (metric) {
                window.open(metric.targetData.graph_url)
            }
        }
    }
</script>

<style scoped>
    @import './main.css';
</style>
