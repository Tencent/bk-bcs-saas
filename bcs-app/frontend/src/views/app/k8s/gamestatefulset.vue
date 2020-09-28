<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-app-title">
                GameStatefulSets
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper" style="padding: 0;" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <template v-if="!isInitLoading">
                <div class="biz-panel-header biz-event-query-query" style="padding-right: 0;">
                    <div class="left">
                        <bk-selector
                            :placeholder="$t('请选择集群')"
                            :searchable="true"
                            :setting-key="'cluster_id'"
                            :display-key="'name'"
                            :selected.sync="selectedClusterId"
                            :list="clusterList"
                            :search-placeholder="$t('输入集群名称搜索')"
                            @item-selected="handleChangeCluster">
                        </bk-selector>
                    </div>
                    <div class="left">
                        <bk-selector
                            :placeholder="$t('请选择命名空间')"
                            :searchable="true"
                            :allow-clear="true"
                            :setting-key="'name'"
                            :display-key="'name'"
                            :selected.sync="selectedNamespaceName"
                            :list="namespaceList"
                            :is-loading="namespaceLoading"
                            :search-placeholder="$t('输入命名空间搜索')"
                            @item-selected="handleChangeNamespace"
                            @clear="handleClearNamespace">
                        </bk-selector>
                    </div>
                    <div class="left">
                        <div class="biz-search-input" style="width: 240px;">
                            <input v-model="searchKey" type="text" class="bk-form-input" :placeholder="$t('输入名称搜索')">
                            <a href="javascript:void(0)" class="biz-search-btn" v-if="searchKey" @click.stop.prevent="clearSearch">
                                <i class="bk-icon icon-close-circle-shape"></i>
                            </a>
                        </div>
                    </div>
                    <div class="left">
                        <bk-button type="primary" :title="$t('查询')" icon="search" @click="handleClick">
                            {{$t('查询')}}
                        </bk-button>
                    </div>
                </div>
                <div v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                    <div class="biz-table-wrapper gamestatefullset-table-wrapper">
                        <table class="bk-table has-table-hover biz-table gamestatefullset-table" :class="curPageData.length ? '' : 'no-data'">
                            <thead>
                                <tr>
                                    <template v-for="(column, index) in columnList">
                                        <th :key="index">
                                            <template v-if="column === 'name'">{{$t('名称')}}</template>
                                            <template v-else-if="column === 'cluster_id'">{{$t('集群')}}</template>
                                            <template v-else-if="column === 'namespace'">{{$t('命名空间')}}</template>
                                            <template v-else>{{column}}</template>
                                        </th>
                                    </template>
                                    <th><span>{{$t('操作')}}</span></th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curPageData.length">
                                    <tr v-for="(item, index) in curPageData" :key="index">
                                        <template v-for="(column, columnIndex) in columnList">
                                            <td :key="columnIndex">
                                                <div class="cell">
                                                    <bk-tooltip :content="item[column] || ''" placement="top">
                                                        <template v-if="column === 'name'">
                                                            <a href="javascript:void(0);" class="bk-text-button name-col" style="font-weight: 700;" @click="showSideslider(item[column], item['namespace'])">{{item[column] || '--'}}</a>
                                                        </template>
                                                        <template v-else>
                                                            {{item[column] || '--'}}
                                                        </template>
                                                    </bk-tooltip>
                                                </div>
                                            </td>
                                        </template>
                                        <td style="width: 100px;">
                                            <a href="javascript:void(0);" class="bk-text-button" @click.stop="update(item, index)">{{$t('更新')}}</a>
                                            <a href="javascript:void(0);" class="bk-text-button" @click.stop="del(item, index)">{{$t('删除')}}</a>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td :colspan="columnList.length + 1">
                                            <div class="bk-message-box">
                                                <p class="message empty-message" v-if="!loading">{{$t('无数据')}}</p>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
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
                        @page-change="pageChangeHandler">
                    </bk-paging>
                </div>
            </template>
        </div>
        <gamestatefulset-sideslider
            :is-show="isShowSideslider"
            :cluster-id="selectedClusterId"
            :namespace-name="curShowNamespace"
            :name="curShowName"
            @hide-sideslider="hideSideslider">
        </gamestatefulset-sideslider>

        <gamestatefulset-update
            :is-show="isShowUpdateDialog"
            :item="updateItem"
            @hide-update="hideGamestatefulsetUpdate"
            @update-success="gamestatefulsetUpdateSuccess">
        </gamestatefulset-update>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'

    import GamestatefulsetSideslider from './gamestatefulset-sideslider'
    import GamestatefulsetUpdate from './gamestatefulset-update'

    export default {
        components: {
            GamestatefulsetSideslider,
            GamestatefulsetUpdate
        },
        data () {
            return {
                CATEGORY: 'gamestatefulset',

                isInitLoading: true,
                isPageLoading: false,

                pageConf: {
                    total: 0,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                bkMessageInstance: null,
                clusterList: [],
                selectedClusterId: '',
                selectedNamespaceName: '',
                namespaceList: [],
                namespaceLoading: false,
                columnList: ['name', 'cluster_id', 'namespace', 'Age'],
                renderList: [],
                renderListTmp: [],
                curPageData: [],
                isShowSideslider: false,
                curShowName: '',
                curShowNamespace: '',
                searchKey: '',
                isShowUpdateDialog: false,
                updateItem: null
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            isEn () {
                return this.$store.state.isEn
            }
        },
        async mounted () {
            await this.getClusters()
            await this.fetchData({
                projId: this.projectId,
                limit: this.pageConf.pageSize,
                offset: 0
            })
        },
        destroyed () {
            this.bkMessageInstance && this.bkMessageInstance.close()
        },
        methods: {
            /**
             * 获取所有的集群
             */
            async getClusters () {
                try {
                    const res = await this.$store.dispatch('cluster/getPermissionClusterList', this.projectId)
                    const list = res.data.results || []
                    this.clusterList.splice(0, this.clusterList.length, ...list)
                    if (this.clusterList.length) {
                        this.selectedClusterId = this.clusterList[0].cluster_id
                        this.getNameSpaceList()
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取命名空间列表
             */
            async getNameSpaceList () {
                try {
                    this.namespaceLoading = true
                    const res = await this.$store.dispatch('crdcontroller/getNameSpaceListByCluster', {
                        projectId: this.projectId,
                        clusterId: this.selectedClusterId
                    })
                    const list = res.data || []
                    this.namespaceList.splice(0, this.namespaceList.length, ...list)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.namespaceLoading = false
                }
            },

            /**
             * 集群下拉框 item-selected 事件
             *
             * @param {string} clusterId 集群 id
             * @param {Object} data 集群对象
             */
            async handleChangeCluster (clusterId, data) {
                this.selectedNamespaceName = ''
                this.selectedClusterId = clusterId
                await this.getNameSpaceList()
            },

            /**
             * 命名空间下拉框 item-selected 事件
             *
             * @param {string} selectedNamespaceName 命名空间 name
             * @param {Object} data 命名空间对象
             */
            handleChangeNamespace (selectedNamespaceName, data) {
                this.selectedNamespaceName = selectedNamespaceName
            },

            /**
             * 命名空间下拉框 clear 事件
             */
            handleClearNamespace () {
                this.selectedNamespaceName = ''
            },

            /**
             * 获取表格数据
             */
            async fetchData () {
                this.isPageLoading = true
                try {
                    const params = {}
                    if (this.selectedNamespaceName) {
                        params.namespace = this.selectedNamespaceName
                    }
                    const res = await this.$store.dispatch('app/getGameStatefulsetList', {
                        projectId: this.projectId,
                        clusterId: this.selectedClusterId,
                        gamestatefulsets: 'gamestatefulsets.tkex.tencent.com',
                        data: params
                    })

                    const data = res.data || { td_list: [], th_list: [] }

                    if (data.th_list.length) {
                        this.columnList.splice(0, this.columnList.length, ...data.th_list)
                    } else {
                        this.columnList.splice(0, this.columnList.length, ...['name', 'cluster_id', 'namespace', 'Age'])
                    }
                    this.renderListTmp.splice(0, this.renderListTmp.length, ...data.td_list)

                    if (this.searchKey.trim()) {
                        this.renderList.splice(
                            0,
                            this.renderList.length,
                            ...this.renderListTmp.filter(item => item.name.indexOf(this.searchKey) > -1)
                        )
                    } else {
                        this.renderList.splice(0, this.renderList.length, ...this.renderListTmp)
                    }

                    this.pageConf.curPage = 1
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isPageLoading = false
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.renderList.length
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
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
                this.pageChangeHandler()
            },

            /**
             * 获取分页数据
             * @param  {number} page 第几页
             * @return {object} data 数据
             */
            getDataByPage (page) {
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.renderList.length) {
                    endIndex = this.renderList.length
                }
                return this.renderList.slice(startIndex, endIndex)
            },

            /**
             * 页数改变回调
             * @param  {number} page 第几页
             */
            pageChangeHandler (page = 1) {
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData = data
            },

            /**
             * 搜索框清除事件
             */
            clearSearch () {
                this.searchKey = ''
                this.handleClick()
            },

            /**
             * 搜索按钮点击
             *
             * @param {Object} e 时间对象
             */
            async handleClick (e) {
                await this.fetchData()
            },

            /**
             * 显示更新弹框
             *
             * @param {Object} item 当前行对象
             * @param {number} index 当前行对象索引
             *
             * @return {string} returnDesc
             */
            update (item, index) {
                this.isShowUpdateDialog = true
                this.updateItem = item
            },

            /**
             * 关闭更新弹框
             */
            hideGamestatefulsetUpdate () {
                this.isShowUpdateDialog = false
                setTimeout(() => {
                    this.updateItem = null
                }, 300)
            },

            /**
             * 更新 gamestatefulset 成功回调
             */
            async gamestatefulsetUpdateSuccess () {
                this.hideGamestatefulsetUpdate()
                await this.fetchData()
            },

            /**
             * 删除当前行
             *
             * @param {Object} item 当前行对象
             * @param {number} index 当前行对象索引
             *
             * @return {string} returnDesc
             */
            async del (item, index) {
                const me = this
                const h = me.$createElement

                let msg = ''
                let msgEn = ''
                if (item.namespace) {
                    msg = `删除命名空间${item.namespace}下名称为${item.name}的资源`
                    msgEn = `Delete the resource named ${item.name} under the namespace ${item.namespace}`
                } else {
                    msg = `删除名称为${item.name}的资源`
                    msgEn = `Delete the resource named ${item.name}`
                }
                me.$bkInfo({
                    clsName: 'del-gamestatefulset-dialog',
                    title: me.$t('确定删除？'),
                    content: h(
                        'p',
                        { style: {} },
                        this.isEn ? msgEn : msg
                    ),
                    async confirmFn () {
                        try {
                            await me.$store.dispatch('app/deleteGameStatefulsetInfo', {
                                projectId: me.projectId,
                                clusterId: me.selectedClusterId,
                                gamestatefulsets: 'gamestatefulsets.tkex.tencent.com',
                                name: item.name,
                                data: {
                                    namespace: item.namespace
                                }
                            })

                            me.bkMessageInstance && me.bkMessageInstance.close()
                            me.bkMessageInstance = me.$bkMessage({
                                theme: 'success',
                                message: me.$t('删除成功'),
                                delay: 1000
                            })
                            await me.fetchData()
                        } catch (e) {
                            console.error(e)
                            me.bkMessageInstance = me.$bkMessage({
                                theme: 'error',
                                message: e.message || e.data.msg || e.statusText
                            })
                        }
                    }
                })
            },

            /**
             * 显示 sideslider
             */
            async showSideslider (name, namespace) {
                this.curShowName = name
                this.curShowNamespace = namespace
                this.isShowSideslider = true
            },

            /**
             * 隐藏 sideslider
             */
            hideSideslider () {
                this.curShowName = ''
                this.curShowNamespace = ''
                this.isShowSideslider = false
            }
        }
    }
</script>

<style scoped>
    @import '../gamestatefulset.css';
</style>
