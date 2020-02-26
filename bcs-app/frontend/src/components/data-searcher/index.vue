<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-app-title">
                {{$t('组件库')}}
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
                    <div class="right">
                        <bk-data-searcher
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="curClusterId"
                            @search="search"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>
                <div class="biz-crdcontroller" v-bkloading="{ isLoading: isPageLoading, opacity: 0.1 }" style="min-height: 180px;">
                    <svg style="display: none;">
                        <title>{{$t('模板集默认图标')}}</title>
                        <symbol id="biz-set-icon" viewBox="0 0 60 60">
                            <g id="图层_6">
                                <g id="图层_32_1_">
                                    <path class="st0" d="M12,8v4H8c-1.1,0-2,0.9-2,2v42c0,1.1,0.9,2,2,2h42c1.1,0,2-0.9,2-2v-4h4c1.1,0,2-0.9,2-2V8c0-1.1-0.9-2-2-2
                                        H14C12.9,6,12,6.9,12,8z M48,48v4v2H10V16h2h4h32V48z M54,48h-2V14c0-1.1-0.9-2-2-2H16v-2h38V48z" />
                                </g>
                                <path class="st1" d="M45.7,33.7h-1.8l-3.4-8.3l1.3-1.3c0.5-0.5,0.5-1.3,0-1.8l0,0c-0.5-0.5-1.3-0.5-1.8,0l-1.3,1.3l-8.4-3.5v-1.8
                                    c0-0.7-0.6-1.3-1.3-1.3l0,0c-0.7,0-1.3,0.6-1.3,1.3V20l-8.4,3.5l-1.2-1.2c-0.5-0.5-1.3-0.5-1.8,0l0,0c-0.5,0.5-0.5,1.3,0,1.8
                                    l1.2,1.2L14,33.7h-1.8c-0.7,0-1.3,0.6-1.3,1.3l0,0c0,0.7,0.6,1.3,1.3,1.3H14l3.5,8.4L16.2,46c-0.5,0.5-0.5,1.3,0,1.8l0,0
                                    c0.5,0.5,1.3,0.5,1.8,0l1.3-1.3l8.3,3.4v1.8c0,0.7,0.6,1.3,1.3,1.3l0,0c0.7,0,1.3-0.6,1.3-1.3v-1.9l8.3-3.4l1.3,1.3
                                    c0.5,0.5,1.3,0.5,1.8,0l0,0c0.5-0.5,0.5-1.3,0-1.8l-1.3-1.3l3.4-8.3h1.9c0.7,0,1.3-0.6,1.3-1.3l0,0C47,34.3,46.4,33.7,45.7,33.7z
                                     M30.3,23.4l6,2.5l-4.6,4.6c-0.4-0.2-0.9-0.4-1.3-0.6v-6.5H30.3z M27.7,23.4V30c-0.5,0.1-0.9,0.3-1.4,0.6l-4.7-4.7L27.7,23.4z
                                     M19.9,27.7l4.7,4.7c-0.2,0.4-0.4,0.9-0.5,1.3h-6.6L19.9,27.7z M17.4,36.3H24c0.1,0.5,0.3,0.9,0.6,1.3l-4.7,4.7L17.4,36.3z
                                     M27.7,46.5l-6-2.5l4.7-4.7c0.4,0.2,0.8,0.4,1.3,0.5V46.5z M29,37.5c-1.4,0-2.6-1.2-2.6-2.6c0-1.4,1.2-2.6,2.6-2.6s2.6,1.2,2.6,2.6
                                    C31.6,36.4,30.4,37.5,29,37.5z M30.3,46.5v-6.6c0.5-0.1,0.9-0.3,1.3-0.5l4.6,4.6L30.3,46.5z M38,42.2l-4.6-4.6
                                    c0.2-0.4,0.4-0.8,0.6-1.3h6.5L38,42.2z M34,33.7c-0.1-0.5-0.3-0.9-0.5-1.3l4.6-4.6l2.5,6H34V33.7z" />
                                <g class="st2">
                                    <path class="st3" d="M41,49H17c-1.1,0-2-0.9-2-2V23c0-1.1,0.9-2,2-2h24c1.1,0,2,0.9,2,2v24C43,48.1,42.1,49,41,49z" />
                                </g>
                                <g>
                                    <path class="st0" d="M42.2,25c-1.9,0-2.9,0.5-2.9,1.5v17.1c0,1,1,1.5,2.9,1.5v1.8H31.4V45c2,0,3-0.5,3-1.5v-8H23.6v8
                                        c0,1,1,1.5,3,1.5v1.8H15.8V45c1.9,0,2.8-0.5,2.8-1.5V26.4c0-1-0.9-1.5-2.8-1.5V23h10.8v2c-2,0-3,0.5-3,1.5v6.8h10.8v-6.8
                                        c0-1-1-1.5-3-1.5v-1.9h10.8V25z" />
                                </g>
                            </g>
                        </symbol>
                    </svg>
                    <table class="bk-table biz-templateset-table mb20">
                        <thead>
                            <tr>
                                <th style="width: 120px; padding-left: 0;" class="center">{{$t('图标')}}</th>
                                <th style="width: 250px; padding-left: 20px;">{{$t('名称')}}</th>
                                <th style="width: 150px; padding-left: 20px;">{{$t('状态')}}</th>
                                <th style="padding-left: 0;">{{$t('描述')}}</th>
                                <th style="width: 170px; padding-left: 0;">{{$t('操作')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="crdControllerList.length">
                                <tr
                                    v-for="crdcontroller of crdControllerList"
                                    :key="crdcontroller.id">
                                    <td colspan="5">
                                        <table class="biz-inner-table">
                                            <tr>
                                                <td class="logo">
                                                    <div class="logo-wrapper" v-if="crdcontroller.logo && isImage(crdcontroller.logo)">
                                                        <img :src="crdcontroller.logo">
                                                        <!-- <img class="logo" src="@open/images/gcs_mysql_logo.png" alt=""> -->
                                                    </div>
                                                    <svg class="biz-set-icon" v-else>
                                                        <use xlink:href="#biz-set-icon"></use>
                                                    </svg>
                                                </td>
                                                <td class="name">
                                                    <p class="text">{{crdcontroller.chinese_name}}</p>
                                                </td>
                                                <td class="status">
                                                    <span class="biz-mark" v-if="crdcontroller.status === 'created'">
                                                        已启用
                                                    </span>
                                                    <span class="biz-mark" v-else>
                                                        未启用
                                                    </span>
                                                    <!-- <p class="text">{{crdcontroller.status === 'created' ? '已启用' : '未启用'}}</p> -->
                                                </td>
                                                <td class="description">
                                                    <p class="text">{{crdcontroller.description}}</p>
                                                </td>
                                                <td class="action">
                                                    <template v-if="crdcontroller.status === 'created'">
                                                        <button class="bk-button bk-primary" @click="goControllerInstances(crdcontroller)">{{$t('前往配置')}}</button>
                                                    </template>
                                                    <template v-else>
                                                        <button class="bk-button bk-primary is-disabled" v-bktooltips.top="$t('联系容器助手部署组件')">{{$t('启用')}}</button>
                                                    </template>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </template>
                            <template v-if="!crdControllerList.length && !showLoading">
                                <tr>
                                    <td colspan="5">
                                        <div class="biz-empty-message" style="padding: 80px;">
                                            {{$t('无数据')}}
                                        </div>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                    <!-- <h4>已启用的服务</h4>
                    <div
                        class="biz-controller-item"
                        v-for="(crdcontroller, index) of crdControllerList"
                        :key="index"
                        @click="goControllerInstances(crdcontroller)">
                        <img class="logo" src="@open/images/gcs_mysql_logo.png" alt="">
                        <span class="title">{{crdcontroller.chinese_name}}</span>
                        <p class="desc">
                            {{crdcontroller.description}}
                        </p>
                        <p class="action">
                            <template v-if="crdcontroller.status === 'created'">
                                {{$t('已启用前往配置')}}
                            </template>
                            <template v-else>
                                {{$t('前往配置')}}
                            </template>
                        </p>
                    </div> -->
                </div>
            </template>
        </div>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'

    export default {
        data () {
            return {
                curClusterId: undefined,
                isInitLoading: true,
                isPageLoading: false,
                crdControllerList: [],
                crdControllerListCache: [],
                searchKeyword: '',
                searchScope: ''
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            projectId () {
                return this.$route.params.projectId
            },
            curProject () {
                return this.$store.state.curProject
            },
            clusterList () {
                return this.$store.state.cluster.clusterList
            },
            searchScopeList () {
                const clusterList = this.$store.state.cluster.clusterList
                let results = []
                if (clusterList.length) {
                    results = []
                    clusterList.forEach(item => {
                        results.push({
                            id: item.cluster_id,
                            name: item.name
                        })
                    })
                }

                return results
            }
        },
        watch: {
            clusterList () {
                if (this.clusterList.length) {
                    if (window.sessionStorage && window.sessionStorage['bcs-crd-cluster']) {
                        this.curClusterId = window.sessionStorage['bcs-crd-cluster']
                    } else {
                        this.curClusterId = this.clusterList[0].cluster_id
                    }

                    this.getCrdControllersByCluster()
                }
            }
        },
        created () {
            // 如果不是mesos类型的项目，无法访问页面，重定向回集群首页
            if (this.curProject && this.curProject.kind === PROJECT_MESOS) {
                this.$router.push({
                    name: 'clusterMain',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
                return false
            }

            this.init()
        },
        methods: {
            init () {
                if (this.clusterList.length) {
                    if (window.sessionStorage && window.sessionStorage['bcs-crd-cluster']) {
                        this.curClusterId = window.sessionStorage['bcs-crd-cluster']
                    } else {
                        this.curClusterId = this.clusterList[0].cluster_id
                    }
                    this.getCrdControllersByCluster()
                }
            },

            async getCrdControllersByCluster () {
                if (this.isPageLoading) {
                    return false
                }
                if (!this.curClusterId) {
                    return false
                }

                const projectId = this.projectId
                const clusterId = this.curClusterId

                this.isPageLoading = true
                try {
                    console.log('clusterId', clusterId)
                    const res = await this.$store.dispatch('crdcontroller/getCrdControllersByCluster', { projectId, clusterId })
                    this.crdControllerList = res.data

                    // 搜索
                    let results = res.data
                    if (this.searchKeyword.trim()) {
                        results = []
                        const keyword = this.searchKeyword.trim()
                        const keyList = ['chinese_name']
                        const list = res.data

                        list.forEach(item => {
                            item.isChecked = false
                            for (const key of keyList) {
                                if (item[key].indexOf(keyword) > -1) {
                                    results.push(item)
                                    return true
                                }
                            }
                        })
                    }

                    this.crdControllerList = results
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    setTimeout(() => {
                        this.isInitLoading = false
                        this.isPageLoading = false
                    }, 200)
                }
            },

            goControllerInstances (crdcontroller) {
                if (window.sessionStorage) {
                    window.sessionStorage['bcs-crd-cluster'] = this.curClusterId
                }
                this.$router.push({
                    name: 'crdcontrollerInstances',
                    params: {
                        crdKind: crdcontroller.name,
                        clusterId: this.curClusterId
                    }
                })
            },

            search () {
                this.getCrdControllersByCluster()
            },

            refresh () {
                this.searchKeyword = ''
                this.getCrdControllersByCluster()
            },

            /**
             * 简单判断是否为图片
             * @param  {string} img 图片url
             * @return {Boolean} true/false
             */
            isImage (img) {
                if (!img) {
                    return false
                }
                if (img.startsWith('http://') || img.startsWith('https://') || img.startsWith('data:image/')) {
                    return true
                }
                return false
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
