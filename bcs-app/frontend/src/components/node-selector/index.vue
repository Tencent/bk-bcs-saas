<template>
    <bk-dialog
        :is-show.sync="dialogConf.isShow"
        :width="dialogConf.width"
        :content="dialogConf.content"
        :has-header="dialogConf.hasHeader"
        :close-icon="dialogConf.closeIcon"
        :ext-cls="'biz-cluster-create-choose-dialog'"
        :quick-close="false"
        class="server-dialog"
        @confirm="chooseServer">
        <div slot="content">
            <div style="margin: -20px;" v-bkloading="{ isLoading: ccHostLoading }">
                <div class="biz-cluster-create-table-header">
                    <div class="left" style="height: 60px;">
                        选择服务器
                        <span class="remain-tip" v-if="remainCount">已选择{{remainCount}}个节点</span>
                    </div>
                </div>
                <div style="min-height: 443px;">
                    <table class="bk-table has-table-hover biz-table biz-cluster-create-table" :style="{ borderBottomWidth: candidateHostList.length ? '1px' : 0 }">
                        <thead>
                            <tr>
                                <th style="width: 60px; text-align: right;">
                                    <label class="bk-form-checkbox">
                                        <input type="checkbox" name="check-all-host" v-model="isCheckCurPageAll" @click="toggleCheckCurPage">
                                    </label>
                                </th>
                                <th style="width: 160px;">主机名/IP</th>
                                <th style="width: 220px;">状态</th>
                                <th style="width: 120px;">容器数量</th>
                                <th style="width: 200px;">配置</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="candidateHostList.length">
                                <tr v-for="(host, index) in candidateHostList" @click.stop="rowClick" :key="index">
                                    <td style="width: 60px; text-align: right; ">
                                        <label class="bk-form-checkbox">
                                            <input type="checkbox" name="check-host" v-model="host.isChecked" @click.stop="selectHost(candidateHostList)" :disabled="host.status !== 'normal'">
                                        </label>
                                    </td>
                                    <td>
                                        {{host.inner_ip || '--'}}
                                    </td>
                                    <td>
                                        {{getHostStatus(host.status)}}
                                    </td>
                                    <td>
                                        {{host.containers}}
                                    </td>
                                    <td>
                                        {{host.device_class || '--'}}
                                    </td>
                                </tr>
                            </template>
                            <template v-if="!candidateHostList.length && !ccHostLoading">
                                <tr>
                                    <td colspan="7" style="top: 0;">
                                        <div class="bk-message-box no-data">
                                            <p class="message empty-message">您在当前业务下没有主机资源，请联系业务运维</p>
                                        </div>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
                <div class="biz-page-box" v-if="pageConf.show && candidateHostList.length">
                    <bk-paging
                        :size="'small'"
                        :cur-page.sync="pageConf.curPage"
                        :total-page="pageConf.totalPage"
                        @page-change="pageChange">
                    </bk-paging>
                </div>
            </div>
        </div>
        <template slot="footer">
            <div class="bk-dialog-outer">
                <div style="float: right;">
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                        @click="chooseServer">
                        确定
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hiseChooseServer">
                        取消
                    </button>
                </div>
            </div>
        </template>
    </bk-dialog>
</template>

<script>
    export default {
        props: {
            selected: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                curClusterId: '',
                dialogConf: {
                    isShow: false,
                    width: 920,
                    hasHeader: false,
                    closeIcon: false
                },
                ccHostLoading: false,
                clusterType: 'stag',
                // 弹层选择 master 节点，已经选择了多少个
                remainCount: 0,
                // 备选服务器集合
                candidateHostList: [],
                pageConf: {
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },

                TRUE: true,
                bkMessageInstance: null,
                // 已选服务器集合
                hostList: [],
                // 已选服务器集合的缓存，用于在弹框中选择，点击确定时才把 hostListCache 赋值给 hostList，同时清空 hostListCache
                // hostListCache: [],
                hostListCache: {},
                // 集群名称
                name: '',
                // nat
                // 当前页是否全选中
                isCheckCurPageAll: false,
                isChange: false,

                showStagTip: false,
                exceptionCode: null,
                curProject: null
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            }
        },
        mounted () {
            const projectList = this.onlineProjectList || window.$projectList
            this.curProject = Object.assign({}, projectList.filter(p => p.project_id === this.projectId)[0] || {})
        },
        methods: {
            /**
             * 获取节点状态
             *
             * @param {string} status 节点状态
             *
             * 正常: normal
             * 不正常: unnormal, not_ready
             * 不可调度: removable, to_removed
             * 初始化失败: initial_failed, so_init_failed, check_failed, bke_failed, schedule_failed
             * 删除失败: delete_failed, remove_failed
             * 初始化中: initializing, so_initializing, initial_checking, uninitialized
             * 删除中: removing
             */
            getHostStatus (status) {
                const statusMap = {
                    'normal': '正常',
                    'unnormal': '不正常',
                    'not_ready': '不正常',
                    'removable': '不可调度',
                    'to_removed': '不可调度',
                    'initial_failed': '初始化失败',
                    'so_init_failed': '初始化失败',
                    'check_failed': '初始化失败',
                    'bke_failed': '初始化失败',
                    'schedule_failed': '初始化失败',
                    'delete_failed': '删除失败',
                    'remove_failed': '删除失败',
                    'initializing': '初始化中',
                    'so_initializing': '初始化中',
                    'initial_checking': '初始化中',
                    'uninitialized': '初始化中',
                    'removing': '删除中'
                }
                return statusMap[status] || '不正常'
            },

            /**
             * 选择服务器弹层搜索事件
             *
             * @param {Array} searchKeys 搜索字符数组
             */
            handleSearch (searchKeys) {
                this.fetchCCData({
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
            chooseServer () {
                const list = Object.keys(this.hostListCache)
                const len = list.length
                if (!len) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择服务器'
                    })
                    return
                }

                const data = []
                list.forEach(key => {
                    data.push(this.hostListCache[key])
                })

                this.dialogConf.isShow = false
                this.hostList.splice(0, this.hostList.length, ...data)
                this.isCheckCurPageAll = false
                this.$emit('selected', data)
            },

            hiseChooseServer () {
                this.dialogConf.isShow = false
            },

            /**
             * 获取 cc 表格数据
             *
             * @param {Object} params ajax 查询参数
             */
            async fetchCCData (params = {}) {
                this.ccHostLoading = true
                try {
                    const res = await this.$store.dispatch('cluster/getNodeList', {
                        projectId: this.projectId,
                        clusterId: this.curClusterId,
                        limit: this.pageConf.pageSize,
                        offset: params.offset
                    })

                    const count = res.data.count

                    this.pageConf.show = !!count
                    this.pageConf.totalPage = Math.ceil(count / this.pageConf.pageSize)
                    if (this.pageConf.totalPage < this.pageConf.curPage) {
                        this.pageConf.curPage = 1
                    }

                    const list = res.data.results || []
                    list.forEach(item => {
                        if (this.hostListCache[`${item.inner_ip}-${item.asset_id}`]) {
                            item.isChecked = true
                        }
                    })

                    this.candidateHostList.splice(0, this.candidateHostList.length, ...list)
                    this.initSelected(this.candidateHostList)
                    this.selectHost(this.candidateHostList)
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.ccHostLoading = false
                }
            },

            /**
             * 打开选择服务器弹层
             */
            async openDialog (clusterId) {
                this.curClusterId = clusterId
                this.remainCount = 0
                this.pageConf.curPage = 1
                this.dialogConf.isShow = true
                this.candidateHostList.splice(0, this.candidateHostList.length, ...[])
                this.isCheckCurPageAll = false
                await this.fetchCCData({
                    offset: 0
                })
            },

            initSelected (list) {
                list.forEach(item => {
                    item.isChecked = false
                    this.selected.forEach(selectItem => {
                        if (String(selectItem.id) === String(item.id)) {
                            item.isChecked = true
                        }
                    })
                })
            },

            /**
             * 翻页回调
             *
             * @param {number} page 当前页
             */
            pageChange (page) {
                this.fetchCCData({
                    offset: this.pageConf.pageSize * (page - 1)
                })
            },

            /**
             * 弹层表格全选
             */
            toggleCheckCurPage () {
                const isChecked = !this.isCheckCurPageAll
                this.candidateHostList.forEach(host => {
                    if (host.status === 'normal') {
                        host.isChecked = isChecked
                    }
                })
                this.selectHost()
            },

            /**
             * 在选择服务器弹层中选择
             */
            selectHost (hosts = this.candidateHostList) {
                if (!hosts.length) {
                    return
                }

                this.$nextTick(() => {
                    const selectedHosts = hosts.filter(host =>
                        host.isChecked === true
                    )

                    const canSelectedHosts = hosts.filter(host =>
                        host.status === 'normal'
                    )

                    if (selectedHosts.length === canSelectedHosts.length) {
                        this.isCheckCurPageAll = true
                    } else {
                        this.isCheckCurPageAll = false
                    }

                    // 清除 hostListCache
                    hosts.forEach(item => {
                        delete this.hostListCache[`${item.inner_ip}-${item.asset_id}`]
                    })

                    // 重新根据选择的 host 设置到 hostListCache 中
                    selectedHosts.forEach(item => {
                        this.hostListCache[`${item.inner_ip}-${item.asset_id}`] = item
                    })

                    this.remainCount = Object.keys(this.hostListCache).length
                })
            },

            /**
             * 已选服务器移除处理
             *
             * @param {Object} host 当前行的服务器
             * @param {number} index 当前行的服务器的索引
             */
            removeHost (host, index) {
                this.hostList.splice(index, 1)
                delete this.hostListCache[`${host.inner_ip}-${host.asset_id}`]
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '../../css/variable.css';
    @import '../../css/mixins/clearfix.css';
    @import '../../css/mixins/ellipsis';
    .biz-cluster-create-table-header {
        @mixin clearfix;
        border: 1px solid #dde4eb;
        background-color: #fff;
        height: 60px;
        line-height: 59px;
        font-size: 16px;
        padding: 0 20px;
        border-bottom: none;
        border-top-left-radius: 2px;
        border-top-right-radius: 2px;
        .left {
            float: left;
            .tip {
                font-size: 12px;
                margin-left: 10px;
                color: #c3cdd7;
            }
            .remain-tip {
                font-size: 12px;
                margin-left: 10px;
                color: $dangerColor;
            }
        }
        .right {
            float: right;
        }

        .page-wrapper {
            height: 22px;
            display: inline-block;
            position: relative;
            top: -2px;
            line-height: 22px;
            ul {
                margin: 0;
                padding: 0;
                display: inline-block;
                overflow: hidden;
                height: 22px;
            }
            .page-item {
                min-width: 22px;
                height: 22px;
                line-height: 20px;
                text-align: center;
                display: inline-block;
                vertical-align: middle;
                font-size: 14px;
                float: left;
                margin-right: 0;
                border: 1px solid #c3cdd7;
                box-sizing: border-box;
                border-radius: 2px;
                overflow: hidden;
                i {
                    font-size: 12px;
                }
                &:first-child {
                    border-top-right-radius: 0;
                    border-bottom-right-radius: 0;
                }
                &:last-child {
                    border-top-left-radius: 0;
                    border-bottom-left-radius: 0;
                }
                &:hover {
                    border-color: $iconPrimaryColor;
                }
                &.disabled {
                    border-color: #c3cdd7 !important;
                    .page-button {
                        cursor: not-allowed;
                        background-color: #fafafa;
                        &:hover {
                            color: #737987;
                        }
                    }
                }
                .page-button {
                    display: block;
                    color: #737987;
                    background-color: #fff;
                    &:hover {
                        color: $iconPrimaryColor;
                    }
                }
            }
        }
    }

    .biz-cluster-create-table {
        background-color: #fff;
        border: 1px solid #dde4eb;
        width: 800px;
        thead {
            background-color: #fafbfd;
            tr {
                th {
                    height: 40px;
                }
            }
        }
        tbody {
            tr {
                &:hover {
                    background-color: #fafbfd;
                }
                td {
                    height: 40px;
                    font-size: 12px;
                }
            }
        }
        .no-data {
            min-height: 399px;
            .empty-message {
                margin-top: 160px;
            }
        }
    }

    .biz-cluster-create-choose-dialog {
        .biz-cluster-create-table {
            border-left: none;
            border-right: none;
            width: 920px;
            thead {
                tr {
                    th {
                        padding-top: 0;
                        padding-bottom: 0;
                    }
                }
            }
            tbody {
                tr {
                    td {
                        padding-top: 0;
                        padding-bottom: 0;
                        position: relative;
                        top: 5px;
                    }
                }
            }
            .name {
                @mixin ellipsis 120px
            }
            .inner-ip {
                @mixin ellipsis 200px
            }
            .idcunit {
                @mixin ellipsis 200px
            }
            .server-rack {
                @mixin ellipsis 130px
            }
            .device-class {
                @mixin ellipsis 80px
            }
        }

        .biz-cluster-create-table-header {
            border-left: none;
            border-right: none;
        }
        .biz-search-input {
            width: 320px;
        }
        .biz-page-box {
            padding: 10px 25px 10px 0;
            background-color: #fafbfd;
            border-top: 1px solid #dde4eb;
            margin-top: -1px;
        }

        .bk-dialog-footer.bk-d-footer {
            background-color: #fff;
        }
    }

    .server-tip {
        float: left;
        line-height: 17px;
        font-size: 12px;
        text-align: left;
        padding: 13px 0 0 20px;
        margin-left: 20px;

        li {
            list-style: circle;
        }
    }

    .biz-page-box {
        @mixin clearfix;
        padding: 30px 40px 35px 0;
        .bk-page {
            float: right;
        }
    }
</style>
