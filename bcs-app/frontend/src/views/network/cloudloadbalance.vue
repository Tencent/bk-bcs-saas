<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-loadbalance-title">
                CloudLoadBalancer
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
                            <span>{{$t('新建CloudLoadBalancer')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="$t('输入关键字，按Enter搜索')"
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
                                    <th style="width: 200px; padding-left: 30px;">{{$t('名称')}}</th>
                                    <th style="width: 130px;">{{$t('区域')}}</th>
                                    <th style="width: 130px;">{{$t('类型')}}</th>
                                    <th>{{$t('所属集群')}}</th>
                                    <th>{{$t('网络类型')}}</th>
                                    <th>{{$t('状态')}}</th>
                                    <th style="min-width: 220px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>

                                <template v-if="loadBalanceList.length">
                                    <tr v-for="(loadBalance, index) in curPageData" :key="index">
                                        <td style="width: 200px; padding-left: 30px;">
                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="loadBalance.clb_status && loadBalance.clb_status !== 'Running'" style="margin-left: -20px;">
                                                <div class="rotate rotate1"></div>
                                                <div class="rotate rotate2"></div>
                                                <div class="rotate rotate3"></div>
                                                <div class="rotate rotate4"></div>
                                                <div class="rotate rotate5"></div>
                                                <div class="rotate rotate6"></div>
                                                <div class="rotate rotate7"></div>
                                                <div class="rotate rotate8"></div>
                                            </div>
                                            <a href="javascript:void(0)" class="bk-text-button biz-table-title" @click="goLoadBalanceDetail(loadBalance)">{{loadBalance.clb_name || '--'}}</a>
                                        </td>
                                        <td>{{loadBalance.region || '--'}}</td>
                                        <td>{{loadBalance.clb_type || '--'}}</td>
                                        <td>
                                            <bk-tooltip :content="loadBalance.cluster_id" placement="top">
                                                <div class="cluster-name biz-text-wrapper">{{loadBalance.cluster_id}}</div>
                                            </bk-tooltip>
                                        </td>
                                        <td>{{loadBalance.network_type || '--'}}</td>
                                        <td>{{loadBalance.clb_status || '--'}}</td>
                                        <td>
                                            <!--
                                                1. "notCreated": u"未创建", "deleted": u"已停止"   : 操作：启动、编辑、删除
                                                2. 'Deploying', 'Running', 'Update', 'UpdatePaused', 'UpdateSuspend'：操作：停止
                                                3. Deleting : 操作：无
                                                4. 为空，操作：无
                                                5. 全部都可以查看
                                            -->
                                            <a href="javascript:void(0)" class="bk-text-button" @click="goLoadBalanceDetail(loadBalance)">{{$t('查看')}}</a>
                                            <template v-if="loadBalance.status === 'not_created' || loadBalance.status === 'deleted'">
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="runLoadBalance(loadBalance, index)">{{$t('启动')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="editLoadBalance(loadBalance, index)">{{$t('编辑')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="removeLoadBalance(loadBalance, index)">{{$t('删除')}}</a>
                                            </template>
                                            <template v-else-if="loadBalance.status !== ''">
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="stopLoadBalance(loadBalance, index)">{{$t('停止')}}</a>
                                            </template>
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
                                
                                <div class="bk-form-inline-item" style="width: 260px;">
                                    <label class="bk-label">{{$t('区域')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :searchable="true"
                                            :placeholder="$t('请选择')"
                                            :selected.sync="curLoadBalance.region"
                                            :setting-key="'region'"
                                            :search-key="'region_name'"
                                            :display-key="'region_name'"
                                            :list="regionList"
                                            :is-link="true"
                                            @item-selected="handlerRegionSelect">
                                        </bk-selector>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 260px; margin-left: 35px;">
                                    <label class="bk-label">{{$t('名称')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请选择')"
                                            :selected.sync="curLoadBalance.clb_name"
                                            :list="nameInRegionList">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px;">
                                    <label class="bk-label">{{$t('所属集群')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :field-type="'cluster'"
                                            :placeholder="$t('请输入')"
                                            :setting-key="'cluster_id'"
                                            :display-key="'longName'"
                                            :selected.sync="curLoadBalance.cluster_id"
                                            :list="clusterList">
                                        </bk-selector>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 260px; margin-left: 35px;">
                                    <label class="bk-label">{{$t('类型')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请选择')"
                                            :selected.sync="curLoadBalance.clb_type"
                                            :list="types">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item" style="width: 260px;">
                                    <label class="bk-label">{{$t('镜像地址')}}：</label>
                                    <div class="bk-form-content">
                                        <input class="bk-form-input" readonly :value="curLoadBalance.image_url" />
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 260px; margin-left: 35px;">
                                    <label class="bk-label">{{$t('镜像版本')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请选择')"
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
                                <div class="bk-form-inline-item" style="width: 260px;">
                                    <label class="bk-label">{{$t('网络类型')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请选择')"
                                            :selected.sync="curLoadBalance.network_type"
                                            :list="networkTypes">
                                        </bk-selector>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item" style="width: 260px; margin-left: 35px;">
                                    <label class="bk-label">{{$t('服务发现机制')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请选择')"
                                            :selected.sync="curLoadBalance.svc_discovery_type"
                                            :list="serviceDiscoveryList">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item mt25">
                            <button class="bk-button bk-primary" @click.stop.prevent="saveLoadBalance">{{$t('保存')}}</button>
                            <button class="bk-button bk-default" @click.stop.prevent="hideLoadBalanceSlider">{{$t('取消')}}</button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'

    export default {
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
                    title: this.$t('新建CloudLoadBalancer'),
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
                statusTimer: {},
                imageVersionList: [],
                searchKeyword: '',
                searchScope: '',
                operatorIndex: -1,
                nameSpaceSelectedList: [],
                loadBalanceListCache: [],
                nameSpaceList: [],
                nameSpaceClusterList: [],
                nameInRegionList: [],
                globalImageId: 'paas/public/bcs/clb-controller',
                curLoadBalance: {
                    'clb_name': '',
                    'cluster_id': '',
                    'region': '',
                    'clb_type': 'private',
                    'image_url': '/' + this.globalImageId,
                    'image_version': '',
                    'image': '/paas/public/bcs/clb-controller:0.2.2',
                    'network_type': 'overlay',
                    'svc_discovery_type': 'custom'
                },
                types: [
                    {
                        id: 'private',
                        name: 'private'
                    },
                    {
                        id: 'public',
                        name: 'public'
                    }
                ],
                networkTypes: [
                    {
                        id: 'underlay',
                        name: 'underlay'
                    },
                    {
                        id: 'overlay',
                        name: 'overlay'
                    }
                ],
                serviceDiscoveryList: [
                    {
                        id: 'custom',
                        name: 'custom'
                    },
                    {
                        id: 'mesos',
                        name: 'mesos'
                    }
                ],
                regionList: []
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
                const list = Object.assign([], this.$store.state.network.cloudLoadBalanceList)
                const keyword = this.searchKeyword.trim()
                const results = list.filter(item => {
                    if (item.clb_name.indexOf(keyword) > -1 || item.cluster_id.indexOf(keyword) > -1) {
                        return true
                    } else {
                        return false
                    }
                })
                return results
            },
            clusterList () {
                const clusterList = this.$store.state.cluster.clusterList
                clusterList.forEach(cluster => {
                    cluster.longName = `${cluster.name}(${cluster.cluster_id})`
                })
                return clusterList
            },
            searchScopeList () {
                const clusterList = this.$store.state.cluster.clusterList
                let results = []
                if (clusterList.length) {
                    results = [{
                        id: '',
                        name: this.$t('全部集群')
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
            },
            isClusterDataReady () {
                return this.$store.state.cluster.isClusterDataReady
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
                    if (item.clb_status && item.clb_status !== 'Running') {
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
            // 如果不是mesos类型的项目，无法访问页面，重定向回集群首页
            if (this.curProject && this.curProject.kind !== PROJECT_MESOS) {
                this.$router.push({
                    name: 'clusterMain',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
                return false
            }

            this.getImageTagList()
            this.getRegions()
        },
        beforeRouteLeave (to, from, next) {
            this.leaveCallback()
            next(true)
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
             * 获取区域列表
             */
            async getRegions () {
                const projectId = this.projectId

                try {
                    const res = await this.$store.dispatch('network/getRegions', { projectId })
                    this.regionList = res.data
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
                this.$store.commit('network/updateCloudLoadBalanceList', [])
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
             * 选择地区回调
             */
            async handlerRegionSelect (data) {
                const region = data
                const projectId = this.projectId
                try {
                    const res = await this.$store.dispatch('network/getCloudLoadBalanceNames', { projectId, region })
                    this.nameInRegionList = []
                    res.data.forEach(item => {
                        this.nameInRegionList.push({
                            id: item,
                            name: item
                        })
                    })
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 查看LB详情
             * @param  {object} loadBalance loadBalance
             */
            async goLoadBalanceDetail (loadBalance) {
                // if (loadBalance.permissions && !loadBalance.permissions.view) {
                //     await this.$store.dispatch('getResourcePermissions', {
                //         project_id: this.projectId,
                //         policy_code: 'view',
                //         resource_code: loadBalance.namespace,
                //         resource_name: loadBalance.namespace_name,
                //         resource_type: 'namespace'
                //     })
                // }
                this.$router.push({
                    name: 'cloudLoadBalanceDetail',
                    params: {
                        instanceId: '0',
                        instanceName: loadBalance.resource_name,
                        instanceNamespace: loadBalance.namespace,
                        instanceCategory: 'deployment'
                    },
                    query: {
                        cluster_id: loadBalance.cluster_id,
                        clb_id: loadBalance.id
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
                    'id': 0,
                    'clb_name': '',
                    'cluster_id': '',
                    'region': 'ap-shanghai',
                    'clb_type': 'private',
                    'image_url': '/' + this.globalImageId,
                    'image_version': '',
                    'image': '',
                    'network_type': 'underlay',
                    'svc_discovery_type': 'custom'
                }

                this.loadBalanceSlider.isShow = true
            },

            /**
             * 编辑LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async editLoadBalance (loadBalance, index) {
                if (loadBalance.permissions && !loadBalance.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: loadBalance.namespace,
                        resource_name: loadBalance.namespace_name,
                        resource_type: 'namespace'
                    })
                }
                const loadBalanceParams = Object.assign({}, loadBalance)
                const imageParams = loadBalanceParams.image.split(':')
                loadBalanceParams.image_url = imageParams[0]
                loadBalanceParams.image_version = imageParams[1]
                this.curLoadBalance = loadBalanceParams
                this.loadBalanceSlider.title = this.$t('编辑CloudLoadBalancer')
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
                if (loadBalance.permissions && !loadBalance.permissions.use) {
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
                const loadBalanceName = loadBalance.clb_name

                this.$bkInfo({
                    title: `${this.$t('确定要启动此CloudLoadBalancer')}: ${loadBalanceName}`,
                    async confirmFn () {
                        const statusTmp = loadBalance.status
                        loadBalance.status = ''
                        try {
                            await self.$store.dispatch('network/runCloudLoadBalance', { projectId, loadBalanceId })
                            self.$bkMessage({
                                theme: 'success',
                                message: self.$t('已经将配置文件下发到后台，请稍后再详情中查看')
                            })
                            self.getLoadBalanceStatus(loadBalance, index)
                        } catch (e) {
                            catchErrorHandler(e, this)
                            loadBalance.status = statusTmp
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
                if (loadBalance.permissions && !loadBalance.permissions.use) {
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
                const loadBalanceName = loadBalance.clb_name

                this.$bkInfo({
                    title: `${this.$t('确定要停止此CloudLoadBalancer')}: ${loadBalanceName}`,
                    async confirmFn () {
                        const statusTmp = loadBalance.status
                        loadBalance.status = ''

                        try {
                            await self.$store.dispatch('network/stopCloudLoadBalance', { projectId, loadBalanceId })
                            self.getLoadBalanceStatus(loadBalance, index)
                        } catch (e) {
                            catchErrorHandler(e, this)
                            loadBalance.status = statusTmp
                        }
                    }
                })
            },

            /**
             * 删除LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async removeLoadBalance (loadBalance, index) {
                if (loadBalance.permissions && !loadBalance.permissions.use) {
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
                
                const loadBalanceName = loadBalance.clb_name
                this.$bkInfo({
                    title: '',
                    clsName: 'biz-remove-dialog max-size',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除CloudLoadBalaner')}【${loadBalance.cluster_id} / ${loadBalanceName}】？`),
                    async confirmFn () {
                        self.isPageLoading = true
                        try {
                            await self.$store.dispatch('network/removeCloudLoadBalance', { projectId, loadBalanceId })
                            self.$bkMessage({
                                theme: 'success',
                                message: self.$t('删除成功')
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
                        const res = await this.$store.dispatch('network/getCloudLoadBalanceDetail', {
                            projectId,
                            loadBalanceId
                        })
                        const lb = res.data
                        if (lb.clb_status === 'Running') {
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
                let list = this.$store.state.network.cloudLoadBalanceList
                let results = []

                if (this.searchScope) {
                    list = list.filter(item => item.cluster_id === this.searchScope)
                }

                results = list.filter(item => {
                    if (item.clb_name.indexOf(keyword) > -1 || item.cluster_id.indexOf(keyword) > -1) {
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
                // this.isPageLoading = true
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
                    if (item.clb_status && item.clb_status !== 'Running') {
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
            // async getLoadBalanceList () {
            //     try {
            //         const projectId = this.projectId
            //         const res = await this.$store.dispatch('network/getCloudLoadBalanceList', { projectId })
            //         this.curPageData = res.data
            //         this.isAllDataLoad = true
            //         this.initPageConf()
            //     } catch (e) {
            //         catchErrorHandler(e, this)
            //     } finally {
            //         // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
            //         setTimeout(() => {
            //             this.isInitLoading = false
            //         }, 200)
            //     }
            // },

            /**
             * 加载LB数据
             */
            async getLoadBalanceList () {
                try {
                    const projectId = this.projectId
                    const params = {
                        cluster_id: this.searchScope
                    }
                    this.isPageLoading = true
                    await this.$store.dispatch('network/getCloudLoadBalanceList', { projectId, params })
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)
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
                if (this.curLoadBalance.clb_name === '') {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择名称')
                    })
                    return false
                }

                if (!this.curLoadBalance.cluster_id) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择所属集群'),
                        delay: 5000
                    })
                    return false
                }

                if (!this.curLoadBalance.image_version) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择镜像版本'),
                        delay: 5000
                    })
                    return false
                }

                // if (!this.curLoadBalance.image_version) {
                //     this.$bkMessage({
                //         theme: 'error',
                //         message: this.$t('请选择镜像版本'),
                //         delay: 5000
                //     })
                //     return false
                // }

                return true
            },

            /**
             * 格式化数据，符合接口需要的格式
             */
            formatData () {
                this.curLoadBalance.image = `/${this.globalImageId}:${this.curLoadBalance.image_version}`
            },

            /**
             * 保存新建的LB
             */
            async createLoadBalance () {
                const projectId = this.projectId
                const data = this.curLoadBalance
                this.isDataSaveing = true
                try {
                    await this.$store.dispatch('network/addCloudLoadBalance', { projectId, data })

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
                const data = this.curLoadBalance
                const loadBalanceId = data.id

                this.isDataSaveing = true

                try {
                    await this.$store.dispatch('network/updateCloudLoadBalance', {
                        projectId,
                        loadBalanceId,
                        data
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
                this.formatData()
                if (this.checkData()) {
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
    .biz-loadbalance-title {
        display: inline-block;
        height: 60px;
        line-height: 60px;
        font-size: 16px;
        margin-left: 20px;
    }
</style>
