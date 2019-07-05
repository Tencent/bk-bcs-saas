<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-cluster-overview-title">
                <template v-if="exceptionCode">
                    <div @click="goIndex">
                        <i class="bk-icon icon-arrows-left back"></i>
                        <span>返回</span>
                    </div>
                </template>
                <template v-else>
                    <i class="bk-icon icon-arrows-left back" @click="goIndex"></i>
                    <template v-if="curClusterInPage.cluster_id">
                        <span @click="refreshCurRouter">{{curClusterInPage.name}}</span>
                        <span style="font-size: 12px; color: #c3cdd7;cursor:default;margin-left: 10px;">
                            （{{curClusterInPage.cluster_id}}）
                        </span>
                    </template>
                </template>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper biz-cluster-overview" v-bkloading="{ isLoading: showLoading }">
            <app-exception
                v-if="exceptionCode && !showLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>
            <div v-if="!exceptionCode && !showLoading" class="biz-cluster-overview-wrapper">
                <div class="biz-cluster-tab-header">
                    <div class="header-item active">
                        <i class="bk-icon icon-bar-chart"></i>总览
                    </div>
                    <div class="header-item" @click="goNode">
                        <i class="bk-icon icon-list"></i>节点管理
                    </div>
                    <div class="header-item" @click="goInfo">
                        <i class="icon-cc icon-cc-machine"></i>集群信息
                    </div>
                </div>
                <div class="biz-cluster-tab-content">
                    <div class="biz-cluster-overview-chart">
                        <div class="chart-box top">
                            <div class="info">
                                <div class="left">CPU使用率</div>
                                <div class="right" v-if="cpuUsagePercent === '无数据'">
                                    <div><span>无数据</span></div>
                                </div>
                                <div class="right" v-else>
                                    <div><span>{{cpuUsagePercent}}</span><sup>%</sup></div>
                                    <div class="cpu"><span>{{cpuUsage}} of {{cpuTotal}} Shares</span></div>
                                </div>
                            </div>
                            <chart :options="cpuLine" ref="cpuLine" auto-resize></chart>
                        </div>

                        <div class="chart-box top">
                            <div class="info">
                                <div class="left">内存使用率</div>
                                <div class="right" v-if="memUsagePercent === '无数据'">
                                    <div><span>无数据</span></div>
                                </div>
                                <div class="right" v-else>
                                    <div><span>{{memUsagePercent}}</span><sup>%</sup></div>
                                    <div class="memory"><span>{{memUsage}}GB of {{memTotal}} GB</span></div>
                                </div>
                            </div>
                            <chart :options="memLine" ref="memLine" auto-resize></chart>
                        </div>

                        <div class="chart-box top">
                            <div class="info">
                                <div class="left">磁盘使用率</div>
                                <div class="right" v-if="diskUsagePercent === '无数据'">
                                    <div><span>无数据</span></div>
                                </div>
                                <div class="right" v-else>
                                    <div><span>{{diskUsagePercent}}</span><sup>%</sup></div>
                                    <div class="disk"><span>{{diskUsage}}GB of {{diskTotal}} GB</span></div>
                                </div>
                            </div>
                            <chart :options="diskLine" ref="diskLine" auto-resize></chart>
                        </div>
                    </div>

                    <div class="biz-cluster-overview-chart">
                        <div class="chart-box bottom">
                            <div class="info">
                                <div class="left">节点</div>
                                <div class="right">
                                    <div>
                                        <i class="bk-icon icon-circle"></i>
                                        <span>使用中</span>
                                        <span>{{nodeActived}}</span>
                                    </div>
                                    <div>
                                        <i class="bk-icon icon-circle"></i>
                                        <span>未使用</span>
                                        <span>{{nodeDisabled}}</span>
                                    </div>
                                </div>
                            </div>
                            <Ring :percent="nodePercent" :size="210" :text="'none'"
                                :stroke-width="10" :fill-width="10" :fill-color="'#3ede78'"
                                :percent-change-handler="percentChangeHandler('node')"
                                :ext-cls="'biz-cluster-ring'">
                                <div slot="text" class="ring-text-inner">
                                    <div class="number">{{nodePercentStr}}</div>
                                </div>
                            </Ring>
                        </div>

                        <div class="chart-box bottom">
                            <div class="info">
                                <div class="left">命名空间</div>
                                <div class="right">
                                    <div>
                                        <i class="bk-icon icon-circle"></i>
                                        <span>已使用</span>
                                        <span>{{namespaceActived}}</span>
                                    </div>
                                    <div>
                                        <i class="bk-icon icon-circle"></i>
                                        <span>总量</span>
                                        <span>{{namespaceTotal}}</span>
                                    </div>
                                </div>
                            </div>
                            <Ring :percent="namespacePercent" :size="210" :text="'none'"
                                :stroke-width="10" :fill-width="10" :fill-color="'#3ede78'"
                                :percent-change-handler="percentChangeHandler('namespace')"
                                :ext-cls="'biz-cluster-ring'">
                                <div slot="text" class="ring-text-inner">
                                    <div class="number">{{namespacePercentStr}}</div>
                                </div>
                            </Ring>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import ECharts from 'vue-echarts/components/ECharts.vue'
    import 'echarts/lib/chart/line'
    import 'echarts/lib/component/tooltip'

    import { overview } from '@open/common/chart-option'
    import Ring from '@open/components/ring'
    import { catchErrorHandler } from '@open/common/util'

    export default {
        components: {
            Ring,
            chart: ECharts
        },
        data () {
            return {
                nodePercent: 0,
                nodePercentStr: 0,
                nodeActived: '',
                nodeDisabled: '',
                namespacePercent: 0,
                namespacePercentStr: 0,
                namespaceActived: '',
                namespaceTotal: '',
                ipPercent: 0,
                ipPercentStr: 0,
                ipUsed: '',
                ipTotal: '',
                cpuLine: overview.cpu,
                memLine: overview.memory,
                diskLine: overview.disk,
                bkMessageInstance: null,
                curClusterInPage: {},
                exceptionCode: null,
                showLoading: false,
                cpuUsagePercent: 0,
                cpuUsage: 0,
                cpuTotal: 0,
                memUsagePercent: 0,
                memUsage: 0,
                memTotal: 0,
                diskUsagePercent: 0,
                diskUsage: 0,
                diskTotal: 0,
                testTimer: null
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            clusterId () {
                return this.$route.params.clusterId
            },
            curCluster () {
                this.curClusterInPage = Object.assign({}, this.$store.state.cluster.curCluster)
                return this.$store.state.cluster.curCluster
            }
        },
        created () {
            if (!this.curCluster || Object.keys(this.curCluster).length <= 0) {
                if (this.projectId && this.clusterId) {
                    this.fetchData()
                }
            } else {
                this.fetchClusterMetrics()
                setTimeout(this.prepareChartData, 0)
            }
        },
        destroyed () {
            this.testTimer && clearInterval(this.testTimer)
        },
        methods: {
            /**
             * 转换百分比
             *
             * @param {number} remain 剩下的数量
             * @param {number} total 总量
             *
             * @return {number} 百分比数字
             */
            conversionPercent (remain, total) {
                if (!remain || !total) {
                    return 0
                }
                return total === 0 ? 0 : ((total - remain) / total * 100).toFixed(2)
            },

            /**
             * 获取数据
             */
            async fetchData () {
                this.showLoading = true
                try {
                    const res = await this.$store.dispatch('cluster/getCluster', {
                        projectId: this.projectId,
                        clusterId: this.clusterId
                    })

                    this.$store.commit('cluster/forceUpdateCurCluster', res.data)
                    this.fetchClusterMetrics()
                    setTimeout(this.prepareChartData, 0)
                } catch (e) {
                    const data = e.data
                    if (data) {
                        if (!data.code || data.code === 404) {
                            this.exceptionCode = {
                                code: '404',
                                msg: '当前访问的页面不存在'
                            }
                        } else if (data.code === 403) {
                            this.exceptionCode = {
                                code: '403',
                                msg: 'Sorry，您的权限不足!'
                            }
                        } else if (data.code === 400) {
                            this.exceptionCode = {
                                code: '404',
                                msg: '当前访问的集群不存在!'
                            }
                        } else {
                            console.error(e)
                            this.bkMessageInstance = this.$bkMessage({
                                theme: 'error',
                                message: e.message || e.data.msg || e.statusText
                            })
                        }
                    } else {
                        console.error(e)
                        this.bkMessageInstance = this.$bkMessage({
                            theme: 'error',
                            message: e.message || e.data.msg || e.statusText
                        })
                    }
                } finally {
                    this.showLoading = false
                }
            },

            /**
             * 构建图表数据
             */
            async prepareChartData () {
                const memRef = this.$refs.memLine
                const diskRef = this.$refs.diskLine
                const cpuRef = this.$refs.cpuLine
                try {
                    cpuRef && cpuRef.showLoading({
                        text: '正在加载',
                        color: '#30d878',
                        maskColor: 'rgba(255, 255, 255, 0.8)'
                    })
                    memRef && memRef.showLoading({
                        text: '正在加载',
                        color: '#30d878',
                        maskColor: 'rgba(255, 255, 255, 0.8)'
                    })
                    diskRef && diskRef.showLoading({
                        text: '正在加载',
                        color: '#30d878',
                        maskColor: 'rgba(255, 255, 255, 0.8)'
                    })

                    const res = await this.$store.dispatch('cluster/getClusterOverview', {
                        projectId: this.curCluster.project_id, // 这里用 this.curCluster 来获取是为了使计算属性生效
                        clusterId: this.curCluster.cluster_id
                    })

                    this.renderCpuChart(res.data.cpu || [])
                    this.renderChart('mem', memRef, res.data.mem || [])
                    this.renderChart('disk', diskRef, res.data.disk || [])
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 渲染图表
             *
             * @param {Array} list 数据
             */
            renderCpuChart (list) {
                const ref = this.$refs.cpuLine
                if (!ref) {
                    return
                }

                let chartData = []
                let emptyData = []

                if (!list.length) {
                    this.cpuUsagePercent = '无数据'
                    this.cpuUsage = '无数据'
                    this.cpuTotal = '无数据'

                    chartData = [{
                        value: [+new Date(), 0, '无数据']
                    }]
                    emptyData = [0]
                } else {
                    const data = list.length ? list : [{ time: +new Date(), remain_cpu: 0, total_cpu: 0 }]
                    const lastData = data[data.length - 1]
                    this.cpuUsagePercent = this.conversionPercent(lastData.remain_cpu, lastData.total_cpu)
                    this.cpuUsage = ((lastData.total_cpu || 0) - (lastData.remain_cpu || 0)).toFixed(2)
                    this.cpuTotal = (lastData.total_cpu || 0).toFixed(2)

                    data.forEach(item => {
                        chartData.push({
                            value: [item.time, this.conversionPercent(item.remain_cpu, item.total_cpu)]
                        })
                        emptyData.push(0)
                    })
                }

                // 先设置 emptyData，再切换数据，这样的话，图表是从中间往两边展开，效果会好一些
                ref.mergeOptions({
                    series: [
                        {
                            data: emptyData
                        }
                    ]
                })
                ref.mergeOptions({
                    series: [
                        {
                            data: chartData
                        }
                    ]
                })
                ref.hideLoading()
            },

            /**
             * 渲染图表
             *
             * @param {string} idx 标识 cpu, mem, disk
             * @param {Object} ref 标识 cpu, mem, disk ref
             * @param {Array} list 数据
             */
            renderChart (idx, ref, list) {
                if (!ref) {
                    return
                }

                let chartData = []
                let emptyData = []

                if (!list.length) {
                    this[`${idx}UsagePercent`] = '无数据'
                    this[`${idx}Usage`] = '无数据'
                    this[`${idx}Total`] = '无数据'

                    chartData = [{
                        value: [+new Date(), 0, '无数据']
                    }]
                    emptyData = [0]
                } else {
                    const data = list.length ? list : [{ time: +new Date(), [`remain_${idx}`]: 0, [`total_${idx}`]: 0 }]
                    const lastData = data[data.length - 1]
                    this[`${idx}UsagePercent`] = this.conversionPercent(lastData[`remain_${idx}`], lastData[`total_${idx}`])
                    this[`${idx}Usage`] = (
                        ((lastData[`total_${idx}`] || 0) - (lastData[`remain_${idx}`] || 0))
                    ).toFixed(2)
                    this[`${idx}Total`] = ((lastData[`total_${idx}`] || 0)).toFixed(2)

                    chartData = []
                    emptyData = []
                    data.forEach(item => {
                        chartData.push({
                            value: [item.time, item[`total_${idx}`] - item[`remain_${idx}`]]
                        })
                        emptyData.push(0)
                    })
                }

                // 先设置 emptyData，再切换数据，这样的话，图表是从中间往两边展开，效果会好一些
                ref.mergeOptions({
                    series: [
                        {
                            data: emptyData
                        }
                    ]
                })
                ref.mergeOptions({
                    series: [
                        {
                            data: chartData
                        }
                    ]
                })
                ref.hideLoading()
            },

            /**
             * 获取下面三个圈的数据
             */
            async fetchClusterMetrics () {
                try {
                    const res = await this.$store.dispatch('cluster/getClusterMetrics', {
                        projectId: this.curCluster.project_id,
                        clusterId: this.curCluster.cluster_id
                    })

                    const nodeActived = res.data.node.actived || 0
                    const nodeTotal = res.data.node.total || 0
                    if (nodeTotal === 0) {
                        this.nodePercent = 0
                    } else {
                        this.nodePercent = nodeActived * 100 / nodeTotal
                    }
                    this.nodeActived = `${nodeActived}台`
                    this.nodeDisabled = `${res.data.node.disabled || 0}台`

                    const namespaceActived = res.data.namespace.actived || 0
                    const namespaceTotal = res.data.namespace.total || 0
                    if (namespaceTotal === 0) {
                        this.namespacePercent = 0
                    } else {
                        this.namespacePercent = namespaceActived * 100 / namespaceTotal
                    }
                    this.namespaceActived = `${namespaceActived}个`
                    this.namespaceTotal = `${namespaceTotal}个`

                    const ipUsed = res.data.ip_resource.used || 0
                    const ipTotal = res.data.ip_resource.total || 0
                    if (ipTotal === 0) {
                        this.ipPercent = 0
                    } else {
                        this.ipPercent = ipUsed * 100 / ipTotal
                    }
                    this.ipUsed = `${ipUsed}个`
                    this.ipTotal = `${ipTotal}个`
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 刷新当前 router
             */
            refreshCurRouter () {
                typeof this.$parent.refreshRouterView === 'function' && this.$parent.refreshRouterView()
            },

            /**
             * 返回集群首页列表
             */
            goIndex () {
                const { params } = this.$route
                if (params.backTarget) {
                    this.$router.push({
                        name: params.backTarget,
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode
                        }
                    })
                } else {
                    this.$router.push({
                        name: 'clusterMain',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode
                        }
                    })
                }
            },

            /**
             * 切换到节点管理
             */
            goNode () {
                this.$router.push({
                    name: 'clusterNode',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        clusterId: this.clusterId,
                        backTarget: this.$route.params.backTarget
                    }
                })
            },

            /**
             * ring 组件百分比变化回调函数
             *
             * @param {string} indicator 标识当前是哪个 ring 组件
             */
            percentChangeHandler (indicator) {
                return percent => (this[`${indicator}PercentStr`] = `${percent}%`)
            },

            /**
             * 切换到集群信息列表
             */
            goInfo () {
                this.$router.push({
                    name: 'clusterInfo',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        clusterId: this.clusterId,
                        backTarget: this.$route.params.backTarget
                    }
                })
            }
        }
    }
</script>
<style scoped lang="postcss">
    @import '../../css/variable.css';
    @import '../../css/mixins/clearfix.css';

    .biz-cluster-overview {
        padding: 20px;
    }

    .biz-cluster-overview-title {
        display: inline-block;
        height: 60px;
        line-height: 60px;
        font-size: 16px;
        margin-left: 20px;
        cursor: pointer;

        .back {
            font-size: 16px;
            font-weight: 700;
            position: relative;
            top: 1px;
            color: $iconPrimaryColor
        }
    }

    .biz-cluster-overview-wrapper {
        background-color: $bgHoverColor;
        border: 1px solid $borderWeightColor;
        display: inline-block;
        width: 100%;
        border-radius: 2px;
    }

    .biz-cluster-tab-header {
        height: 60px;
        line-height: 60px;
        font-size: 0;
        border-bottom: 1px solid $borderWeightColor;

        .header-item {
            font-size: 14px;
            display: inline-block;
            width: 140px;
            text-align: center;
            border: none;
            cursor: pointer;

            i {
                font-size: 16px;
                margin-right: 8px;
                position: relative;
                top: 2px;
            }

            &.active {
                color: $iconPrimaryColor;
                background-color: #fff;
                border-right: 1px solid $borderWeightColor;
                font-weight: 700;
                cursor: default;

                i {
                    font-weight: 700;
                }
            }
        }
    }

    .biz-cluster-tab-content {
        background-color: #fff;
        font-size: 14px;
    }

    .biz-cluster-overview-chart {
        background-color: #fff;
        display: flex;
        justify-content: center;

        &:nth-child(1) {
            border-bottom: 1px solid $borderWeightColor;
        }

        .chart-box {
            @mixin clearfix;
            height: 360px;
            padding: 20px;
            position: relative;
            flex: 1;
            border-left: 1px solid $borderWeightColor;

            &:nth-child(1) {
                border-left: none;
            }
        }

        .ring-text-inner {
            position: absolute;
            transform: translate(-50%, -50%);
            left: 50%;
            top: 50%;
            text-align: center;
        }

        .number {
            font-size: 54px;
        }

        .label {
            font-size: 14px;
        }

        .biz-cluster-ring {
            position: absolute;
            transform: translate(-50%, -50%);
            left: 50%;
            top: 56%;
        }

        .info {
            display: inline-block;
            width: 100%;
        }

        .chart-box.bottom {
            @mixin clearfix;
            font-size: 14px;

            .left {
                font-weight: 700;
                float: left;
            }

            .right {
                float: right;
                font-size: 14px;

                i {
                    font-weight: 700;
                    vertical-align: middle;
                    margin-right: 7px;
                }

                span {
                    display: inline-block;
                    width: 50px;

                    &:last-child {
                        text-align: right;
                        font-weight: 700;
                    }
                }

                div:first-child {
                    margin-bottom: 10px;

                    i {
                        color: #3ede78;
                    }
                }

                div:last-child {
                    i {
                        color: $borderColor;
                    }
                }
            }
        }

        .chart-box.top {
            .left {
                font-weight: 700;
                float: left;
            }

            .right {
                text-align: right;
                float: right;
                font-size: 14px;

                div:first-child {
                    font-size: 36px;

                    sup {
                        font-size: 20px;
                    }
                }

                div:last-child {
                    font-weight: 700;

                    &.cpu {
                        color: #3ede78;
                    }

                    &.memory {
                        color: #3c96ff;
                    }

                    &.disk {
                        color: #853cff;
                    }
                }
            }
        }

        .echarts {
            width: 100%;
            height: 250px;
        }
    }

</style>
