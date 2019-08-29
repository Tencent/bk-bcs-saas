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

import moment from 'moment'
import ECharts from 'vue-echarts/components/ECharts.vue'
import Clipboard from 'clipboard'
import 'echarts/lib/chart/line'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/legend'
import yamljs from 'js-yaml'

import { instanceDetailChart } from '@open/common/chart-option'
import { randomInt, catchErrorHandler, chartColors } from '@open/common/util'
import ace from '@open/components/ace-editor'

export default {
    components: {
        chart: ECharts,
        ace
    },
    data () {
        return {
            terminalWins: {},
            winHeight: 0,
            cpuLine: instanceDetailChart.cpu,
            memLine: instanceDetailChart.mem,
            tabActiveName: 'taskgroup',
            instanceInfo: {},
            labelList: [],
            labelListLoading: true,
            annotationList: [],
            annotationListLoading: true,
            metricList: [],
            metricListLoading: true,
            metricListErrorMessage: '没有数据',
            openTaskgroup: {},
            taskgroupList: [],
            taskgroupLoading: true,
            taskgroupTimer: null,
            openKeys: [],
            containerIdList: [],
            containerIdNameMap: {},
            eventList: [],
            eventListLoading: false,
            eventPageConf: {
                // 总数
                total: 0,
                // 总页数
                totalPage: 1,
                // 每页多少条
                pageSize: 5,
                // 当前页
                curPage: 1,
                // 是否显示翻页条
                show: false
            },
            logSideDialogConf: {
                isShow: false,
                title: '',
                timer: null,
                width: 700
            },
            toJsonDialogConf: {
                isShow: false,
                title: '',
                timer: null,
                width: 700,
                loading: false
            },
            logLoading: false,
            logList: [],
            bkMessageInstance: null,
            exceptionCode: null,
            editorConfig: {
                width: '100%',
                height: '100%',
                lang: 'yaml',
                readOnly: true,
                fullScreen: false,
                value: '',
                editor: null
            },
            clipboardInstance: null,
            copyContent: '',
            taskgroupInfoDialogConf: {
                isShow: false,
                title: '',
                timer: null,
                width: 690,
                loading: false
            },
            baseData: {},
            updateData: {},
            restartData: '',
            killData: '',
            instanceInfoLoading: true,
            reschedulerDialogConf: {
                isShow: false,
                width: 450,
                title: '',
                closeIcon: false,
                curRescheduler: null,
                curReschedulerIndex: -1
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
        instanceId () {
            const instanceId = this.$route.params.instanceId === undefined
                ? 0
                : this.$route.params.instanceId
            return instanceId
        },
        namespaceId () {
            return this.$route.params.namespaceId
        },
        templateId () {
            return this.$route.params.templateId
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
        }
    },
    mounted () {
        this.fetchInstanceInfo()
        this.fetchContainerIds()
        this.winHeight = window.innerHeight
        this.clipboardInstance = new Clipboard('.copy-code-btn')
        this.clipboardInstance.on('success', e => {
            this.$bkMessage({
                theme: 'success',
                message: '复制成功'
            })
        })
    },
    destroyed () {
        this.bkMessageInstance && this.bkMessageInstance.close()
        clearTimeout(this.taskgroupTimer)
        this.taskgroupTimer = null
        this.openTaskgroup = Object.assign({}, {})
    },
    methods: {
        /**
         * 分页大小更改
         *
         * @param {number} pageSize pageSize
         */
        changePageSize (pageSize) {
            this.eventPageConf.pageSize = pageSize
            this.eventPageConf.curPage = 1
            this.fetchEvent()
        },

        /**
         *  编辑器初始化之后的回调函数
         *  @param editor - 编辑器对象
         */
        editorInitAfter (editor) {
            this.editorConfig.editor = editor
            this.editorConfig.editor.setStyle('biz-app-container-tojson-ace')
        },

        /**
         * ace editor 全屏
         */
        setFullScreen () {
            this.editorConfig.fullScreen = true
        },

        /**
         * 取消全屏
         */
        cancelFullScreen () {
            this.editorConfig.fullScreen = false
        },

        /**
         * 关闭 to json
         *
         * @param {Object} cluster 当前集群对象
         */
        closeToJson () {
            this.toJsonDialogConf.isShow = false
            this.toJsonDialogConf.title = ''
            this.editorConfig.value = ''
            this.copyContent = ''
        },

        /**
         * to json, for mesos
         */
        async toJson () {
            try {
                this.toJsonDialogConf.isShow = true
                this.toJsonDialogConf.loading = true
                this.toJsonDialogConf.title = `${this.instanceInfo.name}.json`

                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/toJson', params)
                setTimeout(() => {
                    this.toJsonDialogConf.loading = false
                    setTimeout(() => {
                        this.editorConfig.editor.gotoLine(0, 0, true)
                    }, 10)

                    const data = res.data || {}
                    if (Object.keys(data).length) {
                        this.editorConfig.value = JSON.stringify(res.data || {}, null, 4)
                    } else {
                        this.editorConfig.value = '配置为空'
                    }
                    this.copyContent = this.editorConfig.value
                }, 100)
            } catch (e) {
                console.error(e)
                catchErrorHandler(e, this)
                this.toJsonDialogConf.isShow = false
                this.toJsonDialogConf.loading = false
            }
        },

        /**
         * to yaml, for k8s
         */
        async toYaml () {
            try {
                this.toJsonDialogConf.isShow = true
                this.toJsonDialogConf.loading = true
                this.toJsonDialogConf.title = `${this.instanceInfo.name}.yaml`

                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/toJson', params)
                setTimeout(() => {
                    this.toJsonDialogConf.loading = false
                    setTimeout(() => {
                        this.editorConfig.editor.gotoLine(0, 0, true)
                    }, 10)

                    const data = res.data || {}
                    if (Object.keys(data).length) {
                        this.editorConfig.value = yamljs.dump(res.data || {})
                    } else {
                        this.editorConfig.value = '配置为空'
                    }
                    this.copyContent = this.editorConfig.value
                }, 100)
            } catch (e) {
                console.error(e)
                catchErrorHandler(e, this)
                this.toJsonDialogConf.isShow = false
                this.toJsonDialogConf.loading = false
            }
        },

        /**
         * 获取实例详情信息，上方数据
         */
        async fetchInstanceInfo () {
            this.instanceInfoLoading = true
            const params = {
                projectId: this.projectId,
                instanceId: this.instanceId
            }

            if (String(this.instanceId) === '0') {
                params.name = this.instanceName
                params.namespace = this.instanceNamespace
                params.category = this.instanceCategory
            }

            if (this.CATEGORY) {
                params.category = this.CATEGORY
            }
            this.$refs.instanceCpuLine && this.$refs.instanceCpuLine.showLoading({
                text: '正在加载',
                color: '#30d878',
                maskColor: 'rgba(255, 255, 255, 0.8)'
            })
            this.$refs.instanceMemLine && this.$refs.instanceMemLine.showLoading({
                text: '正在加载',
                color: '#30d878',
                maskColor: 'rgba(255, 255, 255, 0.8)'
            })

            try {
                const res = await this.$store.dispatch('app/getInstanceInfo', params)

                this.instanceInfo = Object.assign({}, res.data || {})

                const createTimeMoment = moment(this.instanceInfo.create_time)
                this.instanceInfo.createTime = createTimeMoment.isValid()
                    ? createTimeMoment.format('YYYY-MM-DD HH:mm:ss')
                    : '--'

                const updateTimeMoment = moment(this.instanceInfo.update_time)
                this.instanceInfo.updateTime = updateTimeMoment.isValid()
                    ? updateTimeMoment.format('YYYY-MM-DD HH:mm:ss')
                    : '--'

                this.fetchTaskgroup(true)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.instanceInfoLoading = false
            }
        },

        /**
         * 获取下方 tab taskgroup 的数据
         *
         * @param {boolean} isLoadContainerMetrics 是否需要加载图表
         */
        async fetchTaskgroup (isLoadContainerMetrics) {
            this.taskgroupLoading = true
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getTaskgroupList', params)

                this.taskgroupList.splice(0, this.taskgroupList.length, ...[])

                const list = res.data || []
                list.forEach(item => {
                    let diffStr = ''
                    if (item.current_time && item.start_time) {
                        const timeDiff = moment.duration(
                            moment(item.current_time, 'YYYY-MM-DD HH:mm:ss').diff(
                                moment(item.start_time, 'YYYY-MM-DD HH:mm:ss')
                            )
                        )
                        const arr = [
                            timeDiff.get('day'),
                            timeDiff.get('hour'),
                            timeDiff.get('minute'),
                            timeDiff.get('second')
                        ]
                        diffStr = (arr[0] !== 0 ? (arr[0] + '天') : '')
                            + (arr[1] !== 0 ? (arr[1] + '小时') : '')
                            + (arr[2] !== 0 ? (arr[2] + '分') : '')
                            + (arr[3] !== 0 ? (arr[3] + '秒') : '')
                    }

                    this.taskgroupList.push({
                        ...item,
                        isOpen: false,
                        containerList: [],
                        containerLoading: false,
                        surviveTime: diffStr
                    })
                })
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.taskgroupLoading = false
            }
        },

        /**
         * 获取所有的 container id
         */
        async fetchContainerIds () {
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getContainerIds', params)
                const containerIdNameMap = {}
                const containerIdList = []
                const list = res.data || []
                // const list = [{container_id: '2aa0d5444531fe63f56da621f9f254596584c6338383f0370d678d8297d4af23', 'container_name': 'container_name111'}]
                list.forEach(item => {
                    containerIdNameMap[item.container_id] = item.container_name
                    containerIdList.push(item.container_id)
                })

                this.containerIdNameMap = JSON.parse(JSON.stringify(containerIdNameMap))
                this.containerIdList.splice(0, this.containerIdList.length, ...containerIdList)

                this.fetchContainerMetricsCpu()
                this.fetchContainerMetricsMem()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                // this.taskgroupLoading = false
            }
        },

        /**
         * 获取 cpu 图表数据
         */
        async fetchContainerMetricsCpu () {
            try {
                const params = {
                    projectId: this.projectId,
                    res_id_list: this.containerIdList,
                    metric: 'cpu_summary'
                }
                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getAllContainerMetrics', params)

                setTimeout(() => {
                    this.renderCpuChart(
                        res.data.list && res.data.list.length
                            ? res.data.list
                            : [
                                {
                                    container_name: 'noData', metrics: [{ usage: 0, time: new Date().getTime() }]
                                }
                            ]
                    )
                }, 0)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.$refs.instanceCpuLine && this.$refs.instanceCpuLine.hideLoading()
            }
        },

        /**
         * 渲染 cpu 图表
         *
         * @param {Array} data 数据
         */
        renderCpuChart (data) {
            const seriesEmpty = []
            const series = []
            const seriesLen = data.length
            const ref = this.$refs.instanceCpuLine
            if (!ref) {
                return
            }

            for (let i = 0; i < seriesLen; i++) {
                const chartData = []
                const emptyData = []

                const curColor = chartColors[i % 10]

                data[i].metrics.forEach(metric => {
                    chartData.push({
                        value: [metric.time, metric.usage, curColor]
                    })
                    emptyData.push(0)
                })

                const name = data[i].container_name || this.containerIdNameMap[data[i].id]

                series.push({
                    type: 'line',
                    name: name,
                    showSymbol: false,
                    hoverAnimation: false,
                    lineStyle: {
                        normal: {
                            color: curColor,
                            opacity: randomInt(7, 10) / 10
                        }
                    },
                    data: chartData
                })
                seriesEmpty.push({
                    type: 'line',
                    name: name,
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
         * 获取 mem 图表数据
         *
         * @param {Object} ref chart ref
         * @param {string} metric 标识是 cpu 还是内存图表
         */
        async fetchContainerMetricsMem (ref, metric) {
            try {
                const params = {
                    projectId: this.projectId,
                    res_id_list: this.containerIdList,
                    metric: 'mem'
                }
                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getAllContainerMetrics', params)

                setTimeout(() => {
                    this.renderMemChart(
                        res.data.list && res.data.list.length
                            ? res.data.list
                            : [
                                {
                                    container_name: 'noData', metrics: [{ used: 0, time: new Date().getTime() }]
                                }
                            ]
                    )
                }, 0)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.$refs.instanceMemLine && this.$refs.instanceMemLine.hideLoading()
            }
        },

        /**
         * 渲染 mem 图表，非内部版
         *
         * @param {Array} data 数据
         */
        renderMemChart (data) {
            const seriesEmpty = []
            const series = []
            const seriesLen = data.length
            const ref = this.$refs.instanceMemLine
            if (!ref) {
                return
            }

            for (let i = 0; i < seriesLen; i++) {
                const chartData = []
                const emptyData = []

                const curColor = chartColors[i % 10]

                data[i].metrics.forEach(metric => {
                    chartData.push({
                        value: [metric.time, metric.used, curColor]
                    })
                    emptyData.push(0)
                })

                // this.containerIdNameMap[data[i].id] 不存在时，data[i].container_name 就是 noData
                // const name = this.containerIdNameMap[data[i].id] || data[i].container_name
                const name = data[i].container_name || this.containerIdNameMap[data[i].id]
                series.push({
                    type: 'line',
                    name: name,
                    showSymbol: false,
                    hoverAnimation: false,
                    lineStyle: {
                        normal: {
                            color: curColor,
                            opacity: 1
                        }
                    },
                    data: chartData
                })
                seriesEmpty.push({
                    type: 'line',
                    name: name,
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
         * 显示 taskgroup 详情
         *
         * @param {Object} taskgroup 当前 taskgroup 对象
         * @param {number} index 当前 taskgroup 对象在 taskgroupList 里的索引
         */
        async showTaskgroupInfo (taskgroup, index) {
            this.taskgroupInfoDialogConf.isShow = true
            this.taskgroupInfoDialogConf.loading = true
            this.taskgroupInfoDialogConf.title = taskgroup.name

            try {
                this.baseData = Object.assign({}, {})
                this.updateData = Object.assign({}, {})
                this.restartData = ''

                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId,
                    taskgroupName: taskgroup.name
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                // k8s
                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                    this.killData = ''
                } else {
                    this.killData = Object.assign({}, {})
                }

                const res = await this.$store.dispatch('app/getTaskgroupInfo', params)

                this.baseData = Object.assign({}, res.data.base_info || {})
                this.baseData.lastUpdateTime = this.baseData.last_update_time
                    ? moment(this.baseData.last_update_time).format('YYYY-MM-DD HH:mm:ss')
                    : ''
                this.baseData.createTime = this.baseData.start_time
                    ? moment(this.baseData.start_time).format('YYYY-MM-DD HH:mm:ss')
                    : ''

                let diffStr = ''
                if (this.baseData.current_time && this.baseData.start_time) {
                    const timeDiff = moment.duration(
                        moment(this.baseData.current_time, 'YYYY-MM-DD HH:mm:ss').diff(
                            moment(this.baseData.start_time, 'YYYY-MM-DD HH:mm:ss')
                        )
                    )
                    const arr = [
                        timeDiff.get('day'),
                        timeDiff.get('hour'),
                        timeDiff.get('minute'),
                        timeDiff.get('second')
                    ]
                    diffStr = (arr[0] !== 0 ? (arr[0] + '天') : '')
                        + (arr[1] !== 0 ? (arr[1] + '小时') : '')
                        + (arr[2] !== 0 ? (arr[2] + '分') : '')
                        + (arr[3] !== 0 ? (arr[3] + '秒') : '')
                }

                this.baseData.surviveTime = diffStr

                this.updateData = Object.assign({}, res.data.update_strategy || {})
                this.restartData = res.data.restart_policy || ''
                if (this.CATEGORY) {
                    this.killData = res.data.kill_policy || ''
                } else {
                    this.killData = Object.assign({}, res.data.kill_policy || {})
                }
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.taskgroupInfoDialogConf.loading = false
            }
        },

        /**
         * 展开/收起 taskgroup 里的表格
         *
         * @param {Object} taskgroup 当前 taskgroup 对象
         * @param {number} index 当前 taskgroup 对象在 taskgroupList 里的索引
         */
        async toggleContainers (taskgroup, index) {
            taskgroup.isOpen = !taskgroup.isOpen
            this.$set(this.taskgroupList, index, taskgroup)
            if (!taskgroup.isOpen) {
                return
            }

            taskgroup.containerLoading = true
            this.$set(this.taskgroupList, index, taskgroup)
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId,
                    taskgroupName: taskgroup.name
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getContainterList', params)
                taskgroup.containerList = res.data || []
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                taskgroup.containerLoading = false
                this.$set(this.taskgroupList, index, taskgroup)
            }
        },

        /**
         * 显示重新调度确认框
         *
         * @param {Object} taskgroup 当前 taskgroup 对象
         * @param {number} index 当前 taskgroup 对象在 taskgroupList 里的索引
         */
        async showRescheduler (taskgroup, index) {
            if (taskgroup.status.toLowerCase() === 'lost') {
                this.reschedulerDialogConf.isShow = true
                this.reschedulerDialogConf.title = '当前taskgroup处于lost状态，请确认上面容器已经不再运行'
                this.reschedulerDialogConf.curRescheduler = Object.assign({}, taskgroup)
                this.reschedulerDialogConf.curReschedulerIndex = index
            } else {
                await this.rescheduler(taskgroup, index)
            }
        },

        /**
         * 隐藏重新调度确认框
         */
        hideRescheduler () {
            this.reschedulerDialogConf.isShow = false
            setTimeout(() => {
                this.reschedulerDialogConf.title = ''
            }, 500)
        },

        /**
         * 重新调度确认框的确认
         */
        reschedulerConfirm () {
            this.hideRescheduler()
            this.rescheduler(this.reschedulerDialogConf.curRescheduler, this.reschedulerDialogConf.curReschedulerIndex)
        },

        /**
         * 重新调度
         *
         * @param {Object} taskgroup 当前 taskgroup 对象
         * @param {number} index 当前 taskgroup 对象在 taskgroupList 里的索引
         */
        async rescheduler (taskgroup, index) {
            clearTimeout(this.taskgroupTimer)
            this.taskgroupTimer = null

            const statusTmp = taskgroup.status

            taskgroup.isOpen = false
            taskgroup.status = 'Starting'

            this.$set(this.taskgroupList, index, taskgroup)
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId,
                    taskgroupName: taskgroup.name
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                await this.$store.dispatch('app/reschedulerTaskgroup', params)
                setTimeout(() => {
                    this.loopTaskgroup()
                }, 5000)
            } catch (e) {
                taskgroup.status = statusTmp
                this.$set(this.taskgroupList, index, taskgroup)
                catchErrorHandler(e, this)
            } finally {
                this.reschedulerDialogConf.curRescheduler = null
                this.reschedulerDialogConf.curReschedulerIndex = -1
            }
        },

        /**
         * 轮询 taskgroup
         */
        async loopTaskgroup () {
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getTaskgroupList', params)

                this.taskgroupList.forEach(item => {
                    if (item.isOpen) {
                        this.openTaskgroup[item.name] = item.containerList
                    }
                })

                this.taskgroupList.splice(0, this.taskgroupList.length, ...[])

                const list = res.data || []
                list.forEach(item => {
                    let diffStr = ''
                    if (item.current_time && item.start_time) {
                        const timeDiff = moment.duration(
                            moment(item.current_time, 'YYYY-MM-DD HH:mm:ss').diff(
                                moment(item.start_time, 'YYYY-MM-DD HH:mm:ss')
                            )
                        )
                        const arr = [
                            timeDiff.get('day'),
                            timeDiff.get('hour'),
                            timeDiff.get('minute'),
                            timeDiff.get('second')
                        ]

                        diffStr = (arr[0] !== 0 ? (arr[0] + '天') : '')
                            + (arr[1] !== 0 ? (arr[1] + '小时') : '')
                            + (arr[2] !== 0 ? (arr[2] + '分') : '')
                            + (arr[3] !== 0 ? (arr[3] + '秒') : '')
                    }

                    this.taskgroupList.push({
                        ...item,
                        isOpen: !!this.openTaskgroup[item.name],
                        containerList: this.openTaskgroup[item.name] || [],
                        surviveTime: diffStr
                    })
                })

                this.taskgroupTimer = setTimeout(() => {
                    this.loopTaskgroup()
                }, 5000)
            } catch (e) {
                console.error(e, this)
            }
        },

        /**
         * 打开到终端入口
         *
         * @param {Object} container 当前容器
         */
        async showTerminal (container) {
            const cluster = this.instanceInfo

            const clusterId = cluster.cluster_id
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
         * 显示容器日志
         *
         * @param {Object} container 当前容器
         */
        async showLog (container) {
            this.logSideDialogConf.isShow = true
            this.logSideDialogConf.title = container.name
            this.logSideDialogConf.container = container
            this.logLoading = true
            try {
                const params = {
                    projectId: this.projectId,
                    containerId: container.container_id
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getContainterLog', params)
                this.logList.splice(0, this.logList.length, ...(res.data || []))
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.logLoading = false
            }
        },

        /**
         * 关闭日志
         *
         * @param {Object} cluster 当前集群对象
         */
        closeLog () {
            this.logSideDialogConf.isShow = false
            this.logSideDialogConf.title = ''
            this.logSideDialogConf.container = null
            this.logList.splice(0, this.logList.length, ...[])
        },

        /**
         * 刷新日志
         */
        async refreshLog () {
            this.logLoading = true
            try {
                const params = {
                    projectId: this.projectId,
                    containerId: this.logSideDialogConf.container.container_id
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getContainterLog', params)
                // this.logList.unshift(...(res.data || []))
                this.logList.splice(0, this.logList.length, ...(res.data || []))
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.logLoading = false
            }
        },

        /**
         * 获取下方 tab 标签的数据
         */
        async fetchLabel () {
            this.labelListLoading = true
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId,
                    instanceName: this.instanceInfo.name
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getLabelList', params)
                const list = res.data || []
                this.labelList.splice(0, this.labelList.length, ...list)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.labelListLoading = false
            }
        },

        /**
         * 获取下方 tab 备注的数据
         */
        async fetchAnnotation () {
            this.annotationListLoading = true
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId,
                    instanceName: this.instanceInfo.name
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getAnnotationList', params)
                const list = res.data || []
                this.annotationList.splice(0, this.annotationList.length, ...list)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.annotationListLoading = false
            }
        },

        /**
         * 获取下方 tab metric 数据
         */
        async fetchMetric () {
            this.metricListLoading = true
            this.metricListErrorMessage = '没有数据'
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getMetricList', params)
                const list = res.data || []
                this.metricList.splice(0, this.metricList.length, ...list)
            } catch (e) {
                this.metricListErrorMessage = e.message || e.data.msg || e.statusText
                catchErrorHandler(e, this)
            } finally {
                this.metricListLoading = false
            }
        },

        /**
         * 获取下方 tab 事件的数据
         *
         * @param {number} offset 起始页码
         * @param {number} limit 偏移量
         */
        async fetchEvent (offset = 0, limit = this.eventPageConf.pageSize) {
            this.eventListLoading = true
            try {
                const params = {
                    projectId: this.projectId,
                    instanceId: this.instanceId,
                    offset,
                    limit
                }

                if (String(this.instanceId) === '0') {
                    params.name = this.instanceName
                    params.namespace = this.instanceNamespace
                    params.category = this.instanceCategory
                }

                if (this.CATEGORY) {
                    params.category = this.CATEGORY
                }

                const res = await this.$store.dispatch('app/getEventList', params)

                const count = res.data.total || 0
                const list = []
                res.data.data.forEach(item => {
                    list.push({
                        eventTime: moment(item.eventTime).format('YYYY-MM-DD HH:mm:ss'),
                        component: item.component,
                        obj: item.extraInfo.name,
                        level: item.level,
                        describe: `${item.type}：${item.describe}`
                    })
                })
                this.eventList.splice(0, this.eventList.length, ...list)
                this.eventPageConf.total = count
                this.eventPageConf.totalPage = Math.ceil(count / this.eventPageConf.pageSize)
                if (this.eventPageConf.totalPage < this.eventPageConf.curPage) {
                    this.eventPageConf.curPage = 1
                }
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.eventListLoading = false
            }
        },

        /**
         * 翻页
         *
         * @param {number} page 页码
         */
        eventPageChange (page) {
            this.fetchEvent(this.eventPageConf.pageSize * (page - 1), this.eventPageConf.pageSize)
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

            clearTimeout(this.taskgroupTimer)
            this.taskgroupTimer = null

            this.openTaskgroup = Object.assign({}, {})

            if (name === 'label') {
                this.labelList.splice(0, this.labelList.length, ...[])
                this.fetchLabel()
            } else if (name === 'annotation') {
                this.annotationList.splice(0, this.annotationList.length, ...[])
                this.fetchAnnotation()
            } else if (name === 'taskgroup') {
                this.fetchTaskgroup(false)
            } else if (name === 'event') {
                this.fetchEvent()
            } else if (name === 'metric') {
                this.fetchMetric()
            }
        }
    }
}
