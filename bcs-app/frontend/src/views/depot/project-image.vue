<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-project-image-title">
                项目镜像
            </div>
            <div class="biz-actions">
                <a :href="PROJECT_CONFIG.doc.harborGuide" target="_blank" class="bk-text-button ml10">如何推镜像？</a>
            </div>
        </div>

        <div class="biz-content-wrapper" style="padding: 0;" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <template v-if="!isInitLoading">
                <div class="biz-panel-header biz-project-image-query">
                    <div class="right">
                        <div class="biz-search-input" style="width: 300px;">
                            <input @keyup.enter="enterHandler" v-model="searchKey" type="text" class="bk-form-input" placeholder="输入镜像名，按Enter搜索">
                            <a href="javascript:void(0)" class="biz-search-btn" @click="handleClick" v-if="!searchKey">
                                <i class="bk-icon icon-search icon-search-li"></i>
                            </a>
                            <a href="javascript:void(0)" class="biz-search-btn" v-else @click.stop.prevent="clearSearch">
                                <i class="bk-icon icon-close-circle-shape"></i>
                            </a>
                        </div>
                    </div>
                </div>
                <div class="biz-project-image-list" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                    <template v-if="dataList.length">
                        <div class="list-item" v-for="(item, index) in dataList" :key="index">
                            <div class="left-wrapper">
                                <img src="@open/images/default_logo.jpg" class="logo" />
                            </div>
                            <div class="right-wrapper">
                                <div class="content">
                                    <div class="info">
                                        <div class="title">
                                            <span>{{item.name}}</span>
                                        </div>
                                        <div class="attr">
                                            <span>类型：{{item.type || '--'}}</span>
                                            <span>来源：{{item.deployBy || '--'}}</span>
                                        </div>
                                        <div class="desc">
                                            简介：{{item.desc || '--'}}
                                        </div>
                                    </div>
                                    <div class="detail" @click="toImageDetail(item)">
                                        详情<i class="bk-icon icon-angle-right"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </template>
                    <template v-else-if="!isPageLoading">
                        <div class="empty">
                            <p class="biz-empty-message">无数据</p>
                        </div>
                    </template>
                    <template v-else>
                        <div class="loading"></div>
                    </template>
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
                        @page-change="pageChange">
                    </bk-paging>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
    export default {
        data () {
            return {
                isInitLoading: true,
                DEVOPS_BCS_API_URL: DEVOPS_BCS_API_URL,
                imageDialogConf: {
                    isShow: false,
                    width: 640,
                    hasHeader: false,
                    closeIcon: false
                },
                isPageLoading: true,
                // 查询条件
                searchKey: '',
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
                bkMessageInstance: null,
                winHeight: 0
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            dataList () {
                return this.$store.state.depot.projectImage.dataList
            }
        },
        watch: {
            searchKey (newVal, oldVal) {
                // 如果删除，为空时触发搜索
                if (oldVal && !newVal) {
                    this.enterHandler()
                }
            }
        },
        mounted () {
            this.winHeight = window.innerHeight
            this.projId = this.$route.params.projectId || '000'
            localStorage.removeItem('backRouterName')
            this.getFirstPage()
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
             * 搜索框清除事件
             */
            clearSearch () {
                this.searchKey = ''
                this.handleClick()
            },

            /**
             * 跳转到镜像详情
             *
             * @param {Object} item 当前镜像对象
             */
            toImageDetail (item) {
                localStorage.setItem('backRouterName', 'projectImage')
                this.$store.commit('depot/forceUpdateCurImage', item)
                this.$router.push({
                    name: 'imageDetail',
                    params: {
                        repo: item.repo
                    }
                })
            },

            /**
             * 搜索框 enter 事件处理
             *
             * @param {Object} e 事件对象
             */
            enterHandler (e) {
                this.getFirstPage()
            },

            /**
             * 获取数据
             *
             * @param {Object} params ajax 查询参数
             */
            async fetchData (params = {}) {
                this.isPageLoading = true

                const search = this.searchKey
                // 去掉类型过滤 默认查询所有数据
                const filters = 'all'
                try {
                    const res = await this.$store.dispatch('depot/getProjectImage', Object.assign({}, params, {
                        search,
                        filters
                    }))

                    const count = res.count || 0
                    this.pageConf.total = count
                    this.pageConf.totalPage = Math.ceil(count / this.pageConf.pageSize)
                    if (this.pageConf.totalPage < this.pageConf.curPage) {
                        this.pageConf.curPage = 1
                    }
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
             * 首页
             */
            getFirstPage () {
                this.fetchData({
                    limit: this.pageConf.pageSize,
                    projId: this.projId,
                    offset: 0
                })
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
             * 搜索按钮点击
             *
             * @param {Object} e 对象
             */
            handleClick (e) {
                this.getFirstPage()
            }
        }
    }
</script>

<style scoped>
    @import './project-image.css';
</style>
