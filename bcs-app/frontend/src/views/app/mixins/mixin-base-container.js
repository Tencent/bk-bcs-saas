/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import ECharts from 'vue-echarts/components/ECharts.vue'
import 'echarts/lib/chart/line'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/legend'

import { containerDetailChart } from '@open/common/chart-option'
import { catchErrorHandler } from '@open/common/util'

export default {
    components: {
        chart: ECharts
    },
    data () {
        return {
            containerInfo: {},
            cpuLine: containerDetailChart.cpu,
            memLine: containerDetailChart.mem,
            netLine: containerDetailChart.net,
            diskLine: containerDetailChart.disk,
            tabActiveName: 'ports',
            portList: [],
            commandList: [],
            volumeList: [],
            envList: [],
            healthList: [],
            labelList: [],
            resourceList: [],
            contentLoading: false,
            bkMessageInstance: null,
            exceptionCode: null,
            envTabLoading: true
        }
    },
    computed: {
        projectId () {
            return this.$route.params.projectId
        },
        projectCode () {
            return this.$route.params.projectCode
        },
        instanceId () {
            const instanceId = this.$route.params.instanceId === undefined
                ? 0
                : this.$route.params.instanceId
            return instanceId
        },
        taskgroupName () {
            return this.$route.params.taskgroupName
        },
        namespaceId () {
            return this.$route.params.namespaceId
        },
        containerId () {
            return this.$route.params.containerId
        },
        instanceName () {
            return this.$route.params.instanceName
        },
        instanceNamespace () {
            return this.$route.params.instanceNamespace
        },
        instanceCategory () {
            return this.$route.params.instanceCategory
        },
        searchParamsList () {
            return this.$route.params.searchParamsList
        },
        clusterId () {
            return this.$route.query.cluster_id || ''
        }
    },
    mounted () {
        this.fetchContainerInfo()
    },
    destroyed () {
        this.bkMessageInstance && this.bkMessageInstance.close()
    },
    methods: {
        /**
         * 获取容器详情信息，上方数据和下方
         */
        async fetchContainerInfo () {
            this.contentLoading = true
            try {
                let url = ''
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId,
                    taskgroupName: this.taskgroupName,
                    containerId: this.containerId,
                    cluster_id: this.clusterId
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                // k8s
                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                    url = 'app/getContainerInfoK8s'
                } else {
                    url = 'app/getContainerInfoMesos'
                }

                const res = await this.$store.dispatch(url, params)
                this.containerInfo = Object.assign({}, res.data || {})

                const portList = this.containerInfo.ports || []
                this.portList.splice(0, this.portList.length, ...portList)

                const commandList = []
                const commands = this.containerInfo.commands || {}
                if (commands.command || commands.args) {
                    commandList.push(this.containerInfo.commands)
                }
                this.commandList.splice(0, this.commandList.length, ...commandList)

                const volumeList = this.containerInfo.volumes || []
                this.volumeList.splice(0, this.volumeList.length, ...volumeList)

                const envList = this.containerInfo.env_args || []
                this.envList.splice(0, this.envList.length, ...envList)

                // mesos，k8s 先隐藏健康检查
                if (!this.CATEGORY) {
                    const healthList = this.containerInfo.health_check || []
                    this.healthList.splice(0, this.healthList.length, ...healthList)
                }

                const labelList = this.containerInfo.labels || []
                this.labelList.splice(0, this.labelList.length, ...labelList)

                const resourceList = []
                const resources = this.containerInfo.resources || {}
                const limits = resources.limits || {}
                if (limits.cpu || limits.memory) {
                    resourceList.push({
                        cpu: limits.cpu,
                        memory: limits.memory
                    })
                }
                this.resourceList.splice(0, this.resourceList.length, ...resourceList)

                this.$refs.containerCpuLine && this.$refs.containerCpuLine.showLoading({
                    text: '正在加载',
                    color: '#30d878',
                    maskColor: 'rgba(255, 255, 255, 0.8)'
                })
                this.$refs.containerMemLine && this.$refs.containerMemLine.showLoading({
                    text: '正在加载',
                    color: '#30d878',
                    maskColor: 'rgba(255, 255, 255, 0.8)'
                })
                this.$refs.containerNetLine && this.$refs.containerNetLine.showLoading({
                    text: '正在加载',
                    color: '#30d878',
                    maskColor: 'rgba(255, 255, 255, 0.8)'
                })
                this.$refs.containerDiskLine && this.$refs.containerDiskLine.showLoading({
                    text: '正在加载',
                    color: '#30d878',
                    maskColor: 'rgba(255, 255, 255, 0.8)'
                })
                this.fetchContainerMetricsCpu()
                this.fetchContainerMetricsMem()
                this.fetchContainerMetricsNet()
                this.fetchContainerMetricsDisk()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.contentLoading = false
            }
        },

        /**
         * 获取 cpu 图表数据
         */
        async fetchContainerMetricsCpu () {
            const ref = this.$refs.containerCpuLine
            try {
                const params = {
                    projectId: this.projectId,
                    containerId: this.containerId,
                    metric: 'cpu_summary',
                    cluster_id: this.clusterId
                }
                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getContainerMetrics', params)

                setTimeout(() => {
                    this.setCpuData(
                        res.data.list && res.data.list.length
                            ? res.data.list
                            : [
                                {
                                    container_name: 'noData', usage: 0, time: new Date().getTime()
                                }
                            ]
                    )
                }, 0)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                ref && ref.hideLoading()
            }
        },

        /**
         * 设置 cpu 图表数据
         *
         * @param {Array} data 数据
         */
        setCpuData (data) {
            const chartData = []
            const emptyData = []
            const ref = this.$refs.containerCpuLine
            if (!ref) {
                return
            }

            data.forEach(item => {
                chartData.push({
                    value: [item.time, item.usage]
                })
                emptyData.push(0)
            })

            const name = this.containerInfo.container_name || data[0].container_name

            // 先设置 emptyData，再切换数据，这样的话，图表是从中间往两边展开，效果会好一些
            ref.mergeOptions({
                series: [
                    {
                        name: name,
                        data: emptyData
                    }
                ]
            })
            ref.mergeOptions({
                series: [
                    {
                        name: name,
                        data: chartData
                    }
                ]
            })
            ref.hideLoading()
        },

        /**
         * 获取 mem 图表数据
         *
         * @param {string} metric 标识是 cpu 还是内存图表
         */
        async fetchContainerMetricsMem (metric) {
            const ref = this.$refs.containerMemLine
            try {
                const params = {
                    projectId: this.projectId,
                    containerId: this.containerId,
                    metric: 'mem',
                    cluster_id: this.clusterId
                }
                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getContainerMetrics', params)

                setTimeout(() => {
                    this.setMemData(
                        res.data.list && res.data.list.length
                            ? res.data.list
                            : [
                                {
                                    container_name: 'noData', used: 0, time: new Date().getTime()
                                }
                            ]
                    )
                }, 0)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                ref && ref.hideLoading()
            }
        },

        /**
         * 设置 mem 图表数据，非内部版
         *
         * @param {Array} data 数据
         */
        setMemData (data) {
            const chartData = []
            const emptyData = []
            const ref = this.$refs.containerMemLine
            if (!ref) {
                return
            }

            data.forEach(item => {
                chartData.push({
                    value: [item.time, item.used]
                })
                emptyData.push(0)
            })

            const name = this.containerInfo.container_name || data[0].container_name

            // 先设置 emptyData，再切换数据，这样的话，图表是从中间往两边展开，效果会好一些
            ref.mergeOptions({
                series: [
                    {
                        name: name,
                        data: emptyData
                    }
                ]
            })
            ref.mergeOptions({
                series: [
                    {
                        name: name,
                        data: chartData
                    }
                ]
            })
            ref.hideLoading()
        },

        /**
         * 获取 net 图表数据
         *
         * @param {string} metric 标识是 cpu 还是内存图表
         */
        async fetchContainerMetricsNet (metric) {
            const ref = this.$refs.containerNetLine
            try {
                const params = {
                    projectId: this.projectId,
                    containerId: this.containerId,
                    metric: 'net',
                    cluster_id: this.clusterId
                }
                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getContainerMetrics', params)

                setTimeout(() => {
                    this.setNetData(
                        res.data.list && res.data.list.length
                            ? res.data.list
                            : [
                                {
                                    container_name: 'noData', txbytes: 0, rxbytes: 0, time: new Date().getTime()
                                }
                            ]
                    )
                }, 0)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                ref && ref.hideLoading()
            }
        },

        /**
         * 设置 net 图表数据
         *
         * @param {Array} data 数据
         */
        setNetData (data) {
            const emptyData = []
            const ref = this.$refs.containerNetLine
            if (!ref) {
                return
            }

            const charOpts = {
                legend: {
                    data: []
                },
                series: []
            }

            const name = this.containerInfo.container_name || data[0].container_name

            // 每秒发送的字节数
            const txbyteData = []

            // 每秒接收的字节数
            const rxbyteData = []

            data.forEach(item => {
                txbyteData.push({
                    value: [item.time, item.txbytes, 'tx', name]
                })
                rxbyteData.push({
                    value: [item.time, item.rxbytes, 'rx', name]
                })
                emptyData.push(0)
            })

            charOpts.legend.data.push('发送')
            charOpts.legend.data.push('接收')

            charOpts.series.push(
                {
                    type: 'line',
                    name: '发送',
                    data: txbyteData
                },
                {
                    type: 'line',
                    name: '接收',
                    data: rxbyteData
                }
            )

            // 先设置 emptyData，再切换数据，这样的话，图表是从中间往两边展开，效果会好一些
            ref.mergeOptions({
                series: [
                    {
                        data: emptyData
                    },
                    {
                        data: emptyData
                    }
                ]
            })

            ref.mergeOptions(charOpts)
            ref.hideLoading()
        },

        /**
         * 获取 disk 图表数据
         *
         * @param {string} metric 标识是 cpu 还是内存图表
         */
        async fetchContainerMetricsDisk (metric) {
            const ref = this.$refs.containerDiskLine
            try {
                const params = {
                    projectId: this.projectId,
                    containerId: this.containerId,
                    metric: 'disk',
                    cluster_id: this.clusterId
                }
                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getContainerMetrics', params)

                setTimeout(() => {
                    this.setDiskData(
                        res.data.list && res.data.list.length
                            ? res.data.list
                            : [
                                {
                                    device_name: 'noData',
                                    metrics: [{
                                        used_pct: 0,
                                        container_name: 'noData',
                                        read_bytes: 0,
                                        write_bytes: 0,
                                        time: new Date().getTime()
                                    }]
                                }
                            ]
                    )
                }, 0)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                ref && ref.hideLoading()
            }
        },

        /**
         * 设置 disk 图表数据，非内部版
         *
         * @param {Array} data 数据
         */
        setDiskData (data) {
            const emptyData = []
            const ref = this.$refs.containerDiskLine
            if (!ref) {
                return
            }

            const charOpts = {
                legend: {
                    data: []
                },
                series: []
            }

            data.forEach(item => {
                const metrics = item.metrics
                const chartData = []
                metrics.forEach(metric => {
                    chartData.push({
                        value: [metric.time, metric.read_bytes, metric.write_bytes, metric.container_name]
                    })
                    emptyData.push(0)
                })

                charOpts.series.push(
                    {
                        type: 'line',
                        name: item.device_name,
                        data: chartData
                    }
                )
            })

            // 先设置 emptyData，再切换数据，这样的话，图表是从中间往两边展开，效果会好一些
            ref.mergeOptions({
                series: [
                    {
                        data: emptyData
                    }
                ]
            })
            ref.mergeOptions(charOpts)
            ref.hideLoading()
        },

        /**
         * 选项卡切换事件
         *
         * @param {string} name 选项卡标识
         */
        async tabChanged (name) {
            if (this.tabActiveName === name) {
                return
            }
            this.tabActiveName = name
            if (this.CATEGORY) {
                try {
                    this.envTabLoading = true
                    const params = {
                        projectId: this.projectId,
                        instanceId: this.instanceId,
                        taskgroupName: this.taskgroupName,
                        containerId: this.containerId,
                        cluster_id: this.clusterId
                    }

                    if (String(this.instanceId) === '0') {
                        params.name = this.instanceName
                        params.namespace = this.instanceNamespace
                        params.category = this.instanceCategory
                    }

                    // k8s
                    if (this.CATEGORY) {
                        params.category = this.CATEGORY
                    }

                    const res = await this.$store.dispatch('app/getEnvInfo', params)
                    const envList = []
                    envList.splice(0, 0, ...(res.data || []))
                    this.envList.splice(0, this.envList.length, ...envList)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.envTabLoading = false
                }
            }
        }
    }
}
