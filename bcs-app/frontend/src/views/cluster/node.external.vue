<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-cluster-node-title">
                <i class="bk-icon icon-arrows-left back" @click="goIndex"></i>
                <template v-if="exceptionCode"><span>返回</span></template>
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
        <div class="biz-content-wrapper">
            <app-exception
                v-if="exceptionCode && !getClusterLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>
            <div v-if="!exceptionCode && !getClusterLoading" class="biz-cluster-node-wrapper">
                <div class="biz-cluster-tab-header">
                    <div class="header-item" @click="goOverview">
                        <i class="bk-icon icon-bar-chart"></i>总览
                    </div>
                    <div class="header-item active">
                        <i class="bk-icon icon-list"></i>节点管理
                    </div>
                    <div class="header-item" @click="goInfo">
                        <i class="cc-icon icon-cc-machine"></i>集群信息
                    </div>
                </div>
                <div class="biz-cluster-tab-content" v-bkloading="{ isLoading: isInitLoading, opacity: 1 }" :style="{ height: isInitLoading ? '300px' : 'auto' }">
                    <div class="biz-cluster-node-content" v-if="!isInitLoading">
                        <div class="biz-cluster-node-header">
                            <button class="bk-button bk-primary" @click.stop="openDialog">
                                <i class="bk-icon icon-plus"></i>
                                <span>添加节点</span>
                            </button>
                            <bk-tooltip v-if="!allowBatch" :content="dontAllowBatchMsg" placement="right">
                                <bk-dropdown-menu :align="'center'" ref="toggleFilterDropdownMenu" class="batch-operate-dropdown" :disabled="true">
                                    <a href="javascript:void(0);" slot="dropdown-trigger" class="bk-text-button batch-operate" :class="!allowBatch ? 'disabled' : ''">
                                        <span class="label">批量操作</span>
                                        <i class="bk-icon icon-angle-down dropdown-menu-angle-down"></i>
                                    </a>
                                </bk-dropdown-menu>
                            </bk-tooltip>
                            <bk-dropdown-menu v-else :align="'center'" ref="toggleFilterDropdownMenu" class="batch-operate-dropdown">
                                <a href="javascript:void(0);" slot="dropdown-trigger" class="bk-text-button batch-operate" :class="!allowBatch ? 'disabled' : ''">
                                    <span class="label">批量操作</span>
                                    <i class="bk-icon icon-angle-down dropdown-menu-angle-down"></i>
                                </a>
                                <ul class="bk-dropdown-list" slot="dropdown-content">
                                    <!-- <li>
                                        <a href="javascript:void(0)" class="disabled" v-if="disableBatchOperate === '1'">允许调度</a>
                                        <a href="javascript:void(0)" v-else @click="batchOperate('1')">允许调度</a>
                                    </li>
                                    <li>
                                        <a href="javascript:void(0)" class="disabled" v-if="disableBatchOperate === '2'">停止调度</a>
                                        <a href="javascript:void(0)" v-else @click="batchOperate('2')">停止调度</a>
                                    </li>
                                    <li>
                                        <a href="javascript:void(0)" class="disabled" v-if="!allowBatchDelete">删除</a>
                                        <a href="javascript:void(0)" v-else @click="batchOperate('3')">删除</a>
                                    </li> -->
                                    <li>
                                        <a href="javascript:void(0)" @click="batchOperate('1')">允许调度</a>
                                    </li>
                                    <li>
                                        <a href="javascript:void(0)" @click="batchOperate('2')">停止调度</a>
                                    </li>
                                    <li>
                                        <a href="javascript:void(0)" @click="batchOperate('3')">删除</a>
                                    </li>
                                </ul>
                            </bk-dropdown-menu>
                            <div class="biz-searcher-wrapper">
                                <!-- <bk-ip-searcher :search-params="ipSearchParams" :disable="searchDisabled" @search="searchNodeList" ref="searcher" /> -->
                                <node-searcher :cluster-id="clusterId" :project-id="projectId" ref="searcher"
                                    :params="ipSearchParams" @search="searchNodeList"></node-searcher>
                            </div>
                            <span class="close-wrapper">
                                <template v-if="$refs.searcher && $refs.searcher.searchParams && $refs.searcher.searchParams.length">
                                    <button class="bk-button bk-default is-outline is-icon" title="清除" @click="clearSearchParams">
                                        <i class="bk-icon icon-close"></i>
                                    </button>
                                </template>
                                <template v-else>
                                    <button class="bk-button bk-default is-outline is-icon">
                                    </button>
                                </template>
                            </span>

                            <span class="refresh-wrapper">
                                <button class="bk-button bk-default is-outline is-icon" title="刷新" @click="refresh">
                                    <i class="bk-icon icon-refresh"></i>
                                </button>
                            </span>
                        </div>
                        <div class="biz-cluster-node-table-wrapper" v-bkloading="{ isLoading: isPageLoading, opacity: 1 }">
                            <table class="bk-table has-table-hover biz-table" :style="{ borderBottomWidth: nodeList.length ? '1px' : 0 }">
                                <thead>
                                    <tr>
                                        <th style="width: 3%; text-align: center; top: 0; position: relative; padding: 0;">
                                            <label class="bk-form-checkbox">
                                                <input type="checkbox" name="check-all-node" v-model="isCheckCurPageAllNode" @click="checkAllNode($event)" />
                                                <!-- <input v-else type="checkbox" name="check-all-node" disabled="disabled" /> -->
                                            </label>
                                        </th>
                                        <th style="width: 12%; padding-left: 10px;">主机名/IP</th>
                                        <th style="width: 12%;">状态</th>
                                        <th style="width: 10%;">容器数量</th>
                                        <th style="width: 9%;">
                                            CPU
                                            <div class="biz-table-sort">
                                                <span class="sort-direction asc"
                                                    :class="sortIdx === 'cpu_summary' ? 'active' : ''"
                                                    :title="sortIdx === 'cpu_summary' ? '取消' : '升序'"
                                                    @click="sortNodeList('cpu_summary', 'asc', 'cpu_summary')"></span>
                                                <span class="sort-direction desc"
                                                    :class="sortIdx === '-cpu_summary' ? 'active' : ''"
                                                    :title="sortIdx === '-cpu_summary' ? '取消' : '降序'"
                                                    @click="sortNodeList('cpu_summary', 'desc', '-cpu_summary')"></span>
                                            </div>
                                        </th>
                                        <th style="width: 9%;">
                                            内存
                                            <div class="biz-table-sort">
                                                <span class="sort-direction asc"
                                                    :class="sortIdx === 'mem' ? 'active' : ''"
                                                    :title="sortIdx === 'mem' ? '取消' : '升序'"
                                                    @click="sortNodeList('mem', 'asc', 'mem')"></span>
                                                <span class="sort-direction desc"
                                                    :class="sortIdx === '-mem' ? 'active' : ''"
                                                    :title="sortIdx === '-mem' ? '取消' : '降序'"
                                                    @click="sortNodeList('mem', 'desc', '-mem')"></span>
                                            </div>
                                        </th>
                                        <th style="width: 9%;">
                                            磁盘IO
                                            <div class="biz-table-sort">
                                                <span class="sort-direction asc "
                                                    :class="sortIdx === 'disk' ? 'active' : ''"
                                                    :title="sortIdx === 'disk' ? '取消' : '升序'"
                                                    @click="sortNodeList('disk', 'asc', 'disk')"></span>
                                                <span class="sort-direction desc"
                                                    :class="sortIdx === '-disk' ? 'active' : ''"
                                                    :title="sortIdx === '-disk' ? '取消' : '降序'"
                                                    @click="sortNodeList('disk', 'desc', '-disk')"></span>
                                            </div>
                                        </th>
                                        <th style="width: 28%; text-align: left;">
                                            <span>操作</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-if="nodeList.length">
                                        <tr v-for="(node, index) in nodeList" :key="index">
                                            <td style="width: 40px; text-align: center; top: 0; position: relative;">
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-node" v-model="node.isChecked" @click="checkNode(node, index)" />
                                                </label>
                                            </td>
                                            <!--
                                                初始化中: initializing, so_initializing, initial_checking, uninitialized
                                                删除中: removing
                                                操作: 查看日志
                                            -->
                                            <template v-if="ingStatus.includes(node.status)">
                                                <td style="padding-left: 10px;">
                                                    {{node.inner_ip}}
                                                </td>
                                                <td>
                                                    <div class="biz-status-node"><loading-cell :style="{ left: 0 }" :ext-cls="['bk-spin-loading-mini', 'bk-spin-loading-danger']"></loading-cell></div>
                                                    {{node.status === 'initializing' || node.status === 'so_initializing' || node.status === 'initial_checking' ? '初始化中' : '删除中'}}
                                                </td>
                                                <td></td>
                                                <td></td>
                                                <td></td>
                                                <td></td>
                                                <td style="text-align: left;">
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="showLog(node)">查看日志</a>
                                                </td>
                                            </template>

                                            <!--
                                                初始化失败: initial_failed, so_init_failed, check_failed, bke_failed, schedule_failed
                                                操作: 查看日志，删除，重试（重试初始化）

                                                删除失败: delete_failed
                                                操作: 查看日志，删除

                                                删除失败: remove_failed
                                                操作: 查看日志，重试（重试删除）
                                            -->
                                            <template v-if="failStatus.includes(node.status)">
                                                <td style="padding-left: 10px;">
                                                    <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                                </td>
                                                <td>
                                                    <div class="biz-status-node"><i class="node danger"></i></div>
                                                    {{node.status === 'initial_failed' || node.status === 'so_init_failed' || node.status === 'check_failed' || node.status === 'bke_failed' || node.status === 'schedule_failed' ? '初始化失败' : '删除失败'}}
                                                </td>
                                                <td>{{node.containers}}</td>
                                                <td v-if="node.cpu !== null && node.cpu !== undefined"><ring-cell :percent="node.cpu" :fill-color="'#3ede78'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.mem !== null && node.mem !== undefined"><ring-cell :percent="node.mem" :fill-color="'#3c96ff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.io !== null && node.io !== undefined"><ring-cell :percent="node.io" :fill-color="'#853cff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td style="text-align: left;">
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="showLog(node)">查看日志</a>
                                                    <template v-if="node.status === 'delete_failed'">
                                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop="delFailedNode(node, index)">删除</a>
                                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop="showFaultRemove(node, index)">故障移除</a>
                                                    </template>
                                                    <template v-else-if="node.status === 'remove_failed'">
                                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop="reTryDel(node, index)">重试</a>
                                                    </template>
                                                    <template v-else>
                                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop="showDelNode(node, index)">删除</a>
                                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop="reInitializationNode(node, index)">重试</a>
                                                    </template>
                                                </td>
                                            </template>

                                            <!--
                                                不可调度: to_removed
                                                操作: 允许调度（启用），删除（没有这个操作，和之前一样，置灰显示 tooltip），强制删除
                                            -->
                                            <template v-if="node.status === 'to_removed'">
                                                <td style="padding-left: 10px;">
                                                    <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                                </td>
                                                <td>
                                                    <div class="biz-status-node"><i class="node warning"></i></div>
                                                    不可调度
                                                </td>
                                                <td>{{node.containers}}</td>
                                                <td v-if="node.cpu !== null && node.cpu !== undefined"><ring-cell :percent="node.cpu" :fill-color="'#3ede78'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.mem !== null && node.mem !== undefined"><ring-cell :percent="node.mem" :fill-color="'#3c96ff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.io !== null && node.io !== undefined"><ring-cell :percent="node.io" :fill-color="'#853cff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td>
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="enableNode(node, index)">允许调度</a>
                                                    <bk-tooltip style="margin: 0 15px;" :content="'请确保该节点已经没有运行中的容器'" placement="top-end">
                                                        <a href="javascript:void(0);" class="bk-text-button is-disabled">删除</a>
                                                    </bk-tooltip>
                                                    <a href="javascript:void(0);" class="bk-text-button" style="margin-right: 15px;" @click.stop="showForceDelNode(node, index)">强制删除</a>
                                                    <bk-dropdown-menu class="dropdown-menu" :align="'center'" ref="dropdown">
                                                        <a href="javascript:void(0);" slot="dropdown-trigger" class="bk-text-button">
                                                            更多
                                                            <i class="bk-icon icon-angle-down dropdown-menu-angle-down"></i>
                                                        </a>
                                                        <ul class="bk-dropdown-list" slot="dropdown-content">
                                                            <li>
                                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="schedulerNode(node, index)">
                                                                    {{curProject.kind === 1 ? 'pod迁移' : 'taskgroup迁移'}}
                                                                </a>
                                                            </li>
                                                        </ul>
                                                    </bk-dropdown-menu>
                                                </td>
                                            </template>

                                            <!--
                                                不可调度: removable
                                                操作: 允许调度（启用），删除，强制删除
                                            -->
                                            <template v-if="node.status === 'removable'">
                                                <td style="padding-left: 10px;">
                                                    <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                                </td>
                                                <td>
                                                    <div class="biz-status-node"><i class="node warning"></i></div>
                                                    不可调度
                                                </td>
                                                <td>{{node.containers}}</td>
                                                <td v-if="node.cpu !== null && node.cpu !== undefined"><ring-cell :percent="node.cpu" :fill-color="'#3ede78'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.mem !== null && node.mem !== undefined"><ring-cell :percent="node.mem" :fill-color="'#3c96ff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.io !== null && node.io !== undefined"><ring-cell :percent="node.io" :fill-color="'#853cff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td style="text-align: left;">
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="enableNode(node, index)">允许调度</a>
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="showDelNode(node, index)">删除</a>
                                                    <a href="javascript:void(0);" class="bk-text-button" style="margin-right: 15px;" @click.stop="showForceDelNode(node, index)">强制删除</a>
                                                    <bk-dropdown-menu class="dropdown-menu" :align="'center'" ref="dropdown">
                                                        <a href="javascript:void(0);" slot="dropdown-trigger" class="bk-text-button">
                                                            更多
                                                            <i class="bk-icon icon-angle-down dropdown-menu-angle-down"></i>
                                                        </a>
                                                        <ul class="bk-dropdown-list" slot="dropdown-content">
                                                            <li>
                                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="schedulerNode(node, index)">
                                                                    {{curProject.kind === 1 ? 'pod迁移' : 'taskgroup迁移'}}
                                                                </a>
                                                            </li>
                                                        </ul>
                                                    </bk-dropdown-menu>
                                                </td>
                                            </template>

                                            <!--
                                                不正常: not_ready
                                                操作: 删除，强制删除
                                            -->
                                            <template v-if="node.status === 'not_ready'">
                                                <td style="padding-left: 10px;">
                                                    <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                                </td>
                                                <td>
                                                    <div class="biz-status-node"><i class="node danger"></i></div>
                                                    不正常
                                                </td>
                                                <td>{{node.containers}}</td>
                                                <td v-if="node.cpu !== null && node.cpu !== undefined"><ring-cell :percent="node.cpu" :fill-color="'#3ede78'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.mem !== null && node.mem !== undefined"><ring-cell :percent="node.mem" :fill-color="'#3c96ff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.io !== null && node.io !== undefined"><ring-cell :percent="node.io" :fill-color="'#853cff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td style="text-align: left;">
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="showDelNode(node, index)">删除</a>
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="showForceDelNode(node, index)">强制删除</a>
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="showFaultRemove(node, index)">故障移除</a>
                                                </td>
                                            </template>

                                            <!--
                                                正常: normal
                                                操作: 停止调度（停止分配）

                                                不正常: unnormal
                                                操作: 停止调度（停止分配）
                                            -->
                                            <template v-if="node.status === 'normal' || node.status === 'unnormal'">
                                                <td style="padding-left: 10px;">
                                                    <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                                </td>
                                                <td v-if="node.status === 'normal'">
                                                    <div class="biz-status-node"><i class="node success"></i></div>
                                                    正常
                                                </td>
                                                <td v-else>
                                                    <div class="biz-status-node"><i class="node danger"></i></div>
                                                    不正常
                                                </td>
                                                <td>{{node.containers}}</td>
                                                <td v-if="node.cpu !== null && node.cpu !== undefined"><ring-cell :percent="node.cpu" :fill-color="'#3ede78'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.mem !== null && node.mem !== undefined"><ring-cell :percent="node.mem" :fill-color="'#3c96ff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td v-if="node.io !== null && node.io !== undefined"><ring-cell :percent="node.io" :fill-color="'#853cff'"></ring-cell></td>
                                                <td v-else><loading-cell></loading-cell></td>
                                                <td style="text-align: left;">
                                                    <a href="javascript:void(0);" class="bk-text-button" @click.stop="stopNode(node, index)">停止调度</a>
                                                </td>
                                            </template>
                                        </tr>
                                    </template>
                                    <template v-else>
                                        <tr class="no-hover">
                                            <td colspan="8">
                                                <div class="bk-message-box">
                                                    <p class="message empty-message">无数据</p>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </div>
                        <div class="bk-table-footer" v-if="nodeListPageConf.total">
                            <div class="biz-page-wrapper" style="margin: 5px 0;">
                                <bk-page-counter
                                    :total="nodeListPageConf.total"
                                    :page-size="nodeListPageConf.pageSize"
                                    @change="changePageSize">
                                </bk-page-counter>
                                <bk-paging
                                    style="float: right;"
                                    :cur-page.sync="nodeListPageConf.curPage"
                                    :total-page="nodeListPageConf.totalPage"
                                    @page-change="nodeListPageChange">
                                </bk-paging>
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
            :close-icon="dialogConf.closeIcon"
            :quick-close="false"
            :ext-cls="'biz-cluster-create-choose-dialog'">
            <div slot="content">
                <div style="margin: -20px;" v-bkloading="{ isLoading: ccHostLoading, opacity: 1 }">
                    <div class="biz-cluster-create-table-header">
                        <div class="left">
                            选择服务器
                            <span style="font-size: 12px;cursor: pointer;">
                                （关联业务：{{ccApplicationName}}）
                            </span>
                            <span class="remain-tip">已选择{{remainCount}}个节点</span>
                        </div>
                        <div style="position: absolute;right: 20px;top: 11px;">
                            <div class="biz-searcher-wrapper">
                                <bk-ip-searcher @search="handleSearch" ref="iPSearcher" :disable="isCreating" />
                            </div>
                        </div>
                    </div>
                    <div style="min-height: 443px;">
                        <table class="bk-table has-table-hover biz-table biz-cluster-create-table" :style="{ borderBottomWidth: candidateHostList.length ? '1px' : 0 }">
                            <thead>
                                <tr>
                                    <th style="width: 60px; text-align: right;">
                                        <label class="bk-form-checkbox">
                                            <input type="checkbox" name="check-all-host" v-model="isCheckCurPageAll" @click="toogleCheckCurPage" v-if="candidateHostList.filter(host => !host.is_used && String(host.agent) === '1').length && !isCreating">
                                            <input type="checkbox" name="check-all-host" style="border: 1px solid #ebf0f5;background-color: #fafbfd;background-image: none;" disabled="disabled" v-else>
                                        </label>
                                    </th>
                                    <th width="480">主机名称</th>
                                    <th>内网IP</th>
                                    <th>Agent状态</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="candidateHostList.length">
                                    <tr v-for="(host, index) in candidateHostList" @click.stop="rowClick" :style="{ cursor: !host.is_used && String(host.agent) === '1' && !isCreating ? 'pointer' : 'not-allowed' }" :key="index">
                                        <template v-if="!isCreating">
                                            <td style="text-align: right;" v-if="host.is_used || String(host.agent) !== '1'">
                                                <bk-tooltip placement="left">
                                                    <label class="bk-form-checkbox">
                                                        <input type="checkbox" name="check-host" style="border: 1px solid #ebf0f5;background-color: #fafbfd;background-image: none;" disabled="disabled">
                                                    </label>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all; width: 240px;">
                                                            当前节点已被项目（{{host.project_name}}）的集群（{{host.cluster_name}}）占用
                                                        </p>
                                                    </template>
                                                </bk-tooltip>
                                            </td>
                                            <td style="text-align: right;" v-else>
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-host" v-model="host.isChecked" @click.stop="selectHost(candidateHostList)">
                                                </label>
                                            </td>
                                        </template>
                                        <template v-else>
                                            <td style="text-align: right;">
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-host" :checked="host.isChecked" disabled="disabled">
                                                </label>
                                            </td>
                                        </template>
                                        <td>
                                            <bk-tooltip placement="top">
                                                <div class="name" style="max-width: 360px;">{{host.host_name || '--'}}</div>
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
                                            <span class="biz-success-text" v-if="String(host.agent) === '1'">
                                                正常
                                            </span>
                                            <template v-else-if="String(host.agent) === '0'">
                                                <bk-tooltip placement="top">
                                                    <span class="biz-warning-text f12" style="vertical-align: super;">
                                                        异常
                                                    </span>
                                                    <template slot="content">
                                                        <p style="text-align: left; white-space: normal;word-break: break-all;">
                                                            Agent异常，请先安装
                                                        </p>
                                                    </template>
                                                </bk-tooltip>
                                            </template>
                                            <span class="biz-danger-text f12" v-else>
                                                错误
                                            </span>
                                        </td>
                                    </tr>
                                </template>
                                <template v-if="!candidateHostList.length && !ccHostLoading">
                                    <tr>
                                        <td colspan="4">
                                            <div class="bk-message-box no-data">
                                                <p class="message empty-message" v-if="ccSearchKeys.length">无匹配的主机资源</p>
                                                <p class="message empty-message" v-else>您在当前业务下没有主机资源，请联系业务运维</p>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                    <div class="biz-page-box" v-if="pageConf.show && candidateHostList.length">
                        <div class="cchost-paging-mask" v-if="isCreating"></div>
                        <bk-paging
                            :size="'small'"
                            :cur-page.sync="pageConf.curPage"
                            :total-page="pageConf.totalPage"
                            @page-change="pageChange">
                        </bk-paging>
                    </div>
                </div>
            </div>
            <div slot="footer">
                <template>
                    <div class="bk-dialog-outer">
                        <template v-if="!isCreating">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                                @click="chooseServer" style="margin-top: 12px;">
                                确定
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="closeDialog" style="margin-top: 12px;">
                                取消
                            </button>
                        </template>
                        <template v-else>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled" style="margin-top: 12px;">
                                添加中...
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled" style="margin-top: 12px;">
                                取消
                            </button>
                        </template>
                    </div>
                </template>
            </div>
        </bk-dialog>

        <bk-sideslider
            :is-show.sync="logSideDialogConf.isShow"
            :title="logSideDialogConf.title"
            @hidden="closeLog"
            :quick-close="true">
            <div class="p20" slot="content">
                <template v-if="logEndState === 'none'">
                    <div style="margin: 0 0 5px 0; text-align: center;">
                        暂无日志信息
                    </div>
                </template>
                <template v-else>
                    <div class="biz-log-box">
                        <div class="operation-item" v-for="(op, index) in logList" :key="index">
                            <p class="log-message title">
                                {{op.prefix_message}}
                            </p>
                            <template v-if="op.log.node_tasks">
                                <p class="log-message item" v-for="(task, taskIndex) in op.log.node_tasks" :key="taskIndex">
                                    <template v-if="op.prefix_message.indexOf('前置检查') > -1">
                                        === <span>{{task.name}}</span> start ===
                                        <br />
                                    </template>
                                    <template v-else>
                                        {{task.name}} -
                                    </template>
                                    <span v-if="task.state.toLowerCase() === 'failure'" class="biz-danger-text">
                                        {{task.state}}
                                    </span>
                                    <span v-else-if="task.state.toLowerCase() === 'success'" class="biz-success-text">
                                        {{task.state}}
                                    </span>
                                    <span v-else-if="task.state.toLowerCase() === 'running'" class="biz-warning-text">
                                        {{task.state}}
                                    </span>
                                    <span v-else v-html="formatLog(task.state)">
                                    </span>
                                </p>
                            </template>
                            <div v-if="op.status.toLowerCase() === 'success'" style="margin: 0 0 5px 0; color: #34d97b; font-size: 14px; font-weight: 700; margin-left: 20px;">
                                操作成功
                            </div>
                            <div v-else-if="op.status.toLowerCase() === 'failed'" style="margin: 0 0 5px 0; color: #e64d34; font-size: 14px; font-weight: 700; margin-left: 20px;">
                                操作失败<span style="margin-left: 10px;" v-if="op.task_url"><a :href="op.task_url" class="bk-text-button" target="_blank">查看详情</a></span>
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
                                正在加载中...
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </bk-sideslider>

        <tip-dialog
            ref="nodeNoticeDialog"
            icon="bk-icon icon-exclamation-triangle"
            title="添加节点"
            sub-title="此操作需要对你的主机进行如下操作，请知悉："
            :check-list="nodeNoticeList"
            confirm-btn-text="确定，添加节点"
            cancel-btn-text="我再想想"
            :confirm-callback="saveNode">
        </tip-dialog>

        <tip-dialog
            ref="removeNodeDialog"
            icon="bk-icon icon-exclamation-triangle"
            :show-close="false"
            sub-title="此操作无法撤回，请确认： "
            :check-list="deleteNodeNoticeList"
            :confirm-btn-text="'确定'"
            :confirming-btn-text="'删除中...'"
            :canceling-btn-text="'取消'"
            :confirm-callback="confirmDelNode"
            :cancel-callback="cancelDelNode">
        </tip-dialog>

        <tip-dialog
            ref="forceRemoveNodeDialog"
            icon="bk-icon icon-exclamation-triangle"
            :show-close="false"
            sub-title="此操作无法撤回，请确认： "
            :check-list="deleteNodeNoticeList"
            :confirm-btn-text="'确定'"
            :confirming-btn-text="'删除中...'"
            :canceling-btn-text="'取消'"
            :confirm-callback="confirmForceRemoveNode"
            :cancel-callback="cancelForceRemoveNode">
        </tip-dialog>

        <tip-dialog
            ref="faultRemoveDialog"
            icon="bk-icon icon-exclamation-triangle"
            :show-close="false"
            sub-title="此操作无法撤回，请确认： "
            :check-list="faultRemoveoticeList"
            :confirm-btn-text="'确定'"
            :confirming-btn-text="'移除中...'"
            :canceling-btn-text="'取消'"
            :confirm-callback="confirmFaultRemove"
            :cancel-callback="cancelFaultRemove">
        </tip-dialog>

        <bk-dialog
            :is-show.sync="reInitializationDialogConf.isShow"
            :width="reInitializationDialogConf.width"
            :title="reInitializationDialogConf.title"
            :close-icon="reInitializationDialogConf.closeIcon"
            :ext-cls="'biz-node-re-initialization-dialog'"
            :quick-close="false">
            <template slot="content">
                <div>{{reInitializationDialogConf.content}}</div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isUpdating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            初始化中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="reInitializationConfirm">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="reInitializationCancel">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="reDelDialogConf.isShow"
            :width="reDelDialogConf.width"
            :title="reDelDialogConf.title"
            :close-icon="reDelDialogConf.closeIcon"
            :ext-cls="'biz-node-re-initialization-dialog'"
            :quick-close="false">
            <template slot="content">
                <div>{{reDelDialogConf.content}}</div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isUpdating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            删除中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="reDelConfirm">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="reDelCancel">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="delDialogConf.isShow"
            :width="delDialogConf.width"
            :title="delDialogConf.title"
            :close-icon="delDialogConf.closeIcon"
            :ext-cls="'biz-node-re-initialization-dialog'"
            :quick-close="false">
            <template slot="content">
                <div>{{delDialogConf.content}}</div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isUpdating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            删除中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="delConfirm">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="delCancel">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="enableDialogConf.isShow"
            :width="enableDialogConf.width"
            :title="enableDialogConf.title"
            :close-icon="enableDialogConf.closeIcon"
            :ext-cls="'biz-node-re-initialization-dialog'"
            :quick-close="false">
            <template slot="content">
                <div>{{enableDialogConf.content}}</div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isUpdating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            启用中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="enableConfirm">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="enableCancel">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="stopDialogConf.isShow"
            :width="stopDialogConf.width"
            :title="stopDialogConf.title"
            :close-icon="stopDialogConf.closeIcon"
            :ext-cls="'biz-node-re-initialization-dialog'"
            :quick-close="false">
            <template slot="content">
                <div>{{stopDialogConf.content}}</div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isUpdating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            停用中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="stopConfirm">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="stopCancel">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="removeDialogConf.isShow"
            :width="removeDialogConf.width"
            :title="removeDialogConf.title"
            :close-icon="removeDialogConf.closeIcon"
            :ext-cls="'biz-node-re-initialization-dialog'"
            :quick-close="false">
            <template slot="content">
                <div>{{removeDialogConf.content}}</div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isUpdating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            删除中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="removeConfirm">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="removeCancel">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="schedulerDialogConf.isShow"
            :width="schedulerDialogConf.width"
            :title="schedulerDialogConf.title"
            :close-icon="schedulerDialogConf.closeIcon"
            :ext-cls="'biz-node-re-initialization-dialog'"
            :quick-close="false">
            <template slot="content">
                <div>{{schedulerDialogConf.content}}</div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isUpdating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            迁移中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="schedulerConfirm">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="schedulerCancel">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="batchDialogConf.isShow"
            :width="batchDialogConf.width"
            :title="batchDialogConf.title"
            :close-icon="batchDialogConf.closeIcon"
            :ext-cls="'biz-node-re-initialization-dialog'"
            :quick-close="false">
            <template slot="content">
                <div>{{batchDialogConf.content}}</div>
            </template>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isUpdating">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            操作中...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            取消
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="batchConfirm">
                            确定
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="batchCancel">
                            取消
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

    </div>
</template>

<script>
    import bkIPSearcher from '@open/components/ip-searcher'
    import applyPerm from '@open/mixins/apply-perm'
    import tipDialog from '@open/components/tip-dialog'
    import RingCell from './ring-cell'
    import LoadingCell from './loading-cell'
    import mixin from './mixin-node'
    import nodeSearcher from './searcher'

    export default {
        components: {
            RingCell,
            LoadingCell,
            tipDialog,
            'bk-ip-searcher': bkIPSearcher,
            nodeSearcher
        },
        mixins: [applyPerm, mixin],
        data () {
            return {
                nodeNoticeList: [
                    {
                        id: 2,
                        text: '按照规则修改主机名',
                        isChecked: true
                    },
                    {
                        id: 3,
                        text: '安装容器服务相关的组件',
                        isChecked: true
                    }
                ]
            }
        },
        methods: {
        }
    }
</script>

<style scoped lang="postcss">
    @import './node.css';
    .server-tip {
        float: left;
        line-height: 17px;
        font-size: 12px;
        text-align: left;
        padding: 13px 0 13px 20px;
        margin-left: 20px;

        li {
            list-style: circle;
        }
    }
    /* .bk-dialog-footer .bk-dialog-outer button {
        margin-top: 30px;
    } */
</style>
