<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-loadbalance-title">
                LoadBalance
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
                            <span>新建LoadBalance</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="'输入关键字，按Enter搜索'"
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="searchLoadBalance"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>

                <div class="biz-loadbalance">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table has-table-hover biz-table biz-loadbalance-table">
                            <thead>
                                <tr>
                                    <th style="width: 160px;">名称</th>
                                    <th>所属集群</th>
                                    <th>网络类型</th>
                                    <th>转发模式</th>
                                    <th style="min-width: 100px;">状态</th>
                                    <th style="min-width: 220px;">操作</th>
                                </tr>
                            </thead>
                            <tbody>

                                <template v-if="loadBalanceList.length">
                                    <tr v-for="(loadBalance, index) in curPageData" :key="index">
                                        <td>
                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="loadBalanceFixStatus.indexOf(loadBalance.status) === -1" style="margin-left: -20px;">
                                                <div class="rotate rotate1"></div>
                                                <div class="rotate rotate2"></div>
                                                <div class="rotate rotate3"></div>
                                                <div class="rotate rotate4"></div>
                                                <div class="rotate rotate5"></div>
                                                <div class="rotate rotate6"></div>
                                                <div class="rotate rotate7"></div>
                                                <div class="rotate rotate8"></div>
                                            </div>
                                            <a href="javascript:void(0)" class="bk-text-button biz-table-title" @click="goLoadBalanceDetail(loadBalance)">{{loadBalance.name || '--'}}</a>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="loadBalance.cluster_id" placement="top">
                                                <div class="cluster-name biz-text-wrapper">{{loadBalance.cluster_name}}</div>
                                            </bk-tooltip>
                                        </td>
                                        <td>{{loadBalance.network_type || '--'}}</td>
                                        <td>{{loadBalance.forward_mode || '--'}}</td>
                                        <td>
                                            <template v-if="loadBalance.status_name && loadBalance.status_name.length">
                                                <bk-tooltip placement="top">
                                                    <p v-for="(item, itemIndex) in loadBalance.status_name" :key="itemIndex">
                                                        {{item}}
                                                    </p>
                                                    <template slot="content">
                                                        <p v-for="(tip, tipIndex) in loadBalance.status_tips" :key="tipIndex">
                                                            {{tip}}
                                                        </p>
                                                    </template>
                                                </bk-tooltip>
                                            </template>
                                            <template v-else>
                                                --
                                            </template>
                                        </td>
                                        <td>
                                            <!--
                                                1. "notCreated": u"未创建", "deleted": u"已停止"   : 操作：启动、编辑、删除
                                                2. 'Deploying', 'Running', 'Update', 'UpdatePaused', 'UpdateSuspend'：操作：停止
                                                3. Deleting : 操作：无
                                                4. 为空，操作：无
                                                5. 全部都可以查看
                                            -->
                                            <a href="javascript:void(0)" class="bk-text-button" @click="goLoadBalanceDetail(loadBalance)">查看</a>
                                            <template v-if="loadBalance.status === 'notCreated' || loadBalance.status === 'deleted'">
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="runLoadBalance(loadBalance, index)">启动</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="editLoadBalance(loadBalance, index)">编辑</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="removeLoadBalance(loadBalance, index)">删除</a>
                                            </template>
                                            <template v-else-if="loadBalance.status !== ''">
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="stopLoadBalance(loadBalance, index)" v-if="loadBalance.is_delete_lb">停止</a>
                                            </template>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="6">
                                            <div class="biz-app-list">
                                                <div class="bk-message-box">
                                                    <p class="message empty-message" v-if="!isInitLoading">无数据</p>
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

            <bk-sideslider
                style="z-index: 150;"
                :quick-close="false"
                :is-show.sync="loadBalanceSlider.isShow"
                :title="loadBalanceSlider.title"
                :width="'640'"
                @shown="handlerShowSideslider"
                @hidden="handlerHideSideslider">
                <div class="p30" slot="content">
                    <div class="bk-form bk-form-vertical" @click="handlerHideSideslider">
                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px;">
                                    <label class="bk-label">名称：</label>
                                    <div class="bk-form-content">
                                        <input
                                            type="text"
                                            class="bk-form-input"
                                            placeholder="请输入30个以内的字符"
                                            v-model="curLoadBalance.name"
                                            maxlength="30" />
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 260px; margin-left: 35px;">
                                    <label class="bk-label">所属集群：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :field-type="'cluster'"
                                            placeholder="请选择"
                                            :setting-key="'cluster_id'"
                                            :display-key="'name'"
                                            :is-link="true"
                                            :selected.sync="curLoadBalance.cluster_id"
                                            :list="clusterList"
                                            @item-selected="handlerSelectCluster">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px;">
                                    <label class="bk-label">镜像地址：</label>
                                    <div class="bk-form-content">
                                        <input class="bk-form-input" readonly :value="curLoadBalance.image_url" />
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 260px; margin-left: 35px;">
                                    <label class="bk-label">镜像版本：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            placeholder="请选择"
                                            :setting-key="'_id'"
                                            :display-key="'_name'"
                                            :selected.sync="curLoadBalance.image_version"
                                            :list="imageVersionList">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px;">
                                    <label class="bk-label">实例数量：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            type="number"
                                            placeholder="请输入"
                                            style="width: 260px;"
                                            :value.sync="curLoadBalance.instance">
                                        </bk-input>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <label class="bk-label">调度约束：</label>
                                <div class="bk-form-content">
                                    <div class="biz-keys-list mb10">
                                        <div class="biz-key-item" v-for="(constraint, index) in curLoadBalance.constraints" :key="index">
                                            <div class="bk-dropdown-box">
                                                <bk-combobox
                                                    type="text"
                                                    placeholder="请输入"
                                                    style="width: 130px;"
                                                    :value.sync="constraint.unionData[0].name"
                                                    :display-key="'name'"
                                                    :search-key="'name'"
                                                    :setting-key="'id'"
                                                    :list="constraintNameList">
                                                </bk-combobox>
                                            </div>
                                            <div class="bk-dropdown-box">
                                                <template v-if="constraint.unionData[0].name !== 'ip-resources'">
                                                    <bk-selector
                                                        placeholder="请选择"
                                                        :setting-key="'id'"
                                                        :selected.sync="constraint.unionData[0].operate"
                                                        :list="operatorList"
                                                        @item-selected="handlerSelectOperate(constraint.unionData[0])">
                                                    </bk-selector>
                                                </template>
                                                <template v-else>
                                                    <bk-selector
                                                        placeholder="请选择"
                                                        :setting-key="'id'"
                                                        :disabled="true"
                                                        :selected.sync="constraint.unionData[0].operate"
                                                        :list="operatorListForIP">
                                                    </bk-selector>
                                                </template>
                                            </div>

                                            <template v-if="constraint.unionData[0].name !== 'ip-resources'">
                                                <bk-input
                                                    type="text"
                                                    placeholder="多个值以管道符分隔"
                                                    style="width: 220px;"
                                                    :disabled="constraint.unionData[0].operate === 'UNIQUE'"
                                                    :value.sync="constraint.unionData[0].arg_value"
                                                    :list="varList">
                                                </bk-input>
                                            </template>
                                            <template v-else>
                                                <bk-input
                                                    type="number"
                                                    placeholder="请输入"
                                                    style="width: 220px;"
                                                    :value.sync="constraint.unionData[0].arg_value"
                                                    :list="varList">
                                                </bk-input>
                                            </template>

                                            <button class="action-btn" @click.stop.prevent="removeConstraint(constraint, index)" v-show="curLoadBalance.constraints.length > 1">
                                                <i class="bk-icon icon-minus"></i>
                                            </button>
                                            <button class="action-btn" @click.stop.prevent="addConstraint()">
                                                <i class="bk-icon icon-plus"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item" style="width: 260px;">
                                    <label class="bk-label">CPU：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            type="number"
                                            placeholder="请输入"
                                            style="width: 260px;"
                                            :value.sync="curLoadBalance.resources.limits.cpu">
                                        </bk-input>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item" style="width: 260px; margin-left: 35px;">
                                    <label class="bk-label">内存：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            type="number"
                                            placeholder="请输入"
                                            style="width: 260px;"
                                            :value.sync="curLoadBalance.resources.limits.memory">
                                        </bk-input>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <label class="bk-label">网络类型：</label>
                                <div class="bk-form-content">
                                    <label class="bk-form-radio">
                                        <input type="radio" name="network_model" value="cni" v-model="curLoadBalance.network_type">
                                        <i class="bk-radio-text">cni</i>
                                    </label>
                                    <label class="bk-form-radio">
                                        <input type="radio" name="network_model" value="cnm" v-model="curLoadBalance.network_type" :disabled="curLoadBalance.network_mode === 'USER'">
                                        <i class="bk-radio-text">cnm</i>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px; ">
                                    <label class="bk-label">网络模式：</label>
                                    <div class="bk-form-content">
                                        <div class="bk-dropdown-box" style="width: 260px;">
                                            <bk-selector
                                                placeholder="请选择"
                                                :setting-key="'id'"
                                                :display-key="'name'"
                                                :selected.sync="curLoadBalance.network_mode"
                                                :list="netList"
                                                @item-selected="handlerSelectNetwork">
                                            </bk-selector>
                                        </div>
                                        <transition name="fade">
                                            <input type="text" class="bk-form-input" style="width: 220px;" placeholder="自定义值" v-model="curLoadBalance.custom_value" v-if="curLoadBalance.network_mode === 'CUSTOM'">
                                        </transition>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 260px; margin-left: 35px;" v-if="curLoadBalance.network_mode === 'BRIDGE'">
                                    <label class="bk-label">端口：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            type="number"
                                            placeholder="请输入"
                                            style="width: 260px;"
                                            :min="31000"
                                            :max="32000"
                                            :value.sync="curLoadBalance.host_port">
                                        </bk-input>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <label class="bk-label">转发模式：</label>
                                <div class="bk-form-content">
                                    <label class="bk-form-radio">
                                        <input type="radio" name="forward_mode" value="haproxy" v-model="curLoadBalance.forward_mode" />
                                        <i class="bk-radio-text">haproxy</i>
                                    </label>
                                    <label class="bk-form-radio">
                                        <input type="radio" name="forward_mode" value="nginx" v-model="curLoadBalance.forward_mode" />
                                        <i class="bk-radio-text">nginx</i>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px;">
                                    <label class="bk-label">网卡：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            type="text"
                                            placeholder="请输入"
                                            style="width: 260px;"
                                            :value.sync="curLoadBalance.eth_value"
                                            :list="varList">
                                        </bk-input>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item mt25">
                            <button class="bk-button bk-primary" @click.stop.prevent="saveLoadBalance">保存</button>
                            <button class="bk-button bk-default" @click.stop.prevent="hideLoadBalanceSlider">取消</button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import bkCombobox from '@open/components/bk-combobox'
    import { catchErrorHandler } from '@open/common/util'

    export default {
        components: {
            bkCombobox
        },
        data () {
            return {

                isInitLoading: true,
                isPageLoading: false,
                exceptionCode: null,
                isNamespacePanelShow: false,
                curPageData: [],
                isAllDataLoad: false,
                isDataSaveing: false,
                prmissions: {},
                pageConf: {
                    total: 0,
                    totalPage: 1,
                    pageSize: 5,
                    curPage: 1,
                    show: true
                },
                loadBalanceSlider: {
                    title: '新建LoadBalance',
                    isShow: false
                },
                clusterIndex: 0,
                constraintNameIndex: 'hostname',
                loadBalanceFixStatus: [
                    'notCreated',
                    'deleted',
                    'Running',
                    'UpdateSuspend',
                    'UpdatePaused'
                ],
                constraintNameList: [
                    {
                        id: 'hostname',
                        name: 'hostname'
                    },
                    {
                        id: 'InnerIP',
                        name: 'InnerIP'
                    }
                ],
                statusTimer: {},
                imageVersionList: [],
                searchKeyword: '',
                searchScope: '',
                operatorIndex: -1,
                operatorList: [
                    {
                        id: 'CLUSTER',
                        name: 'CLUSTER'
                    },
                    {
                        id: 'GROUPBY',
                        name: 'GROUPBY'
                    },
                    {
                        id: 'LIKE',
                        name: 'LIKE'
                    },
                    {
                        id: 'UNLIKE',
                        name: 'UNLIKE'
                    },
                    {
                        id: 'UNIQUE',
                        name: 'UNIQUE'
                    },
                    {
                        id: 'MAXPER',
                        name: 'MAXPER'
                    }
                ],
                operatorListForIP: [
                    {
                        id: 'GREATER',
                        name: 'GREATER'
                    }
                ],
                nameSpaceSelectedList: [],
                loadBalanceListCache: [],
                nameSpaceList: [],
                nameSpaceClusterList: [],
                globalImageId: 'public/bcs/mesos/bcs-loadbalance',
                curLoadBalance: {
                    'name': '',
                    'cluster_id': '',
                    'ips': '',
                    'ip_list': [],
                    'instance': '',
                    'network_mode': 'BRIDGE',
                    'custom_value': '',
                    'network_type': 'cnm',
                    'resources': {
                        'limits': {
                            'cpu': '1',
                            'memory': '1024'
                        }
                    },
                    'forward_mode': 'haproxy',
                    'image_url': '/' + this.globalImageId,
                    'image_version': '',
                    'eth_value': 'eth1',
                    'host_port': 31000,
                    'constraints': [
                        {
                            'unionData': [
                                {
                                    'name': 'hostname',
                                    'operate': 'CLUSTER',
                                    'type': 4,
                                    'arg_value': '',
                                    'text': {
                                        value: ''
                                    },
                                    'set': {
                                        item: []
                                    }
                                }
                            ]
                        }
                    ],
                    'type': 'append'
                },
                netList: [
                    {
                        id: 'HOST',
                        name: 'HOST'
                    },
                    {
                        id: 'BRIDGE',
                        name: 'BRIDGE'
                    },
                    {
                        id: 'FLANNEL',
                        name: 'FLANNEL'
                    },
                    {
                        id: 'MACVLAN',
                        name: 'MACVLAN'
                    },
                    {
                        id: 'CUSTOM',
                        name: '自定义'
                    }
                ]
            }
        },
        computed: {
            varList () {
                return this.$store.state.variable.varList
            },
            projectId () {
                return this.$route.params.projectId
            },
            loadBalanceList () {
                return Object.assign([], this.$store.state.network.loadBalanceList)
            },
            clusterList () {
                const clusterList = this.$store.state.network.clusterList
                clusterList.forEach(cluster => {
                    cluster.name = `${cluster.name}(${cluster.cluster_id})`
                })
                return clusterList
            },
            searchScopeList () {
                const clusterList = this.$store.state.cluster.clusterList
                let results = []
                if (clusterList.length) {
                    results = [{
                        id: '',
                        name: '全部集群'
                    }]
                    clusterList.forEach(item => {
                        results.push({
                            id: item.cluster_id,
                            name: item.name
                        })
                    })
                }

                return results
            },
            curProject () {
                return this.$store.state.curProject
            }
        },
        watch: {
            'curLoadBalance.network_mode' (val) {
                if (val === 'USER') {
                    this.curLoadBalance.network_type = 'cni'
                } else if (val !== 'CUSTOM') {
                    this.curLoadBalance.network_type = 'cnm'
                }
            },
            loadBalanceList () {
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },
            curPageData () {
                this.curPageData.forEach(item => {
                    if (this.loadBalanceFixStatus.indexOf(item.status) === -1) {
                        this.getLoadBalanceStatus(item)
                    }
                })
            }
        },
        created () {
            if (!this.loadBalanceList.length) {
                this.getLoadBalanceListFirstPage()
                this.getClusterList()
            } else {
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
                this.isInitLoading = false
                this.isAllDataLoad = true
            }
            this.getImageTagList()
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
             * 获取镜像Tag列表
             */
            async getImageTagList (value, data, isInitTrigger) {
                const projectId = this.projectId
                const imageId = this.globalImageId
                const isPub = true

                try {
                    const res = await this.$store.dispatch('mesosTemplate/getImageVertionList', { projectId, imageId, isPub })
                    const data = res.data
                    data.forEach(item => {
                        item._id = item.text
                        item._name = item.text
                    })
                    this.imageVersionList.splice(0, this.imageVersionList.length, ...data)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
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
             * 选择操作回调
             * @param  {object} data 操作
             */
            handlerSelectOperate (data) {
                const operate = data.operate
                if (operate === 'UNIQUE') {
                    data.type = 0
                    data.arg_value = ''
                }
            },

            /**
             * 查看LB详情
             * @param  {object} loadBalance loadBalance
             */
            async goLoadBalanceDetail (loadBalance) {
                if (!loadBalance.permissions.view) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: loadBalance.namespace,
                        resource_name: loadBalance.namespace_name,
                        resource_type: 'namespace'
                    })
                }

                this.$router.push({
                    name: 'loadBalanceDetail',
                    params: {
                        lbId: loadBalance.id
                    }
                })
            },

            /**
             * 删除调度约束
             * @param  {object} item 调度约束配置
             * @param  {number} index 索引
             */
            removeConstraint (item, index) {
                const constraints = this.curLoadBalance.constraints
                constraints.splice(index, 1)
            },

            /**
             * 添加调度约束
             */
            addConstraint () {
                const constraints = this.curLoadBalance.constraints
                constraints.push({
                    unionData: [
                        {
                            name: 'hostname',
                            operate: 'CLUSTER',
                            type: 4,
                            arg_value: '',
                            text: {
                                value: ''
                            },
                            set: {
                                item: []
                            }
                        }
                    ]
                })
            },

            /**
             * 新建LB
             */
            createLoadBlance () {
                this.nameSpaceSelectedList = []
                this.curLoadBalance = {
                    'name': '',
                    'cluster_id': '',
                    'ips': '',
                    'ip_list': [],
                    'network_mode': 'BRIDGE',
                    'custom_value': '',
                    'network_type': 'cnm',
                    'resources': {
                        'limits': {
                            'cpu': '1',
                            'memory': '1024'
                        }
                    },
                    'forward_mode': 'haproxy',
                    'image_url': '/' + this.globalImageId,
                    'image_version': '',
                    'eth_value': 'eth1',
                    'host_port': 31000,
                    'constraints': [
                        {
                            'unionData': [
                                {
                                    'name': 'hostname',
                                    'operate': 'CLUSTER',
                                    'type': 4,
                                    'arg_value': '',
                                    'text': {
                                        value: ''
                                    },
                                    'set': {
                                        item: []
                                    }
                                }
                            ]
                        }
                    ],
                    'ns_id_list': [],
                    'type': 'append'
                }

                this.loadBalanceSlider.isShow = true
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
                const loadBalanceParams = Object.assign({}, loadBalance)
                this.nameSpaceSelectedList = []
                loadBalanceParams.ips = loadBalanceParams.ip_list.join(' ')
                loadBalanceParams.type = 'append'
                this.nameSpaceList.forEach(namespace => {
                    namespace.isSelected = false
                })
                loadBalanceParams.ns_id_list.forEach(id => {
                    this.nameSpaceList.forEach(namespace => {
                        if (namespace.id === id) {
                            namespace.isSelected = true
                            this.nameSpaceSelectedList.push(namespace)
                        }
                    })
                })
                this.curLoadBalance = loadBalanceParams
                this.loadBalanceSlider.title = '编辑LoadBalance'
                this.loadBalanceSlider.isShow = true
            },

            /**
             * 选择网络回调
             */
            handlerSelectNetwork () {
                this.curLoadBalance.custom_value = ''
            },

            /**
             * 启动LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async runLoadBalance (loadBalance, index) {
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
                const loadBalanceId = loadBalance.id
                const loadBalanceName = loadBalance.name

                this.$bkInfo({
                    title: `确定要启动此LoadBalance: ${loadBalanceName}`,
                    async confirmFn () {
                        loadBalance.status = ''
                        try {
                            await self.$store.dispatch('network/createBcsLoadBalance', { projectId, loadBalanceId })
                            this.$bkMessage({
                                theme: 'success',
                                message: '已经将配置文件下发到后台，请稍后再详情中查看'
                            })
                            self.getLoadBalanceStatus(loadBalance, index)
                        } catch (e) {
                            catchErrorHandler(e, this)
                            e.is_update && self.getLoadBalanceList()
                        }
                    }
                })
            },

            /**
             * 停止LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async stopLoadBalance (loadBalance, index) {
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
                const loadBalanceId = loadBalance.id
                const loadBalanceName = loadBalance.name

                this.$bkInfo({
                    title: `确定要停止此LoadBalance: ${loadBalanceName}`,
                    async confirmFn () {
                        loadBalance.status = ''

                        try {
                            await self.$store.dispatch('network/stopBcsLoadBalance', { projectId, loadBalanceId })
                            self.getLoadBalanceStatus(loadBalance, index)
                        } catch (e) {
                            catchErrorHandler(e, this)
                        }
                    }
                })
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
                const loadBalanceId = loadBalance.id
                const loadBalanceName = loadBalance.name
                this.$bkInfo({
                    title: '',
                    clsName: 'biz-remove-dialog',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `确定要删除LoadBalance【${loadBalanceName}】？`),
                    async confirmFn () {
                        self.isPageLoading = true
                        try {
                            await self.$store.dispatch('network/removeLoadBalance', { projectId, loadBalanceId })
                            self.$bkMessage({
                                theme: 'success',
                                message: '删除成功！'
                            })
                            self.getLoadBalanceList()
                        } catch (e) {
                            catchErrorHandler(e, this)
                        } finally {
                            self.isPageLoading = false
                        }
                    }
                })
            },

            /**
             * 获取LB
             * @param  {number} loadBalanceId id
             * @return {object} loadBalance loadBalance
             */
            getLoadBalanceById (loadBalanceId) {
                return this.loadBalanceList.find(item => {
                    return item.id === loadBalanceId
                })
            },

            /**
             * 获取LB状态
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            getLoadBalanceStatus (loadBalance, index) {
                const projectId = this.projectId
                const loadBalanceId = loadBalance.id
                const self = this

                clearInterval(this.statusTimer[loadBalance.id])

                this.statusTimer[loadBalance.id] = setInterval(async () => {
                    if (this.loadBalanceSlider.isShow) {
                        return
                    }
                    try {
                        const res = await this.$store.dispatch('network/getLoadBalanceStatus', {
                            projectId,
                            loadBalanceId
                        })
                        const lb = res.results
                        if (self.loadBalanceFixStatus.indexOf(lb.status) > -1) {
                            clearInterval(self.statusTimer[loadBalance.id])
                        }
                    } catch (e) {
                        catchErrorHandler(e, this)
                    }
                }, 2000)
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
                let list = this.$store.state.network.loadBalanceList
                let results = []

                if (this.searchScope) {
                    list = list.filter(item => item.cluster_id === this.searchScope)
                }

                results = list.filter(item => {
                    if (item.name.indexOf(keyword) > -1 || item.cluster_name.indexOf(keyword) > -1 || item.ip_list.join(',').indexOf(keyword) > -1 || item.ns_name_list.join(',').indexOf(keyword) > -1) {
                        return true
                    } else {
                        return false
                    }
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
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
            },

            /**
             * 重新加载当前页
             */
            reloadCurPage () {
                this.initPageConf()
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
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
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData = JSON.parse(JSON.stringify(data))
            },

            /**
             * 隐藏lb侧面板
             */
            hideLoadBalanceSlider () {
                this.loadBalanceSlider.isShow = false
            },

            /**
             * 显示命名空间选择面板
             */
            showNamespacePanel () {
                this.nameSpaceList.forEach(namespace => {
                    namespace.isSelected = false
                })
                this.nameSpaceSelectedList.forEach(item => {
                    this.nameSpaceList.forEach(namespace => {
                        if (namespace.id === item.id) {
                            namespace.isSelected = true
                        }
                    })
                })
                this.isNamespacePanelShow = true
            },

            /**
             * 确认选择命名空间
             */
            confirmSelected () {
                const ids = []
                const resutls = []
                this.nameSpaceList.forEach(item => {
                    if (item.isSelected) {
                        resutls.push(item)
                        ids.push(item.id)
                    }
                })
                this.nameSpaceSelectedList = resutls
                this.curLoadBalance.ns_id_list = ids
                this.isNamespacePanelShow = false
            },

            /**
             * 隐藏创建LB侧栏回调
             */
            handlerHideSideslider () {
                this.isNamespacePanelShow = false
                // 重启状态轮询
                this.curPageData.forEach(item => {
                    if (this.loadBalanceFixStatus.indexOf(item.status) === -1) {
                        this.getLoadBalanceStatus(item)
                    }
                })
            },

            /**
             * 显示创建LB侧栏回调
             */
            handlerShowSideslider () {
                // 清除状态轮询
                for (const key in this.statusTimer) {
                    clearInterval(this.statusTimer[key])
                }
            },

            /**
             * 加载第一页LB数据，成功后再把所有数据加载进来，为加快首页渲染
             */
            async getLoadBalanceListFirstPage () {
                try {
                    const res = await this.$store.dispatch('network/getLoadBalanceListByPage', this.curProject)
                    this.curPageData = res.results
                    if (this.curPageData.length) {
                        await this.$store.dispatch('network/getLoadBalanceList', this.curProject)
                    }
                    this.isAllDataLoad = true
                    this.initPageConf()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 加载LB数据
             */
            async getLoadBalanceList () {
                try {
                    await this.$store.dispatch('network/getLoadBalanceList', this.curProject)
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)

                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchScope || this.searchKeyword) {
                        this.searchLoadBalance()
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 获取命名空间列表
             */
            async getNameSpaceList () {
                try {
                    const res = await this.$store.dispatch('network/getNameSpaceList', this.projectId)
                    const list = res.data
                    list.forEach(item => {
                        item.isSelected = false
                    })
                    this.nameSpaceList.splice(0, this.nameSpaceList.length, ...list)
                } catch (e) {
                    catchErrorHandler(e, this)
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
             * 选择/取消选择命名空间
             * @param  {object} nameSpace 命名空间
             * @param  {number} index 索引
             */
            toggleSelected (nameSpace, index) {
                nameSpace.isSelected = !nameSpace.isSelected
                this.nameSpaceList = JSON.parse(JSON.stringify(this.nameSpaceList))
            },

            /**
             * 检查提交的数据
             * @return {boolean} true/false 是否合法
             */
            checkData () {
                const appNameReg = /^[a-z]{1}[a-z0-9-]{0,29}$/
                const ipReg = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)($|(?!\.$)\.)){4}$/
                if (this.curLoadBalance.name === '') {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入名称！'
                    })
                    return false
                }
                if (!appNameReg.test(this.curLoadBalance.name)) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                        delay: 5000
                    })
                    return false
                }

                if (!this.curLoadBalance.cluster_id) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择所属集群！',
                        delay: 5000
                    })
                    return false
                }

                if (!this.curLoadBalance.image_version) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择镜像版本！',
                        delay: 5000
                    })
                    return false
                }

                if (this.curLoadBalance.ip_list.length) {
                    for (const ip of this.curLoadBalance.ip_list) {
                        if (!ipReg.test(ip)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: '请输入正确IP地址！',
                                delay: 3000
                            })
                            return false
                        }
                    }

                    if (this.curLoadBalance.ip_list.length !== Number(this.curLoadBalance.instance)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: 'IP数量和实例数量不相等',
                            delay: 3000
                        })
                        return false
                    }
                }

                if (!this.curLoadBalance.instance) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请填写实例数量！',
                        delay: 5000
                    })
                    return false
                }

                if (!this.curLoadBalance.eth_value) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请填写网卡！',
                        delay: 5000
                    })
                    return false
                }

                if (this.curLoadBalance.network_mode === 'BRIDGE' && !this.curLoadBalance.host_port) {
                    this.$bkMessage({
                        theme: 'error',
                        message: 'BRIDGE网络模式下，端口必填！',
                        delay: 5000
                    })
                    return false
                }

                return true
            },

            /**
             * 格式化数据，符合接口需要的格式
             */
            formatData () {
                // 转换ips
                const ips = this.curLoadBalance.ips
                if (ips) {
                    this.curLoadBalance.ip_list = ips.split(' ')
                } else {
                    this.curLoadBalance.ip_list = []
                }

                // 转换调度约束
                const constraints = this.curLoadBalance.constraints
                constraints.forEach(item => {
                    const data = item.unionData[0]
                    const operate = data.operate
                    switch (operate) {
                        case 'UNIQUE':
                            delete data.type
                            delete data.set
                            delete data.text
                            break
                        case 'MAXPER':
                            data.type = 3
                            data.text = {
                                'value': data.arg_value
                            }
                            delete data.set
                            break
                        case 'GREATER':
                            data.type = 1
                            delete data.set
                            delete data.text
                            data.scalar = {
                                'value': data.arg_value
                            }
                            break
                        case 'CLUSTER':
                            data.type = 4
                            if (data.arg_value.trim().length) {
                                data.set = {
                                    'item': data.arg_value.split('|')
                                }
                            } else {
                                data.set = {
                                    'item': []
                                }
                            }

                            delete data.text
                            break
                        case 'GROUPBY':
                            data.type = 4
                            if (data.arg_value.trim().length) {
                                data.set = {
                                    'item': data.arg_value.split('|')
                                }
                            } else {
                                data.set = {
                                    'item': []
                                }
                            }
                            delete data.text
                            break
                        case 'LIKE':
                            if (data.arg_value.indexOf('|') > -1) {
                                data.type = 4
                                if (data.arg_value.trim().length) {
                                    data.set = {
                                        'item': data.arg_value.split('|')
                                    }
                                } else {
                                    data.set = {
                                        'item': []
                                    }
                                }
                                delete data.text
                            } else {
                                data.type = 3
                                data.text = {
                                    'value': data.arg_value
                                }
                                delete data.set
                            }
                            break
                        case 'UNLIKE':
                            if (data.arg_value.indexOf('|') > -1) {
                                data.type = 4
                                if (data.arg_value.trim().length) {
                                    data.set = {
                                        'item': data.arg_value.split('|')
                                    }
                                } else {
                                    data.set = {
                                        'item': []
                                    }
                                }
                                delete data.text
                            } else {
                                data.type = 3
                                data.text = {
                                    'value': data.arg_value
                                }
                                delete data.set
                            }
                            break
                    }
                })
            },

            /**
             * 保存新建的LB
             */
            async createLoadBalance () {
                const projectId = this.projectId
                const data = this.curLoadBalance
                this.isDataSaveing = true
                try {
                    await this.$store.dispatch('network/addLoadBalance', { projectId, data })

                    this.$bkMessage({
                        theme: 'success',
                        message: '数据保存成功！'
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
                const data = this.curLoadBalance
                const loadBalanceId = data.id

                this.isDataSaveing = true

                try {
                    await this.$store.dispatch('network/updateLoadBalance', {
                        projectId,
                        loadBalanceId,
                        data
                    })

                    this.$bkMessage({
                        theme: 'success',
                        message: '数据保存成功！'
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
                this.formatData()
                if (this.checkData()) {
                    delete this.curLoadBalance.namespace

                    if (this.curLoadBalance.id > 0) {
                        this.updateLoadBalance()
                    } else {
                        this.createLoadBalance()
                    }
                }
            },

            /**
             * 获取变量列表
             */
            async getVarList () {
                try {
                    await this.$store.dispatch('variable/getVarList', this.projectId)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            }
        }
    }
</script>

<style scoped>
    @import '../../loadbalance.css';
    @import './index.css';
</style>
