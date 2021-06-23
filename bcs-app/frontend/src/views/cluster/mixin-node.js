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

import axios from 'axios'
import Clipboard from 'clipboard'
import CheckMode from '@open/components/check-mode/check-mode'
import { catchErrorHandler } from '@open/common/util'

export default {
    components: {
        CheckMode
    },
    data () {
        return {
            ingStatus: [
                // 初始化中
                'initializing',
                // 初始化中
                'so_initializing',
                // 移除中
                'removing',
                // 初始化中
                'initial_checking',
                // 初始化中
                'uninitialized'
            ],
            failStatus: [
                // 初始化失败
                'initial_failed',
                // 初始化失败
                'so_init_failed',
                // 初始化失败
                'check_failed',
                // 初始化失败
                'bke_failed',
                // 初始化失败
                'schedule_failed',
                // 删除失败
                'delete_failed',
                // 删除失败
                'remove_failed'
            ],
            ccSearchKeys: [],
            permissions: {},
            // 弹出层搜索
            search: '',
            curClusterInPage: {},
            exceptionCode: null,
            isPageLoading: false,
            // isInitLoading: true,
            pageConf: {
                total: 1,
                pageSize: 10,
                curPage: 1,
                allCount: 0,
                show: true
            },
            deleteNodeNoticeList: [
                {
                    id: 1,
                    text: this.$t('当前节点上正在运行的容器会被调度到其它可用节点'),
                    isChecked: false
                },
                {
                    id: 2,
                    text: this.$t('清理容器服务系统组件'),
                    isChecked: false
                }
            ],
            faultRemoveoticeList: [
                {
                    id: 1,
                    text: this.$t('仅删除节点的信息记录，需要手动清理节点及其服务'),
                    isChecked: false
                }
            ],
            recordRemoveNoticeList: [
                {
                    id: 1,
                    text: this.$t('此操作仅移除节点在平台中的记录；如果集群中节点处于正常状态，会再次同步到平台的记录中'),
                    isChecked: true,
                    isText: true
                }
            ],
            // nodeList 分页配置
            nodeListPageConf: {
                // 总数
                total: 0,
                // 总页数
                totalPage: 1,
                // 每页多少条
                pageSize: 5,
                // 当前页
                curPage: 1,
                // 是否显示翻页条
                show: true
            },
            dialogConf: {
                isShow: false,
                width: 920,
                hasHeader: false,
                closeIcon: false
            },
            logSideDialogConf: {
                isShow: false,
                title: '',
                timer: null
            },
            logList: [],
            logEndState: '',
            curNode: null,
            curNodeIndex: -1,
            nodeList: [],
            // nodeList 缓存，用于 nodeList 中每条记录分别发送 cpu 内存 磁盘的接口
            nodeListTmp: [],
            // 如果列表还在加载 cpu 内存 磁盘数据的时候，此时搜索的话，会重新渲染列表，但是之前的 cpu 内存 磁盘数据请求还未返回
            // 所以这个时候会报错，但是也不能依此串行请求，需要并行请求提高速度，所以设置此变量来配合 searchDisabled
            alreadyGetNodeSummaryList: [],
            sortIdx: '',
            ccHostLoading: false,
            // 已选服务器集合
            hostList: [],
            // 已选服务器集合的缓存，用于在弹框中选择，点击确定时才把 hostListCache 赋值给 hostList，同时清空 hostListCache
            // hostListCache: [],
            hostListCache: {},
            // 备选服务器集合
            candidateHostList: [],
            // 备选服务器集合缓存，用于搜索
            candidateHostListTmp: [],
            curPageData: [],
            // 当前页是否全选中
            isCheckCurPageAll: false,
            // 添加节点弹层 全选模式
            // page 为全选当页，all 为全选所有页，为空表示没有全选
            checkAllMode: '',
            // 当前选择的 checkAllMode
            curCheckAllMode: '',
            // 是否正在创建节点
            isCreating: false,
            // 弹层选择 master 节点，已经选择了多少个
            remainCount: 0,
            searchDisabled: false,
            ccApplicationName: '',
            cancelLoop: false,
            timer: null,
            // 节点 cpu 磁盘 内存占用数据的缓存
            nodeSummaryMap: {},
            reInitializationDialogConf: {
                isShow: false,
                width: 400,
                title: '',
                closeIcon: false
            },
            reDelDialogConf: {
                isShow: false,
                width: 400,
                title: '',
                closeIcon: false
            },
            delDialogConf: {
                isShow: false,
                width: 400,
                title: '',
                closeIcon: false
            },
            enableDialogConf: {
                isShow: false,
                width: 400,
                title: '',
                closeIcon: false
            },
            stopDialogConf: {
                isShow: false,
                width: 550,
                title: '',
                closeIcon: false
            },
            schedulerDialogConf: {
                isShow: false,
                width: 450,
                title: '',
                closeIcon: false
            },
            removeDialogConf: {
                isShow: false,
                width: 400,
                title: '',
                closeIcon: false
            },
            isUpdating: false,
            ipSearchParams: [],
            allowBatch: false,
            // 已经选中的 node 集合
            checkedNodes: {},
            isCheckCurPageAllNode: false,
            dontAllowBatchMsg: this.$t('请选择节点'),
            batchDialogConf: {
                isShow: false,
                width: 400,
                title: ' ',
                closeIcon: false,
                operateType: '',
                len: 0,
                operate: ''
            },
            // 是否允许批量操作 -> 重新添加
            isBatchReInstall: false,
            // 允许批量操作 -> 重新添加的状态
            batchReInstallStatusList: ['initial_failed', 'check_failed', 'so_init_failed', 'schedule_failed', 'bke_failed'],
            clipboardInstance: null,
            // hostSourceKey: 'biz_host_pool',
            // hostSourceList: [{ id: 'biz_host_pool', name: this.$t('业务资源池') }, { id: 'bcs_host_pool', name: this.$t('平台资源池') }],
            nodeList4Copy: [],
            cpuManagementList: [{ id: 'none', name: 'none' }, { id: 'static', name: 'static' }],
            cpuManagementKey: 'none',
            checkMode: 0,
            modeType: 'page'
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
        },
        curProject () {
            const project = this.$store.state.curProject
            return project
        },
        isEn () {
            return this.$store.state.isEn
        }
    },
    watch: {
        checkedNodes (obj) {
            const arr = Object.keys(obj)
            const len = arr.length
            if (!len) {
                this.allowBatch = false
                this.dontAllowBatchMsg = this.$t('请选择节点')
                return
            }
            this.allowBatch = true
            this.dontAllowBatchMsg = ''
        },
        checkAllMode (v) {
            this.checkMode = ['page', 'all'].includes(v) ? 2 : 0
        }
    },
    beforeDestroy () {
        this.release()
        this.cancelLoop = true
    },
    destroyed () {
        this.release()
        this.cancelLoop = true
    },
    async created () {
        this.release()
        this.cancelLoop = false

        if (!this.curCluster || Object.keys(this.curCluster).length <= 0) {
            if (this.projectId && this.clusterId) {
                await this.fetchClusterData()
            }
        } else {
            const params = {
                limit: this.nodeListPageConf.pageSize,
                offset: 0,
                with_containers: '1'
            }
            if (this.$route.query.inner_ip) {
                params.ip = this.$route.query.inner_ip
                this.ipSearchParams.splice(0, this.ipSearchParams.length, ...[{
                    id: 'ip',
                    text: this.$t('IP地址'),
                    value: params.ip,
                    valueArr: [params.ip]
                }])
            }
            this.getNodeList(params)
        }
        this.fetchNodeList4Copy()
    },
    methods: {
        async fetchNodeList4Copy () {
            try {
                const res = await this.$store.dispatch('cluster/getNodeList4Copy', {
                    projectId: this.projectId,
                    clusterId: this.clusterId
                })
                this.nodeList4Copy.splice(0, this.nodeList4Copy.length, ...(res.data || []))
            } catch (e) {
                catchErrorHandler(e, this)
            }
        },

        /**
         * 渲染 table header checkbox
         *
         */
        handleRenderCheckboxHeader (h) {
            return <CheckMode
                v-model={this.checkMode}
                mode={this.modeType}
                disabled={!this.candidateHostList.filter(host => !host.is_used && String(host.agent) === '1' && host.is_valid).length && this.isCreating}
                on-change={(v) => {
                    this.checkAll(this.modeType)
                }}
                on-mode-change={(mode) => {
                    this.modeType = mode
                }}>
            </CheckMode>
        },

        /**
         * 格式化日志
         *
         * @param {string} log 日志内容
         *
         * @return {strin} 格式化后的日志内容
         */
        formatLog (log) {
            // 换行
            log = log.replace(/##/ig, '<p class="html-tag"></p>').replace(/\|/ig, '<p class="html-tag"></p>')
            // 着色
            log = log.replace(/(Failed)/ig, '<span class="biz-danger-text">$1</span>')
            log = log.replace(/(OK)/ig, '<span class="biz-success-text">$1</span>')
            return log
        },

        /**
         * 获取当前集群数据
         */
        async fetchClusterData () {
            this.isPageLoading = true
            try {
                const res = await this.$store.dispatch('cluster/getCluster', {
                    projectId: this.projectId,
                    clusterId: this.clusterId
                })

                this.$store.commit('cluster/forceUpdateCurCluster', res.data)

                const params = {
                    limit: this.nodeListPageConf.pageSize,
                    offset: 0,
                    with_containers: '1'
                }
                if (this.$route.query.inner_ip) {
                    params.ip = this.$route.query.inner_ip
                    this.ipSearchParams.splice(0, this.ipSearchParams.length, ...[{
                        id: 'ip',
                        text: this.$t('IP地址'),
                        value: params.ip,
                        valueArr: [params.ip]
                    }])
                }
                this.getNodeList(params, true)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                // this.isInitLoading = false
            }
        },

        /**
         * 释放资源，重置 timer 等等
         */
        release () {
            clearTimeout(this.timer) && (this.timer = null)
            clearTimeout(this.logSideDialogConf.timer) && (this.logSideDialogConf.timer = null)
        },

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
         * 获取节点管理数据
         *
         * @param {Object} params ajax 参数
         * @param {Boolean} isPolling 是否是轮询，如果是，那么不显示 loading
         */
        async getNodeList (params = {}, isPolling) {
            if (!isPolling) {
                this.isPageLoading = true
            }

            try {
                const res = await this.$store.dispatch('cluster/getNodeListByLabelAndIp', Object.assign({}, {
                    projectId: this.projectId,
                    clusterId: this.curCluster.cluster_id // 这里用 this.curCluster 来获取是为了使计算属性生效
                }, params))

                this.permissions = JSON.parse(JSON.stringify(res.permissions || {}))

                const list = res.data.results || []

                list.forEach(item => {
                    item.isChecked = !!this.checkedNodes[item.id]
                })

                if (!list.length) {
                    this.dontAllowBatchMsg = this.$t('请选择节点')
                }

                this.isCheckCurPageAllNode = list.length && list.every(item => this.checkedNodes[item.id])

                this.nodeList.splice(0, this.nodeList.length, ...list)
                this.nodeListTmp.splice(0, this.nodeListTmp.length, ...list)
                this.alreadyGetNodeSummaryList.splice(0, this.alreadyGetNodeSummaryList.length, ...[])

                if (!this.nodeList.length) {
                    this.searchDisabled = false
                }

                if (!isPolling) {
                    this.nodeListTmp.forEach((item, index) => {
                        this.getNodeSummary(item, index)
                    })
                } else {
                    // 轮询时不用发送 getNodeSummary 请求，直接从 nodeSummaryMap 中获取数据
                    this.nodeListTmp.forEach((item, index) => {
                        if (this.nodeSummaryMap[item.id]) {
                            item.cpuMetric = this.nodeSummaryMap[item.id].cpuMetric
                            item.memMetric = this.nodeSummaryMap[item.id].memMetric
                            item.diskMetric = this.nodeSummaryMap[item.id].diskMetric
                            item.diskioMetric = this.nodeSummaryMap[item.id].diskioMetric
                            item.containerCount = this.nodeSummaryMap[item.id].containerCount
                            item.podCount = this.nodeSummaryMap[item.id].podCount
                            item.mesosMemoryUsage = this.nodeSummaryMap[item.id].mesosMemoryUsage
                            item.mesosIpRemainCount = this.nodeSummaryMap[item.id].mesosIpRemainCount
                            item.mesosCpuUsage = this.nodeSummaryMap[item.id].mesosCpuUsage
                        }
                    })
                }

                const count = res.data.count || 0
                this.nodeListPageConf.total = count
                this.nodeListPageConf.totalPage = Math.ceil(count / this.nodeListPageConf.pageSize)
                if (this.nodeListPageConf.totalPage < this.nodeListPageConf.curPage) {
                    this.nodeListPageConf.curPage = 1
                }
                this.nodeListPageConf.show = this.nodeListPageConf.totalPage > 1

                if (this.cancelLoop) {
                    clearTimeout(this.timer)
                    this.timer = null
                } else {
                    this.timer = setTimeout(() => {
                        this.refreshWithCurCondition()
                    }, 10000)
                }
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isPageLoading = false
                setTimeout(() => {
                    this.isInitLoading = false
                }, 300)
            }
        },

        /**
         * 带上搜索条件以及翻页的刷新列表，这个情况的刷新主要是为了轮训的，所以不需要 loading
         *
         * @param {number} curPage 待刷新的页码，默认当前页
         * @param {boolean} notLoading 是否不需要 loading，默认不需要
         */
        refreshWithCurCondition () {
            this.sortIdx = ''
            // 如果日志的 sidesilder 没有显示，那么移除日志的 sidesilder 的轮训
            if (!this.logSideDialogConf.isShow) {
                clearTimeout(this.logSideDialogConf.timer) && (this.logSideDialogConf.timer = null)
            }
            clearTimeout(this.timer) && (this.timer = null)

            const searchParams = this.getSearchParams()

            this.getNodeList({
                labels: searchParams.labels,
                ip: searchParams.ipParams,
                status_list: searchParams.statusList,
                limit: this.nodeListPageConf.pageSize,
                offset: this.nodeListPageConf.pageSize * (this.nodeListPageConf.curPage - 1),
                with_containers: '1'
            }, true)
        },

        /**
         * 节点管理分页大小更改
         *
         * @param {number} pageSize pageSize
         */
        changePageSize (pageSize) {
            this.nodeListPageConf.pageSize = pageSize
            this.nodeListPageConf.curPage = 1
            this.checkedNodes = {}
            this.nodeListPageChange(this.pageConf.curPage)
        },

        /**
         * 节点管理 nodeList 翻页回调
         *
         * @param {number} page 当前页
         */
        nodeListPageChange (page) {
            this.release()
            const searchParams = this.getSearchParams()
            this.nodeListPageConf.curPage = page
            // this.checkedNodes = {}
            this.getNodeList({
                labels: searchParams.labels,
                ip: searchParams.ipParams,
                status_list: searchParams.statusList,
                limit: this.nodeListPageConf.pageSize,
                offset: this.nodeListPageConf.pageSize * (page - 1),
                with_containers: '1'
            })
        },

        /**
         * 获取 searcher 的参数
         *
         * @return {Object} 参数
         */
        getSearchParams () {
            const searchParams = (this.$refs.searcher && this.$refs.searcher.searchParams) || []
            const ipParams = searchParams.filter(item => item.id === 'ip').map(
                item => item.valueArr.join(',')
            ).join(',')

            const labelsParams = searchParams.filter(item => item.id === 'labels')
            const labels = []
            labelsParams.forEach(label => {
                label.valueArr.forEach(item => {
                    labels.push({
                        [`${label.key}`]: item
                    })
                })
            })

            const statusListParams = searchParams.filter(item => item.id === 'status_list')
            const statusMap = {}
            statusListParams.forEach(statusItem => {
                statusItem.valueArr.forEach(statusVal => {
                    statusMap[statusVal] = 1
                })
            })
            return { ipParams, labels, statusList: Object.keys(statusMap) }
        },

        /**
         * nodeList 搜索
         *
         * @param {Array} searchKey 搜索词
         */
        searchNodeList () {
            this.sortIdx = ''
            this.release()
            this.nodeListPageConf.curPage = 1

            this.checkedNodes = Object.assign({}, {})

            const searchParams = this.getSearchParams()
            this.getNodeList({
                labels: searchParams.labels,
                ip: searchParams.ipParams,
                status_list: searchParams.statusList,
                limit: this.nodeListPageConf.pageSize,
                offset: 0,
                with_containers: '1'
            })
        },

        /**
         * 清除 searcher 搜索条件
         */
        clearSearchParams () {
            this.$refs.searcher.clear()
            this.getSearchParams()
        },

        /**
         * 节点管理获取 cpu 磁盘 内存占用的数据
         *
         * @param {Object} cur 当前节点
         * @param {number} index 当前节点索引
         */
        async getNodeSummary (cur, index) {
            try {
                const args = {}
                if (this.curClusterInPage.type === 'mesos' && this.curClusterInPage.func_wlist && this.curClusterInPage.func_wlist.indexOf('MesosResource') > -1) {
                    args.dimensions = 'mesos_memory_usage,mesos_ip_remain_count,mesos_cpu_usage'
                }

                const res = await this.$store.dispatch('cluster/getNodeOverview', {
                    projectId: cur.project_id,
                    clusterId: cur.cluster_id,
                    nodeIp: cur.inner_ip,
                    data: args
                })

                cur.cpuMetric = parseFloat(res.data.cpu_usage).toFixed(2)
                cur.memMetric = parseFloat(res.data.memory_usage).toFixed(2)
                cur.diskMetric = parseFloat(res.data.disk_usage).toFixed(2)
                cur.diskioMetric = parseFloat(res.data.diskio_usage).toFixed(2)
                cur.containerCount = res.data.container_count || 0
                cur.podCount = res.data.pod_count || 0
                cur.mesosMemoryUsage = res.data.mesos_memory_usage || { remain: 0, total: 0 }
                cur.mesosIpRemainCount = res.data.mesos_ip_remain_count || 0
                cur.mesosCpuUsage = res.data.mesos_cpu_usage || { remain: 0, total: 0 }

                this.nodeSummaryMap[cur.id] = {
                    cpuMetric: cur.cpuMetric,
                    memMetric: cur.memMetric,
                    diskMetric: cur.diskMetric,
                    diskioMetric: cur.diskioMetric,
                    containerCount: cur.containerCount,
                    podCount: cur.podCount,
                    mesosMemoryUsage: cur.mesosMemoryUsage,
                    mesosIpRemainCount: cur.mesosIpRemainCount,
                    mesosCpuUsage: cur.mesosCpuUsage
                }

                this.$set(this.nodeList, index, cur)

                this.alreadyGetNodeSummaryList.push(index)

                if (this.alreadyGetNodeSummaryList.length === this.nodeListTmp.length) {
                    this.searchDisabled = false
                }
            } catch (e) {
                catchErrorHandler(e, this)
            }
        },

        /**
         * 排序
         *
         * @param {string} field 字段
         * @param {string} order 顺序
         * @param {string} targetOrder 当前点击的操作的目标排序顺序
         */
        async sortNodeList (field, order, targetOrder) {
            this.release()

            const searchParams = this.getSearchParams()

            if (targetOrder === this.sortIdx) {
                this.getNodeList({
                    labels: searchParams.labels,
                    ip: searchParams.ipParams,
                    status_list: searchParams.statusList,
                    limit: this.nodeListPageConf.pageSize,
                    offset: 0,
                    with_containers: '1'
                })
                this.sortIdx = ''
                this.nodeListPageConf.curPage = 1
                return
            }

            let ordering = ''
            if (order === 'desc') {
                ordering = `-${field}`
                this.sortIdx = `-${field}`
            } else {
                ordering = field
                this.sortIdx = field
            }
            this.getNodeList({
                labels: searchParams.labels,
                ip: searchParams.ipParams,
                limit: this.nodeListPageConf.pageSize,
                offset: 0,
                ordering: ordering,
                with_containers: '1'
            })
        },

        /**
         * 手动刷新表格数据
         */
        refresh () {
            this.sortIdx = ''
            this.nodeListPageConf.curPage = 1
            this.clearSearchParams()
        },

        /**
         * 打开选择服务器弹层
         */
        async openDialog () {
            if (!this.permissions.create) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'create',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.remainCount = 0
            this.pageConf.curPage = 1
            this.pageConf.allCount = 0
            this.dialogConf.isShow = true
            this.candidateHostList.splice(0, this.candidateHostList.length, ...[])
            this.hostListCache = Object.assign({}, {})
            this.hostList.splice(0, this.hostList.length, ...[])
            this.isCheckCurPageAll = false
            this.$refs.iPSearcher && this.$refs.iPSearcher.clearSearchParams()

            // 这里不需要请求了，handleSearch 方法会请求
            // await this.fetchCCData({
            //     offset: 0
            // })
        },

        /**
         * 关闭选择服务器弹层
         */
        closeDialog () {
            this.dialogConf.isShow = false
            this.checkAllMode = ''
        },

        /**
         * cc host 弹框中 change 机器来源下拉框回调函数
         */
        async changeHostSource (index, data) {
            await this.fetchCCData()
        },

        /**
         * 获取 cc 表格数据
         *
         * @param {Object} params ajax 查询参数
         */
        async fetchCCData (params = {}) {
            this.ccHostLoading = true
            try {
                const args = {
                    projectId: this.projectId,
                    limit: this.pageConf.pageSize,
                    offset: params.offset,
                    ip_list: params.ipList || []
                }
                if (this.curClusterInPage.type === 'tke') {
                    args.node_role = 'node'
                    // args.host_source = this.hostSourceKey
                    args.cluster_id = this.clusterId
                }
                const res = await this.$store.dispatch('cluster/getCCHostList', args)

                this.ccApplicationName = res.data.cc_application_name || ''

                const count = res.data.count

                this.pageConf.show = !!count
                this.pageConf.total = Math.ceil(count / this.pageConf.pageSize)
                if (this.pageConf.total < this.pageConf.curPage) {
                    this.pageConf.curPage = 1
                }
                this.pageConf.show = true
                this.pageConf.allCount = count

                const list = res.data.results || []

                if (this.checkAllMode === 'all') {
                    list.forEach(item => {
                        item.isChecked = true
                    })
                } else {
                    list.forEach(item => {
                        if (this.hostListCache[`${item.inner_ip}-${item.asset_id}`]) {
                            item.isChecked = true
                        }
                    })
                }

                this.candidateHostList.splice(0, this.candidateHostList.length, ...list)
                this.selectHost(this.candidateHostList)
            } catch (e) {
                console.log(e)
            } finally {
                this.ccHostLoading = false
            }
        },

        /**
         * 弹框翻页回调
         *
         * @param {number} page 当前页
         */
        pageChange (page) {
            this.pageConf.curPage = page
            this.fetchCCData({
                offset: this.pageConf.pageSize * (page - 1),
                ipList: this.ccSearchKeys || []
            })
        },

        /**
         * 弹层表格全选
         */
        toogleCheckCurPage () {
            this.$nextTick(() => {
                const isChecked = this.isCheckCurPageAll
                this.candidateHostList.forEach(host => {
                    if (!host.is_used && String(host.agent) === '1' && host.is_valid) {
                        host.isChecked = isChecked
                    }
                })
                this.selectHost()
            })
        },

        /**
         * 弹层表格全选
         *
         * @param {string} idx 全选当前页还是全选所有页的标识。page 为全选当前页，all 为全选所有页面
         */
        checkAll (idx) {
            // 说明当前选中的是已经选中的那个，这时需要取消
            if (this.checkAllMode === idx) {
                this.isCheckCurPageAll = false
            } else {
                this.isCheckCurPageAll = true
            }
            this.curCheckAllMode = idx
            this.toogleCheckCurPage()

            this.$nextTick(() => {
                this.$refs.pageSelectDropdownMenu && this.$refs.pageSelectDropdownMenu.hide()
            })
        },

        /**
         * 在选择服务器弹层中选择
         */
        selectHost (hosts = this.candidateHostList) {
            if (!hosts.length) {
                return
            }

            this.$nextTick(() => {
                const illegalLen = hosts.filter(host => host.is_used || String(host.agent) !== '1' || !host.is_valid).length
                const selectedHosts = hosts.filter(host =>
                    host.isChecked === true && !host.is_used && String(host.agent) === '1' && host.is_valid
                )

                if (selectedHosts.length === hosts.length - illegalLen && hosts.length !== illegalLen) {
                    this.isCheckCurPageAll = true
                    if (this.curCheckAllMode) {
                        // checkAllMode 变化之前是 all，那么变化之后，需要把 hostListCache 清空一下
                        if (this.checkAllMode === 'all') {
                            this.hostListCache = Object.assign({}, {})
                        }
                        this.checkAllMode = this.curCheckAllMode
                        this.curCheckAllMode = ''
                    } else {
                        if (this.checkAllMode === 'fromall') {
                            this.checkAllMode = 'all'
                        } else if (this.checkAllMode === 'frompage') {
                            this.checkAllMode = 'page'
                        }
                    }
                } else {
                    this.isCheckCurPageAll = false
                    if (this.curCheckAllMode) {
                        // 说明当前选中的是已经选中的那个，这时需要取消
                        if (this.checkAllMode === this.curCheckAllMode) {
                            this.checkAllMode = ''
                            this.hostListCache = Object.assign({}, {})
                        } else {
                            this.checkAllMode = this.curCheckAllMode
                        }
                        this.curCheckAllMode = ''
                    } else {
                        if (this.checkAllMode === 'all') {
                            this.checkAllMode = 'fromall'
                        } else if (this.checkAllMode === 'page') {
                            this.checkAllMode = 'frompage'
                        }
                    }
                }

                // 清除 hostListCache
                hosts.forEach(item => {
                    delete this.hostListCache[`${item.inner_ip}-${item.asset_id}`]
                })

                // 重新根据选择的 host 设置到 hostListCache 中
                selectedHosts.forEach(item => {
                    this.hostListCache[`${item.inner_ip}-${item.asset_id}`] = item
                })

                // this.remainCount = Object.keys(this.hostListCache).length
                if (this.checkAllMode === 'all') {
                    this.remainCount = this.pageConf.allCount
                } else {
                    this.remainCount = Object.keys(this.hostListCache).length
                }
            })
        },

        /**
         * 选择服务器弹层搜索事件
         *
         * @param {Array} searchKeys 搜索字符数组
         */
        async handleSearch (searchKeys) {
            this.ccSearchKeys = searchKeys
            await this.fetchCCData({
                offset: 0,
                ipList: searchKeys
            })
        },

        /**
         * 弹层表格行选中
         *
         * @param {Object} e 事件对象
         */
        rowClick (e) {
            let target = e.target
            while (target.nodeName.toLowerCase() !== 'tr') {
                target = target.parentNode
            }
            const checkboxNode = target.querySelector('input[type="checkbox"]')
            checkboxNode && checkboxNode.click()
        },

        /**
         * 选择服务器弹层确定按钮
         */
        async chooseServer () {
            const list = Object.keys(this.hostListCache)
            const len = list.length
            if (!len) {
                this.$bkMessage({
                    theme: 'error',
                    message: this.$t('请选择服务器')
                })
                return
            }
            this.$refs.nodeNoticeDialog.show()
        },

        /**
         * 选择服务器弹层保存节点
         */
        async saveNode () {
            const params = {
                ip: [],
                projectId: this.projectId,
                clusterId: this.clusterId,
                is_select_all: false
            }
            if (this.checkAllMode === 'all') {
                params.is_select_all = true
                params.ip = this.ccSearchKeys
            } else {
                const list = Object.keys(this.hostListCache)

                const data = []
                list.forEach(key => {
                    data.push(this.hostListCache[key])
                })

                this.hostList.splice(0, this.hostList.length, ...data)

                this.hostList.forEach(item => {
                    params.ip.push(item.inner_ip)
                })
            }

            // if (this.curClusterInPage.type === 'tke') {
            //     params.host_source = this.hostSourceKey
            // }

            params.cpu_manager_policy = this.cpuManagementKey

            // alert('打开控制台查看参数')
            // console.warn(params)
            // console.warn('\n')
            // console.warn('JSON.stringify: \n')
            // console.warn(JSON.stringify(params))
            this.isCreating = true
            this.$refs.nodeNoticeDialog.hide()

            setTimeout(async () => {
                try {
                    await this.$store.dispatch('cluster/addNode', params)

                    this.cancelLoop = false
                    this.sortIdx = ''
                    this.nodeListPageConf.curPage = 1
                    this.clearSearchParams()

                    this.isCheckCurPageAll = false
                    this.dialogConf.isShow = false
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isCreating = false
                }
            }, 100)
        },

        /**
         * 重新初始化节点
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async reInitializationNode (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.reInitializationDialogConf.isShow = true
            this.reInitializationDialogConf.title = ' '
            this.reInitializationDialogConf.content = this.$t(`确认要重新初始化节点【{innerIp}】？`, {
                innerIp: node.inner_ip
            })

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
        },

        /**
         * 确认重新初始化节点
         */
        async reInitializationConfirm () {
            this.isUpdating = true
            try {
                const res = await this.$store.dispatch('cluster/reInitializationNode', {
                    projectId: this.curNode.project_id,
                    clusterId: this.curNode.cluster_id,
                    nodeId: this.curNode.id
                })
                this.curNode.status = res.data.status
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)

                this.resetBatchStatus()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isUpdating = false
                this.reInitializationCancel()
            }
        },

        /**
         * 取消重新初始化节点
         */
        reInitializationCancel () {
            this.reInitializationDialogConf.isShow = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
            setTimeout(() => {
                this.reInitializationDialogConf.title = ''
                this.reInitializationDialogConf.content = ''
                this.curNode = null
                this.curNodeIndex = -1
            }, 200)
        },

        /**
         * remove_failed 的删除，重试删除
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async reTryDel (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.reDelDialogConf.isShow = true
            this.reDelDialogConf.title = ' '
            this.reDelDialogConf.content = this.$t(`确认要强制删除节点【{innerIp}】？`, {
                innerIp: node.inner_ip
            })

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
        },

        /**
         * remove_failed 的删除，确认重试删除
         */
        async reDelConfirm () {
            this.isUpdating = true
            try {
                await this.$store.dispatch('cluster/forceRemoveNode', {
                    projectId: this.curNode.project_id,
                    clusterId: this.curNode.cluster_id,
                    nodeId: this.curNode.id
                })

                this.curNode.status = 'removing'
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)

                this.resetBatchStatus()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isUpdating = false
                this.reDelCancel()
            }
        },

        /**
         * remove_failed 的删除，取消重试删除
         */
        reDelCancel () {
            this.reDelDialogConf.isShow = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
            setTimeout(() => {
                this.reDelDialogConf.title = ''
                this.reDelDialogConf.content = ''

                this.curNode = null
                this.curNodeIndex = -1
            }, 200)
        },

        /**
         * delete_failed 状态的删除
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async delFailedNode (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: node.cluster_id,
                    resource_name: node.cluster_name,
                    resource_type: `cluster_${node.cluster_env === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.delDialogConf.isShow = true
            this.delDialogConf.title = ' '
            this.delDialogConf.content = this.$t(`确认要删除节点【{innerIp}】？`, {
                innerIp: node.inner_ip
            })

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
        },

        /**
         * delete_failed 状态的删除，确认重试删除
         */
        async delConfirm () {
            this.isUpdating = true
            try {
                await this.$store.dispatch('cluster/failedDelNode', {
                    projectId: this.curNode.project_id,
                    clusterId: this.curNode.cluster_id,
                    nodeId: this.curNode.id
                })
                this.curNode.status = 'removing'
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)

                this.resetBatchStatus()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isUpdating = false
                this.delCancel()
            }
        },

        /**
         * delete_failed 状态的删除，取消重试删除
         */
        delCancel () {
            this.delDialogConf.isShow = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
            setTimeout(() => {
                this.curNode = null
                this.delDialogConf.title = ''
                this.delDialogConf.content = ''

                this.curNode = null
                this.curNodeIndex = -1
            }, 200)
        },

        /**
         * 启用节点
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async enableNode (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.enableDialogConf.isShow = true
            this.enableDialogConf.title = ' '
            this.enableDialogConf.content = this.$t(`确认允许调度节点【{innerIp}】？`, {
                innerIp: node.inner_ip
            })

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
        },

        /**
         * 确认启用节点
         */
        async enableConfirm () {
            this.isUpdating = true
            try {
                const res = await this.$store.dispatch('cluster/updateNodeStatus', {
                    projectId: this.curNode.project_id,
                    clusterId: this.curNode.cluster_id,
                    nodeId: this.curNode.id,
                    status: 'normal'
                })
                this.curNode.status = res.data.status
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)

                this.resetBatchStatus()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isUpdating = false
                this.enableCancel()
            }
        },

        /**
         * 取消启用节点
         */
        enableCancel () {
            this.enableDialogConf.isShow = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
            setTimeout(() => {
                this.enableDialogConf.title = ''
                this.enableDialogConf.content = ''

                this.curNode = null
                this.curNodeIndex = -1
            }, 200)
        },

        /**
         * 停止调度节点
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async stopNode (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.stopDialogConf.isShow = true

            if (this.curClusterInPage.type === 'mesos') {
                this.stopDialogConf.title = ' '
                this.stopDialogConf.content = this.$t(`确认要停止调度节点【{innerIp}】？`, {
                    innerIp: node.inner_ip
                })
            } else {
                this.stopDialogConf.title = this.$t(`确认要停止调度节点【{innerIp}】？`, {
                    innerIp: node.inner_ip
                })
                this.stopDialogConf.content = this.$t(
                    '注意: 如果有使用Ingress及LoadBalancer类型的Service，节点停止调度后，Service Controller会剔除LB到nodePort的映射，请确认是否停止调度'
                )
            }

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
        },

        /**
         * 确认停止调度节点
         */
        async stopConfirm () {
            this.isUpdating = true
            try {
                const res = await this.$store.dispatch('cluster/updateNodeStatus', {
                    projectId: this.curNode.project_id,
                    clusterId: this.curNode.cluster_id,
                    nodeId: this.curNode.id,
                    status: 'to_removed'
                })
                this.curNode.status = res.data.status
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)

                this.resetBatchStatus()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isUpdating = false
                this.stopCancel()
            }
        },

        /**
         * 取消停止调度节点
         */
        stopCancel () {
            this.stopDialogConf.isShow = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
            setTimeout(() => {
                this.stopDialogConf.title = ''
                this.stopDialogConf.content = ''

                this.curNode = null
                this.curNodeIndex = -1
            }, 200)
        },

        /**
         * 查询节点日志
         *
         * @param {Object} node 当前节点
         */
        async showLog (node) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'view',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.logSideDialogConf.isShow = true
            this.logSideDialogConf.title = node.inner_ip
            try {
                const res = await this.$store.dispatch('cluster/getNodeLogs', {
                    projectId: node.project_id,
                    clusterId: node.cluster_id,
                    nodeId: node.id
                })

                const { status, log = [], error_msg_list: errorMsgList = [], task_url: taskUrl = '' } = res.data

                // 最终的状态
                // running / failed / success
                this.logEndState = status

                const tasks = []
                log.forEach(operation => {
                    operation.errorMsgList = errorMsgList
                    operation.taskUrl = taskUrl
                    tasks.push(operation)
                })
                this.logList.splice(0, this.logList.length, ...tasks)

                if (this.logEndState === 'success' || this.logEndState === 'failed' || this.logEndState === 'none') {
                    clearTimeout(this.logSideDialogConf.timer)
                    this.logSideDialogConf.timer = null
                    // node 状态是运行中的，日志已经到结束状态了，那么要刷新列表
                    if (this.ingStatus.includes(node.status)) {
                        this.refreshWithCurCondition()
                    }
                } else {
                    this.$nextTick(() => {
                        this.logSideDialogConf.timer = setTimeout(() => {
                            this.showLog(node)
                        }, 3500)
                    })
                }
            } catch (e) {
                console.error(e)
            }
        },

        /**
         * 关闭日志
         *
         * @param {Object} cluster 当前集群对象
         */
        closeLog () {
            this.cancelLoop = false
            // 还未轮询完即日志还未到最终状态
            if (this.logSideDialogConf.timer) {
                clearTimeout(this.logSideDialogConf.timer)
                this.logSideDialogConf.timer = null
            } else {
                if (this.logEndState !== 'none') {
                    this.refreshWithCurCondition()
                }
            }
            this.logList.splice(0, this.logList.length, ...[])
            this.logEndState = ''
        },

        /**
         * 显示删除节点弹框
         * initial_failed, so_init_failed, check_failed, bke_failed, schedule_failed removable not_ready 状态的删除
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async showDelNode (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index

            if (this.failStatus.includes(node.status)) {
                this.removeDialogConf.isShow = true
                this.removeDialogConf.title = ' '
                this.removeDialogConf.content = this.$t(`确认要删除节点【{innerIp}】？`, {
                    innerIp: node.inner_ip
                })
            } else {
                this.$refs.removeNodeDialog.title = this.$t(`确认要删除节点【{innerIp}】？`, {
                    innerIp: node.inner_ip
                })
                this.$refs.removeNodeDialog.show()
            }
        },

        /**
         * 删除节点
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async confirmDelNode () {
            const node = this.curNode

            this.$refs.removeNodeDialog.isConfirming = true
            try {
                await this.$store.dispatch('cluster/removeNode', {
                    projectId: node.project_id,
                    clusterId: node.cluster_id,
                    nodeId: node.id
                })
                this.$refs.removeNodeDialog.isConfirming = false

                this.curNode.status = 'removing'
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)
                this.cancelLoop = false
                this.refreshWithCurCondition()

                this.resetBatchStatus()

                setTimeout(() => {
                    this.curNode = null
                    this.curNodeIndex = -1
                }, 200)
            } catch (e) {
                catchErrorHandler(e, this)
            }
        },

        /**
         * 删除节点弹层取消
         */
        cancelDelNode () {
            setTimeout(() => {
                this.$refs.removeNodeDialog.title = this.$t('确定删除节点？')
            }, 300)
            this.curNode = null
            this.curNodeIndex = -1
            this.cancelLoop = false
            this.refreshWithCurCondition()
        },

        /**
         * 确认删除节点，failStauts 里的状态的删除
         */
        async removeConfirm () {
            this.isUpdating = true
            try {
                await this.$store.dispatch('cluster/removeNode', {
                    projectId: this.curNode.project_id,
                    clusterId: this.curNode.cluster_id,
                    nodeId: this.curNode.id
                })

                this.curNode.status = 'removing'
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)

                this.resetBatchStatus()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isUpdating = false
                this.removeCancel()
            }
        },

        /**
         * 取消删除节点，failStauts 里的状态的删除
         */
        removeCancel () {
            this.removeDialogConf.isShow = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
            setTimeout(() => {
                this.removeDialogConf.title = ''
                this.removeDialogConf.content = ''

                this.curNode = null
                this.curNodeIndex = -1
            }, 200)
        },

        /**
         * 显示强制删除节点弹框
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async showForceDelNode (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
            this.$refs.forceRemoveNodeDialog.title = this.$t(`确认要强制删除节点【{innerIp}】？`, {
                innerIp: node.inner_ip
            })
            this.$refs.forceRemoveNodeDialog.show()
        },

        /**
         * 强制删除节点
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async confirmForceRemoveNode () {
            const node = this.curNode

            this.$refs.forceRemoveNodeDialog.isConfirming = true
            try {
                await this.$store.dispatch('cluster/forceRemoveNode', {
                    projectId: node.project_id,
                    clusterId: node.cluster_id,
                    nodeId: node.id
                })

                this.curNode.status = 'removing'
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)
                this.cancelLoop = false
                this.refreshWithCurCondition()

                this.resetBatchStatus()

                setTimeout(() => {
                    this.curNode = null
                    this.curNodeIndex = -1
                }, 200)
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.$refs.forceRemoveNodeDialog.isConfirming = false
            }
        },

        /**
         * 强制删除节点弹层取消
         */
        cancelForceRemoveNode () {
            setTimeout(() => {
                this.$refs.forceRemoveNodeDialog.title = this.$t('确定强制删除节点？')
            }, 300)
            this.curNode = null
            this.curNodeIndex = -1
            this.cancelLoop = false
            this.refreshWithCurCondition()
        },
        /**
         * 显示移除记录弹框
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async showRecordRemove (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
            this.$refs.recordRemoveDialog.show()
        },

        /**
         * 显示故障移除节点弹框
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async showFaultRemove (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
            this.$refs.faultRemoveDialog.title = this.$t(`确定移除故障节点：{innerIp}？`, {
                innerIp: node.inner_ip
            })
            this.$refs.faultRemoveDialog.show()
        },

        /**
         * 移除记录
         */
        async confirmRecordRemove () {
            const node = this.curNode

            this.$refs.recordRemoveDialog.isConfirming = true
            try {
                await this.$store.dispatch('cluster/faultRemoveNode', {
                    projectId: node.project_id,
                    clusterId: node.cluster_id,
                    nodeId: node.id
                })
                this.$refs.recordRemoveDialog.isConfirming = false

                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)
                this.cancelLoop = false
                this.refreshWithCurCondition()

                this.resetBatchStatus()

                setTimeout(() => {
                    this.curNode = null
                    this.curNodeIndex = -1
                }, 200)
            } catch (e) {
                this.$refs.recordRemoveDialog.isConfirming = false
                catchErrorHandler(e, this)
            }
        },
        /**
         * 移除记录弹层取消
         */
        cancelRecordRemove () {
            this.curNode = null
            this.curNodeIndex = -1
            this.$refs.recordRemoveDialog.isConfirming = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
        },
        /**
         * 故障移除节点
         */
        async confirmFaultRemove () {
            const node = this.curNode

            this.$refs.faultRemoveDialog.isConfirming = true
            try {
                await this.$store.dispatch('cluster/faultRemoveNode', {
                    projectId: node.project_id,
                    clusterId: node.cluster_id,
                    nodeId: node.id
                })
                this.$refs.faultRemoveDialog.isConfirming = false

                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)
                this.cancelLoop = false
                this.refreshWithCurCondition()

                this.resetBatchStatus()

                setTimeout(() => {
                    this.curNode = null
                    this.curNodeIndex = -1
                }, 200)
            } catch (e) {
                this.$refs.faultRemoveDialog.isConfirming = false
                catchErrorHandler(e, this)
            }
        },

        /**
         * 故障移除节点弹层取消
         */
        cancelFaultRemove () {
            setTimeout(() => {
                this.$refs.faultRemoveDialog.title = this.$t('确定移除故障节点？')
            }, 300)
            this.curNode = null
            this.curNodeIndex = -1
            this.$refs.faultRemoveDialog.isConfirming = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
        },

        /**
         * 节点上的 pod 或 taskgroup 迁移
         *
         * @param {Object} node 节点对象
         * @param {number} index 节点对象在节点管理中的索引
         */
        async schedulerNode (node, index) {
            if (!node.permissions.edit) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'edit',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.schedulerDialogConf.isShow = true
            this.schedulerDialogConf.title = ' '
            this.schedulerDialogConf.content = this.isEn
                ? 'Confirm that you want to migrate the '
                    + `${(this.curProject.kind === PROJECT_K8S || this.curProject.kind === PROJECT_TKE) ? 'Pod' : 'taskgroup'} on node【${node.inner_ip}】?`
                : `确认要对节点【${node.inner_ip}】上的`
                    + `${(this.curProject.kind === PROJECT_K8S || this.curProject.kind === PROJECT_TKE) ? 'Pod' : 'taskgroup'}进行迁移？`

            this.curNode = Object.assign({}, node)
            this.curNodeIndex = index
        },

        /**
         * 确认节点上的 pod 或 taskgroup 迁移
         */
        async schedulerConfirm () {
            this.isUpdating = true
            try {
                const res = await this.$store.dispatch('cluster/schedulerNode', {
                    projectId: this.curNode.project_id,
                    clusterId: this.curNode.cluster_id,
                    nodeId: this.curNode.id
                })
                this.curNode.status = res.data.status
                this.$set(this.nodeList, this.curNodeIndex, this.curNode)
                this.$set(this.nodeListTmp, this.curNodeIndex, this.curNode)

                this.resetBatchStatus()
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isUpdating = false
                this.schedulerCancel()
            }
        },

        /**
         * 取消节点上的 pod 或 taskgroup 迁移
         */
        schedulerCancel () {
            this.schedulerDialogConf.isShow = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
            setTimeout(() => {
                this.schedulerDialogConf.title = ''
                this.schedulerDialogConf.content = ''

                this.curNode = null
                this.curNodeIndex = -1
            }, 200)
        },

        /**
         * 刷新当前 router
         */
        refreshCurRouter () {
            typeof this.$parent.refreshRouterView === 'function' && this.$parent.refreshRouterView()
        },

        /**
         * 节点列表多选框选中
         *
         * @param {Object} node 节点对象
         * @param {boolean} checked 是否选中
         */
        checkNode (node, checked) {
            const checkedNodes = Object.assign({}, this.checkedNodes)
            this.$nextTick(() => {
                if (node.isChecked) {
                    checkedNodes[node.id] = node
                } else {
                    delete checkedNodes[node.id]
                }
                this.checkedNodes = Object.assign({}, checkedNodes)
                this.isCheckCurPageAllNode = this.nodeList.every(item => this.checkedNodes[item.id])

                const statusList = Object.keys(this.checkedNodes).map(key => this.checkedNodes[key].status)
                this.isBatchReInstall = statusList.every(status => this.batchReInstallStatusList.indexOf(status) > -1)
            })
        },

        /**
         * 节点列表多选框全选
         *
         * @param {boolean} isAllChecked 是否选中
         */
        checkAllNode (isAllChecked) {
            const checkedNodes = {}
            const nodeList = []
            nodeList.splice(0, 0, ...this.nodeList)
            this.$nextTick(() => {
                this.isCheckCurPageAllNode = isAllChecked
                nodeList.forEach(item => {
                    item.isChecked = isAllChecked
                    if (item.isChecked) {
                        checkedNodes[item.id] = item
                    }
                })

                this.checkedNodes = Object.assign({}, checkedNodes)
                this.nodeList.splice(0, this.nodeList.length, ...nodeList)

                const statusList = Object.keys(this.checkedNodes).map(key => this.checkedNodes[key].status)
                this.isBatchReInstall = statusList.every(status => this.batchReInstallStatusList.indexOf(status) > -1)
            })
        },

        /**
         * 节点列表批量操作
         *
         * @param {string} idx 操作标识
         */
        batchOperate (idx) {
            const len = Object.keys(this.checkedNodes).length
            let str = ''
            if (idx === '1') {
                str = this.$t('允许调度')
            } else if (idx === '2') {
                str = this.$t('停止调度')
            } else if (idx === '3') {
                str = this.$t('删除')
            } else {
                str = this.$t('重新添加')
            }
            this.batchDialogConf.operateType = idx
            this.batchDialogConf.isShow = true
            this.batchDialogConf.title = ' '
            this.batchDialogConf.len = len
            this.batchDialogConf.operate = str
        },

        /**
         * 确认节点列表批量操作
         */
        async batchConfirm () {
            this.isUpdating = true
            try {
                if (this.batchDialogConf.operateType === '4') {
                    await this.$store.dispatch('cluster/batchNodeReInstall', {
                        projectId: this.projectId,
                        clusterId: this.clusterId,
                        node_id_list: Object.keys(this.checkedNodes).map(id => id)
                    })
                } else {
                    await this.$store.dispatch('cluster/batchNode', {
                        projectId: this.projectId,
                        operateType: this.batchDialogConf.operateType,
                        clusterId: this.clusterId,
                        idList: Object.keys(this.checkedNodes).map(id => id),
                        status: this.batchDialogConf.operateType === '1' ? 'normal' : 'to_removed'
                    })
                }
                this.refreshWithCurCondition()

                // 删除
                if (this.batchDialogConf.operateType === '3') {
                    this.resetBatchStatus()
                }
            } catch (e) {
                catchErrorHandler(e, this)
            } finally {
                this.isUpdating = false
                this.batchCancel()
            }
        },

        /**
         * 取消节点列表批量操作
         */
        batchCancel () {
            this.batchDialogConf.isShow = false
            this.cancelLoop = false
            this.refreshWithCurCondition()
            setTimeout(() => {
                this.batchDialogConf.title = ' '
                this.batchDialogConf.operateType = ''
                this.batchDialogConf.len = 0
                this.batchDialogConf.operate = ''
            }, 200)
        },

        /**
         * 重置多选的状态，多选框全部不选中，并且每行节点不选中
         */
        resetBatchStatus () {
            this.checkedNodes = Object.assign({}, {})
            const nodeList = []
            nodeList.splice(0, 0, ...this.nodeList)
            nodeList.forEach(item => {
                item.isChecked = false
            })
            this.nodeList.splice(0, this.nodeList.length, ...nodeList)
            this.isCheckCurPageAllNode = false
            // this.allowBatchDelete = true
        },

        /**
         * 节点导出
         */
        async exportNode () {
            // const link = document.createElement('a')
            // link.style.display = 'none'
            // link.href = `${DEVOPS_BCS_API_URL}/api/projects/${this.projectId}/nodes/export/?cluster_id=${this.clusterId}`
            // document.body.appendChild(link)
            // link.click()

            const url = `${DEVOPS_BCS_API_URL}/api/projects/${this.projectId}/nodes/export/`

            const response = await axios({
                url: url,
                method: 'post',
                responseType: 'blob', // 这句话很重要
                data: {
                    cluster_id: this.clusterId,
                    node_id_list: Object.keys(this.checkedNodes).map(item => parseInt(item, 10))
                }
            })

            if (response.status !== 200) {
                console.log('系统异常，请稍候再试')
                return
            }

            const blob = new Blob([response.data], { type: response.headers['content-type'] })
            const a = window.document.createElement('a')
            const downUrl = window.URL.createObjectURL(blob)
            let filename = 'download.xls'
            const contentDisposition = response.headers['content-disposition']
            if (contentDisposition && contentDisposition.indexOf('filename=') !== -1) {
                filename = contentDisposition.split('filename=')[1]
                a.href = downUrl
                a.download = filename || 'download.xls'
                a.click()
                window.URL.revokeObjectURL(downUrl)
            }
        },

        /**
         * 进入节点详情页面
         *
         * @param {Object} node 节点信息
         */
        async goNodeOverview (node) {
            if (!node.permissions.view) {
                await this.$store.dispatch('getResourcePermissions', {
                    project_id: this.projectId,
                    policy_code: 'view',
                    resource_code: this.curClusterInPage.cluster_id,
                    resource_name: this.curClusterInPage.name,
                    resource_type: `cluster_${this.curClusterInPage.environment === 'stag' ? 'test' : 'prod'}`
                })
            }

            this.$router.push({
                name: 'clusterNodeOverview',
                params: {
                    nodeId: node.inner_ip
                }
            })
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
        goOverview () {
            this.$router.push({
                name: 'clusterOverview',
                params: {
                    projectId: this.projectId,
                    projectCode: this.projectCode,
                    clusterId: this.clusterId,
                    backTarget: this.$route.params.backTarget
                }
            })
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
        },

        /**
         * 复制 IP
         *
         * @param {string} idx 复制的标识
         */
        async copyIp (idx) {
            this.$refs.copyIpDropdownMenu && this.$refs.copyIpDropdownMenu.hide()

            let successMsg = ''
            // 复制所选 ip
            if (idx === 'selected') {
                this.clipboardInstance = new Clipboard('.copy-ip-dropdown .selected', {
                    text: trigger => Object.keys(this.checkedNodes).map(key => this.checkedNodes[key].inner_ip).join('\n')
                })
                successMsg = this.$t('复制 {len} 个IP成功', { len: Object.keys(this.checkedNodes).length })
            } else if (idx === 'cur-page') {
                // 复制当前页 IP
                if (!this.nodeList.length) {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'primary',
                        message: this.$t('当前页无数据')
                    })
                    return
                }
                this.clipboardInstance = new Clipboard('.copy-ip-dropdown .cur-page', {
                    text: trigger => this.nodeList.map(node => node.inner_ip).join('\n')
                })
                successMsg = this.$t('复制当前页IP成功')
            } else if (idx === 'all') {
                // 复制所有 IP
                if (!this.nodeList4Copy.length) {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'primary',
                        message: this.$t('无数据')
                    })
                    return
                }
                this.clipboardInstance = new Clipboard('.copy-ip-dropdown .all', {
                    text: trigger => this.nodeList4Copy.map(ip => ip).join('\n')
                })
                successMsg = this.$t('复制所有IP成功')
            }
            this.clipboardInstance.on('success', e => {
                this.bkMessageInstance && this.bkMessageInstance.close()
                this.bkMessageInstance = this.$bkMessage({
                    theme: 'success',
                    message: successMsg
                })
                this.clipboardInstance.destroy()
            })
        }
    }
}
