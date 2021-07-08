<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-cluster-title">
                {{$t('集群')}}
                <template v-if="ccAppName && arrangeType">
                    <span class="cc-info">（{{$t('业务')}}: {{ccAppName}}&nbsp;&nbsp;&nbsp;{{$t('编排类型')}}: {{arrangeType}}）</span>
                </template>
                <a href="javascript:void(0)" class="bk-text-button bk-default f12" @click="showProjectConfDialog">
                    <i class="bcs-icon bcs-icon-edit"></i>
                </a>
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
                <div class="cluster-btns" v-if="isK8SProject">
                    <bk-button theme="primary" icon="plus" @click="gotCreateCluster">{{$t('新建集群')}}</bk-button>
                    <apply-host class="ml10" v-if="$INTERNAL" />
                </div>
                <div class="biz-cluster-list" :style="{ paddingTop: isK8SProject ? 0 : '30px' }">
                    <div class="biz-cluster" v-for="(cluster, clusterIndex) in clusterList.filter(item => item && (item.cluster_id !== 'all'))" :key="clusterIndex">
                        <!-- 异常状态 -->
                        <div class="bk-mark-corner bk-warning" v-if="
                            cluster.status === 'normal'
                                && (
                                    conversionPercent(cluster.cpu_usage.used, cluster.cpu_usage.total) >= 80
                                    || conversionPercent(cluster.mem_usage.used_bytes, cluster.mem_usage.total_bytes) >= 80
                                    || conversionPercent(cluster.disk_usage.used_bytes, cluster.disk_usage.total_bytes) >= 80
                                )
                        ">
                            <p>!</p>
                        </div>
                        <template v-else>
                            <status-mark-corner v-if="cluster.status === 'normal' && cluster.cpu_usage !== undefined"
                                :cur-cluster="cluster"
                            ></status-mark-corner>
                        </template>

                        <div class="biz-cluster-header">
                            <bcs-popover :content="cluster.name" :delay="500" placement="top">
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
                            </bcs-popover>
                            <p class="cluster-metadata">
                                <bcs-popover :content="cluster.cluster_id" :delay="500" placement="top">
                                    <span class="cluster-id">{{cluster.cluster_id}}</span>
                                </bcs-popover>
                                <template v-if="$INTERNAL">
                                    <span v-if="cluster.environment === 'stag'" class="stag">
                                        {{$t('测试')}}
                                    </span>
                                    <span v-if="cluster.environment === 'prod'" class="prod">
                                        {{$t('正式')}}
                                    </span>
                                </template>
                                <span v-if="cluster.state === 'existing'" class="prod">{{$t('自有集群')}}</span>
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
                                <bk-button class="cluster-opera-btn" :id="`operaBtn${clusterIndex}`" slot="dropdown-trigger">
                                    <i class="bcs-icon bcs-icon-more"></i>
                                </bk-button>
                                <ul class="bk-dropdown-list" slot="dropdown-content" style="max-height: 210px; overflow: visible;">
                                    <li>
                                        <a href="javascript:void(0)" @click="goOverviewOrNode('clusterOverview', cluster)">{{$t('总览')}}</a>
                                    </li>
                                    <li>
                                        <a href="javascript:void(0)" @click="goClusterInfo(cluster)">{{$t('集群信息')}}</a>
                                    </li>
                                    <li v-if="cluster.type === 'k8s' && cluster.status === 'normal' && $INTERNAL">
                                        <a href="javascript:void(0)" @click="showUpdateCluster(cluster)">{{$t('集群升级')}}</a>
                                    </li>
                                    <template v-if="cluster.allow">
                                        <li>
                                            <a href="javascript:void(0)" @click="confirmDeleteCluster(cluster, clusterIndex)">{{$t('删除')}}</a>
                                        </li>
                                    </template>
                                    <template v-else>
                                        <li style="position: relative;">
                                            <a class="bk-dropdown-item"
                                                style="width: 100%; cursor: not-allowed; color: #ccc !important;"
                                                v-bk-tooltips="{
                                                    content: $t('您需要删除集群内所有节点后，再进行集群删除操作'),
                                                    placement: 'right',
                                                    boundary: window,
                                                    interactive: false
                                                }">
                                                {{$t('删除')}}
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
                                <bk-button class="cluster-opera-btn" :id="`operaBtn${clusterIndex}`" slot="dropdown-trigger">
                                    <i class="bcs-icon bcs-icon-more"></i>
                                </bk-button>
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

                        <!-- 升级中 -->
                        <div class="biz-cluster-content" v-else-if="cluster.status === 'upgrading'">
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
                                <p class="status-text">{{$t('正在升级中，请稍等···')}}</p>
                                <div class="status-opera">
                                    <a href="javascript:void(0);" class="bk-text-button" @click.prevent="showLog(cluster)">{{$t('查看日志')}}</a>
                                </div>
                            </div>
                        </div>

                        <!-- 升级失败 -->
                        <div class="biz-cluster-content" v-else-if="cluster.status === 'upgrade_failed'">
                            <div class="biz-status-box">
                                <div class="status-icon danger">
                                    <i class="bcs-icon bcs-icon-close-circle"></i>
                                </div>
                                <p class="status-text">{{$t('升级失败，请重试')}}</p>
                                <div class="status-opera">
                                    <a href="javascript:void(0);" class="bk-text-button" @click.prevent="showLog(cluster)">{{$t('查看日志')}}</a> |
                                    <a href="javascript:void(0);" class="bk-text-button" @click="reUpgrade(cluster, clusterIndex)">{{$t('重新升级')}}</a>
                                </div>
                            </div>
                        </div>

                        <!-- 删除失败 -->
                        <div class="biz-cluster-content" v-else-if="cluster.status === 'remove_failed'">
                            <div class="biz-status-box">
                                <div class="status-icon danger">
                                    <i class="bcs-icon bcs-icon-close-circle"></i>
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
                                    <i class="bcs-icon bcs-icon-close-circle"></i>
                                </div>
                                <p class="status-text">{{$t('初始化失败，请重试')}}</p>
                                <div class="status-opera">
                                    <a href="javascript:void(0);" class="bk-text-button" @click.prevent="showLog(cluster)">{{$t('查看日志')}}</a> |
                                    <a href="javascript:void(0);" class="bk-text-button" @click="reInitializationCluster(cluster, clusterIndex)">{{$t('重新初始化')}}</a>
                                </div>
                            </div>
                        </div>

                        <!-- 集群创建成功！提示 -->
                        <div class="biz-cluster-content" v-else-if="cluster.status === 'showSuccess'">
                            <div class="biz-status-box">
                                <div class="status-icon success">
                                    <i class="bcs-icon bcs-icon-check-circle"></i>
                                </div>
                                <p class="status-text">{{$t('恭喜，集群创建成功！')}}</p>
                            </div>
                        </div>

                        <!-- 正常状态 -->
                        <template v-else>
                            <status-progress
                                :loading="!Object.keys(cluster.cpu_usage).length"
                                :cur-project="curProject"
                                :cur-cluster="cluster">
                            </status-progress>
                            <div class="add-node-btn-wrapper">
                                <bk-button class="add-node-btn" @click="goOverviewOrNode('clusterNode', cluster)">
                                    <span>{{$t('添加节点')}}</span>
                                </bk-button>
                            </div>
                        </template>
                    </div>
                    <div class="biz-cluster biz-cluster-add" @click="gotCreateCluster">
                        <div class="add-btn">
                            <i class="bcs-icon bcs-icon-plus"></i>
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
                        <a :href="PROJECT_CONFIG.doc.quickStart" class="guide-link" target="_blank">{{$t('请点击了解更多')}}<i class="bcs-icon bcs-icon-angle-double-right ml5"></i></a>
                    </p>
                    <div class="guide-btn-group">
                        <a href="javascript:void(0);" class="bk-button bk-primary bk-button-large" @click="gotCreateCluster">
                            <span style="margin-left: 0;">{{$t('创建容器集群')}}</span>
                        </a>

                        <a class="bk-button bk-default bk-button-large" :href="PROJECT_CONFIG.doc.quickStart" target="_blank">
                            <span style="margin-left: 0;">{{$t('快速入门指引')}}</span>
                        </a>
                        <apply-host class="apply-host ml5" />
                    </div>
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
                        <template v-if="logList && logList.length">
                            <div class="operation-item">
                                <p class="log-message title">
                                    {{logList[0].prefix_message}}
                                </p>
                                <div class="log-message item" v-for="(task, taskIndex) in logList[0].log.node_tasks" :key="taskIndex">
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
                                <div v-if="logList[0].status.toLowerCase() === 'success'" class="biz-success-text f14" style="margin: 0 0 5px 0; font-weight: 700; margin-left: 20px;">
                                    {{$t('操作成功')}}
                                </div>
                                <div v-else-if="logList[0].status.toLowerCase() === 'failed'" class="biz-danger-text f14" style="margin: 0 0 5px 0; font-weight: 700; margin-left: 20px;">
                                    {{$t('操作失败')}}
                                    <template v-if="logList[0].errorMsgList && logList[0].errorMsgList.length">
                                        <span>{{logList[0].errorMsgList[0]}}</span>
                                        <template v-for="(msg, msgIndex) in logList[0].errorMsgList">
                                            <div :key="msgIndex" v-if="msgIndex > 0">{{msg}}</div>
                                        </template>
                                    </template>
                                    <template v-else>
                                        <i18n path="请联系“{user}”解决">
                                            <a place="user" :href="PROJECT_CONFIG.doc.contact" class="bk-text-button">{{$t('蓝鲸容器助手')}}</a>
                                        </i18n>
                                    </template>
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
                        </template>

                        <template v-for="(op, index) in logList">
                            <div class="operation-item" :key="index" v-if="index > 0">
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
                                    <template v-if="op.errorMsgList && op.errorMsgList.length">
                                        <span>{{op.errorMsgList[0]}}</span>
                                        <template v-for="(msg, msgIndex) in op.errorMsgList">
                                            <div :key="msgIndex" v-if="msgIndex > 0">{{msg}}</div>
                                        </template>
                                    </template>
                                    <template v-else>
                                        <i18n path="请联系“{user}”解决">
                                            <a place="user" :href="PROJECT_CONFIG.doc.contact" class="bk-text-button">{{$t('蓝鲸容器助手')}}</a>
                                        </i18n>
                                    </template>
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
                        </template>
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
            <template slot="content">
                <pre class="bk-intro bk-danger biz-error-message" v-if="helmEnableMessage">
                    {{helmEnableMessage}}
                </pre>

                <div class="helm-repos-detail" v-else>
                    <div class="repos-item">
                        <div class="wrapper mb10">
                            <i18n path="您可以通过{method}的方式管理K8S资源" class="url mb15" tag="p">
                                <router-link place="method" class="bk-text-button bk-primary" :to="{ name: 'helmTplList' }">Helm Chart</router-link>
                            </i18n>
                            <p class="url mb25">
                                <a :href="PROJECT_CONFIG.doc.serviceAccess" target="_blank" class="bk-text-button">{{$t('点击了解更多')}}</a>
                            </p>
                        </div>
                    </div>
                </div>

                <div class="biz-message" v-if="helmErrorCode === 40032">
                    <template>
                        <h3>{{$t('集群下没有节点，您需要：')}}</h3>
                        <p>{{$t('1、在集群下，添加节点')}}</p>
                        <i18n path="2、或者联系【{user}】" tag="p">
                            <a place="user" :href="PROJECT_CONFIG.doc.contact" class="bk-text-button">{{$t('蓝鲸容器助手')}}</a>
                        </i18n>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="updateClusterDialog.isShow"
            :width="450"
            :has-footer="true"
            :close-icon="false"
            :quick-close="false"
            :title="updateClusterDialog.title"
            @confirm="confirmUpdateCluster"
            @cancel="cancelUpdateCluster">
            <template slot="content">
                <main class="bk-form update-cluster-form" v-bkloading="{ isLoading: updateClusterDialog.loading, opacity: 1 }">
                    <template v-if="updateClusterDialog.versionList.length && !updateClusterDialog.loading">
                        <bk-alert type="error" class="mb15" :title="$t('升级过程需要业务停机；升级完后暂不支持版本回退')"></bk-alert>
                        <div class="form-item">
                            <label class="mb10">{{$t('集群版本')}}：<span class="red">*</span></label>
                            <div class="form-item-inner">
                                <div style="display: inline-block;" class="mr5">
                                    <bk-selector
                                        style="width: 402px;"
                                        :placeholder="$t('请选择')"
                                        :searchable="true"
                                        :setting-key="'id'"
                                        :display-key="'name'"
                                        :selected.sync="updateClusterDialog.version"
                                        :list="updateClusterDialog.versionList">
                                    </bk-selector>
                                </div>
                            </div>
                        </div>
                    </template>
                    <template v-if="!updateClusterDialog.versionList.length && !updateClusterDialog.loading">
                        <bk-exception type="empty" scene="part" style="margin: 0 0 30px 0;">
                            <p>{{$t('当前集群暂无可用的升级版本')}}</p>
                        </bk-exception>
                    </template>
                </main>
            </template>
        </bk-dialog>

        <bk-dialog
            class="reupgrade-cluster"
            :is-show.sync="reUpgradeDialog.isShow"
            :width="350"
            :title="$t('确认操作')"
            :quick-close="false"
            :close-icon="false">
            <template slot="content">
                <div>{{$t('确定重新升级？')}}</div>
            </template>
            <div slot="footer">
                <div class="bk-dialog-outer">
                    <bk-button type="primary" :loading="isReUpgrading" @click="confirmReUpgrade">
                        {{$t('确定')}}
                    </bk-button>
                    <bk-button type="button" :disabled="isReUpgrading" @click="cancelReUpgrade">
                        {{$t('取消')}}
                    </bk-button>
                </div>
            </div>
        </bk-dialog>

        <tip-dialog
            ref="clusterNoticeDialog"
            icon="bcs-icon bcs-icon-exclamation-triangle"
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

    import StatusProgress from './status-progress'
    import StatusMarkCorner from './status-mark-corner'
    import statusHoc from './status-hoc'
    import ApplyHost from './apply-host'

    export default {
        components: {
            'cluster-guide': ClusterGuide,
            tipDialog,
            StatusProgress: statusHoc(StatusProgress),
            StatusMarkCorner: statusHoc(StatusMarkCorner),
            ApplyHost
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
                ccAppName: '',
                arrangeType: '',
                // 存储集群 cpu, 内存, 磁盘使用率的数据，第一次进来请求时获取这些数据，之后轮询时不会在请求
                overviewList: [],
                overviewLoading: true,
                updateClusterDialog: {
                    title: '',
                    isShow: false,
                    loading: false,
                    version: '',
                    versionList: [],
                    cluster: {}
                },
                isReUpgrading: false,
                reUpgradeDialog: {
                    isShow: false,
                    cluster: {}
                }
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
                    if (!item.cpu_usage) {
                        item.cpu_usage = {}
                    }
                    if (!item.mem_usage) {
                        item.mem_usage = {}
                    }
                    if (!item.disk_usage) {
                        item.disk_usage = {}
                    }
                    clusterList.push(item)
                })
                return clusterList
            },
            isHelmEnable () {
                const curProject = this.$store.state.curProject
                if (curProject && (curProject.kind === PROJECT_K8S || curProject.kind === PROJECT_TKE)) {
                    return true
                }
                return false
            },
            isEn () {
                return this.$store.state.isEn
            },
            curProject () {
                return this.$store.state.curProject
            },
            isK8SProject () {
                return this.curProject.kind === PROJECT_K8S
            },
            isMESOSProject () {
                return this.curProject.kind === PROJECT_MESOS
            }
        },
        created () {
            console.log(this.isK8SProject)
            // created 时也需要执行一次 release，因为如果仅仅只在 destroyed 中执行的话，有时候不会 clearTimeout，
            // 在 getClusters 请求完毕正要执行 setTimeout 的时候切换，有可能不会 clearTimeout，所以在 created 里再执行一次
            this.release()
            this.cancelLoop = false
            this.getClusters()
            this.getProject()
        },
        mounted () {
            const guide = this.$refs.clusterGuide
            guide && guide.hide()
        },
        beforeDestroy () {
            this.release()
        },
        methods: {
            /**
             * 获取关联 CC 的数据
             */
            async getProject () {
                try {
                    const res = await this.$store.dispatch('getProject', { projectId: this.projectId })
                    const data = res.data || {}
                    this.ccAppName = data.cc_app_name
                    if (data.kind === 2) {
                        this.arrangeType = 'Mesos'
                    } else if (data.kind === 1) {
                        this.arrangeType = 'K8S'
                    }
                } catch (e) {
                    console.log(e)
                }
            },
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
                document.getElementById(`operaBtn${clusterIndex}`).classList.add('hover')
            },

            /**
             * 隐藏集群更多下拉框
             *
             * @param {number} clusterIndex 当前集群索引
             */
            hideDropdownMenu (clusterIndex) {
                document.getElementById(`operaBtn${clusterIndex}`).classList.remove('hover')
            },

            /**
             * 转换百分比
             *
             * @param {number} used 使用的量
             * @param {number} total 总量
             *
             * @return {number} 百分比数字
             */
            conversionPercent (used, total) {
                if (!total || parseFloat(total) === 0) {
                    return 0
                }
                let ret = parseFloat(used) / parseFloat(total) * 100
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

                    const { status, log = [], error_msg_list: errorMsgList = [] } = res.data

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
                        operation.errorMsgList = errorMsgList
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
             *
             * @param {boolean} notLoading notLoading 是否不需要 loading，如果为 true 说明是轮询来的
             */
            async getClusters (notLoading) {
                if (this.cancelLoop) {
                    return
                }

                if (!notLoading) {
                    this.showLoading = true
                }

                // 清空缓存，重新拉取数据
                this.$store.commit('cluster/forceUpdateClusterList', [])
                try {
                    const res = await this.$store.dispatch('cluster/getClusterList', this.projectId)
                    this.permissions = JSON.parse(JSON.stringify(res.permissions || {}))

                    const list = res.data.results || []

                    list.forEach((item, index) => {
                        item.cpu_usage = {}
                        item.mem_usage = {}
                        item.disk_usage = {}

                        item.activeip = 0
                        item.availableip = 0
                        item.reservedip = 0
                        item.allip = 0
                        if (item.type === 'mesos' && item.func_wlist && item.func_wlist.indexOf('MesosResource') > -1) {
                            if (!notLoading) {
                                this.getClusterIp(item, index)
                            }
                        }
                    })

                    if (this.clusterList.length) {
                        this.clusterList.forEach(c => {
                            const resListItem = list.find(item => item.cluster_id === c.cluster_id)
                            if (resListItem) {
                                resListItem.cpu_usage = c.cpu_usage
                                resListItem.mem_usage = c.mem_usage
                                resListItem.disk_usage = c.disk_usage
                                resListItem.activeip = c.activeip
                                resListItem.availableip = c.availableip
                                resListItem.reservedip = c.reservedip
                                resListItem.allip = c.allip
                            }
                        })
                    }
                    this.showLoading = false // 关闭loading，让集群列表先出来，指标慢慢加载（后面重构）

                    for (const [index, item] of list.entries()) {
                        if (!notLoading) {
                            const args = {}
                            if (item.type === 'mesos' && item.func_wlist && item.func_wlist.indexOf('MesosResource') > -1) {
                                args.dimensions = 'mesos_memory_usage,mesos_cpu_usage'
                            }

                            const d = await this.$store.dispatch('cluster/clusterOverview', {
                                projectId: this.projectId,
                                clusterId: item.cluster_id,
                                data: args
                            })
                            item.cpu_usage = d.data.cpu_usage
                            item.mem_usage = d.data.mem_usage
                            item.disk_usage = d.data.disk_usage

                            // 如果是 mesos，返回是 mesos_memory_usage 和 mesos_cpu_usage
                            if (item.type === 'mesos' && item.func_wlist && item.func_wlist.indexOf('MesosResource') > -1) {
                                item.cpu_usage = d.data.mesos_cpu_usage
                                item.mem_usage = d.data.mesos_memory_usage
                            }
                        }
                        if (item.status === 'initializing' || item.status === 'so_initializing') {
                            this.setStorage(item)
                        } else {
                            this.checkStorage(item, index, list, item.status)
                        }
                    }
                    this.$store.commit('cluster/forceUpdateClusterList', list)

                    if (this.cancelLoop) {
                        clearTimeout(this.timer)
                        this.timer = null
                    } else if (notLoading) {
                        this.timer = setTimeout(() => {
                            this.getClusters(true)
                        }, 5000)
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

                    cluster.activeip = data.activeip || 0
                    cluster.availableip = data.availableip || 0
                    cluster.reservedip = data.reservedip || 0
                    cluster.allip = cluster.activeip + cluster.availableip
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
            },

            /**
             * 显示升级集群弹框
             *
             * @param {Object} curCluster 当前升级的集群
             */
            async showUpdateCluster (curCluster) {
                this.updateClusterDialog.title = this.$t('集群升级')
                this.updateClusterDialog.isShow = true
                this.updateClusterDialog.loading = true
                this.updateClusterDialog.cluster = Object.assign({}, curCluster)
                try {
                    const versionList = []
                    const res = await this.$store.dispatch('cluster/getClusterVersion', {
                        projectId: this.projectId,
                        clusterId: curCluster.cluster_id
                    })
                    const list = res.data || []
                    list.forEach(item => {
                        versionList.push({
                            id: item,
                            name: item
                        })
                    })
                    this.updateClusterDialog.versionList.splice(
                        0,
                        this.updateClusterDialog.versionList.length,
                        ...versionList
                    )
                    if (versionList.length) {
                        this.updateClusterDialog.version = versionList[0].id
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.updateClusterDialog.loading = false
                }
            },

            /**
             * 确认升级集群
             */
            async confirmUpdateCluster () {
                if (!this.updateClusterDialog.versionList.length) {
                    this.cancelUpdateCluster()
                    return
                }
                try {
                    const { version, cluster } = this.updateClusterDialog
                    if (!version.trim()) {
                        this.bkMessageInstance = this.$bkMessage({
                            theme: 'error',
                            delay: 1000,
                            message: this.$t('请选择集群版本')
                        })
                        return
                    }
                    await this.$store.dispatch('cluster/upgradeCluster', {
                        projectId: this.projectId,
                        clusterId: cluster.cluster_id,
                        data: {
                            version: version,
                            operation: 'upgrade'
                        }
                    })
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'success',
                        delay: 1000,
                        message: this.$t('任务下发成功')
                    })
                    this.cancelUpdateCluster()
                    this.getClusters(true)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.updateClusterDialog.loading = false
                }
            },

            /**
             * 取消升级集群
             */
            cancelUpdateCluster () {
                this.updateClusterDialog.isShow = false
                setTimeout(() => {
                    this.updateClusterDialog.title = ''
                    this.updateClusterDialog.version = ''
                    this.updateClusterDialog.versionList.splice(0, this.updateClusterDialog.versionList.length, ...[])
                    this.updateClusterDialog.cluster = Object.assign({}, {})
                }, 300)
            },

            /**
             * 显示重新升级弹框
             *
             * @param {Object} cluster 集群对象
             */
            reUpgrade (cluster) {
                this.reUpgradeDialog.isShow = true
                this.reUpgradeDialog.cluster = Object.assign({}, cluster)
            },

            /**
             * 确认重新升级
             */
            async confirmReUpgrade () {
                try {
                    this.isReUpgrading = true
                    await this.$store.dispatch('cluster/upgradeCluster', {
                        projectId: this.projectId,
                        clusterId: this.reUpgradeDialog.cluster.cluster_id,
                        data: {
                            version: '',
                            operation: 'reupgrade'
                        }
                    })
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'success',
                        delay: 1000,
                        message: this.$t('任务下发成功')
                    })
                    this.getClusters(true)
                    this.cancelReUpgrade()
                } catch (e) {
                    console.log(e)
                } finally {
                    setTimeout(() => {
                        this.isReUpgrading = false
                    }, 300)
                }
            },

            /**
             * 取消重新升级
             */
            cancelReUpgrade () {
                this.reUpgradeDialog.isShow = false
                setTimeout(() => {
                    this.reUpgradeDialog.cluster = Object.assign({}, {})
                }, 300)
            },

            showProjectConfDialog () {
                if (window.bus) {
                    window.bus.$emit('showProjectConfDialog')
                }
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
    .guide-link {
        display: flex;
        align-items: center;
        justify-content: center;
        i {
            font-size: 12px;
        }
    }
    .guide-btn-group {
        display: flex;
        align-items: center;
        justify-content: center;
        /deep/ .bk-button-normal {
            height: 38px;
        }
    }
    .apply-host {
        /deep/ .bk-button-normal {
            line-height: 38px;
            font-size: 16px;
        }
    }
</style>
