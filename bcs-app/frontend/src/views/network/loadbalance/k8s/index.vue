<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-loadbalance-title">
                LoadBalancer
                <span data-v-67a1b199="" class="biz-tip f12 ml10">{{$t('K8S官方维护的ingress-nginx')}}</span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper" style="padding: 0;" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <app-exception
                v-if="exceptionCode && !isInitLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>

            <template v-if="!exceptionCode && !isInitLoading">
                <div class="biz-panel-header">
                    <div class="left">
                        <button class="bk-button bk-primary" @click.stop.prevent="createLoadBlance">
                            <i class="bk-icon icon-plus"></i>
                            <span>{{$t('新建LoadBalancer')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="$t('输入命名空间，按Enter搜索')"
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="getLoadBalanceList"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>
                <div class="biz-loadbalance">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table has-table-hover biz-table biz-loadbalance-table">
                            <thead>
                                <tr>
                                    <th>{{$t('所属集群')}}</th>
                                    <th>{{$t('命名空间')}}</th>
                                    <th>{{$t('端口')}}</th>
                                    <th>{{$t('更新时间')}}</th>
                                    <th>{{$t('更新人')}}</th>
                                    <th style="width: 160px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="loadBalanceList.length">
                                    <tr v-for="(loadBalance, index) in curPageData" :key="loadBalance.id">
                                        <td>
                                            <bk-tooltip :content="loadBalance.cluster_id" placement="top">
                                                <div class="cluster-name">{{loadBalance.cluster_name}}</div>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            {{loadBalance.namespace_name}}
                                        </td>
                                        <td>
                                            <template v-for="key of Object.keys(loadBalance.protocol)">
                                                <div class="biz-key-label" :key="key" v-if="loadBalance.protocol[key].isUse && key">
                                                    <span class="key">{{key}}</span>
                                                    <span class="value">{{loadBalance.protocol[key].port}}</span>
                                                </div>
                                            </template>
                                        </td>
                                        <td>
                                            {{formatDate(loadBalance.updated)}}
                                        </td>
                                        <td>
                                            {{loadBalance.updator}}
                                        </td>
                                        <td>
                                            <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="editLoadBalance(loadBalance, index)">{{$t('编辑')}}</a>
                                            <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="removeLoadBalance(loadBalance, index)">{{$t('删除')}}</a>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="7">
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
                            @page-change="handlerPageChange">
                        </bk-paging>
                    </div>
                </div>
            </template>
        </div>

        <bk-sideslider
            style="z-index: 150;"
            :quick-close="false"
            :is-show.sync="loadBalanceSlider.isShow"
            :title="loadBalanceSlider.title"
            :width="630"
            @hidden="hideLoadBalanceSlider">
            <div class="p30" slot="content">
                <div class="bk-form bk-form-vertical mb20" v-bkloading="{ isLoading: isDataSaveing }">
                    <div class="bk-form-item is-required">
                        <div class="bk-form-content">
                            <label class="bk-label">{{$t('所属集群')}}：</label>
                            <div class="bk-form-content">
                                <bk-selector
                                    style="width:565px;"
                                    :field-type="'cluster'"
                                    :placeholder="$t('请选择')"
                                    :setting-key="'cluster_id'"
                                    :display-key="'longName'"
                                    :is-link="true"
                                    :selected.sync="curLoadBalance.cluster_id"
                                    :list="clusterList"
                                    @item-selected="handlerSelectCluster">
                                </bk-selector>
                            </div>
                        </div>
                    </div>

                    <div class="bk-form-item is-required">
                        <div class="bk-form-content">
                            <label class="bk-label">{{$t('命名空间')}}：</label>
                            <div class="bk-form-content">
                                <div style="width: 565px;">
                                    <bk-selector
                                        :searchable="true"
                                        :field-type="'namespace'"
                                        :placeholder="$t('请选择')"
                                        :setting-key="'id'"
                                        :display-key="'name'"
                                        :selected.sync="curLoadBalance.namespace"
                                        :list="nameSpaceClusterList">
                                    </bk-selector>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bk-form-item">
                        <label class="bk-label">{{$t('设置协议')}}：<span class="biz-tip">{{$t('至少有一个勾选')}}</span></label>
                        <div class="bk-form-content">
                            <div class="bk-form-inline-item is-required" style="width: 260px;">
                                <label class="bk-form-checkbox" style="width: 100px;">
                                    <input
                                        type="checkbox"
                                        name="portocal"
                                        v-model="curLoadBalance.protocol.http.isUse"
                                        :disabled="!curLoadBalance.protocol.https.isUse" />
                                    <i class="bk-checkbox-text">{{$t('启用Http')}}</i>
                                </label>
                                <bk-input
                                    type="number"
                                    :placeholder="$t('启用Http')"
                                    style="width: 154px;"
                                    :min="0"
                                    :value.sync="curLoadBalance.protocol.http.port">
                                </bk-input>
                            </div>
                            <div class="bk-form-inline-item is-required" style="width: 263px; margin-left: 35px;">
                                <label class="bk-form-checkbox" style="width: 100px;">
                                    <input
                                        type="checkbox"
                                        name="portocal"
                                        v-model="curLoadBalance.protocol.https.isUse"
                                        :disabled="!curLoadBalance.protocol.http.isUse" />
                                    <i class="bk-checkbox-text">{{$t('启用Https')}}</i>
                                </label>
                                <bk-input
                                    type="number"
                                    :placeholder="$t('启用Https')"
                                    style="width: 157px;"
                                    :min="0"
                                    :value.sync="curLoadBalance.protocol.https.port">
                                </bk-input>
                            </div>
                        </div>
                    </div>

                    <div class="bk-form-item is-required mt15">
                        <div class="head">
                            <label class="bk-label">{{$t('节点IP')}}：</label>
                            <bk-button type="primary" size="mini" @click="showNodeSelector">{{$t('添加节点')}}</bk-button>
                        </div>
                        <table class="bk-table biz-data-table has-table-bordered">
                            <thead>
                                <tr>
                                    <th>IP</th>
                                    <th style="width: 160px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curLoadBalance.node_list.length">
                                    <tr v-for="(node, index) in curLoadBalance.node_list" :key="index">
                                        <td>
                                            {{node.inner_ip}}
                                        </td>
                                        <td>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="removeNode(index)">{{$t('删除')}}</a>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr>
                                        <td colspan="2">
                                            <div class="biz-no-data p30">{{$t('无数据')}}</div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>

                    <div class="bk-form-item mt25">
                        <bk-button type="primary" @click="saveLoadBalance">{{$t('保存')}}</bk-button>
                        <bk-button @click="hideLoadBalanceSlider">{{$t('取消')}}</bk-button>
                    </div>
                </div>
            </div>
        </bk-sideslider>

        <node-selector
            ref="bkNodeSelector"
            :selected="curLoadBalance.node_list"
            @selected="handlerSelectNode">
        </node-selector>
    </div>
</template>

<script>
    import nodeSelector from '@open/components/node-selector'
    import { catchErrorHandler, formatDate } from '@open/common/util'

    export default {
        components: {
            nodeSelector
        },
        data () {
            return {
                formatDate: formatDate,
                isPageLoading: false,
                pageConf: {
                    total: 0,
                    totalPage: 1,
                    pageSize: 5,
                    curPage: 1,
                    show: true
                },
                curLoadBalance: {
                    'name': '',
                    'namespace': '',
                    'project_id': '',
                    'cluster_id': '',
                    'protocol': {
                        'http': {
                            port: 80,
                            isUse: true
                        },
                        'https': {
                            port: 443,
                            isUse: true
                        }
                    },
                    'node_list': []
                },
                statusTimer: [],
                nameSpaceClusterList: [],
                isAllDataLoad: false,
                searchKeyword: '',
                searchScope: '',
                isInitLoading: true,
                exceptionCode: null,
                isDataSaveing: false,
                isLoadBalanceLoading: false,
                prmissions: {},
                clusterIndex: 0,
                loadBalanceSlider: {
                    title: '',
                    isShow: false
                }
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            varList () {
                return this.$store.state.variable.varList
            },
            projectId () {
                return this.$route.params.projectId
            },
            loadBalanceList () {
                let list = Object.assign([], this.$store.state.network.loadBalanceList)
                list = this.formatDataToClient(list)
                return list
            },
            clusterList () {
                const clusterList = this.$store.state.cluster.clusterList
                const list = clusterList.map(cluster => {
                    cluster.longName = `${cluster.name}(${cluster.cluster_id})`
                    return cluster
                })
                return list
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
            curProject () {
                return this.$store.state.curProject
            },
            isClusterDataReady () {
                return this.$store.state.cluster.isClusterDataReady
            }
        },
        watch: {
            loadBalanceList () {
                const data = this.getDataByPage(this.pageConf.curPage)
                this.curPageData = this.formatDataToClient(data)
            },
            curPageData () {
                this.curPageData.forEach(item => {
                    if (this.loadBalanceFixStatus.indexOf(item.status) === -1) {
                        this.getLoadBalanceStatus(item)
                    }
                })
            },
            isClusterDataReady: {
                immediate: true,
                handler (val) {
                    if (val) {
                        setTimeout(() => {
                            if (this.searchScopeList.length) {
                                const clusterIds = this.searchScopeList.map(item => item.id)
                                // 使用当前缓存
                                if (sessionStorage['bcs-cluster'] && clusterIds.includes(sessionStorage['bcs-cluster'])) {
                                    this.searchScope = sessionStorage['bcs-cluster']
                                } else {
                                    this.searchScope = this.searchScopeList[1].id
                                }
                            }
                            
                            this.getLoadBalanceList()
                        }, 1000)
                    }
                }
            }
        },
        created () {
            this.initPageConf()
        },
        methods: {
            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.getLoadBalanceList()
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
                this.handlerPageChange()
            },

            /**
             * 切换页面时回调
             */
            leaveCallback () {
                for (const key of Object.keys(this.statusTimer)) {
                    clearInterval(this.statusTimer[key])
                }
                this.$store.commit('network/updateLoadBalanceList', [])
            },

            /**
             * 显示节点选择器
             */
            showNodeSelector () {
                if (!this.curLoadBalance.cluster_id) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择所属集群')
                    })
                    return false
                }
                this.$refs.bkNodeSelector.openDialog(this.curLoadBalance.cluster_id)
            },

            /**
             * 选择节点
             * @param  {object} data 节点
             */
            handlerSelectNode (data) {
                const nodeList = data.map(item => {
                    return {
                        id: item.id,
                        inner_ip: item.inner_ip,
                        unshared: false
                    }
                })

                this.curLoadBalance.node_list = nodeList
            },

            /**
             * 删除节点
             * @param  {number} index 节点索引
             */
            removeNode (index) {
                this.curLoadBalance.node_list.splice(index, 1)
            },

            /**
             * 创建新的LB
             */
            createLoadBlance () {
                this.nameSpaceSelectedList = []
                this.curLoadBalance = {
                    'name': '',
                    'namespace': '',
                    'project_id': this.projectId,
                    'cluster_id': '',
                    'protocol': {
                        'http': {
                            port: 80,
                            isUse: true
                        },
                        'https': {
                            port: 443,
                            isUse: true
                        }
                    },
                    'node_list': []
                }
                this.loadBalanceSlider.title = this.$t('新建LoadBalancer')
                this.loadBalanceSlider.isShow = true
            },

            /**
             * 对返回的lb进行处理
             * @param  {object} loadBalance loadBalance
             * @return {object} loadBalance loadBalance
             */
            formatLoadBalance (loadBalance) {
                const protocols = loadBalance.protocol_type.split(';')
                loadBalance.protocol = {
                    'http': {
                        port: 80,
                        isUse: false
                    },
                    'https': {
                        port: 443,
                        isUse: false
                    }
                }
                protocols.forEach(protocol => {
                    const confs = protocol.split(':')
                    loadBalance.protocol[confs[0]] = {
                        port: confs[1],
                        isUse: true
                    }
                })
                loadBalance.namespace = loadBalance.namespace_id
                loadBalance.node_list = JSON.parse(loadBalance.ip_info)
                return loadBalance
            },

            /**
             * 编辑LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async editLoadBalance (loadBalance, index) {
                if (!loadBalance.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: loadBalance.namespace,
                        resource_name: loadBalance.namespace_name,
                        resource_type: 'namespace'
                    })
                }

                const projectId = this.projectId
                const projectKind = this.curProject.kind
                const loadBalanceId = loadBalance.id

                this.nameSpaceSelectedList = []
                this.isDataSaveing = true

                try {
                    const res = await this.$store.dispatch('network/getLoadBalanceDetail', {
                        projectId,
                        loadBalanceId,
                        projectKind
                    })

                    const loadBalance = this.formatLoadBalance(res.data)
                    this.curLoadBalance = loadBalance
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }

                this.loadBalanceSlider.title = this.$t('编辑LoadBalancer')
                this.loadBalanceSlider.isShow = true
            },

            /**
             * 选择集群回调
             * @param  {number}  index 集群索引（ID）
             * @param  {object}  data 集群
             * @param  {boolean} isInitTrigger 是否在进入页面时触发
             */
            async handlerSelectCluster (index, data, isInitTrigger) {
                const projectId = this.projectId
                const clusterId = index
                if (!isInitTrigger) {
                    this.curLoadBalance.namespace = ''
                }
                if (projectId && clusterId) {
                    try {
                        const res = await this.$store.dispatch('network/getNameSpaceClusterList', { projectId, clusterId })
                        this.nameSpaceClusterList = res.data
                        this.nameSpaceList = res.data
                        this.nameSpaceList.forEach(item => {
                            item.isSelected = false
                        })
                        this.nameSpaceSelectedList = []
                    } catch (e) {
                        catchErrorHandler(e, this)
                    }
                } else {
                    this.nameSpaceClusterList = []
                }
            },

            /**
             * 删除LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async removeLoadBalance (loadBalance, index) {
                if (!loadBalance.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: loadBalance.namespace,
                        resource_name: loadBalance.namespace_name,
                        resource_type: 'namespace'
                    })
                }

                const self = this
                const projectId = this.projectId
                const projectKind = this.curProject.kind
                const loadBalanceId = loadBalance.id
                this.$bkInfo({
                    title: '',
                    clsName: 'biz-remove-dialog',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, this.$t('确定要删除LoadBalancer')),
                    async confirmFn () {
                        self.isPageLoading = true

                        try {
                            await self.$store.dispatch('network/removeLoadBalance', {
                                projectId,
                                loadBalanceId,
                                projectKind
                            })
                            self.$bkMessage({
                                theme: 'success',
                                message: self.$t('删除成功')
                            })
                            self.getLoadBalanceList()
                        } catch (e) {
                            catchErrorHandler(e, this)
                            self.isPageLoading = false
                        }
                    }
                })
            },

            /**
             * 清空搜索
             */
            clearSearch () {
                this.searchKeyword = ''
                this.searchLoadBalance()
            },

            /**
             * 搜索LB
             */
            searchLoadBalance () {
                const keyword = this.searchKeyword.trim()
                const keyList = ['cluster_name', 'namespace_name']
                let list = this.$store.state.network.loadBalanceList
                let results = []

                if (this.searchScope) {
                    list = list.filter(item => item.cluster_id === this.searchScope)
                }

                results = list.filter(item => {
                    for (const key of keyList) {
                        if (item[key].indexOf(keyword) > -1) {
                            return true
                        }
                    }
                    return false
                })
                this.loadBalanceList.splice(0, this.loadBalanceList.length, ...results)
                this.pageConf.curPage = 1
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.loadBalanceList.length
                this.pageConf.total = total
                this.pageConf.curPage = 1
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
            },

            /**
             * 重新加载当前页
             */
            reloadCurPage () {
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 获取页数据
             * @param  {number} page 页
             * @return {object} data lb
             */
            getDataByPage (page) {
                // 如果没有page，重置
                if (!page) {
                    this.pageConf.curPage = page = 1
                }
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                this.isPageLoading = true
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.loadBalanceList.length) {
                    endIndex = this.loadBalanceList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.loadBalanceList.slice(startIndex, endIndex)
            },

            /**
             * 分页改变回调
             * @param  {number} page 页
             */
            handlerPageChange (page = 1) {
                this.isPageLoading = true
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData = JSON.parse(JSON.stringify(data))
            },

            /**
             * 隐藏lb侧面板
             * @return {[type]} [description]
             */
            hideLoadBalanceSlider () {
                this.curLoadBalance = {
                    'name': '',
                    'namespace': '',
                    'project_id': this.projectId,
                    'cluster_id': '',
                    'protocol': {
                        'http': {
                            port: 80,
                            isUse: true
                        },
                        'https': {
                            port: 443,
                            isUse: true
                        }
                    },
                    'node_list': []
                }

                this.loadBalanceSlider.isShow = false
            },

            /**
             * 获取loadBalanceList
             */
            async getLoadBalanceList () {
                try {
                    const project = this.curProject
                    const params = {
                        cluster_id: this.searchScope
                    }
                    this.isPageLoading = true
                    await this.$store.dispatch('network/getLoadBalanceListByPage', {
                        project,
                        params
                    })
                    this.isAllDataLoad = true
                    this.initPageConf()
                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchKeyword) {
                        this.searchLoadBalance()
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
             * 获取集群列表
             */
            async getClusterList () {
                try {
                    await this.$store.dispatch('network/getClusterList', this.projectId)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 检查提交的数据
             * @return {boolean} true/false 是否合法
             */
            checkData () {
                const data = this.formatDataToServer()
                if (!data.cluster_id) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择所属集群'),
                        delay: 5000
                    })
                    return false
                }

                if (!data.namespace_id) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择命名空间'),
                        delay: 5000
                    })
                    return false
                }

                if (data.protocols.http.isUse && !data.protocols.http.port) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入http端口'),
                        delay: 5000
                    })
                    return false
                }

                if (data.protocols.https.isUse && !data.protocols.https.port) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入https端口'),
                        delay: 5000
                    })
                    return false
                }

                if (data.ip_info === '{}') {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请添加节点'),
                        delay: 5000
                    })
                    return false
                }

                return true
            },

            /**
             * 对接口返回的数据进行格式化以适应前端数据
             * @param  {array} list loadBalance列表
             * @return {array} list loadBalance列表
             */
            formatDataToClient (list) {
                list.forEach(item => {
                    item.namespace = item.namespace_id
                    item.protocol = {
                        'http': {
                            port: 80,
                            isUse: false
                        },
                        'https': {
                            port: 443,
                            isUse: false
                        }
                    }

                    // eg: http:8080;https:443;
                    const protocols = item.protocol_type.split(';')
                    protocols.forEach(protocol => {
                        const confs = protocol.split(':')
                        if (['http', 'https'].includes(confs[0])) {
                            item.protocol[confs[0]] = {
                                port: confs[1],
                                isUse: true
                            }
                        }
                    })

                    // 例如"{"244":true}"
                    const ipInfo = JSON.parse(item.ip_info)
                    item.node_list = []
                    item.unsharedNum = 0

                    for (const key in ipInfo) {
                        item.node_list.push({
                            id: key,
                            unshared: ipInfo[key]
                        })
                        if (ipInfo[key]) {
                            item.unsharedNum++
                        }
                    }
                    item.nodeNum = item.node_list.length
                })
                return list
            },

            /**
             * 对前端数据进行格式化以适应接口数据
             * @return {object} serverData serverData
             */
            formatDataToServer () {
                const data = this.curLoadBalance
                const protocols = data.protocol
                const nodeList = data.node_list
                const nodeTmp = {}
                const serverData = {
                    id: 0,
                    name: data.name,
                    project_id: data.project_id,
                    cluster_id: data.cluster_id,
                    namespace_id: data.namespace,
                    protocol_type: '',
                    ip_info: {},
                    protocols: data.protocol
                }

                if (data.id) {
                    serverData.id = data.id
                }

                if (protocols.http.isUse) {
                    serverData.protocol_type = `http:${protocols.http.port}`
                }

                if (protocols.https.isUse) {
                    serverData.protocol_type += `;https:${protocols.https.port};`
                }

                nodeList.forEach(node => {
                    nodeTmp[node.id] = node.unshared
                })
                serverData.ip_info = JSON.stringify(nodeTmp)
                return serverData
            },

            /**
             * 保存新建的LB
             */
            async createLoadBalance () {
                const projectId = this.projectId
                const data = this.formatDataToServer()

                this.isDataSaveing = true

                try {
                    await this.$store.dispatch('network/addK8sLoadBalance', { projectId, data })
                    this.searchScope = data.cluster_id
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('数据保存成功')
                    })
                    this.getLoadBalanceList()
                    this.hideLoadBalanceSlider()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }
            },

            /**
             * 保存更新的LB
             */
            async updateLoadBalance () {
                const projectId = this.projectId
                const data = this.formatDataToServer()
                const loadBalanceId = data.id
                const projectKind = this.curProject.kind

                this.isDataSaveing = true

                try {
                    await this.$store.dispatch('network/updateLoadBalance', {
                        projectId,
                        loadBalanceId,
                        data,
                        projectKind
                    })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('数据保存成功')
                    })
                    this.getLoadBalanceList()
                    this.hideLoadBalanceSlider()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }
            },

            /**
             * 保存LB
             */
            saveLoadBalance () {
                if (this.checkData()) {
                    if (this.curLoadBalance.id > 0) {
                        this.updateLoadBalance()
                    } else {
                        this.createLoadBalance()
                    }
                }
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '../../loadbalance.css';
    @import './index.css';
</style>
