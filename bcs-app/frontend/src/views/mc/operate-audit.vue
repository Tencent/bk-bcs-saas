<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-operate-audit-title">
                {{$t('操作审计')}}
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper" style="padding: 0;" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <template v-if="!isInitLoading">
                <div class="biz-panel-header biz-operate-audit-query">
                    <div class="left">
                        <bk-selector :placeholder="$t('操作对象类型')"
                            :selected.sync="resourceTypeIndex"
                            :list="resourceTypeList"
                            :setting-key="'id'"
                            :display-key="'name'"
                            :allow-clear="true"
                            @clear="resourceTypeClear">
                        </bk-selector>
                    </div>
                    <div class="left">
                        <bk-selector :placeholder="$t('操作类型')"
                            :selected.sync="activityTypeIndex"
                            :list="activityTypeList"
                            :setting-key="'id'"
                            :display-key="'name'"
                            :allow-clear="true"
                            @clear="activityTypeClear">
                        </bk-selector>
                    </div>
                    <div class="left">
                        <bk-selector :placeholder="$t('状态')"
                            :selected.sync="activityStatusIndex"
                            :list="activityStatusList"
                            :setting-key="'id'"
                            :display-key="'name'"
                            :allow-clear="true"
                            @clear="activityStatusClear">
                        </bk-selector>
                    </div>
                    <div class="left range-picker">
                        <bk-date-range
                            @change="change"
                            :range-separator="'-'"
                            :disabled="false"
                            :position="'bottom-left'"
                            :timer="true">
                        </bk-date-range>
                    </div>
                    <div class="left">
                        <bk-button type="primary" :title="$t('查询')" icon="search" @click="handleClick">
                            {{$t('查询')}}
                        </bk-button>
                    </div>
                </div>
                <div v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                    <div class="biz-table-wrapper">
                        <table class="bk-table has-table-hover biz-table biz-operate-audit-table">
                            <thead>
                                <tr>
                                    <th style="width: 260px; text-align: left;padding-left: 30px;">
                                        {{$t('时间')}}
                                    </th>
                                    <th style="width: 100px;">{{$t('操作类型')}}</th>
                                    <th style="width: 170px;">{{$t('对象及类型')}}</th>
                                    <th style="width: 130px;">{{$t('状态')}}</th>
                                    <th style="width: 150px;">{{$t('发起者')}}</th>
                                    <th style="width: 200px;">{{$t('描述')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="dataList.length">
                                    <tr v-for="(item, index) in dataList" :key="index">
                                        <td style="text-align: left;padding-left: 30px;">
                                            {{item.activityTime}}
                                        </td>
                                        <td>
                                            {{item.activityType}}
                                        </td>
                                        <td>
                                            <p class="extra-info" :title="item.extra.resourceType || '--'"><span>{{$t('类型：')}}</span>{{item.extra.resourceType || '--'}}</p>
                                            <p class="extra-info" :title="item.extra.resource || '--'"><span>{{$t('对象：')}}</span>{{item.extra.resource || '--'}}</p>
                                        </td>
                                        <td>
                                            <i class="bk-icon" :class="item.activityStatus === $t('完成1') || item.activityStatus === $t('成功1') ? 'success icon-check-circle' : 'fail icon-close-circle'"></i>{{item.activityStatus}}
                                        </td>
                                        <td>{{item.user}}</td>
                                        <td>
                                            <bk-tooltip placement="top" :delay="500">
                                                <div class="description vm">
                                                    {{item.description}}
                                                </div>
                                                <template slot="content">
                                                    <p style="text-align: left; white-space: normal;word-break: break-all;">{{item.description}}</p>
                                                </template>
                                            </bk-tooltip>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else-if="!dataList.length && !isPageLoading">
                                    <tr class="no-hover">
                                        <td colspan="6">
                                            <div class="bk-message-box" v-if="!isPageLoading">
                                                <p class="message empty-message">{{$t('无数据')}}</p>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr class="no-hover">
                                        <td colspan="6">
                                            <div class="bk-message-box">
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="biz-page-wrapper" v-if="pageConf.show">
                    <bk-page-counter
                        :is-en="isEn"
                        :total="pageConf.total"
                        :page-size="pageConf.pageSize"
                        @change="changePageSize">
                    </bk-page-counter>
                    <bk-paging
                        :cur-page.sync="pageConf.curPage"
                        :total-page="pageConf.totalPage"
                        @page-change="pageChange">
                    </bk-paging>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'operate-audit',
        data () {
            // 操作类型下拉框 list
            const activityTypeList = [
                { id: 'all', name: this.$t('全部1') },
                { id: 'note', name: this.$t('注意1') },
                { id: 'add', name: this.$t('创建1') },
                { id: 'modify', name: this.$t('更新1') },
                { id: 'delete', name: this.$t('删除1') },
                { id: 'begin', name: this.$t('开始1') },
                { id: 'end', name: this.$t('结束1') },
                { id: 'start', name: this.$t('启动1') },
                { id: 'pause', name: this.$t('暂停1') },
                { id: 'carryon', name: this.$t('继续1') },
                { id: 'stop', name: this.$t('停止1') },
                { id: 'restart', name: this.$t('重启1') },
                { id: 'query', name: this.$t('查询1') }
            ]
            // 操作类型 map
            const activityTypeMap = {}
            activityTypeList.forEach(item => {
                activityTypeMap[item.id] = item.name
            })

            // 状态下拉框 list
            const activityStatusList = [
                { id: 'all', name: this.$t('全部1') },
                { id: 'unknown', name: this.$t('未知1') },
                { id: 'completed', name: this.$t('完成1') },
                { id: 'error', name: this.$t('错误1') },
                { id: 'busy', name: this.$t('处理中1') },
                { id: 'succeed', name: this.$t('成功1') },
                { id: 'failed', name: this.$t('失败1') }
            ]
            // 操作状态 map
            const activityStatusMap = {}
            activityStatusList.forEach(item => {
                activityStatusMap[item.id] = item.name
            })
            // 服务类型
            let serviceType = 'container-service'
            if (this.$route.fullPath.indexOf('/bcs') === 0) {
                serviceType = 'container-service'
            } else if (this.$route.fullPath.indexOf('/monitor') === 0) {
                serviceType = 'monitor'
            }
            // 自定义页数
            const pageCountData = [
                { count: 10, id: '10' },
                { count: 20, id: '20' },
                { count: 50, id: '50' },
                { count: 100, id: '100' }
            ]
            return {
                // 操作类型 map
                activityTypeMap,
                // 操作类型下拉框 list
                activityTypeList,
                activityTypeIndex: -1,

                // 操作状态 map
                activityStatusMap,
                // 状态下拉框 list
                activityStatusList,
                activityStatusIndex: -1,

                // 操作对象类型下拉框 list
                resourceTypeList: [],
                // 操作对象类型下拉框 map
                resourceTypeMap: {},
                resourceTypeIndex: -1,

                // 查询时间范围
                dataRange: '',
                // 列表数据
                dataList: [],

                // 服务类型
                serviceType,

                isInitLoading: true,
                isPageLoading: false,

                pageConf: {
                    // 总数
                    total: 0,
                    // 总页数
                    totalPage: 1,
                    // 每页多少条
                    pageSize: 10,
                    // 当前页
                    curPage: 1,
                    // 是否显示翻页条
                    show: false
                },
                // 自定义页数 对象
                pageCountList: pageCountData,
                pageCountListIndex: '10',
                bkMessageInstance: null
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            }
        },
        watch: {
            '$route.params.projectId': {
                handler: 'routerChangeHandler',
                immediate: true
            }
        },
        mounted () {
        },
        destroyed () {
            this.bkMessageInstance && this.bkMessageInstance.close()
        },
        methods: {
            /**
             * 分页大小更改
             *
             * @param {number} pageSize pageSize
             */
            changePageSize (pageSize) {
                this.pageConf.pageSize = pageSize
                this.pageConf.curPage = 1
                this.pageChange()
            },
            /**
             * router change 回调(根据projectId变化更新数据)
             */
            async routerChangeHandler () {
                this.projId = this.$route.params.projectId || '000'
                this.fetchData({
                    projId: this.projId,
                    limit: this.pageConf.pageSize,
                    offset: 0
                })
                this.getResourceTypes()
            },

            /**
             * 获取所有的操作对象类型
             */
            async getResourceTypes () {
                try {
                    const res = await this.$store.dispatch('mc/getResourceTypes', {
                        serviceType: this.serviceType
                    })
                    this.resourceTypeMap = res.data
                    this.resourceTypeList.splice(0, this.resourceTypeList.length)
                    Object.keys(this.resourceTypeMap).forEach(key => {
                        this.resourceTypeList.push({
                            id: key,
                            name: this.resourceTypeMap[key]
                        })
                    })
                    this.resourceTypeList.unshift({ id: 'all', name: this.$t('全部1') })
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 获取表格数据
             *
             * @param {Object} params ajax 查询参数
             */
            async fetchData (params = {}) {
                // 操作类型
                // const activityType = this.activityTypeIndex !== -1
                //     ? this.activityTypeList[this.activityTypeIndex].id
                //     : null
                const activityType = this.activityTypeIndex === -1 ? null : this.activityTypeIndex

                // 状态
                // const activityStatus = this.activityStatusIndex !== -1
                //     ? this.activityStatusList[this.activityStatusIndex].id
                //     : null
                const activityStatus = this.activityStatusIndex === -1 ? null : this.activityStatusIndex

                // 操作对象类型
                // const resourceType = this.resourceTypeIndex !== -1
                //     ? this.resourceTypeList[this.resourceTypeIndex].id
                //     : null
                const resourceType = this.resourceTypeIndex === -1 ? null : this.resourceTypeIndex

                // 开始结束时间
                let [beginTime, endTime] = ['', '']
                if (this.dataRange) {
                    [beginTime, endTime] = this.dataRange.split(' - ')
                }

                this.isPageLoading = true
                try {
                    const res = await this.$store.dispatch('mc/getActivityLogs', Object.assign({}, params, {
                        activityType,
                        activityStatus,
                        resourceType,
                        beginTime,
                        endTime,
                        serviceType: this.serviceType
                    }))

                    this.dataList = []

                    const count = res.count
                    if (count <= 0) {
                        this.pageConf.totalPage = 0
                        this.total = 0
                        this.pageConf.show = false
                        return
                    }

                    this.pageConf.total = count
                    this.pageConf.totalPage = Math.ceil(count / this.pageConf.pageSize)
                    if (this.pageConf.totalPage < this.pageConf.curPage) {
                        this.pageConf.curPage = 1
                    }
                    this.pageConf.show = true

                    const list = res.results || []
                    list.forEach(item => {
                        this.dataList.push({
                            // 操作时间
                            activityTime: item.activity_time,
                            // 操作类型
                            activityType: this.activityTypeMap[item.activity_type],
                            extra: {
                                // 操作对象类型
                                resourceType: this.resourceTypeMap[item.resource_type] || item.resource_type,
                                // 操作对象
                                resource: item.resource
                            },
                            // 状态
                            activityStatus: this.activityStatusMap[item.activity_status],
                            user: item.user,
                            description: item.description
                        })
                    })
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.isPageLoading = false
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 翻页
             *
             * @param {number} page 页码
             */
            pageChange (page = 1) {
                this.fetchData({
                    projId: this.projId,
                    limit: this.pageConf.pageSize,
                    offset: this.pageConf.pageSize * (page - 1)
                })
            },

            /**
             * 清除操作对象类型
             */
            resourceTypeClear () {
                this.resourceTypeIndex = -1
            },

            /**
             * 清除操作类型
             */
            activityTypeClear () {
                this.activityTypeIndex = -1
            },

            /**
             * 清除状态
             */
            activityStatusClear () {
                this.activityStatusIndex = -1
            },

            /**
             * 日期范围搜索条件
             *
             * @param {string} oldValue 变化前的值
             * @param {string} newValue 变化后的值
             */
            change (oldValue, newValue) {
                this.dataRange = newValue
            },

            /**
             * 搜索按钮点击
             *
             * @param {Object} e 事件对象
             */
            handleClick (e) {
                this.pageConf.curPage = 1
                this.fetchData({
                    projId: this.projId,
                    limit: this.pageConf.pageSize,
                    offset: 0
                })
            },

            /**
             * 分页大小更改
             *
             * @param {Object} e 事件对象
             */
            handlePageSizeChange () {
                this.fetchData({
                    projId: this.projId,
                    limit: this.pageConf.pageSize,
                    offset: 0
                })
            }
        }
    }
</script>

<style scoped>
    @import './operate-audit.css';
</style>
