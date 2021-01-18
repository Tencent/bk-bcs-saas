<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <i class="biz-back bk-icon icon-arrows-left" @click="goLoadBalanceList"></i>
            <div class="biz-templateset-title">
                <span v-if="loadBalanceDetail">{{loadBalanceDetail.name}}</span>
            </div>
        </div>
        <div class="biz-content-wrapper" v-bkloading="{ isLoading: isDataLoading }">
            <app-exception
                v-if="exceptionCode && !isDataLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>

            <template v-if="!exceptionCode && !isDataLoading && loadBalanceDetail">
                <div class="lb-panel">
                    <div class="lb-data-box">
                        <div class="biz-metadata-box mb20">
                            <div class="data-item" style="width: 200px;">
                                <p class="key">{{$t('所属集群')}}：</p>
                                <p class="value" :title="loadBalanceDetail.cluster_id">
                                    {{loadBalanceDetail.cluster_id}}
                                </p>
                            </div>
                            <div class="data-item">
                                <p class="key">VIP：</p>
                                <p class="value" :title="loadBalanceDetail.ip_list.join(', ')">
                                    {{loadBalanceDetail.ip_list.join(', ')}}
                                </p>
                            </div>
                        </div>
                        <div class="biz-metadata-group" style="display: none;">
                            <div class="biz-metadata-box top">
                                <div class="data-item" style="width: 200px;">
                                    <p class="key">Running Tasks：</p>
                                    <p class="value" title="1/122; idle = 100 %">
                                        --
                                    </p>
                                </div>
                                <div class="data-item">
                                    <p class="key">Uptime：</p>
                                    <p class="value">--</p>
                                </div>
                            </div>

                            <div class="biz-metadata-box bottom">
                                <div class="data-item" style="width: 200px;">
                                    <p class="key">Current Status：</p>
                                    <p class="value">
                                        <span>--</span>
                                    </p>
                                </div>
                                <div class="data-item">
                                    <p class="key">System Limits：</p>
                                    <p class="value">--</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="lb-chart-box" style="display: none;">
                        <div class="info">
                            <div class="left">{{$t('流量')}}</div>
                            <div class="right">
                                <span class="mr15"><i class="biz-dot bk-primary large"></i>{{$t('入带宽')}}</span>
                                <span><i class="biz-dot bk-warning large"></i>{{$t('出带宽')}}</span>
                            </div>
                        </div>
                        <chart :options="chartOptions" ref="instance" auto-resize></chart>
                    </div>
                </div>

                <div class="mt20">
                    <bk-tab :type="'fill'" :active-name="tabActiveName">
                        <bk-tabpanel name="taskgroup" :title="$t('映射Taskgroup')">
                            <div class="biz-app-instance-taskgroup-list" v-if="taskGroup && Object.keys(taskGroup).length">
                                <div class="list-item-tpl" v-for="(key, index) in Object.keys(taskGroup)" :key="index">
                                    <div class="list-item-tpl-inner">
                                        <div style="cursor: pointer;" @click="toggleTaskGroup(taskGroup[key])">
                                            <i class="bk-icon toggle" :class="taskGroup[key].isOpen ? 'icon-minus' : 'icon-plus'"></i>
                                            <span class="name">{{taskGroup[key].name}}</span>
                                            <span class="ver">{{taskGroup[key].type}}</span>

                                            <div class="key-item">
                                                <div class="key-label">{{$t('状态')}}：</div>
                                                <div class="value-label">
                                                    <span class="status-val" v-if="taskGroup[key].status === 'Running' || taskGroup[key].status === 'Finish'" style="color: #34d97b;">
                                                        Normal
                                                    </span>
                                                    <span class="status-val" v-else-if="taskGroup[key].status === 'Starting'">
                                                        Running
                                                    </span>
                                                    <span class="status-val" v-else style="color: #ff5656;">
                                                        <bk-tooltip :content="taskGroup[key].message" placement="top" class="biz-error-tooltip">
                                                            <i class="bk-icon icon-info-circle mr5 f14"></i>Error
                                                        </bk-tooltip>
                                                    </span>
                                                </div>
                                            </div>

                                            <div class="key-item">
                                                <div class="key-label">Host IP：</div>
                                                <div class="value-label">
                                                    {{taskGroup[key].host_ip || '--'}}
                                                </div>
                                            </div>
                                        </div>

                                    </div>
                                    <transition name="fade">
                                        <div class="list-item-tpl-table" v-show="taskGroup[key].isOpen">
                                            <table class="bk-table has-table-hover biz-table" style="overflow: hidden; border-top: 1px solid #e6e6e6;">
                                                <thead>
                                                    <tr>
                                                        <th style="text-align: left;padding-left: 23px; width: 150px;">
                                                            {{$t('名称')}}
                                                        </th>
                                                        <th style="width: 150px;">{{$t('所属namespace')}}</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <template v-if="taskGroup[key].container_list.length">
                                                        <tr v-for="(container, containerIndex) in taskGroup[key].container_list" :key="containerIndex">
                                                            <td>
                                                                <bk-tooltip placement="top">
                                                                    <span class="name" style="margin-left: 13px;">
                                                                        {{container.name}}
                                                                    </span>
                                                                    <template slot="content">
                                                                        <p style="text-align: left; white-space: normal;word-break: break-all;font-weight: 400;">{{container.name}}</p>
                                                                    </template>
                                                                </bk-tooltip>
                                                            </td>
                                                            <td>{{taskGroup[key].namespace}}</td>
                                                        </tr>
                                                    </template>
                                                    <template v-else>
                                                        <tr>
                                                            <td colspan="4">
                                                                <div class="bk-message-box">
                                                                    <p class="message empty-message">{{$t('无数据')}}</p>
                                                                </div>
                                                            </td>
                                                        </tr>
                                                    </template>
                                                </tbody>
                                            </table>
                                        </div>
                                    </transition>
                                </div>
                            </div>
                            <div class="biz-app-instance-taskgroup-list" v-else>
                                <div class="bk-message-box">
                                    <p class="message empty-message">{{$t('无数据')}}</p>
                                </div>
                            </div>
                        </bk-tabpanel>
                        <bk-tabpanel name="rule" :title="$t('调度约束规则')">
                            <table class="bk-table has-table-hover biz-table biz-rule-table" style="border-bottom: none;">
                                <thead>
                                    <tr>
                                        <th style="width: 200px; padding-left: 35px;">Field</th>
                                        <th style="width: 250px;">Operator</th>
                                        <th>value</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(constraint, index) in loadBalanceDetail.constraints" :key="index">
                                        <td style="padding-left: 35px;">{{constraint.unionData[0].name}}</td>
                                        <td>{{constraint.unionData[0].operate}}</td>
                                        <td>{{constraint.unionData[0].arg_value}}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </bk-tabpanel>
                    </bk-tab>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
    import chartOptions from '../../chart_options.js'
    import chartData from '../../chart_data.json'
    import ECharts from 'vue-echarts/components/ECharts.vue'
    import { catchErrorHandler } from '@open/common/util'
    import 'echarts/lib/chart/line'
    import 'echarts/lib/component/tooltip'
    import 'echarts/lib/component/legend'

    export default {
        components: {
            chart: ECharts
        },
        data () {
            return {
                isDataLoading: true,
                exceptionCode: null,
                tabActiveName: 'taskgroup',
                isDropdownShow: false,
                chartOptions: chartOptions,
                loadBalanceDetail: null,
                taskGroup: null
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            loadBalanceId () {
                return this.$route.params.lbId
            },
            clusterIdForLoadBalance () {
                return this.$route.params.clusterId
            },
            namespaceForLoadBalance () {
                return this.$route.params.namespace
            },
            curProject () {
                return this.$store.state.curProject
            },
            curLoadBalance () {
                const loadBalanceId = this.loadBalanceId
                const loadBalanceList = this.$store.state.network.loadBalanceList
                const result = loadBalanceList.find(lb => {
                    return lb.id === loadBalanceId
                })
                return result
            }
        },
        created () {
            this.initLoadBalanceTaskGroup()
            this.initLoadBalanceDetail()
        },
        methods: {
            /**
             * 返回LB列表
             */
            goLoadBalanceList () {
                this.$router.push({
                    name: 'loadBalance',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
            },

            /**
             * 生成一定范围随机数
             * @param  {number} min 最大值
             * @param  {number} max 最小值
             */
            randomInt (min, max) {
                return Math.floor(Math.random() * (max - min + 1) + min)
            },

            /**
             * 渲染图表
             */
            renderChart () {
                const data = chartData
                const seriesEmpty = []
                const series = []
                const seriesLen = data.length
                const ref = this.$refs.instance
                const colors = ['#51a1ff', '#ffbf24']

                for (let i = 0; i < seriesLen; i++) {
                    const chartData = []
                    const emptyData = []
                    data[i].metrics.forEach(metric => {
                        chartData.push({
                            value: [metric.time, metric.usage]
                        })
                        emptyData.push(0)
                    })
                    series.push({
                        type: 'line',
                        name: data[i].container_name,
                        showSymbol: false,
                        hoverAnimation: false,
                        lineStyle: {
                            normal: {
                                color: colors[i],
                                opacity: this.randomInt(7, 10) / 10
                            }
                        },
                        data: chartData
                    })
                    seriesEmpty.push({
                        type: 'line',
                        name: data[i].container_name,
                        showSymbol: false,
                        hoverAnimation: false,
                        data: emptyData
                    })
                }

                ref.mergeOptions({
                    series: seriesEmpty
                })
                ref.mergeOptions({
                    series: series
                })
            },

            /**
             * 初始化LB taskGroup
             */
            async initLoadBalanceTaskGroup () {
                const projectId = this.projectId
                const loadBalanceId = this.loadBalanceId
                const projectKind = this.curProject.kind
                try {
                    const res = await this.$store.dispatch('network/getTaskGroup', { projectId, loadBalanceId, projectKind })
                    if (res.data) {
                        Object.keys(res.data).forEach(key => {
                            res.data[key].isOpen = false
                        })
                    }
                    this.taskGroup = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 初始化LB 详情
             */
            async initLoadBalanceDetail () {
                const projectId = this.projectId
                const loadBalanceId = this.loadBalanceId
                const clusterId = this.clusterIdForLoadBalance
                const namespace = this.namespaceForLoadBalance
                this.isDataLoading = true
                try {
                    const res = await this.$store.dispatch('network/getMesosLoadBalanceDetail', { projectId, loadBalanceId, clusterId, namespace })
                    const data = {
                        ...res.data,
                        ...res.data.data
                    }
                    this.loadBalanceDetail = data
                    this.$nextTick(() => {
                        this.renderChart()
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataLoading = false
                }
            },

            /**
             * 展示/折叠TaskGroup
             * @param  {object} item TaskGroup
             */
            toggleTaskGroup (item) {
                item.isOpen = !item.isOpen
                this.taskGroup = JSON.parse(JSON.stringify(this.taskGroup))
            }
        }
    }
</script>

<style scoped>
    @import './detail.css';
</style>
