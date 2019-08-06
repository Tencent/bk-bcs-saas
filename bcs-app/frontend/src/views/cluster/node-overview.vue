<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-cluster-node-overview-title">
                <i class="bk-icon icon-arrows-left back" @click="goNode"></i>
                <span @click="refreshCurRouter">{{nodeId}}</span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper biz-cluster-node-overview">
            <app-exception
                v-if="exceptionCode"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>
            <div v-else class="biz-cluster-node-overview-wrapper">
                <div class="biz-cluster-node-overview-header">
                    <div class="header-item">
                        <div class="key-label">IP：</div>
                        <bk-tooltip :content="nodeInfo.innerIP" placement="bottom">
                            <div class="value-label">{{nodeInfo.innerIP}}</div>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">CPU：</div>
                        <bk-tooltip :content="nodeInfo.cpu" placement="bottom">
                            <div class="value-label">{{nodeInfo.cpu}}</div>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">内存：</div>
                        <bk-tooltip :content="nodeInfo.mem" placement="bottom">
                            <div class="value-label">{{nodeInfo.mem}}</div>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">存储：</div>
                        <bk-tooltip :content="nodeInfo.disk" placement="bottom">
                            <div class="value-label">{{nodeInfo.disk}}</div>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">IP来源：</div>
                        <bk-tooltip :content="nodeInfo.provider" placement="bottom">
                            <div class="value-label">{{nodeInfo.provider}}</div>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">内核：</div>
                        <bk-tooltip :content="nodeInfo.kernel" placement="bottom">
                            <div class="value-label">{{nodeInfo.kernel}}</div>
                        </bk-tooltip>
                    </div>
                    <div class="header-item">
                        <div class="key-label">操作系统：</div>
                        <bk-tooltip :content="nodeInfo.os" placement="bottom">
                            <div class="value-label">{{nodeInfo.os}}</div>
                        </bk-tooltip>
                    </div>
                </div>
                <div class="biz-cluster-node-overview-chart-wrapper">
                    <div class="biz-cluster-node-overview-chart">
                        <div class="part top-left">
                            <div class="info">
                                <div class="left">CPU</div>
                                <div class="right">
                                    <bk-dropdown-menu :align="'right'" ref="cpuDropdown">
                                        <div style="cursor: pointer;" slot="dropdown-trigger">
                                            <span>{{cpuToggleRangeStr}}</span>
                                            <button class="biz-dropdown-button">
                                                <i class="bk-icon icon-angle-down"></i>
                                            </button>
                                        </div>
                                        <ul class="bk-dropdown-list" slot="dropdown-content">
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('cpuDropdown', 'cpuToggleRangeStr', 'cpu_summary', '1')">1小时</a>
                                            </li>
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('cpuDropdown', 'cpuToggleRangeStr', 'cpu_summary', '2')">24小时</a>
                                            </li>
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('cpuDropdown', 'cpuToggleRangeStr', 'cpu_summary', '3')">近7天</a>
                                            </li>
                                        </ul>
                                    </bk-dropdown-menu>
                                </div>
                            </div>
                            <chart :options="cpuLine" ref="cpuLine1" auto-resize></chart>
                        </div>
                        <div class="part top-right">
                            <div class="info">
                                <div class="left">内存</div>
                                <div class="right">
                                    <bk-dropdown-menu :align="'right'" ref="memoryDropdown">
                                        <div style="cursor: pointer;" slot="dropdown-trigger">
                                            <span>{{memToggleRangeStr}}</span>
                                            <button class="biz-dropdown-button">
                                                <i class="bk-icon icon-angle-down"></i>
                                            </button>
                                        </div>
                                        <ul class="bk-dropdown-list" slot="dropdown-content">
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('memoryDropdown', 'memToggleRangeStr', 'mem', '1')">1小时</a>
                                            </li>
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('memoryDropdown', 'memToggleRangeStr', 'mem', '2')">24小时</a>
                                            </li>
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('memoryDropdown', 'memToggleRangeStr', 'mem', '3')">近7天</a>
                                            </li>
                                        </ul>
                                    </bk-dropdown-menu>
                                </div>
                            </div>
                            <chart :options="memoryLine" ref="memoryLine1" auto-resize></chart>
                        </div>
                    </div>
                    <div class="biz-cluster-node-overview-chart">
                        <div class="part bottom-left">
                            <div class="info">
                                <div class="left">网络</div>
                                <div class="right">
                                    <bk-dropdown-menu :align="'right'" ref="networkDropdown">
                                        <div style="cursor: pointer;" slot="dropdown-trigger">
                                            <span>{{networkToggleRangeStr}}</span>
                                            <button class="biz-dropdown-button">
                                                <i class="bk-icon icon-angle-down"></i>
                                            </button>
                                        </div>
                                        <ul class="bk-dropdown-list" slot="dropdown-content">
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('networkDropdown', 'networkToggleRangeStr', 'net', '1')">1小时</a>
                                            </li>
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('networkDropdown', 'networkToggleRangeStr', 'net', '2')">24小时</a>
                                            </li>
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('networkDropdown', 'networkToggleRangeStr', 'net', '3')">近7天</a>
                                            </li>
                                        </ul>
                                    </bk-dropdown-menu>
                                </div>
                            </div>
                            <chart :options="networkLine" ref="networkLine1" auto-resize></chart>
                        </div>
                        <div class="part">
                            <div class="info">
                                <div class="left">IO</div>
                                <div class="right">
                                    <bk-dropdown-menu :align="'right'" ref="storageDropdown">
                                        <div style="cursor: pointer;" slot="dropdown-trigger">
                                            <span>{{storageToggleRangeStr}}</span>
                                            <button class="biz-dropdown-button">
                                                <i class="bk-icon icon-angle-down"></i>
                                            </button>
                                        </div>
                                        <ul class="bk-dropdown-list" slot="dropdown-content">
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('storageDropdown', 'storageToggleRangeStr', 'io', '1')">1小时</a>
                                            </li>
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('storageDropdown', 'storageToggleRangeStr', 'io', '2')">24小时</a>
                                            </li>
                                            <li>
                                                <a href="javascript:;" @click.stop="toggleRange('storageDropdown', 'storageToggleRangeStr', 'io', '3')">近7天</a>
                                            </li>
                                        </ul>
                                    </bk-dropdown-menu>
                                </div>
                            </div>
                            <chart :options="storageLine" ref="storageLine1" auto-resize></chart>
                        </div>
                    </div>
                </div>
                <div class="biz-cluster-node-overview-table-wrapper">
                    <bk-tab :type="'fill'" :active-name="'container'" @tab-changed="tabChanged">
                        <bk-tabpanel name="container" title="容器">
                            <div class="container-table-wrapper" v-bkloading="{ isLoading: containerTableLoading }">
                                <table class="bk-table has-table-hover biz-table biz-cluster-node-overview-table">
                                    <thead>
                                        <tr>
                                            <th style="padding-left: 20px;">名称</th>
                                            <th>状态</th>
                                            <th>镜像</th>
                                            <template v-if="curProject.kind === PROJECT_K8S">
                                                <th style="min-width: 120px;">操作</th>
                                            </template>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <template v-if="containerTableCurPageData.length">
                                            <tr v-for="(containerTableItem, index) in containerTableCurPageData" :key="index">
                                                <td style="padding-left: 20px;" v-if="curProject.kind === 1 && containerTableItem.status !== 'running'">
                                                    <div class="name">
                                                        <a href="javascript:void(0)" class="bk-text-button is-disabled">{{containerTableItem.name}}</a>
                                                    </div>
                                                </td>
                                                <td style="padding-left: 20px;" v-else>
                                                    <bk-tooltip placement="top" :delay="500" :transfer="true">
                                                        <div class="name">
                                                            <a href="javascript:void(0)" @click="goContainerDetail(containerTableItem)" class="bk-text-button">{{containerTableItem.name}}</a>
                                                        </div>
                                                        <template slot="content">
                                                            <p style="text-align: left; white-space: normal;word-break: break-all;font-weight: 400;">{{containerTableItem.name}}</p>
                                                        </template>
                                                    </bk-tooltip>
                                                </td>
                                                <td v-if="containerTableItem.status === 'terminated'">
                                                    <i class="bk-icon icon-circle-shape danger"></i>terminated
                                                </td>
                                                <td v-else-if="containerTableItem.status === 'running'">
                                                    <i class="bk-icon icon-circle-shape running"></i>running
                                                </td>
                                                <td v-else>
                                                    <i class="bk-icon icon-circle-shape warning"></i>{{containerTableItem.status}}
                                                </td>
                                                <td>
                                                    <bk-tooltip placement="top" :delay="500" :transfer="true">
                                                        <div class="mirror">
                                                            {{containerTableItem.image}}
                                                        </div>
                                                        <template slot="content">
                                                            <p style="text-align: left; white-space: normal; word-break: break-all;font-weight: 400;">{{containerTableItem.image}}</p>
                                                        </template>
                                                    </bk-tooltip>
                                                </td>
                                                <template v-if="curProject.kind === PROJECT_K8S">
                                                    <td>
                                                        <template v-if="containerTableItem.status === 'running'">
                                                            <a href="javascript: void(0);" class="bk-text-button" @click.stop="showTerminal(containerTableItem)">WebConsole</a>
                                                        </template>
                                                        <template v-else>
                                                            <bk-tooltip content="容器状态不是running" placement="right">
                                                                <a href="javascript: void(0);" class="bk-text-button is-disabled">WebConsole</a>
                                                            </bk-tooltip>
                                                        </template>
                                                    </td>
                                                </template>
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
                                <div class="biz-page-box biz-cluster-node-overview-page" v-if="containerTablePageConf.show">
                                    <bk-paging
                                        :size="'small'"
                                        :cur-page.sync="containerTablePageConf.curPage"
                                        :total-page="containerTablePageConf.totalPage"
                                        @page-change="pageChange">
                                    </bk-paging>
                                </div>
                            </div>
                        </bk-tabpanel>
                        <bk-tabpanel name="label" title="标签">
                            <div class="container-table-wrapper" v-bkloading="{ isLoading: labelListLoading }">
                                <table class="bk-table has-table-hover biz-table biz-app-instance-label-table">
                                    <thead>
                                        <tr>
                                            <th style="text-align: left;padding-left: 27px; width: 200px">
                                                键
                                            </th>
                                            <th style="width: 260px">值</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <template v-if="labelList.length">
                                            <tr v-for="(label, index) in labelList" :key="index">
                                                <td style="text-align: left;padding-left: 27px;">
                                                    {{label.key}}
                                                </td>
                                                <td>{{label.val}}</td>
                                            </tr>
                                        </template>
                                        <template v-else>
                                            <tr>
                                                <td colspan="2">
                                                    <div class="bk-message-box no-data">
                                                        <p class="message empty-message" v-if="!labelListLoading">无数据</p>
                                                    </div>
                                                </td>
                                            </tr>
                                        </template>
                                    </tbody>
                                </table>
                            </div>
                        </bk-tabpanel>
                    </bk-tab>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import ECharts from 'vue-echarts/components/ECharts.vue'
    import 'echarts/lib/chart/line'
    import 'echarts/lib/component/tooltip'
    import 'echarts/lib/component/legend'

    import { nodeOverview } from '@open/common/chart-option'
    import { catchErrorHandler } from '@open/common/util'

    export default {
        components: {
            chart: ECharts
        },
        data () {
            return {
                PROJECT_MESOS: PROJECT_MESOS,
                tabActiveName: 'container',
                cpuLine: nodeOverview.cpu,
                memoryLine: nodeOverview.memory,
                networkLine: nodeOverview.network,
                storageLine: nodeOverview.storage,
                bkMessageInstance: null,
                cpuToggleRangeStr: '1小时',
                memToggleRangeStr: '1小时',
                networkToggleRangeStr: '1小时',
                storageToggleRangeStr: '1小时',
                nodeInfo: {},
                containerTableLoading: false,
                containerTableList: [],
                containerTablePageConf: {
                    totalPage: 1,
                    pageSize: 5,
                    curPage: 1,
                    show: false
                },
                containerTableCurPageData: [],
                labelList: [],
                labelListLoading: true,
                exceptionCode: null,
                terminalWins: {}
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
            nodeId () {
                return this.$route.params.nodeId
            },
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            },
            curProject () {
                return this.$store.state.curProject
            }
        },
        created () {
            this.cpuLine.series[0].data
                = this.memoryLine.series[0].data = this.memoryLine.series[1].data
                = this.networkLine.series[0].data = this.networkLine.series[1].data
                = this.storageLine.series[0].data = this.storageLine.series[1].data
                = [0]
            nodeOverview.storage.series[0].data = [9, 0, 22, 40, 12, 31, 2, 12, 18, 27, 27]
        },
        mounted () {
            this.fetchData('cpu_summary', '1')
            this.fetchData('mem', '1')
            this.fetchData('net', '1')
            this.fetchData('io', '1')
            this.fetchNodeInfo()
            this.fetchNodeContainers()
        },
        methods: {
            /**
             * 打开到终端入口
             *
             * @param {Object} container 当前容器
             */
            async showTerminal (container) {
                const clusterId = this.$route.params.clusterId
                const containerId = container.container_id
                const url = `${DEVOPS_BCS_API_URL}/web_console/projects/${this.projectId}/clusters/${clusterId}/?container_id=${containerId}`
                if (this.terminalWins.hasOwnProperty(clusterId)) {
                    const win = this.terminalWins[clusterId]
                    if (!win.closed) {
                        this.terminalWins[clusterId].focus()
                    } else {
                        const win = window.open(url, '', 'width=990,height=618')
                        this.terminalWins[clusterId] = win
                    }
                } else {
                    const win = window.open(url, '', 'width=990,height=618')
                    this.terminalWins[clusterId] = win
                }
            },

            /**
             * 获取上方的信息
             */
            async fetchNodeInfo () {
                const { projectId, clusterId, nodeId } = this
                try {
                    const res = await this.$store.dispatch('cluster/getNodeInfo', {
                        projectId,
                        clusterId,
                        nodeId
                    })

                    const nodeInfo = {}

                    const { InnerIP = '--', Cpu = {}, Memory = {}, Disk = {}, provider = '--', System = {}, id = '' } = res.data

                    nodeInfo.id = id
                    nodeInfo.innerIP = InnerIP
                    nodeInfo.cpu = Cpu.CpuNum || '--'

                    let mem = parseInt(Memory.Total || 0, 10)
                    if (isNaN(mem)) {
                        mem = '--'
                    } else {
                        mem = mem / 1024 / 1024 / 1024
                    }
                    nodeInfo.mem = `${mem.toFixed(2)}GB`

                    let disk = parseInt(Disk.Total || 0, 10)
                    if (isNaN(disk)) {
                        disk = '--'
                    } else {
                        disk = disk / 1024 / 1024 / 1024
                    }
                    nodeInfo.disk = `${disk.toFixed(2)}GB`

                    nodeInfo.provider = provider || '--'
                    nodeInfo.kernel = System.kernelVersion || '--'
                    nodeInfo.docker = System.serverDockerVersion || '--'
                    nodeInfo.os = System.OS || '--'
                    this.nodeInfo = Object.assign({}, nodeInfo)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取下方容器选项卡表格数据
             */
            async fetchNodeContainers () {
                const { projectId, clusterId, nodeId } = this
                this.containerTableLoading = true
                try {
                    const res = await this.$store.dispatch('cluster/getNodeContainerList', {
                        projectId,
                        clusterId,
                        nodeId
                    })
                    this.containerTableList = res.data || []
                    this.initPageConf()
                    this.containerTableCurPageData = this.getDataByPage(this.containerTablePageConf.curPage)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.containerTableLoading = false
                }
            },

            /**
             * 获取下方 tab 标签的数据
             */
            async fetchLabel () {
                this.labelListLoading = true
                try {
                    const res = await this.$store.dispatch('cluster/getNodeLabel', {
                        projectId: this.projectId,
                        nodeIds: [this.nodeInfo.id]
                    })

                    const labelList = []
                    const labels = res.data || {}
                    Object.keys(labels).forEach(key => {
                        labelList.push({
                            key: key,
                            val: labels[key]
                        })
                    })
                    this.labelList.splice(0, this.labelList.length, ...labelList)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.labelListLoading = false
                }
            },

            /**
             * 初始化下方容器选项卡表格翻页条
             */
            initPageConf () {
                const total = this.containerTableList.length
                this.containerTablePageConf.show = total > 0
                this.containerTablePageConf.totalPage = Math.ceil(total / this.containerTablePageConf.pageSize) || 1
            },

            /**
             * 获取当前这一页的数据
             *
             * @param {number} page 当前页
             *
             * @return {Array} 当前页数据
             */
            getDataByPage (page) {
                let startIndex = (page - 1) * this.containerTablePageConf.pageSize
                let endIndex = page * this.containerTablePageConf.pageSize
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.containerTableList.length) {
                    endIndex = this.containerTableList.length
                }
                const data = this.containerTableList.slice(startIndex, endIndex)
                return data
            },

            /**
             * 翻页回调
             *
             * @param {number} page 当前页
             */
            pageChange (page) {
                this.containerTablePageConf.curPage = page
                const data = this.getDataByPage(page)
                this.containerTableCurPageData.splice(0, this.containerTableCurPageData.length, ...data)
            },

            /**
             * 获取中间图表数据
             *
             * @param {string} idx 标识，cpu / memory / network / storage
             * @param {string} range 时间范围，1: 1 小时，2: 24 小时，3：近 7 天
             */
            async fetchData (idx, range) {
                const params = {
                    startAt: null,
                    endAt: moment().format('YYYY-MM-DD HH:mm:ss'),
                    resId: this.nodeId,
                    metric: idx,
                    projectId: this.projectId
                }

                // 1 小时
                if (range === '1') {
                    params.startAt = moment().subtract(1, 'hours').format('YYYY-MM-DD HH:mm:ss')
                } else if (range === '2') { // 24 小时
                    params.startAt = moment().subtract(1, 'days').format('YYYY-MM-DD HH:mm:ss')
                } else if (range === '3') { // 近 7 天
                    params.startAt = moment().subtract(7, 'days').format('YYYY-MM-DD HH:mm:ss')
                }

                // 图表组件 ref
                let ref

                // 设置图表数据的方法名
                let hookFuncName
                if (idx === 'cpu_summary') {
                    ref = this.$refs.cpuLine1
                    hookFuncName = 'setCpuData'
                } else if (idx === 'mem') {
                    ref = this.$refs.memoryLine1
                    hookFuncName = 'setMemData'
                } else if (idx === 'io') {
                    ref = this.$refs.storageLine1
                    hookFuncName = 'setStorageData'
                } else if (idx === 'net') {
                    ref = this.$refs.networkLine1
                    hookFuncName = 'setNetworkData'
                }

                ref && ref.showLoading({
                    text: '正在加载',
                    color: '#30d878',
                    maskColor: 'rgba(255, 255, 255, 0.8)'
                })

                try {
                    const res = await this.$store.dispatch('cluster/getNodeMetrics', params)
                    const list = res.data.list || []
                    this[hookFuncName](ref, list)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 设置 cpu 图表数据
             *
             * @param {Object} ref 图表组件 ref
             * @param {Array} data 数据
             */
            setCpuData (ref, data) {
                if (!ref) {
                    return
                }

                const chartData = []
                const emptyData = []

                if (!data.length) {
                    let startTime = null
                    if (this.cpuToggleRangeStr === '1小时') {
                        startTime = moment().subtract(1, 'hours').valueOf()
                    } else if (this.cpuToggleRangeStr === '24小时') {
                        startTime = moment().subtract(24, 'hours').valueOf()
                    } else if (this.cpuToggleRangeStr === '近7天') {
                        startTime = moment().subtract(7, 'days').valueOf()
                    }
                    data = [
                        {
                            usage: '-',
                            time: startTime
                        },
                        {
                            usage: '-',
                            time: moment().valueOf()
                        }
                    ]
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
             * 设置 mem 图表数据
             *
             * @param {Object} ref 图表组件 ref
             * @param {Array} data 数据
             */
            setMemData (ref, data) {
                if (!ref) {
                    return
                }

                const totalData = []
                const usedData = []
                const emptyData = []

                if (!data.length) {
                    let startTime = null
                    if (this.memToggleRangeStr === '1小时') {
                        startTime = moment().subtract(1, 'hours').valueOf()
                    } else if (this.memToggleRangeStr === '24小时') {
                        startTime = moment().subtract(24, 'hours').valueOf()
                    } else if (this.memToggleRangeStr === '近7天') {
                        startTime = moment().subtract(7, 'days').valueOf()
                    }
                    data = [
                        {
                            total: '-',
                            used: '-',
                            time: startTime
                        },
                        {
                            total: '-',
                            used: '-',
                            time: moment().valueOf()
                        }
                    ]
                }

                data.forEach(item => {
                    totalData.push({
                        value: [item.time, item.total]
                    })
                    usedData.push({
                        value: [item.time, item.used]
                    })
                    emptyData.push(0)
                })
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
                ref.mergeOptions({
                    series: [
                        {
                            data: totalData
                        },
                        {
                            data: usedData
                        }
                    ]
                })
                ref.hideLoading()
            },

            /**
             * 设置 network 图表数据
             *
             * @param {Object} ref 图表组件 ref
             * @param {Array} data 数据
             */
            setNetworkData (ref, list) {
                if (!ref) {
                    return
                }

                const emptyData = []

                const charOpts = {
                    legend: {
                        data: []
                    },
                    series: []
                }

                if (!list.length) {
                    let startTime = null
                    if (this.networkToggleRangeStr === '1小时') {
                        startTime = moment().subtract(1, 'hours').valueOf()
                    } else if (this.networkToggleRangeStr === '24小时') {
                        startTime = moment().subtract(24, 'hours').valueOf()
                    } else if (this.networkToggleRangeStr === '近7天') {
                        startTime = moment().subtract(7, 'days').valueOf()
                    }
                    list = [
                        {
                            device_name: 'noData',
                            metrics: [
                                {
                                    time: startTime,
                                    speedSent: '-',
                                    speedRecv: '-'
                                },
                                {
                                    time: moment().valueOf(),
                                    speedSent: '-',
                                    speedRecv: '-'
                                }
                            ]
                        }
                    ]
                }

                list.forEach(item => {
                    const metrics = item.metrics
                    // 加上这句那么在图表中就会显示 legend
                    // charOpts.legend.data.push(item.device_name)
                    const sentData = []
                    const recvData = []
                    metrics.forEach(metric => {
                        sentData.push({
                            value: [metric.time, metric.speedSent, 'sent']
                        })
                        recvData.push({
                            value: [metric.time, metric.speedRecv, 'recv']
                        })
                        emptyData.push(0)
                    })

                    charOpts.series.push(
                        {
                            type: 'line',
                            name: item.device_name,
                            data: sentData
                        },
                        {
                            type: 'line',
                            name: item.device_name,
                            data: recvData
                        }
                    )
                })

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
             * 设置 storage 图表数据
             *
             * @param {Object} ref 图表组件 ref
             * @param {Array} data 数据
             */
            setStorageData (ref, list) {
                if (!ref) {
                    return
                }

                const emptyData = []
                const charOpts = {
                    legend: {
                        data: []
                    },
                    series: []
                }

                if (!list.length) {
                    let startTime = null
                    if (this.storageToggleRangeStr === '1小时') {
                        startTime = moment().subtract(1, 'hours').valueOf()
                    } else if (this.storageToggleRangeStr === '24小时') {
                        startTime = moment().subtract(24, 'hours').valueOf()
                    } else if (this.storageToggleRangeStr === '近7天') {
                        startTime = moment().subtract(7, 'days').valueOf()
                    }
                    list = [
                        {
                            device_name: 'noData',
                            metrics: [
                                {
                                    time: startTime,
                                    rkb_s: '-',
                                    wkb_s: '-'
                                },
                                {
                                    time: moment().valueOf(),
                                    rkb_s: '-',
                                    wkb_s: '-'
                                }
                            ]
                        }
                    ]
                }

                list.forEach(item => {
                    const metrics = item.metrics
                    // charOpts.legend.data.push(item.device_name)
                    const readData = []
                    const writeData = []
                    metrics.forEach(metric => {
                        readData.push({
                            value: [metric.time, metric.rkb_s, 'read']
                        })
                        writeData.push({
                            value: [metric.time, metric.wkb_s, 'write']
                        })
                        emptyData.push(0)
                    })

                    charOpts.series.push(
                        {
                            type: 'line',
                            name: item.device_name,
                            data: readData
                        },
                        {
                            type: 'line',
                            name: item.device_name,
                            data: writeData
                        }
                    )
                })

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
             * 切换时间范围
             *
             * @param {Object} dropdownRef dropdown 标识
             * @param {string} toggleRangeStr 标识
             * @param {string} idx 标识，cpu / memory / network / storage
             * @param {string} range 时间范围，1: 1 小时，2: 24 小时，3：近 7 天
             */
            toggleRange (dropdownRef, toggleRangeStr, idx, range) {
                if (range === '1') {
                    this[toggleRangeStr] = '1小时'
                } else if (range === '2') {
                    this[toggleRangeStr] = '24小时'
                } else if (range === '3') {
                    this[toggleRangeStr] = '近7天'
                }

                this.$refs[dropdownRef].hide()
                this.fetchData(idx, range)
            },

            /**
             * 刷新当前 router
             */
            refreshCurRouter () {
                typeof this.$parent.refreshRouterView === 'function' && this.$parent.refreshRouterView()
            },

            /**
             * 返回节点管理
             */
            goNode () {
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
                        name: 'clusterNode',
                        params: {
                            projectId: this.projectId,
                            projectCode: this.projectCode,
                            clusterId: this.clusterId
                        }
                    })
                }
            },

            /**
             * 跳转到容器详情
             *
             * @param {Object} container 当前容器对象
             */
            async goContainerDetail (container) {
                this.$router.push({
                    name: 'containerDetailForNode',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        clusterId: this.clusterId,
                        containerId: container.container_id,
                        nodeId: this.nodeId
                    }
                })
            },

            tabChanged (name) {
                if (this.tabActiveName === name) {
                    return
                }
                this.tabActiveName = name

                clearTimeout(this.taskgroupTimer)
                this.taskgroupTimer = null

                this.openTaskgroup = Object.assign({}, {})

                if (name === 'label') {
                    this.labelList.splice(0, this.labelList.length, ...[])
                    this.fetchLabel()
                } else if (name === 'container') {
                    this.containerTableList.splice(0, this.containerTableList.length, ...[])
                    this.containerTablePageConf.curPage = 1
                    this.fetchNodeContainers()
                }
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '../../css/variable.css';

    .biz-cluster-node-overview {
        padding: 20px;
    }

    .biz-cluster-node-overview-title {
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

    .biz-cluster-node-overview-wrapper {
        background-color: $bgHoverColor;
        display: inline-block;
        width: 100%;
    }

    .biz-cluster-node-overview-header {
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
                max-width: 130px;
                padding-top: 4px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
    }

    .biz-cluster-node-overview-chart-wrapper {
        margin-top: 20px;
        background-color: #fff;
        box-shadow: 1px 0 2px rgba(0, 0, 0, 0.1);
        border: 1px solid $borderWeightColor;
        font-size: 0;
        border-radius: 2px;

        .biz-cluster-node-overview-chart {
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
            }
        }
    }

    .echarts {
        width: 100%;
        height: 180px;
    }

    .biz-cluster-node-overview-table-wrapper {
        margin-top: 20px;
    }

    .biz-cluster-node-overview-table {
        border-bottom: none;

        .name {
            width: 400px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .mirror {
            width: 500px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        i {
            top: 1px;
            position: relative;
            margin-right: 7px;

            &.running {
                color: $iconSuccessColor;
            }

            &.warning {
                color: $iconWarningColor;
            }

            &.danger {
                color: $failColor;
            }
        }
    }

    .biz-cluster-node-overview-page {
        border-top: 1px solid #e6e6e6;
        padding: 20px 40px 20px 0;
    }

    @media screen and (max-width: $mediaWidth) {
        .biz-cluster-node-overview-header {
            .header-item {
                div {
                    &:last-child {
                        width: 100px;
                    }
                }
            }
        }

        .biz-cluster-node-overview-table {
            border-bottom: none;

            .name {
                width: 350px;
            }

            .mirror {
                width: 450px;
            }
        }
    }

</style>
