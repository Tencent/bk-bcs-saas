<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-cluster-node-title">
                <i class="bk-icon icon-arrows-left back" @click="goIndex"></i>
                <template v-if="exceptionCode"><span>{{$t('返回')}}</span></template>
                <template v-else>
                    <template v-if="curClusterInPage.cluster_id">
                        <span @click="refreshCurRouter">{{curClusterInPage.name}}</span>
                        <span style="font-size: 12px; color: #c3cdd7;cursor:default;margin-left: 10px;">
                            （{{curClusterInPage.cluster_id}}）
                        </span>
                    </template>
                </template>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper biz-cluster-info-wrapper">
            <app-exception
                v-if="exceptionCode && !containerLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>

            <div v-if="!exceptionCode" class="biz-cluster-info-inner">
                <div class="biz-cluster-tab-header">
                    <div class="header-item" @click="goOverview">
                        <i class="bk-icon icon-bar-chart"></i>{{$t('总览')}}
                    </div>
                    <div class="header-item" @click="goNode">
                        <i class="bk-icon icon-list"></i>{{$t('节点管理')}}
                    </div>
                    <div class="header-item active">
                        <i class="cc-icon icon-cc-machine"></i>{{$t('集群信息')}}
                    </div>
                </div>
                <div class="biz-cluster-tab-content" v-bkloading="{ isLoading: containerLoading, opacity: 1 }">
                    <div class="biz-cluster-info-form-wrapper">
                        <div class="label">
                            {{$t('基本信息')}}
                        </div>
                        <div class="content">
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('集群名称')}}</p>
                                </div>
                                <div class="right">
                                    <template v-if="!isClusterNameEdit">
                                        {{curClusterName}}
                                        <a href="javascript:void(0);" class="bk-text-button ml10" @click="editClusterName">
                                            <span class="bk-icon icon-edit"></span>
                                        </a>
                                    </template>
                                    <template v-else>
                                        <div class="bk-form bk-name-form">
                                            <div class="bk-form-item">
                                                <div class="bk-form-inline-item">
                                                    <input maxlength="64" type="text" :placeholder="$t('请输入集群名称，不超过64个字符')" class="bk-form-input cluster-name" v-model="clusterEditName">
                                                </div>
                                                <div class="bk-form-inline-item">
                                                    <a href="javascript:void(0);" class="bk-text-button" @click="updateClusterName">
                                                        {{$t('保存')}}
                                                    </a>
                                                    <a href="javascript:void(0);" class="bk-text-button" @click="cancelEditClusterName">
                                                        {{$t('取消')}}
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </template>
                                </div>
                            </div>
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('集群ID')}}</p>
                                </div>
                                <div class="right">{{curClusterId}}</div>
                            </div>
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('状态')}}</p>
                                </div>
                                <div class="right">{{statusName}}</div>
                            </div>
                            <!-- <div class="row">
                                <div class="left">
                                    <p>版本</p>
                                </div>
                                <div class="right">{{ver}}</div>
                            </div> -->
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('Master数量')}}</p>
                                </div>
                                <div class="right">
                                    <a href="javascript:void(0);" class="bk-text-button" @click="showMasterInfo">
                                        {{masterCount}}
                                    </a>
                                </div>
                            </div>
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('节点数量')}}</p>
                                </div>
                                <div class="right">{{nodeCount}}</div>
                            </div>
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('配置')}}</p>
                                </div>
                                <div class="right">{{configInfo}}</div>
                            </div>
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('创建时间')}}</p>
                                </div>
                                <div class="right">{{createdTime}}</div>
                            </div>
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('更新时间')}}</p>
                                </div>
                                <div class="right">{{updatedTime}}</div>
                            </div>
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('集群描述')}}</p>
                                </div>
                                <div class="right">
                                    <template v-if="!isClusterDescEdit">
                                        {{description}}
                                        <a href="javascript:void(0);" class="bk-text-button ml10" @click="editClusterDesc">
                                            <span class="bk-icon icon-edit"></span>
                                        </a>
                                    </template>
                                    <template v-else>
                                        <div class="bk-form bk-desc-form">
                                            <div class="bk-form-item">
                                                <div class="bk-form-inline-item">
                                                    <textarea maxlength="128" :placeholder="$t('请输入集群描述，不超过128个字符')" class="bk-form-textarea" v-model="clusterEditDesc"></textarea>
                                                </div>
                                                <div class="bk-form-inline-item">
                                                    <a href="javascript:void(0);" class="bk-text-button" @click="updateClusterDesc">
                                                        {{$t('保存')}}
                                                    </a>
                                                    <a href="javascript:void(0);" class="bk-text-button" @click="cancelEditClusterDesc">
                                                        {{$t('取消')}}
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </template>
                                </div>
                            </div>
                            <div class="row">
                                <div class="left">
                                    <p>{{$t('集群变量')}}</p>
                                </div>
                                <div class="right">
                                    <a href="javascript:void(0);" class="bk-text-button" @click="showSetVariable" v-if="variableCount !== '--'">
                                        {{variableCount}}
                                    </a>
                                    <span v-else>{{variableCount}}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <bk-dialog
            :is-show.sync="dialogConf.isShow"
            :width="dialogConf.width"
            :content="dialogConf.content"
            :has-header="dialogConf.hasHeader"
            :has-footer="dialogConf.hasFooter"
            :close-icon="dialogConf.closeIcon"
            :ext-cls="'biz-cluster-node-dialog'"
            :quick-close="true"
            @confirm="dialogConf.isShow = false">
            <div slot="content">
                <div style="margin: -20px;" v-bkloading="{ isLoading: dialogConf.loading, opacity: 1 }">
                    <div class="biz-cluster-node-dialog-header">
                        <div class="left">
                            {{dialogConf.title}}
                        </div>
                        <div class="bk-dialog-tool" @click="closeDialog">
                            <i class="bk-dialog-close bk-icon icon-close"></i>
                        </div>
                    </div>
                    <div style="min-height: 441px;" :style="{ borderBottomWidth: curPageData.length ? '1px' : 0 }">
                        <table class="bk-table has-table-hover biz-table biz-cluster-node-dialog-table">
                            <thead>
                                <tr>
                                    <th style="width: 350px; padding-left: 30px;">{{$t('主机名称')}}</th>
                                    <th style="width: 220px;">{{$t('内网IP')}}</th>
                                    <th style="width: 120px;">{{$t('Agent状态')}}</th>

                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curPageData.length">
                                    <tr v-for="(host, index) in curPageData" :key="index">
                                        <td style="padding-left: 30px;">
                                            <bk-tooltip placement="top">
                                                <div class="name biz-text-wrapper" style="max-width: 350px;">{{host.host_name || '--'}}</div>
                                                <template slot="content">
                                                    <p style="text-align: left; white-space: normal;word-break: break-all;">{{host.host_name || '--'}}</p>
                                                </template>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            <bk-tooltip placement="top">
                                                <div class="inner-ip">{{host.inner_ip || '--'}}</div>
                                                <template slot="content">
                                                    <p style="text-align: left; white-space: normal;word-break: break-all;">{{host.inner_ip || '--'}}</p>
                                                </template>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            <span class="biz-success-text" style="vertical-align: super;" v-if="String(host.agent) === '1'">
                                                {{$t('正常')}}
                                            </span>
                                            <template v-else-if="String(host.agent) === '0'">
                                                <bk-tooltip placement="top">
                                                    <span class="biz-warning-text f12" style="vertical-align: super;">
                                                        {{$t('异常')}}
                                                    </span>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">
                                                            <template v-if="isEn">
                                                                Agent abnormal, please install first
                                                            </template>
                                                            <template v-else>
                                                                Agent异常，请先安装
                                                            </template>
                                                        </p>
                                                    </template>
                                                </bk-tooltip>
                                            </template>
                                            <span class="biz-danger-text f12" style="vertical-align: super;" v-else>
                                                {{$t('错误')}}
                                            </span>
                                        </td>
                                    </tr>
                                </template>
                                <template v-if="!curPageData.length && !dialogConf.loading">
                                    <tr>
                                        <td colspan="3">
                                            <div class="bk-message-box no-data">
                                                <p class="message empty-message">{{$t('无数据')}}</p>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                    <div class="biz-page-box" v-if="pageConf.show && curPageData.length && (curPageData.length >= pageConf.pageSize || pageConf.curPage !== 1)">
                        <bk-paging
                            :size="'small'"
                            :cur-page.sync="pageConf.curPage"
                            :total-page="pageConf.totalPage"
                            @page-change="pageChange">
                        </bk-paging>
                    </div>
                </div>
            </div>
        </bk-dialog>

        <bk-sideslider
            :is-show.sync="setVariableConf.isShow"
            :title="setVariableConf.title"
            :width="setVariableConf.width"
            @hidden="hideSetVariable"
            class="biz-cluster-set-variable-sideslider"
            :quick-close="false">
            <template slot="content">
                <div class="wrapper" style="position: relative;" v-bkloading="{ isLoading: setVariableConf.loading, opacity: 1 }">
                    <form class="bk-form bk-form-vertical set-label-form">
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <label class="bk-label label">{{$t('变量：')}}</label>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="biz-key-value-wrapper mb10">
                                    <div class="biz-key-value-item" v-for="(variable, index) in variableList" :key="index">
                                        <bk-tooltip placement="top" :delay="500">
                                            <input type="text" class="bk-form-input" disabled v-model="variable.leftContent">
                                            <template slot="content">
                                                <p style="text-align: left; white-space: normal;word-break: break-all;">{{variable.leftContent}}</p>
                                            </template>
                                        </bk-tooltip>
                                        <span class="equals-sign">=</span>
                                        <input type="text" class="bk-form-input right" :placeholder="$t('值')" v-model="variable.value">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="action-inner">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="confirmSetVariable">
                                {{$t('保存')}}
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideSetVariable">
                                {{$t('取消')}}
                            </button>
                        </div>
                    </form>
                </div>
            </template>
        </bk-sideslider>
    </div>
</template>

<script>
    import moment from 'moment'

    import { catchErrorHandler } from '@open/common/util'

    export default {
        data () {
            return {
                isClusterNameEdit: false,
                isClusterDescEdit: false,
                containerLoading: false,
                curClusterInPage: {},
                dialogConf: {
                    isShow: false,
                    width: 920,
                    hasHeader: false,
                    hasFooter: false,
                    closeIcon: false,
                    title: '',
                    loading: false
                },
                pageConf: {
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                curPageData: [],
                masterList: [],
                winHeight: 0,
                curClusterName: '',
                curClusterId: '',
                clusterEditName: '',
                clusterEditDesc: '',
                status: '',
                statusName: '',
                ver: '',
                masterCount: '',
                nodeCount: '',
                areaName: '',
                createdTime: '',
                updatedTime: '',
                description: '',
                configInfo: '',
                variableCount: '',
                variableList: [],
                setVariableConf: {
                    isShow: false,
                    title: this.$t('设置变量'),
                    width: 680,
                    loading: false
                },
                bkMessageInstance: null,
                exceptionCode: null
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
                return this.$store.state.cluster.curCluster || {}
            },
            isEn () {
                return this.$store.state.isEn
            }
        },
        destroyed () {
            this.bkMessageInstance && this.bkMessageInstance.close()
        },
        created () {
            if (!this.curCluster || Object.keys(this.curCluster).length <= 0) {
                if (this.projectId && this.clusterId) {
                    this.fetchData()
                }
            } else {
                this.fetchClusterInfo()
            }
        },
        mounted () {
            this.winHeight = window.innerHeight
        },
        methods: {
            editClusterName () {
                this.clusterEditName = this.curClusterName
                this.isClusterNameEdit = true
            },
            editClusterDesc () {
                this.clusterEditDesc = this.description
                this.isClusterDescEdit = true
            },
            cancelEditClusterName () {
                this.clusterEditName = ''
                this.isClusterNameEdit = false
            },
            cancelEditClusterDesc () {
                this.clusterEditDesc = this.curClusterDesc
                this.isClusterDescEdit = false
            },

            /**
             * 获取当前集群数据
             */
            async fetchData () {
                this.containerLoading = true
                try {
                    const res = await this.$store.dispatch('cluster/getCluster', {
                        projectId: this.projectId,
                        clusterId: this.clusterId
                    })

                    this.$store.commit('cluster/forceUpdateCurCluster', res.data)
                    this.fetchClusterInfo()
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取当前集群数据
             */
            async fetchClusterInfo () {
                this.containerLoading = true
                try {
                    const res = await this.$store.dispatch('cluster/getClusterInfo', {
                        projectId: this.projectId,
                        clusterId: this.curCluster.cluster_id // 这里用 this.curCluster 来获取是为了使计算属性生效
                    })

                    const data = res.data || {}
                    this.curClusterName = data.cluster_name || '--'
                    this.curClusterId = data.cluster_id || '--'
                    this.status = data.status || '--'
                    this.statusName = data.chinese_status_name || '--'
                    this.ver = data.ver || '--'
                    let masterCount = data.master_count || 0
                    if (masterCount) {
                        masterCount += this.isEn ? '' : '个'
                    } else {
                        masterCount = '--'
                    }
                    this.masterCount = masterCount

                    this.nodeCount = data.node_count || '--'
                    this.areaName = data.area_name || '--'
                    this.createdTime = data.created_at ? moment(data.created_at).format('YYYY-MM-DD HH:mm:ss') : '--'
                    this.updatedTime = data.updated_at ? moment(data.updated_at).format('YYYY-MM-DD HH:mm:ss') : '--'
                    this.description = data.description || '--'

                    this.configInfo = this.isEn ? `${data.total_cpu}core${(data.total_mem).toFixed(0)}GB` : `${data.total_cpu}核${(data.total_mem).toFixed(0)}GB`

                    this.fetchVariableInfo()
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取变量信息
             */
            async fetchVariableInfo () {
                try {
                    const res = await this.$store.dispatch('cluster/getClusterVariableInfo', {
                        projectId: this.projectId,
                        clusterId: this.curCluster.cluster_id // 这里用 this.curCluster 来获取是为了使计算属性生效
                    })

                    let variableCount = res.count || 0
                    if (variableCount) {
                        variableCount += this.isEn ? '' : '个'
                    } else {
                        variableCount = '--'
                    }
                    this.variableCount = variableCount
                    const variableList = []
                    ;(res.data || []).forEach(item => {
                        item.leftContent = `${item.name}(${item.key})`
                        variableList.push(item)
                    })

                    this.variableList.splice(0, this.variableList.length, ...variableList)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.containerLoading = false
                    setTimeout(() => {
                        this.setVariableConf.loading = false
                    }, 300)
                }
            },

            /**
             * 显示集群变量 sideslider
             */
            async showSetVariable () {
                this.setVariableConf.isShow = true
                this.setVariableConf.loading = true
                await this.fetchVariableInfo()
            },

            /**
             * 设置变量 sideslder 确认按钮
             */
            async confirmSetVariable () {
                const variableList = []

                const len = this.variableList.length
                for (let i = 0; i < len; i++) {
                    const variable = this.variableList[i]
                    variableList.push({
                        id: variable.id,
                        key: variable.key,
                        name: variable.name,
                        value: variable.value
                    })
                }

                try {
                    this.setVariableConf.loading = true
                    await this.$store.dispatch('cluster/updateClusterVariableInfo', {
                        projectId: this.projectId,
                        clusterId: this.curCluster.cluster_id, // 这里用 this.curCluster 来获取是为了使计算属性生效
                        cluster_vars: variableList
                    })

                    this.hideSetVariable()
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    setTimeout(() => {
                        this.setVariableConf.loading = false
                    }, 300)
                }
            },

            /**
             * 设置标签 sideslder 取消按钮
             */
            hideSetVariable () {
                this.setVariableConf.isShow = false
                this.variableList.splice(0, this.variableList.length, ...[])
            },

            /**
             * 显示 master 信息
             */
            async showMasterInfo () {
                try {
                    this.pageConf.curPage = 1
                    this.dialogConf.isShow = true
                    this.dialogConf.title = this.$t('Master信息')
                    this.dialogConf.loading = true
                    this.curPageData.splice(0, this.curPageData.length, ...[])

                    const res = await this.$store.dispatch('cluster/getClusterMasterInfo', {
                        projectId: this.projectId,
                        clusterId: this.curCluster.cluster_id // 这里用 this.curCluster 来获取是为了使计算属性生效
                    })
                    const list = res.data || []
                    this.masterList.splice(0, this.masterList.length, ...list)
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)
                } catch (e) {
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.dialogConf.loading = false
                }
            },

            /**
             * 初始化弹层翻页条
             */
            initPageConf () {
                const total = this.masterList.length
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize) || 1
            },

            /**
             * 翻页回调
             *
             * @param {number} page 当前页
             */
            pageChange (page) {
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData.splice(0, this.curPageData.length, ...data)
            },

            /**
             * 获取当前这一页的数据
             *
             * @param {number} page 当前页
             *
             * @return {Array} 当前页数据
             */
            getDataByPage (page) {
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.masterList.length) {
                    endIndex = this.masterList.length
                }
                const data = this.masterList.slice(startIndex, endIndex)
                return data
            },

            /**
             * 关闭弹窗
             */
            closeDialog () {
                this.dialogConf.isShow = false
            },

            /**
             * 刷新当前 router
             */
            refreshCurRouter () {
                typeof this.$parent.refreshRouterView === 'function' && this.$parent.refreshRouterView()
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
             * 切换到节点管理
             */
            goNode () {
                this.$router.push({
                    name: 'clusterNode',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        clusterId: this.clusterId,
                        backTarget: this.$route.params.backTarget
                    }
                })
            },

            updateClusterName () {
                const projectId = this.projectId
                const clusterId = this.clusterId
                const data = {
                    name: this.clusterEditName
                }
                if (!data.name) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入集群名称')
                    })
                    return false
                }
                this.$store.dispatch(
                    'cluster/updateCluster',
                    { projectId: projectId, clusterId: clusterId, data }
                ).then(res => {
                    this.isClusterNameEdit = false
                    this.clusterEditName = ''
                    this.curClusterName = data.name
                    this.curClusterInPage.name = data.name
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('修改成功！')
                    })
                }).catch(res => {
                    this.$bkMessage({
                        theme: 'error',
                        message: res.message || res.data.msg || res.statusText
                    })
                })
            },

            updateClusterDesc () {
                const projectId = this.projectId
                const clusterId = this.clusterId
                const data = {
                    description: this.clusterEditDesc
                }
                if (!data.description) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入集群描述')
                    })
                    return false
                }
                this.$store.dispatch(
                    'cluster/updateCluster',
                    { projectId: projectId, clusterId: clusterId, data }
                ).then(res => {
                    this.isClusterDescEdit = false
                    this.clusterEditDesc = ''
                    this.description = data.description
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('修改成功！')
                    })
                }).catch(res => {
                    this.$bkMessage({
                        theme: 'error',
                        message: res.message || res.data.msg || res.statusText
                    })
                })
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import './info.css';

    .bk-name-form {
        line-height: 36px;

        .bk-form-input {
            width: 400px;
            margin-right: 15px;
            font-size: 12px;
        }
    }

    .bk-desc-form {
        line-height: 70px;

        .bk-form-textarea {
            width: 400px;
            margin-right: 15px;
            font-size: 12px;
        }
    }

</style>
