<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-app-instance-title">
                <i class="bk-icon icon-arrows-left back" @click="goNodeOverview"></i>
                <span @click="refreshCurRouter">{{containerInfo.container_name || '--'}}</span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper biz-app-instance">
            <app-exception v-if="exceptionCode" :type="exceptionCode.code" :text="exceptionCode.msg"></app-exception>
            <div v-else class="biz-app-instance-wrapper">
                <div class="biz-app-instance-header">
                    <div class="header-item">
                        <div class="key-label">主机名称：</div>
                        <bk-tooltip :delay="500" placement="bottom-start">
                            <div class="value-label">{{containerInfo.host_name || '--'}}</div>
                            <template slot="content">
                                <p style="text-align: left; white-space: normal;word-break: break-all;font-weight: 400;">{{containerInfo.host_name || '--'}}</p>
                            </template>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">主机IP：</div>
                        <bk-tooltip :delay="500" placement="bottom">
                            <div class="value-label">{{containerInfo.host_ip || '--'}}</div>
                            <template slot="content">
                                <p style="text-align: left; white-space: normal;word-break: break-all;font-weight: 400;">{{containerInfo.host_ip || '--'}}</p>
                            </template>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">容器IP：</div>
                        <bk-tooltip :delay="500" placement="bottom">
                            <div class="value-label">{{containerInfo.container_ip || '--'}}</div>
                            <template slot="content">
                                <p style="text-align: left; white-space: normal;word-break: break-all;font-weight: 400;">{{containerInfo.container_ip || '--'}}</p>
                            </template>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">容器ID：</div>
                        <bk-tooltip :delay="500" placement="bottom">
                            <div class="value-label">{{containerInfo.container_id || '--'}}</div>
                            <template slot="content">
                                <p style="text-align: left; white-space: normal;word-break: break-all;font-weight: 400;">{{containerInfo.container_id || '--'}}</p>
                            </template>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">镜像：</div>
                        <bk-tooltip :delay="500" placement="bottom">
                            <div class="value-label">{{containerInfo.image || '--'}}</div>
                            <template slot="content">
                                <p style="text-align: left; white-space: normal;word-break: break-all;font-weight: 400;">{{containerInfo.image || '--'}}</p>
                            </template>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">网络模式：</div>
                        <bk-tooltip :delay="500" placement="bottom">
                            <div class="value-label">{{containerInfo.network_mode || '--'}}</div>
                            <template slot="content">
                                <p style="text-align: left; white-space: normal;word-break: break-all;font-weight: 400;">{{containerInfo.network_mode || '--'}}</p>
                            </template>
                        </bk-tooltip>
                    </div>
                </div>
                <div class="biz-app-instance-chart-wrapper">
                    <div class="biz-app-instance-chart">
                        <div class="part top-left">
                            <div class="info">
                                <div class="left">CPU使用率</div>
                            </div>
                            <chart :options="cpuLine" ref="containerCpuLine" auto-resize></chart>
                        </div>
                        <div class="part top-right">
                            <div class="info">
                                <div class="left">内存</div>
                            </div>
                            <chart :options="memLine" ref="containerMemLine" auto-resize></chart>
                        </div>
                    </div>
                    <div class="biz-app-instance-chart">
                        <div class="part bottom-left">
                            <div class="info">
                                <div class="left">网络</div>
                            </div>
                            <chart :options="netLine" ref="containerNetLine" auto-resize></chart>
                        </div>
                        <div class="part">
                            <div class="info">
                                <div class="left">磁盘IO</div>
                            </div>
                            <chart :options="diskLine" ref="containerDiskLine" auto-resize></chart>
                        </div>
                    </div>
                </div>
                <div class="biz-app-container-table-wrapper">
                    <bk-tab :type="'fill'" :active-name="tabActiveName" @tab-changed="tabChanged">
                        <bk-tabpanel name="ports" title="端口映射">
                            <table class="bk-table has-table-hover biz-table biz-app-container-ports-table">
                                <thead>
                                    <tr>
                                        <th style="text-align: left;padding-left: 27px; width: 300px">
                                            Name
                                        </th>
                                        <th style="width: 150px">Host Port</th>
                                        <th style="width: 150px">Container Port</th>
                                        <th style="width: 100px">Protocol</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-if="portList.length">
                                        <tr v-for="(port, index) in portList" :key="index">
                                            <td style="text-align: left;padding-left: 27px;">
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="port-name">{{port.name}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{port.name}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                            <td>{{port.hostPort}}</td>
                                            <td>{{port.containerPort}}</td>
                                            <td>
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="port-protocol">{{port.protocol}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{port.protocol}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                        </tr>
                                    </template>
                                    <template v-else>
                                        <tr>
                                            <td colspan="4">
                                                <div class="bk-message-box no-data">
                                                    <p class="message empty-message">该应用的网络模式无需端口映射</p>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </bk-tabpanel>
                        <bk-tabpanel name="commands" title="命令">
                            <table class="bk-table has-table-hover biz-table biz-app-container-commands-table">
                                <thead>
                                    <tr>
                                        <th style="text-align: left;padding-left: 27px; width: 300px">
                                            Command
                                        </th>
                                        <th style="width: 200px">Args</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-if="commandList.length">
                                        <tr v-for="(command, index) in commandList" :key="index">
                                            <td style="text-align: left;padding-left: 27px;">
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="command-name">{{command.command}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{command.command}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="command-args">{{command.args}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{command.args}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                        </tr>
                                    </template>
                                    <template v-else>
                                        <tr>
                                            <td colspan="2">
                                                <div class="bk-message-box no-data">
                                                    <p class="message empty-message">无数据</p>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </bk-tabpanel>
                        <bk-tabpanel name="volumes" title="挂载卷">
                            <table class="bk-table has-table-hover biz-table biz-app-container-volumes-table">
                                <thead>
                                    <tr>
                                        <th style="text-align: left;padding-left: 27px; width: 250px">
                                            Host Path
                                        </th>
                                        <th style="width: 250px">Mount Path</th>
                                        <th style="width: 140px">ReadOnly</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-if="volumeList.length">
                                        <tr v-for="(volume, index) in volumeList" :key="index">
                                            <td style="text-align: left;padding-left: 27px;">
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="volume-host">{{volume.hostPath}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{volume.hostPath}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="volume-mount">{{volume.mountPath}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{volume.mountPath}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                            <td>{{volume.readOnly}}</td>
                                        </tr>
                                    </template>
                                    <template v-else>
                                        <tr>
                                            <td colspan="3">
                                                <div class="bk-message-box no-data">
                                                    <p class="message empty-message">无数据</p>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </bk-tabpanel>
                        <bk-tabpanel name="env_args" title="环境变量">
                            <table class="bk-table has-table-hover biz-table biz-app-container-env-table">
                                <thead>
                                    <tr>
                                        <th style="text-align: left;padding-left: 27px; width: 150px">
                                            Key
                                        </th>
                                        <th style="width: 350px">Value</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-if="envList.length">
                                        <tr v-for="(env, index) in envList" :key="index">
                                            <td style="text-align: left;padding-left: 27px;">
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="env-key">{{env.key}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{env.key}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="env-value">{{env.value}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{env.value}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                        </tr>
                                    </template>
                                    <template v-else>
                                        <tr>
                                            <td colspan="2">
                                                <div class="bk-message-box no-data">
                                                    <p class="message empty-message">无数据</p>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </bk-tabpanel>
                        <bk-tabpanel name="health_check" title="健康检查">
                            <table class="bk-table has-table-hover biz-table biz-app-container-health-table">
                                <thead>
                                    <tr>
                                        <th style="text-align: left;padding-left: 27px; width: 150px">
                                            Type
                                        </th>
                                        <th style="width: 140px">Result</th>
                                        <th style="width: 350px">Message</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-if="healthList.length">
                                        <tr v-for="(health, index) in healthList" :key="index">
                                            <td style="text-align: left;padding-left: 27px;">
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="health-type">{{health.type}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{health.type}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                            <td>{{health.result}}</td>
                                            <td>
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="health-message">{{health.message}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{health.message}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                        </tr>
                                    </template>
                                    <template v-else>
                                        <tr>
                                            <td colspan="3">
                                                <div class="bk-message-box no-data">
                                                    <p class="message empty-message">无数据</p>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </bk-tabpanel>
                        <bk-tabpanel name="labels" title="标签">
                            <table class="bk-table has-table-hover biz-table biz-app-container-label-table">
                                <thead>
                                    <tr>
                                        <th style="text-align: left;padding-left: 27px; width: 150px">
                                            Key
                                        </th>
                                        <th style="width: 350px">Value</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-if="labelList.length">
                                        <tr v-for="(label, index) in labelList" :key="index">
                                            <td style="text-align: left;padding-left: 27px;">
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="label-key">{{label.key}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{label.key}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="label-value">{{label.val}}</p>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">{{label.val}}</p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                        </tr>
                                    </template>
                                    <template v-else>
                                        <tr>
                                            <td colspan="2">
                                                <div class="bk-message-box no-data">
                                                    <p class="message empty-message">无数据</p>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </bk-tabpanel>
                        <bk-tabpanel name="resources" title="资源限制">
                            <table class="bk-table has-table-hover biz-table biz-app-container-resource-table">
                                <thead>
                                    <tr>
                                        <th style="text-align: left;padding-left: 27px; width: 150px">
                                            Cpu
                                        </th>
                                        <th style="width: 350px">Memory</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-if="resourceList.length">
                                        <tr v-for="(resource, index) in resourceList" :key="index">
                                            <td style="text-align: left;padding-left: 27px;">
                                                <p class="resource-cpu">{{parseFloat(resource.cpu)}}</p>
                                            </td>
                                            <td>
                                                <p class="resource-mem">{{parseFloat(resource.memory)}}</p>
                                            </td>
                                        </tr>
                                    </template>
                                    <template v-else>
                                        <tr>
                                            <td colspan="2">
                                                <div class="bk-message-box no-data">
                                                    <p class="message empty-message">无数据</p>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </bk-tabpanel>
                    </bk-tab>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
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
                bkMessageInstance: null,
                exceptionCode: null,
                curProject: null,
                projectIdTimer: null
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
            containerId () {
                return this.$route.params.containerId
            },
            nodeId () {
                return this.$route.params.nodeId
            }
        },
        async mounted () {
            await this.fetchContainerInfo()
            this.fetchContainerMetricsCpu()
            this.fetchContainerMetricsMem()
            this.fetchContainerMetricsNet()
            this.fetchContainerMetricsDisk()
        },
        destroyed () {
            this.bkMessageInstance && this.bkMessageInstance.close()
        },
        methods: {
            /**
             * 获取容器详情信息，上方数据和下方
             */
            async fetchContainerInfo () {
                try {
                    const res = await this.$store.dispatch('cluster/getContainerInfo', {
                        projectId: this.projectId,
                        clusterId: this.clusterId,
                        containerId: this.containerId
                    })
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

                    const envList = []
                    const envArgs = this.containerInfo.env_args || {}
                    Object.keys(envArgs).forEach(key => {
                        envList.push({
                            key: key,
                            value: envArgs[key]
                        })
                    })
                    this.envList.splice(0, this.envList.length, ...envList)

                    const healthList = this.containerInfo.health_check || []
                    this.healthList.splice(0, this.healthList.length, ...healthList)

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
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取 cpu 图表数据
             */
            async fetchContainerMetricsCpu () {
                const ref = this.$refs.containerCpuLine
                try {
                    ref && ref.showLoading({
                        text: '正在加载',
                        color: '#30d878',
                        maskColor: 'rgba(255, 255, 255, 0.8)'
                    })

                    const res = await this.$store.dispatch('app/getContainerMetrics', {
                        projectId: this.projectId,
                        containerId: this.containerId,
                        metric: 'cpu_summary'
                    })

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
                // 先设置 emptyData，再切换数据，这样的话，图表是从中间往两边展开，效果会好一些
                ref.mergeOptions({
                    series: [
                        {
                            // name: data[0].container_name,
                            name: this.containerInfo.container_name,
                            data: emptyData
                        }
                    ]
                })
                ref.mergeOptions({
                    series: [
                        {
                            // name: data[0].container_name,
                            name: this.containerInfo.container_name,
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
                    ref && ref.showLoading({
                        text: '正在加载',
                        color: '#30d878',
                        maskColor: 'rgba(255, 255, 255, 0.8)'
                    })

                    const res = await this.$store.dispatch('app/getContainerMetrics', {
                        projectId: this.projectId,
                        containerId: this.containerId,
                        metric: 'mem'
                    })

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
                data.forEach(item => {
                    chartData.push({
                        value: [item.time, item.used]
                    })
                    emptyData.push(0)
                })
                if (!ref) {
                    return
                }

                // 先设置 emptyData，再切换数据，这样的话，图表是从中间往两边展开，效果会好一些
                ref.mergeOptions({
                    series: [
                        {
                            // name: data[0].container_name,
                            name: this.containerInfo.container_name,
                            data: emptyData
                        }
                    ]
                })
                ref.mergeOptions({
                    series: [
                        {
                            // name: data[0].container_name,
                            name: this.containerInfo.container_name,
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
                    ref && ref.showLoading({
                        text: '正在加载',
                        color: '#30d878',
                        maskColor: 'rgba(255, 255, 255, 0.8)'
                    })

                    const res = await this.$store.dispatch('app/getContainerMetrics', {
                        projectId: this.projectId,
                        containerId: this.containerId,
                        metric: 'net'
                    })

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

                // 每秒发送的字节数
                const txbyteData = []

                // 每秒接收的字节数
                const rxbyteData = []

                data.forEach(item => {
                    txbyteData.push({
                        value: [
                            item.time,
                            item.txbytes,
                            'tx',
                            data[0].container_name === 'noData'
                                ? data[0].container_name : this.containerInfo.container_name
                        ]
                    })
                    rxbyteData.push({
                        value: [
                            item.time,
                            item.rxbytes,
                            'rx',
                            data[0].container_name === 'noData'
                                ? data[0].container_name : this.containerInfo.container_name
                        ]
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
                    ref && ref.showLoading({
                        text: '正在加载',
                        color: '#30d878',
                        maskColor: 'rgba(255, 255, 255, 0.8)'
                    })

                    const res = await this.$store.dispatch('app/getContainerMetrics', {
                        projectId: this.projectId,
                        containerId: this.containerId,
                        metric: 'disk'
                    })

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
                    // charOpts.legend.data.push(item.device_name)
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
             * 刷新当前 router
             */
            refreshCurRouter () {
                typeof this.$parent.refreshRouterView === 'function' && this.$parent.refreshRouterView()
            },

            /**
             * 返回 node overview
             */
            goNodeOverview () {
                this.$router.push({
                    name: 'clusterNodeOverview',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        clusterId: this.clusterId,
                        nodeId: this.nodeId
                    }
                })
            },

            /**
             * 选项卡切换事件
             *
             * @param {string} name 选项卡标识
             */
            tabChanged (name) {
                if (this.tabActiveName === name) {
                    return
                }
                this.tabActiveName = name
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '../../css/variable.css';
    @import '../../css/mixins/ellipsis.css';

    .biz-app-instance {
        padding: 20px;
    }

    .biz-app-instance-title {
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
            color: $iconPrimaryColor;
        }
    }

    .biz-app-instance-wrapper {
        background-color: $bgHoverColor;
        display: inline-block;
        width: 100%;
    }

    .biz-app-instance-header {
        display: flex;
        border: 1px solid $borderWeightColor;
        border-radius: 2px;

        .header-item {
            font-size: 14px;
            flex: 1;
            height: 75px;
            border-right: 1px solid $borderWeightColor;
            padding-left: 20px;

            &:last-child {
                border-right: none;
            }

            .key-label {
                font-weight: 700;
                padding-top: 13px;
                padding-bottom: 5px;
            }

            .value-label {
                @mixin ellipsis 180px;
                padding-top: 4px;
            }
        }
    }

    .biz-app-instance-chart-wrapper {
        margin-top: 20px;
        background-color: #fff;
        box-shadow: 1px 0 2px rgba(0, 0, 0, 0.1);
        border: 1px solid $borderWeightColor;
        font-size: 0;
        border-radius: 2px;

        .biz-app-instance-chart {
            display: inline-block;
            width: 100%;

            .part {
                width: 50%;
                float: left;
                height: 250px;

                &.top-left {
                    border-right: 1px solid $borderWeightColor;
                    border-bottom: 1px solid $borderWeightColor;
                }

                &.top-right {
                    border-bottom: 1px solid $borderWeightColor;
                }

                &.bottom-left {
                    border-right: 1px solid $borderWeightColor;
                }

                .info {
                    font-size: 14px;
                    display: flex;
                    padding: 20px 30px;

                    .left,
                    .right {
                        flex: 1;
                    }

                    .left {
                        font-weight: 700;
                    }

                    .right {
                        text-align: right;
                    }
                }

                .right {

                    .system,
                    .user {
                        display: inline-block;
                        font-size: 14px;

                        .circle {
                            display: inline-block;
                            width: 14px;
                            height: 14px;
                            border-radius: 50%;
                            position: relative;
                            top: 2px;
                        }
                    }

                    .system {
                        .circle {
                            border: 3px solid #3c96ff;
                        }
                    }

                    .user {
                        margin-left: 30px;

                        .circle {
                            border: 3px solid #30d873;
                        }
                    }
                }
            }
        }
    }

    .echarts {
        width: 100%;
        height: 180px;
    }

    .biz-app-container-table-wrapper {
        margin-top: 20px;
    }

    .biz-app-container-ports-table,
    .biz-app-container-commands-table,
    .biz-app-container-volumes-table,
    .biz-app-container-health-table,
    .biz-app-container-env-table,
    .biz-app-container-label-table,
    .biz-app-container-resource-table {
        border-bottom: none;

        .no-data {
            min-height: 180px;

            .empty-message {
                margin-top: 50px;
            }
        }
    }

    .biz-app-container-ports-table {
        .port-name {
            @mixin ellipsis 300px;
        }

        .port-protocol {
            @mixin ellipsis 100px;
        }
    }

    .biz-app-container-commands-table {
        .command-name {
            @mixin ellipsis 300px;
        }

        .command-args {
            @mixin ellipsis 200px;
        }
    }

    .biz-app-container-volumes-table {
        .volume-host {
            @mixin ellipsis 250px;
        }

        .volume-mount {
            @mixin ellipsis 250px;
        }
    }

    .biz-app-container-health-table {
        .health-type {
            @mixin ellipsis 150px;
        }

        .health-message {
            @mixin ellipsis 350px;
        }
    }

    @media screen and (max-width: $mediaWidth) {
        .biz-app-instance-header {
            .header-item {
                div {
                    &:last-child {
                        width: 120px;
                    }
                }
            }
        }
    }

</style>
