<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-cluster-title">
                {{$t('集群')}}
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper biz-cluster-wrapper" v-bkloading="{ isLoading: showLoading, opacity: 0.1 }">
            <app-exception
                v-if="exceptionCode && !showLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>
            <template v-if="!exceptionCode && clusterList.length && !showLoading">
                <div class="biz-cluster-list">
                    <div class="biz-cluster" v-for="(cluster, clusterIndex) in clusterList" :key="clusterIndex">
                        <!-- 异常状态 -->
                        <div class="bk-mark-corner bk-warning" v-if="
                            cluster.status === 'normal'
                                && (
                                    conversionPercent(cluster.remain_cpu, cluster.total_cpu) >= 80
                                || conversionPercent(cluster.remain_mem, cluster.total_mem) >= 80
                                || conversionPercent(cluster.remain_disk, cluster.total_disk) >= 80
                                )
                        ">
                            <p>!</p>
                        </div>
                        <div class="biz-cluster-header">
                            <bk-tooltip :content="cluster.name" :delay="500" placement="top">
                                <h2 class="cluster-title">
                                    <a href="javascript:void(0)"
                                        v-if="cluster.status !== 'initializing'
                                            && cluster.status !== 'so_initializing'
                                            && cluster.status !== 'initial_checking'
                                            && cluster.status !== 'initial_failed'
                                            && cluster.status !== 'so_init_failed'
                                            && cluster.status !== 'check_failed'
                                            && cluster.status !== 'removing'
                                            && cluster.status !== 'remove_failed'
                                        "
                                        @click="goOverviewOrNode('clusterOverview', cluster)">
                                        {{cluster.name}}
                                    </a>
                                    <span v-else>{{cluster.name}}</span>
                                </h2>
                            </bk-tooltip>
                            <p class="cluster-metadata">
                                <bk-tooltip :content="cluster.cluster_id" :delay="500" placement="top">
                                    <span class="cluster-id">{{cluster.cluster_id}}</span>
                                </bk-tooltip>
                            </p>
                            <bk-dropdown-menu
                                v-if="
                                    cluster.status !== 'initializing'
                                        && cluster.status !== 'so_initializing'
                                        && cluster.status !== 'initial_checking'
                                        && cluster.status !== 'initial_failed'
                                        && cluster.status !== 'so_init_failed'
                                        && cluster.status !== 'check_failed'
                                        && cluster.status !== 'removing'
                                        && cluster.status !== 'remove_failed'
                                "
                                @show="showDropdownMenu(clusterIndex)"
                                @hide="hideDropdownMenu(clusterIndex)">
                                <button class="cluster-opera-btn" :ref="`operaBtn${clusterIndex}`" slot="dropdown-trigger">
                                    <i class="bk-icon icon-more"></i>
                                </button>
                                <ul class="bk-dropdown-list" slot="dropdown-content" style="max-height: 210px; overflow: visible;">
                                    <li>
                                        <a href="javascript:void(0)" @click="goOverviewOrNode('clusterOverview', cluster)">{{$t('总览')}}</a>
                                    </li>
                                    <li>
                                        <a href="javascript:void(0)" @click="goClusterInfo(cluster)">{{$t('集群信息')}}</a>
                                    </li>
                                    <li v-if="isHelmEnable">
                                        <a href="javascript:void(0)" @click="enableClusterHelm(cluster)">{{$t('启用Helm')}}</a>
                                    </li>
                                    <template v-if="cluster.allow">
                                        <li>
                                            <a href="javascript:void(0)" @click="confirmDeleteCluster(cluster, clusterIndex)">{{$t('删除')}}</a>
                                        </li>
                                    </template>
                                    <template v-else>
                                        <li style="position: relative;">
                                            <a class="bk-tooltip biz-cluster-delete-tooltip">
                                                <bk-tooltip :content="$t('您需要删除集群内所有节点后，再进行集群删除操作')" placement="right">
                                                    <div class="bk-dropdown-item cluster-btn-disabled">{{$t('删除')}}</div>
                                                </bk-tooltip>
                                            </a>
                                        </li>
                                    </template>
                                    <li v-if="!cluster.permissions.use">
                                        <a :href="createApplyPermUrl({
                                            policy: 'use',
                                            projectCode: projectCode,
                                            idx: `cluster_${cluster.environment === 'stag' ? 'test' : 'prod'}:${cluster.cluster_id}`
                                        })" target="_blank">{{$t('申请使用权限')}}</a>
                                    </li>
                                </ul>
                            </bk-dropdown-menu>
                            <bk-dropdown-menu
                                v-else-if="cluster.allow === true"
                                @show="showDropdownMenu(clusterIndex)"
                                @hide="hideDropdownMenu(clusterIndex)">
                                <button class="cluster-opera-btn" :ref="`operaBtn${clusterIndex}`" slot="dropdown-trigger">
                                    <i class="bk-icon icon-more"></i>
                                </button>
                                <ul class="bk-dropdown-list" slot="dropdown-content">
                                    <li>
                                        <a href="javascript:void(0)" @click="confirmDeleteCluster(cluster, clusterIndex)">{{$t('删除')}}</a>
                                    </li>
                                </ul>
                            </bk-dropdown-menu>
                        </div>
                        <div class="biz-cluster-content" v-if="cluster.status === 'removing'">
                            <div class="biz-status-box">
                                <div class="status-icon">
                                    <div class="bk-spin-loading bk-spin-loading-large bk-spin-loading-primary">
                                        <div class="rotate rotate1"></div>
                                        <div class="rotate rotate2"></div>
                                        <div class="rotate rotate3"></div>
                                        <div class="rotate rotate4"></div>
                                        <div class="rotate rotate5"></div>
                                        <div class="rotate rotate6"></div>
                                        <div class="rotate rotate7"></div>
                                        <div class="rotate rotate8"></div>
                                    </div>
                                </div>
                                <p class="status-text">{{$t('正在删除中，请稍等···')}}</p>
                                <div class="status-opera">
                                    <a href="javascript:void(0);" class="bk-text-button" @click.prevent="showLog(cluster)">{{$t('查看日志')}}</a>
                                </div>
                            </div>
                        </div>

                        <!-- 删除失败 -->
                        <div class="biz-cluster-content" v-else-if="cluster.status === 'remove_failed'">
                            <div class="biz-status-box">
                                <div class="status-icon danger">
                                    <i class="bk-icon icon-close-circle"></i>
                                </div>
                                <p class="status-text">{{$t('删除失败，请重试')}}</p>
                                <div class="status-opera">
                                    <a href="javascript:void(0);" class="bk-text-button" @click.prevent="showLog(cluster)">{{$t('查看日志')}}</a> |
                                    <a href="javascript:void(0);" class="bk-text-button" @click="confirmDeleteCluster(cluster, clusterIndex)">{{$t('重新删除')}}</a>
                                </div>
                            </div>
                        </div>

                        <!-- 初始化中 -->
                        <div class="biz-cluster-content" v-else-if="cluster.status === 'initializing' || cluster.status === 'so_initializing' || cluster.status === 'initial_checking'">
                            <div class="biz-status-box">
                                <div class="status-icon">
                                    <div class="bk-spin-loading bk-spin-loading-large bk-spin-loading-primary">
                                        <div class="rotate rotate1"></div>
                                        <div class="rotate rotate2"></div>
                                        <div class="rotate rotate3"></div>
                                        <div class="rotate rotate4"></div>
                                        <div class="rotate rotate5"></div>
                                        <div class="rotate rotate6"></div>
                                        <div class="rotate rotate7"></div>
                                        <div class="rotate rotate8"></div>
                                    </div>
                                </div>
                                <p class="status-text">{{$t('正在初始化中，请稍等···')}}</p>
                                <div class="status-opera">
                                    <a href="javascript:void(0);" class="bk-text-button" @click.prevent="showLog(cluster)">{{$t('查看日志')}}</a>
                                </div>
                            </div>
                        </div>

                        <!-- 初始化失败 -->
                        <div class="biz-cluster-content" v-else-if="cluster.status === 'initial_failed' || cluster.status === 'so_init_failed' || cluster.status === 'check_failed'">
                            <div class="biz-status-box">
                                <div class="status-icon danger">
                                    <i class="bk-icon icon-close-circle"></i>
                                </div>
                                <p class="status-text">{{$t('初始化失败，请重试')}}</p>
                                <div class="status-opera">
                                    <a href="javascript:void(0);" class="bk-text-button" @click.prevent="showLog(cluster)">{{$t('查看日志')}}</a> |
                                    <a href="javascript:void(0);" class="bk-text-button" @click="reInitializationCluster(cluster, clusterIndex)">{{$t('重新初始化')}}</a> <!-- |
                                    <a href="javascript:void(0);" class="bk-text-button">修改参数</a> -->
                                </div>
                            </div>
                        </div>

                        <!-- 集群创建成功！提示 -->
                        <div class="biz-cluster-content" v-else-if="cluster.status === 'showSuccess'">
                            <div class="biz-status-box">
                                <div class="status-icon success">
                                    <i class="bk-icon icon-check-circle"></i>
                                </div>
                                <p class="status-text">{{$t('恭喜，集群创建成功！')}}</p>
                            </div>
                        </div>

                        <!-- 正常状态 -->
                        <template v-else>
                            <div class="biz-cluster-content" :class="curProject.kind === PROJECT_MESOS ? 'more-info' : ''">
                                <div class="biz-progress-box">
                                    <div class="progress-header">
                                        <span class="title">{{$t('CPU使用率')}}</span>
                                        <span class="percent">
                                            {{conversionPercent(cluster.remain_cpu, cluster.total_cpu)}}%
                                        </span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar primary"
                                            :style="{ width: `${conversionPercent(cluster.remain_cpu, cluster.total_cpu)}%` }"></div>
                                    </div>
                                </div>
                                <div class="biz-progress-box">
                                    <div class="progress-header">
                                        <span class="title">{{$t('内存使用率')}}</span>
                                        <span class="percent">
                                            {{conversionPercent(cluster.remain_mem, cluster.total_mem)}}%
                                        </span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar success" :style="{ width: `${conversionPercent(cluster.remain_mem, cluster.total_mem)}%` }"></div>
                                    </div>
                                </div>
                                <div class="biz-progress-box">
                                    <div class="progress-header">
                                        <span class="title">{{$t('磁盘使用率')}}</span>
                                        <span class="percent">
                                            {{conversionPercent(cluster.remain_disk, cluster.total_disk)}}%
                                        </span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar warning" :style="{ width: `${conversionPercent(cluster.remain_disk, cluster.total_disk)}%` }"></div>
                                    </div>
                                </div>
                                <div class="biz-progress-box" v-if="curProject.kind === PROJECT_MESOS">
                                    <div class="progress-header">
                                        <span class="title">{{$t('集群IP')}}</span>
                                        <span class="percent">
                                            {{cluster.ip_resource_total === 0 ? 0 : `${cluster.ip_resource_used} / ${cluster.ip_resource_total}`}}
                                        </span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar warning" :style="{ width: `${cluster.ip_resource_total === 0 ? 0 : conversionPercent(cluster.ip_resource_total - cluster.ip_resource_used, cluster.ip_resource_total)}%` }"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="add-node-btn-wrapper">
                                <button class="bk-button bk-default add-node-btn" @click="goOverviewOrNode('clusterNode', cluster)">
                                    <span>{{$t('添加节点')}}</span>
                                </button>
                            </div>
                        </template>
                    </div>
                    <div class="biz-cluster biz-cluster-add" @click="gotCreateCluster">
                        <div class="add-btn">
                            <!-- <i class="bk-icon icon-plus"></i> -->
                            <img src="@open/images/plus.svg" />
                            <strong>{{$t('点击新建集群')}}</strong>
                        </div>
                    </div>
                </div>
            </template>
            <template v-else-if="!exceptionCode && !clusterList.length && !showLoading">
                <div :class="['biz-guide-box',{ 'show-guide': isShowGuide }]" v-show="!showLoading">
                    <p class="title">{{$t('欢迎使用容器服务')}}</p>
                    <p class="desc">{{$t('使用容器服务，蓝鲸将为您快速搭建、运维和管理容器集群，您可以轻松对容器进行启动、停止等操作，也可以查看集群、容器及服务的状态，以及使用各种组件服务。')}}</p>
                    <p class="desc">
                        <a :href="PROJECT_CONFIG.doc.quickStart" target="_blank">{{$t('请点击了解更多')}}<i class="bk-icon icon-angle-double-right ml5"></i></a>
                    </p>
                    <a href="javascript:void(0);" class="bk-button bk-primary bk-button-large" @click="gotCreateCluster">
                        <span style="margin-left: 0;">{{$t('创建容器集群')}}</span>
                    </a>

                    <a class="bk-button bk-default bk-button-large" :href="PROJECT_CONFIG.doc.quickStart" target="_blank">
                        <span style="margin-left: 0;">{{$t('快速入门指引')}}</span>
                    </a>
                </div>
            </template>
        </div>

        <cluster-guide ref="clusterGuide" @status-change="toggleGuide"></cluster-guide>

        <bk-sideslider
            :is-show.sync="logSideDialogConf.isShow"
            :title="logSideDialogConf.title"
            @hidden="closeLog"
            :quick-close="true">
            <div slot="content" style="margin: 0 0 0 20px;">
                <template v-if="logEndState === 'none'">
                    <div class="biz-no-data">
                        {{$t('暂无日志信息')}}
                    </div>
                </template>
                <template v-else>
                    <div class="biz-log-box">
                        <div class="operation-item" v-for="(op, index) in logList" :key="index">
                            <p class="log-message title">
                                {{op.prefix_message}}
                            </p>
                            <div class="log-message item" v-for="(task, taskIndex) in op.log.node_tasks" :key="taskIndex">
                                {{task.name}} -
                                <span v-if="task.state.toLowerCase() === 'failure'" class="biz-danger-text">
                                    {{task.state}}
                                </span>
                                <span v-else-if="task.state.toLowerCase() === 'success'" class="biz-success-text">
                                    {{task.state}}
                                </span>
                                <span v-else-if="task.state.toLowerCase() === 'running'" class="biz-warning-text">
                                    {{task.state}}
                                </span>
                                <div v-else-if="task.state.indexOf('html-tag') > -1" v-html="task.state">
                                </div>
                                <span v-else>
                                    {{task.state}}
                                </span>
                            </div>
                            <div v-if="op.status.toLowerCase() === 'success'" class="biz-success-text f14" style="margin: 0 0 5px 0; font-weight: 700; margin-left: 20px;">
                                {{$t('操作成功')}}
                            </div>
                            <div v-else-if="op.status.toLowerCase() === 'failed'" class="biz-danger-text f14" style="margin: 0 0 5px 0; font-weight: 700; margin-left: 20px;">
                                {{$t('操作失败')}}
                                <span style="margin-left: 10px;" v-if="op.taskUrl"><a :href="op.taskUrl" class="bk-text-button" target="_blank">{{$t('查看详情')}}</a></span>
                            </div>
                            <div style="margin: 10px 0px 5px 13px; font-size: 10px;" v-else>
                                <div class="bk-spin-loading bk-spin-loading-small bk-spin-loading-primary">
                                    <div class="rotate rotate1"></div>
                                    <div class="rotate rotate2"></div>
                                    <div class="rotate rotate3"></div>
                                    <div class="rotate rotate4"></div>
                                    <div class="rotate rotate5"></div>
                                    <div class="rotate rotate6"></div>
                                    <div class="rotate rotate7"></div>
                                    <div class="rotate rotate8"></div>
                                </div>
                                {{$t('正在加载中...')}}
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </bk-sideslider>

        <bk-dialog
            :is-show.sync="helmDialog.isShow"
            :width="500"
            :has-footer="false"
            :title="helmDialog.title"
            :quick-close="true"
            @cancel="helmDialog.isShow = false">
            <div slot="content">
                <pre class="bk-intro bk-danger biz-error-message" v-if="helmEnableMessage">
                    {{helmEnableMessage}}
                </pre>

                <div class="helm-repos-detail" v-else>
                    <div class="repos-item">
                        <div class="wrapper mb10">
                            <p class="url mb15" v-if="isEn">You can manage K8S resources through <router-link class="bk-text-button bk-primary" :to="{ name: 'helmTplList' }">Helm Chart</router-link></p>
                            <p class="url mb15" v-else>您可以通过<router-link class="bk-text-button bk-primary" :to="{ name: 'helmTplList' }">Helm Chart</router-link>的方式管理K8S资源</p>
                            <p class="url mb25">
                                <a :href="PROJECT_CONFIG.doc.serviceAccess" target="_blank" class="bk-text-button">{{$t('点击了解更多')}}</a>
                            </p>
                        </div>
                    </div>
                </div>

                <div class="biz-message" v-if="helmErrorCode === 40032">
                    <template v-if="isEn">
                        <h3>No nodes under cluster, and you need to:</h3>
                        <p>Under cluster, add nodes</p>
                    </template>
                    <template v-else>
                        <h3>集群下没有节点，您需要：</h3>
                        <p>在集群下，添加节点</p>
                    </template>
                </div>
            </div>
        </bk-dialog>

        <tip-dialog
            ref="clusterNoticeDialog"
            icon="bk-icon icon-exclamation-triangle"
            :title="$t('确定删除集群？')"
            :sub-title="$t('此操作无法撤回，请确认：')"
            :check-list="clusterNoticeList"
            :confirm-btn-text="$t('确定')"
            :cancel-btn-text="$t('取消')"
            :confirm-callback="deleteCluster">
        </tip-dialog>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'
    import applyPerm from '@open/mixins/apply-perm'
    import tipDialog from '@open/components/tip-dialog'
    import ClusterGuide from './guide'

    export default {
        components: {
            'cluster-guide': ClusterGuide,
            tipDialog
        },
        mixins: [applyPerm],
        data () {
            return {
                helmErrorCode: 0,
                helmEnableMessage: '',
                clusterNoticeList: [
                    {
                        id: 1,
                        text: this.$t('将master主机归还到你业务的空闲机模块'),
                        isChecked: false
                    },
                    {
                        id: 2,
                        text: this.$t('清理其它容器服务相关组件'),
                        isChecked: false
                    }
                ],
                isShowGuide: false,
                showLoading: false,
                timer: null,
                storage: localStorage || {},
                logSideDialogConf: {
                    isShow: false,
                    title: '',
                    timer: null
                },
                helmDialog: {
                    title: '',
                    isShow: false
                },
                curClusterHelm: null,
                logList: [],
                logEndState: '',
                exceptionCode: null,
                curCluster: null,
                curClusterIndex: 0,
                permissions: {},
                cancelLoop: false,
                PROJECT_MESOS: window.PROJECT_MESOS
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            clusterList () {
                const clusterList = []
                this.$store.state.cluster.clusterList.forEach(item => {
                    clusterList.push(item)
                })

                return clusterList
            },
            isHelmEnable () {
                return false
            },
            isEn () {
                return this.$store.state.isEn
            },
            curProject () {
                return this.$store.state.curProject
            }
        },
        created () {
            // created 时也需要执行一次 release，因为如果仅仅只在 destroyed 中执行的话，有时候不会 clearTimeout，
            // 在 getClusters 请求完毕正要执行 setTimeout 的时候切换，有可能不会 clearTimeout，所以在 created 里再执行一次
            this.release()
            this.cancelLoop = false
            this.getClusters()
            const guide = this.$refs.clusterGuide
            guide && guide.hide()
        },
        beforeDestroy () {
            this.release()
        },
        methods: {
            /**
             * 创建集群
             */
            async gotCreateCluster () {
                if (!this.permissions.create) {
                    await this.$store.dispatch('getMultiResourcePermissions', {
                        project_id: this.projectId,
                        operator: 'or',
                        resource_list: [
                            {
                                policy_code: 'create',
                                resource_type: 'cluster_test'
                            },
                            {
                                policy_code: 'create',
                                resource_type: 'cluster_prod'
                            }
                        ]
                    })
                }

                this.$router.push({
                    name: 'clusterCreate',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
            },

            /**
             * 释放资源，重置 timer 等等
             */
            release () {
                clearTimeout(this.timer)
                this.timer = null
                this.cancelLoop = true
                this.storage.removeItem('initializingClusters')
                clearTimeout(this.logSideDialogConf.timer)
                this.logSideDialogConf.timer = null
            },

            /**
             * 显示集群更多下拉框
             *
             * @param {number} clusterIndex 当前集群索引
             */
            showDropdownMenu (clusterIndex) {
                this.$refs[`operaBtn${clusterIndex}`][0].classList.add('hover')
            },

            /**
             * 隐藏集群更多下拉框
             *
             * @param {number} clusterIndex 当前集群索引
             */
            hideDropdownMenu (clusterIndex) {
                this.$refs[`operaBtn${clusterIndex}`][0].classList.remove('hover')
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
                if (!total || total === 0) {
                    return 0
                }

                let ret = (total - remain) / total * 100
                if (ret !== 0 && ret !== 100) {
                    ret = ret.toFixed(2)
                }
                return ret
            },

            /**
             * 设置 localStorage
             *
             * @param {Object} cluster 当前集群对象
             */
            setStorage (cluster) {
                const storage = JSON.parse(this.storage.getItem('initializingClusters') || JSON.stringify({}))
                storage[`${cluster.project_id}_${cluster.cluster_id}`] = '1'
                this.storage.setItem('initializingClusters', JSON.stringify(storage))
            },

            /**
             * 检测 localStorage
             *
             * @param {Object} cluster 当前集群对象
             * @param {number} index 集群对象在集群列表中的索引
             * @param {Array} clusterList 集群列表
             * @param {string} status 当前集群状态
             */
            checkStorage (cluster, index, clusterList, status) {
                let storage = this.storage.getItem('initializingClusters')
                if (storage) {
                    storage = JSON.parse(storage)
                    if (storage[`${cluster.project_id}_${cluster.cluster_id}`]) {
                        if (status === 'normal') {
                            clusterList[index].status = 'showSuccess'
                            this.$set(clusterList, index, clusterList[index])
                            let t = setTimeout(() => {
                                clearTimeout(t) && (t = null)
                                clusterList[index].status = 'normal'
                                this.$set(clusterList, index, clusterList[index])
                            }, 3000)
                        }
                        delete storage[`${cluster.project_id}_${cluster.cluster_id}`]
                        this.storage.setItem('initializingClusters', JSON.stringify(storage))
                    }
                }
            },

            /**
             * 查看日志
             *
             * @param {Object} cluster 当前集群对象
             */
            async showLog (cluster) {
                this.logSideDialogConf.isShow = true
                this.logSideDialogConf.title = cluster.cluster_id
                try {
                    const res = await this.$store.dispatch('cluster/getClusterLogs', {
                        projectId: cluster.project_id,
                        clusterId: cluster.cluster_id
                    })

                    const { status, log = [], task_url: taskUrl = '' } = res.data

                    // 最终的状态
                    // running / failed / success
                    this.logEndState = status

                    const tasks = []
                    log.forEach(operation => {
                        if (operation.log.node_tasks) {
                            operation.log.node_tasks.forEach(task => {
                                task.state = task.state.replace(/\|/ig, '<p class="html-tag"></p>')
                                task.state = task.state.replace(/(Failed)/ig, '<span class="biz-danger-text">$1</span>')
                                task.state = task.state.replace(/(OK)/ig, '<span class="biz-success-text">$1</span>')
                            })
                        }
                        operation.taskUrl = taskUrl
                        tasks.push(operation)
                    })

                    this.logList.splice(0, this.logList.length, ...tasks)

                    if (this.logEndState === 'success'
                        || this.logEndState === 'failed'
                        || this.logEndState === 'none'
                    ) {
                        clearTimeout(this.logSideDialogConf.timer)
                        this.logSideDialogConf.timer = null
                    } else {
                        this.logSideDialogConf.timer = setTimeout(() => {
                            this.showLog(cluster)
                        }, 5000)
                    }
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 关闭日志
             *
             * @param {Object} cluster 当前集群对象
             */
            closeLog () {
                // 还未轮询完即日志还未到最终状态
                if (this.logSideDialogConf.timer) {
                    clearTimeout(this.logSideDialogConf.timer)
                    this.logSideDialogConf.timer = null
                } else {
                    if (this.logEndState !== 'none') {
                        this.getClusters(true)
                    }
                }
                this.logList.splice(0, this.logList.length, ...[])
                this.logEndState = ''
            },

            /**
             * 获取所有的集群
             */
            async getClusters (notLoading) {
                if (this.cancelLoop) {
                    return
                }

                if (!notLoading) {
                    this.showLoading = true
                }

                try {
                    const res = await this.$store.dispatch('cluster/getClusterList', this.projectId)
                    this.permissions = JSON.parse(JSON.stringify(res.permissions || {}))

                    const list = res.data.results || []

                    list.forEach((item, index) => {
                        this.getClusterIp(item, index)
                        // item.remain_cpu = 50
                        // item.total_cpu = 100

                        // item.remain_mem = 20
                        // item.total_mem = 80

                        // item.remain_disk = 16
                        // item.total_disk = 97

                        // item.ip_resource_used = 38
                        // item.ip_resource_total = 65
                    })

                    this.$store.commit('cluster/forceUpdateClusterList', list)

                    list.forEach((item, index) => {
                        if (item.status === 'initializing' || item.status === 'so_initializing') {
                            this.setStorage(item)
                        } else {
                            this.checkStorage(item, index, list, item.status)
                        }
                    })

                    if (this.cancelLoop) {
                        clearTimeout(this.timer)
                        this.timer = null
                    } else {
                        this.timer = setTimeout(() => {
                            this.getClusters(true)
                        }, 29000)
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.showLoading = false
                }
            },

            /**
             * 获取 mesos 集群 ip 信息
             *
             * @param {Object} cluster 集群对象
             * @param {number} index 集群对象索引
             */
            async getClusterIp (cluster, index) {
                try {
                    const res = await this.$store.dispatch('cluster/getIpPools', {
                        projectId: this.projectId,
                        clusterId: cluster.cluster_id
                    })
                    const data = res.data || {}
                    cluster.ip_resource_total = data.availableip + data.activeip
                    cluster.ip_resource_used = data.availableip
                    this.$set(this.clusterList, index, cluster)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 重新初始化
             *
             * @param {Object} cluster 当前集群对象
             * @param {number} index 集群对象在集群列表中的索引
             */
            async reInitializationCluster (cluster, index) {
                cluster.status = 'initializing'
                this.$set(this.clusterList, index, cluster)
                try {
                    await this.$store.dispatch('cluster/reInitializationCluster', {
                        projectId: cluster.project_id,
                        clusterId: cluster.cluster_id
                    })

                    cluster.status = 'initializing'
                    this.$set(this.clusterList, index, cluster)

                    clearTimeout(this.timer) && (this.timer = null)
                    this.getClusters(true)
                } catch (e) {
                    cluster.status = 'initial_failed'
                    this.$set(this.clusterList, index, cluster)

                    catchErrorHandler(e, this)
                }
            },

            /**
             * 切换到集群总览 router
             *
             * @param {string} target 目标 router
             * @param {Object} cluster 当前集群对象
             */
            async goOverviewOrNode (target, cluster) {
                if (!cluster.permissions.view) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: cluster.cluster_id,
                        resource_name: cluster.name,
                        resource_type: `cluster_${cluster.environment === 'stag' ? 'test' : 'prod'}`
                    })
                }

                this.$store.commit('cluster/forceUpdateCurCluster', cluster)
                this.$router.push({
                    name: target,
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        clusterId: cluster.cluster_id
                    }
                })
            },

            /**
             * 打开 web console
             *
             * @param {Object} cluster 当前集群对象
             * @param {number} index 集群对象在集群列表中的索引
             */
            openWebConsole (cluster, index) {
                // {host}/backend/web_console/projects/this.projectId/clusters/cluster.cluster_id/
                const location = window.location
                window.open(
                    `${location.protocol}//${location.host.replace(/\.bcs/, '')}/backend/web_console/projects/`
                        + `${this.projectId}/clusters/${cluster.cluster_id}/`,
                    'web-console',
                    'left=100,top=100,width=990,height=590,toolbar=0,resizable=1'
                )
            },

            /**
             * 到集群信息页面
             *
             * @param {Object} cluster 当前集群对象
             */
            async goClusterInfo (cluster) {
                if (!cluster.permissions.view) {
                    const type = `cluster_${cluster.environment === 'stag' ? 'test' : 'prod'}`
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: cluster.cluster_id,
                        resource_name: cluster.name,
                        resource_type: type
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.$store.commit('cluster/forceUpdateCurCluster', cluster)
                this.$router.push({
                    name: 'clusterInfo',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        clusterId: cluster.cluster_id
                    }
                })
            },

            async enableClusterHelm (cluster) {
                this.curClusterHelm = null
                this.helmEnableMessage = ''
                this.helmErrorCode = 0
                if (!cluster.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: cluster.cluster_id,
                        resource_name: cluster.name,
                        resource_type: `cluster_${cluster.environment === 'stag' ? 'test' : 'prod'}`
                    })
                }

                try {
                    await this.$store.dispatch('cluster/enableClusterHelm', {
                        projectId: this.projectId,
                        clusterId: cluster.cluster_id
                    })
                    this.helmDialog.title = this.$t('启用Helm成功')
                    this.helmDialog.isShow = true
                } catch (e) {
                    this.helmDialog.title = this.$t('启用Helm失败')
                    this.helmErrorCode = e.code
                    this.helmEnableMessage = e.message || e.data.msg || e.statusText
                    this.helmDialog.isShow = true
                }
            },

            async confirmDeleteCluster (cluster, index) {
                if (!cluster.permissions.delete) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'delete',
                        resource_code: cluster.cluster_id,
                        resource_name: cluster.name,
                        resource_type: `cluster_${cluster.environment === 'stag' ? 'test' : 'prod'}`
                    })
                }
                this.curCluster = cluster
                this.curClusterIndex = index
                this.$refs.clusterNoticeDialog.show()
            },

            /**
             * 删除 cluster
             *
             * @param {Object} cluster 当前集群对象
             * @param {number} index 集群对象在集群列表中的索引
             */
            async deleteCluster () {
                const me = this
                const cluster = this.curCluster
                const index = this.curClusterIndex

                cluster.status = 'removing'
                me.$set(me.clusterList, index, cluster)

                try {
                    await me.$store.dispatch('cluster/deleteCluster', {
                        projectId: cluster.project_id,
                        clusterId: cluster.cluster_id
                    })

                    cluster.status = 'removing'
                    me.$set(me.clusterList, index, cluster)

                    clearTimeout(me.timer) && (me.timer = null)
                    me.getClusters(true)
                } catch (e) {
                    cluster.status = 'remove_failed'
                    me.$set(me.clusterList, index, cluster)

                    catchErrorHandler(e, me)
                }
            },

            toggleGuide (status) {
                this.isShowGuide = status
            },

            showGuide () {
                this.$refs.guideTooltip.visible = false
                const guide = this.$refs.clusterGuide
                guide.show()
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import './index.css';
    .biz-error-message {
        white-space: normal;
        text-align: left;
        max-height: 200px;
        overflow: auto;
        margin: 0 0 15px 0;
    }

    .biz-message {
        margin-bottom: 0;
        h3 {
            text-align: left;
            font-size: 14px;
        }
        p {
            text-align: left;
            font-size: 13px;
        }
    }
</style>
