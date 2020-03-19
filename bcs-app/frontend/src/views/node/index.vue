<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-app-title">
                {{$t('节点')}}
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper biz-node-loading biz-node-content-wrapper" style="padding: 0;" v-bkloading="{ isLoading: pageLoading, opacity: 0.1 }">
            <app-exception
                v-if="exceptionCode && !pageLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>
            <template v-if="!exceptionCode && !pageLoading">
                <div class="biz-panel-header biz-node-query">
                    <div class="left">
                        <button class="bk-button bk-default" @click="showSetLabel">
                            <span>{{$t('设置标签')}}</span>
                        </button>
                        <button class="bk-button bk-default" @click="exportNode">
                            <span>{{$t('导出')}}</span>
                        </button>
                        <bk-dropdown-menu :align="'left'" ref="copyIpDropdownMenu" class="copy-ip-dropdown">
                            <a href="javascript:void(0);" slot="dropdown-trigger" class="bk-text-button copy-ip-btn">
                                <span class="label">{{$t('复制IP')}}</span>
                                <i class="bk-icon icon-angle-down dropdown-menu-angle-down"></i>
                            </a>
                            <ul class="bk-dropdown-list" slot="dropdown-content">
                                <li>
                                    <a href="javascript:void(0)" @click="copyIp('selected')" class="selected" :class="!checkedNodeList.length ? 'disabled' : ''">{{$t('复制所选IP')}}</a>
                                </li>
                                <li>
                                    <a href="javascript:void(0)" @click="copyIp('cur-page')" class="cur-page">{{$t('复制当前页IP')}}</a>
                                </li>
                                <li>
                                    <a href="javascript:void(0)" @click="copyIp('all')" class="all">{{$t('复制所有IP')}}</a>
                                </li>
                            </ul>
                        </bk-dropdown-menu>
                    </div>
                    <div class="right">
                        <bk-dropdown-menu :align="'left'" :trigger="'click'" ref="toggleFilterDropdownMenu">
                            <a href="javascript:void(0);" slot="dropdown-trigger" class="bk-text-button toggle-filter">
                                <span class="label">{{curSelectedClusterName === 'all' ? $t('全部集群') : curSelectedClusterName}}</span>
                                <i class="bk-icon icon-angle-down dropdown-menu-angle-down"></i>
                            </a>
                            <ul class="bk-dropdown-list" slot="dropdown-content">
                                <li @click.stop="changeCluster({ name: 'all' })">
                                    <a href="javascript:void(0)" :title="$t('全部集群')">{{$t('全部集群')}}</a>
                                </li>
                                <li v-for="(cluster, index) in clusterList" @click.stop="changeCluster(cluster)" :key="index">
                                    <a href="javascript:void(0)" :title="cluster.name">{{cluster.name}}</a>
                                </li>
                            </ul>
                        </bk-dropdown-menu>
                        <div class="biz-searcher-wrapper">
                            <!-- <bk-ip-searcher @search="searchNodeList" ref="searcher" /> -->
                            <node-searcher :cluster-id="clusterId" :project-id="projectId" ref="searcher" @search="searchNodeList"></node-searcher>
                        </div>
                        <span class="close-wrapper">
                            <template v-if="$refs.searcher && $refs.searcher.searchParams && $refs.searcher.searchParams.length">
                                <button class="bk-button bk-default is-outline is-icon" :title="$t('清除')" @click="clearSearchParams">
                                    <i class="bk-icon icon-close"></i>
                                </button>
                            </template>
                            <template v-else>
                                <button class="bk-button bk-default is-outline is-icon">
                                </button>
                            </template>
                        </span>
                        <span class="refresh-wrapper">
                            <bk-tooltip class="refresh" :content="$t('重置')" :transfer="true" :placement="'top-end'">
                                <button class="bk-button bk-default is-outline is-icon" @click="refresh">
                                    <i class="bk-icon icon-refresh"></i>
                                </button>
                            </bk-tooltip>
                        </span>
                    </div>
                </div>
                <div class="biz-node-list">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: showLoading, opacity: 0.9 }">
                        <table class="bk-table has-table-hover biz-table" style="overflow: hidden;">
                            <thead>
                                <tr>
                                    <th style="width: 20px; text-align: center; top: 0; position: relative; padding: 0;">
                                        <label class="bk-form-checkbox" v-if="curPageData.length">
                                            <input type="checkbox" name="check-all-node" v-model="isCheckAllNode" @click="checkAllNode" v-if="curPageData.filter(node => node.permissions && node.permissions.edit && node.status === 'normal').length">
                                            <input type="checkbox" v-else name="check-instance" disabled="disabled" />
                                        </label>
                                    </th>
                                    <th style="width: 120px; text-align: left;">{{$t('主机名/IP')}}</th>
                                    <th style="width: 100px;">{{$t('状态')}}</th>
                                    <th style="width: 150px;">{{$t('所属集群')}}</th>
                                    <th style="width: 300px;">{{$t('标签')}}</th>
                                    <th style="width: 200px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curPageData.length">
                                    <tr v-for="(node, index) in curPageData" @click.stop="nodeRowClick" :key="node.id">
                                        <!--
                                            初始化中: initializing, so_initializing, initial_checking, uninitialized
                                            删除中: removing
                                        -->
                                        <template v-if="ingStatus.includes(node.status)">
                                            <td style="width: 40px; text-align: center; position: relative;">
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-node" style="border: 1px solid #ebf0f5;background-color: #fafbfd;background-image: none;" disabled="disabled">
                                                </label>
                                            </td>
                                            <td>{{node.inner_ip}}</td>
                                            <td style="white-space: nowrap;">
                                                <div class="biz-status-node"><loading-cell :style="{ left: 0 }" :ext-cls="['bk-spin-loading-mini', 'bk-spin-loading-danger']"></loading-cell></div>
                                                {{node.status === 'initializing' || node.status === 'so_initializing' || node.status === 'initial_checking' ? $t('初始化中') : $t('删除中')}}
                                            </td>
                                            <td style="white-space: nowrap;">
                                                <bk-tooltip :content="`${node.cluster_id}`" placement="top">
                                                    <p class="biz-text-wrapper">{{node.cluster_name}}</p>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <template v-if="node.transformLabels.length">
                                                    <div class="labels-container" :class="node.isExpandLabels ? 'expand' : ''">
                                                        <div class="labels-wrapper" :class="node.isExpandLabels ? 'expand' : ''" :ref="`${pageConf.curPage}-real${index}`">
                                                            <div class="labels-inner" v-for="(label, labelIndex) in node.transformLabels" :key="labelIndex">
                                                                <span class="key" :title="label.key">{{label.key}}</span>
                                                                <span class="value" :title="label.value">{{label.value}}</span>
                                                            </div>
                                                            <a href="javascript:void(0);" class="bk-text-button toggle-labels"
                                                                :class="node.isExpandLabels ? 'expand' : ''"
                                                                v-if="node.showExpand"
                                                                @click.stop="toggleLabel(node, index)">
                                                                <template v-if="!node.isExpandLabels">
                                                                    {{$t('展开')}}<i class="bk-icon icon-angle-down"></i>
                                                                </template>
                                                                <template v-else>
                                                                    {{$t('收起')}}<i class="bk-icon icon-angle-up"></i>
                                                                </template>
                                                            </a>
                                                        </div>
                                                    </div>
                                                </template>
                                                <template v-else>--</template>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0);" class="bk-text-button disabled">{{$t('设置标签')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="goClusterNode(node)">{{$t('更多操作')}}</a>
                                            </td>
                                        </template>

                                        <!--
                                            初始化失败: initial_failed, so_init_failed, check_failed, bke_failed, schedule_failed
                                            删除失败: delete_failed
                                            删除失败: remove_failed
                                        -->
                                        <template v-if="failStatus.includes(node.status)">
                                            <td style="width: 40px; text-align: center; position: relative;">
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-node" style="border: 1px solid #ebf0f5;background-color: #fafbfd;background-image: none;" disabled="disabled">
                                                </label>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                            </td>
                                            <td style="white-space: nowrap;">
                                                <div class="biz-status-node"><i class="node danger"></i></div>
                                                {{node.status === 'initial_failed' || node.status === 'so_init_failed' || node.status === 'check_failed' || node.status === 'schedule_failed' || node.status === 'bke_failed' ? $t('初始化失败') : $t('移除失败')}}
                                            </td>
                                            <td>
                                                <bk-tooltip :content="`${node.cluster_id}`" placement="top">
                                                    <a href="javascript: void(0);" class="bk-text-button" @click.stop="goClusterOverview(node)">
                                                        <p class="biz-text-wrapper">{{node.cluster_name}}</p>
                                                    </a>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <template v-if="node.transformLabels.length">
                                                    <div class="labels-container" :class="node.isExpandLabels ? 'expand' : ''">
                                                        <div class="labels-wrapper" :class="node.isExpandLabels ? 'expand' : ''" :ref="`${pageConf.curPage}-real${index}`">
                                                            <div class="labels-inner" v-for="(label, labelIndex) in node.transformLabels" :key="labelIndex">
                                                                <span class="key" :title="label.key">{{label.key}}</span>
                                                                <span class="value" :title="label.value">{{label.value}}</span>
                                                            </div>
                                                            <a href="javascript:void(0);" class="bk-text-button toggle-labels"
                                                                :class="node.isExpandLabels ? 'expand' : ''"
                                                                v-if="node.showExpand"
                                                                @click.stop="toggleLabel(node, index)">
                                                                <template v-if="!node.isExpandLabels">
                                                                    {{$t('展开')}}<i class="bk-icon icon-angle-down"></i>
                                                                </template>
                                                                <template v-else>
                                                                    {{$t('收起')}}<i class="bk-icon icon-angle-up"></i>
                                                                </template>
                                                            </a>
                                                        </div>
                                                    </div>
                                                </template>
                                                <template v-else>--</template>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0);" class="bk-text-button disabled">{{$t('设置标签')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="goClusterNode(node)">{{$t('更多操作')}}</a>
                                            </td>
                                        </template>

                                        <!--
                                            不可调度: to_removed
                                        -->
                                        <template v-if="node.status === 'to_removed'">
                                            <td style="width: 40px; text-align: center; position: relative;">
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-node" style="border: 1px solid #ebf0f5;background-color: #fafbfd;background-image: none;" disabled="disabled">
                                                </label>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                            </td>
                                            <td>
                                                <div class="biz-status-node"><i class="node warning"></i></div>
                                                {{$t('不可调度')}}
                                            </td>
                                            <td>
                                                <bk-tooltip :content="`${node.cluster_id}`" placement="top">
                                                    <a href="javascript: void(0);" class="bk-text-button" @click.stop="goClusterOverview(node)">
                                                        <p class="biz-text-wrapper">{{node.cluster_name}}</p>
                                                    </a>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <template v-if="node.transformLabels.length">
                                                    <div class="labels-container" :class="node.isExpandLabels ? 'expand' : ''">
                                                        <div class="labels-wrapper" :class="node.isExpandLabels ? 'expand' : ''" :ref="`${pageConf.curPage}-real${index}`">
                                                            <div class="labels-inner" v-for="(label, labelIndex) in node.transformLabels" :key="labelIndex">
                                                                <span class="key" :title="label.key">{{label.key}}</span>
                                                                <span class="value" :title="label.value">{{label.value}}</span>
                                                            </div>
                                                            <a href="javascript:void(0);" class="bk-text-button toggle-labels"
                                                                :class="node.isExpandLabels ? 'expand' : ''"
                                                                v-if="node.showExpand"
                                                                @click.stop="toggleLabel(node, index)">
                                                                <template v-if="!node.isExpandLabels">
                                                                    {{$t('展开')}}<i class="bk-icon icon-angle-down"></i>
                                                                </template>
                                                                <template v-else>
                                                                    {{$t('收起')}}<i class="bk-icon icon-angle-up"></i>
                                                                </template>
                                                            </a>
                                                        </div>
                                                    </div>
                                                </template>
                                                <template v-else>--</template>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0);" class="bk-text-button disabled">{{$t('设置标签')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="goClusterNode(node)">{{$t('更多操作')}}</a>
                                            </td>
                                        </template>

                                        <!--
                                            不可调度: removable
                                        -->
                                        <template v-if="node.status === 'removable'">
                                            <td style="width: 40px; text-align: center; position: relative;">
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-node" style="border: 1px solid #ebf0f5;background-color: #fafbfd;background-image: none;" disabled="disabled">
                                                </label>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                            </td>
                                            <td>
                                                <div class="biz-status-node"><i class="node warning"></i></div>
                                                {{$t('不可调度')}}
                                            </td>
                                            <td>
                                                <bk-tooltip :content="`${node.cluster_id}`" placement="top">
                                                    <a href="javascript: void(0);" class="bk-text-button" @click.stop="goClusterOverview(node)">
                                                        <p class="biz-text-wrapper">{{node.cluster_name}}</p>
                                                    </a>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <template v-if="node.transformLabels.length">
                                                    <div class="labels-container" :class="node.isExpandLabels ? 'expand' : ''">
                                                        <div class="labels-wrapper" :class="node.isExpandLabels ? 'expand' : ''" :ref="`${pageConf.curPage}-real${index}`">
                                                            <div class="labels-inner" v-for="(label, labelIndex) in node.transformLabels" :key="labelIndex">
                                                                <span class="key" :title="label.key">{{label.key}}</span>
                                                                <span class="value" :title="label.value">{{label.value}}</span>
                                                            </div>
                                                            <a href="javascript:void(0);" class="bk-text-button toggle-labels"
                                                                :class="node.isExpandLabels ? 'expand' : ''"
                                                                v-if="node.showExpand"
                                                                @click.stop="toggleLabel(node, index)">
                                                                <template v-if="!node.isExpandLabels">
                                                                    {{$t('展开')}}<i class="bk-icon icon-angle-down"></i>
                                                                </template>
                                                                <template v-else>
                                                                    {{$t('收起')}}<i class="bk-icon icon-angle-up"></i>
                                                                </template>
                                                            </a>
                                                        </div>
                                                    </div>
                                                </template>
                                                <template v-else>--</template>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0);" class="bk-text-button disabled">{{$t('设置标签')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="goClusterNode(node)">{{$t('更多操作')}}</a>
                                            </td>
                                        </template>

                                        <!--
                                            不正常: not_ready
                                            不正常: unnormal
                                        -->
                                        <template v-if="node.status === 'not_ready' || node.status === 'unnormal'">
                                            <td style="width: 40px; text-align: center; position: relative;">
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-node" style="border: 1px solid #ebf0f5;background-color: #fafbfd;background-image: none;" disabled="disabled">
                                                </label>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                            </td>
                                            <td>
                                                <div class="biz-status-node"><i class="node danger"></i></div>
                                                {{$t('不正常')}}
                                            </td>
                                            <td>
                                                <bk-tooltip :content="`${node.cluster_id}`" placement="top">
                                                    <a href="javascript: void(0);" class="bk-text-button" @click.stop="goClusterOverview(node)">
                                                        <p class="biz-text-wrapper">{{node.cluster_name}}</p>
                                                    </a>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <template v-if="node.transformLabels.length">
                                                    <div class="labels-container" :class="node.isExpandLabels ? 'expand' : ''">
                                                        <div class="labels-wrapper" :class="node.isExpandLabels ? 'expand' : ''" :ref="`${pageConf.curPage}-real${index}`">
                                                            <div class="labels-inner" v-for="(label, labelIndex) in node.transformLabels" :key="labelIndex">
                                                                <span class="key" :title="label.key">{{label.key}}</span>
                                                                <span class="value" :title="label.value">{{label.value}}</span>
                                                            </div>
                                                            <a href="javascript:void(0);" class="bk-text-button toggle-labels"
                                                                :class="node.isExpandLabels ? 'expand' : ''"
                                                                v-if="node.showExpand"
                                                                @click.stop="toggleLabel(node, index)">
                                                                <template v-if="!node.isExpandLabels">
                                                                    {{$t('展开')}}<i class="bk-icon icon-angle-down"></i>
                                                                </template>
                                                                <template v-else>
                                                                    {{$t('收起')}}<i class="bk-icon icon-angle-up"></i>
                                                                </template>
                                                            </a>
                                                        </div>
                                                    </div>
                                                </template>
                                                <template v-else>--</template>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0);" class="bk-text-button disabled">{{$t('设置标签')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="goClusterNode(node)">{{$t('更多操作')}}</a>
                                            </td>
                                        </template>

                                        <!--
                                            正常: normal
                                        -->
                                        <template v-if="node.status === 'normal'">
                                            <td style="width: 40px; text-align: center; position: relative;">
                                                <label class="bk-form-checkbox">
                                                    <input type="checkbox" name="check-node" v-model="node.isChecked" @click.stop="checkNode(node)" :disabled="!node.permissions.edit" />
                                                </label>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0)" class="bk-text-button" @click="goNodeOverview(node)">{{node.inner_ip}}</a>
                                            </td>
                                            <td>
                                                <div class="biz-status-node"><i class="node success"></i></div>
                                                {{$t('正常')}}
                                            </td>
                                            <td>
                                                <bk-tooltip :content="`${node.cluster_id}`" placement="top">
                                                    <a href="javascript: void(0);" class="bk-text-button" @click.stop="goClusterOverview(node)">
                                                        <p class="biz-text-wrapper">{{node.cluster_name}}</p>
                                                    </a>
                                                </bk-tooltip>
                                            </td>
                                            <td>
                                                <template v-if="node.transformLabels.length">
                                                    <div class="labels-container" :class="node.isExpandLabels ? 'expand' : ''">
                                                        <div class="labels-wrapper" :class="node.isExpandLabels ? 'expand' : ''" :ref="`${pageConf.curPage}-real${index}`">
                                                            <div class="labels-inner" v-for="(label, labelIndex) in node.transformLabels" :key="labelIndex">
                                                                <span class="key" :title="label.key">{{label.key}}</span>
                                                                <span class="value" :title="label.value">{{label.value}}</span>
                                                            </div>
                                                            <a href="javascript:void(0);" class="bk-text-button toggle-labels"
                                                                :class="node.isExpandLabels ? 'expand' : ''"
                                                                v-if="node.showExpand"
                                                                @click.stop="toggleLabel(node, index)">
                                                                <template v-if="!node.isExpandLabels">
                                                                    {{$t('展开')}}<i class="bk-icon icon-angle-down"></i>
                                                                </template>
                                                                <template v-else>
                                                                    {{$t('收起')}}<i class="bk-icon icon-angle-up"></i>
                                                                </template>
                                                            </a>
                                                        </div>
                                                    </div>
                                                </template>
                                                <template v-else>--</template>
                                            </td>
                                            <td>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="showSetLabelInRow(node)">{{$t('设置标签')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop="goClusterNode(node)">{{$t('更多操作')}}</a>
                                            </td>
                                        </template>
                                    </tr>
                                </template>
                                <template v-if="!curPageData.length">
                                    <tr>
                                        <td colspan="6">
                                            <div class="bk-message-box no-data">
                                                <p class="message empty-message">{{$t('无数据')}}</p>
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
                            @page-change="pageChange">
                        </bk-paging>
                        <template v-if="isEn">
                            <div class="already-selected-nums" v-if="alreadySelectedNums">Checked: {{alreadySelectedNums}}</div>
                        </template>
                        <template v-else>
                            <div class="already-selected-nums" v-if="alreadySelectedNums">已选{{alreadySelectedNums}}条</div>
                        </template>
                    </div>
                </div>
            </template>
        </div>

        <bk-sideslider
            :is-show.sync="setLabelConf.isShow"
            :title="setLabelConf.title"
            :width="setLabelConf.width"
            :quick-close="false"
            class="biz-cluster-set-label-sideslider"
            @hidden="hideSetLabel">
            <template slot="content">
                <div class="title-tip" v-if="isEn">Tags help organize your resources (like env:prod), <a :href="labelDocUrl" target="_blank" class="bk-text-button">Show detail</a></div>
                <div class="title-tip" v-else>标签有助于整理你的资源（如 env:prod），详情可查看<a :href="labelDocUrl" target="_blank" class="bk-text-button">帮助文档</a></div>
                <div class="wrapper" style="position: relative;" v-bkloading="{ isLoading: setLabelConf.loading }">
                    <form class="bk-form bk-form-vertical set-label-form">
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <label class="bk-label label">{{$t('键')}}：</label>
                            </div>
                            <div class="right">
                                <label class="bk-label label">{{$t('值')}}：
                                    <template v-if="showMixinTip">
                                        <bk-tooltip :delay="300" placement="top">
                                            <i class="bk-icon icon-question-circle" style="vertical-align: middle;"></i>
                                            <div slot="content">
                                                <p class="app-biz-node-label-tip-content">{{$t('为什么会有混合值')}}：</p>
                                                <p class="app-biz-node-label-tip-content">{{$t('已选节点的标签中存在同一个键对应多个值')}}</p>
                                            </div>
                                        </bk-tooltip>
                                    </template>
                                </label>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="biz-key-value-wrapper mb10">
                                    <div class="biz-key-value-item" v-for="(label, index) in labelList" :key="index">
                                        <template v-if="label.key && label.fromData">
                                            <input type="text" class="bk-form-input" disabled v-model="label.key">
                                        </template>
                                        <template v-else>
                                            <input type="text" :placeholder="$t('键')" maxlength="30" class="bk-form-input" v-model="label.key">
                                        </template>
                                        <span class="equals-sign">=</span>
                                        <input type="text" maxlength="30" class="bk-form-input right" :placeholder="$t('混合值')" v-if="label.isMixin" v-model="label.value">
                                        <input type="text" maxlength="30" class="bk-form-input right" :placeholder="$t('值')" v-else-if="!label.value" v-model="label.value">
                                        <input type="text" maxlength="30" class="bk-form-input right" :placeholder="$t('值')" v-else v-model="label.value">

                                        <template v-if="labelList.length === 1">
                                            <button class="action-btn">
                                                <i class="bk-icon icon-plus" @click.stop.prevent="addLabel"></i>
                                            </button>
                                        </template>
                                        <template v-else>
                                            <template v-if="index === labelList.length - 1">
                                                <button class="action-btn" @click.stop.prevent>
                                                    <i class="bk-icon icon-plus mr5" @click.stop.prevent="addLabel"></i>
                                                    <i class="bk-icon icon-minus" @click.stop.prevent="delLabel(label, index)"></i>
                                                </button>
                                            </template>
                                            <template v-else>
                                                <button class="action-btn">
                                                    <i class="bk-icon icon-plus mr5" @click.stop.prevent="addLabel"></i>
                                                    <i class="bk-icon icon-minus" @click.stop.prevent="delLabel(label, index)"></i>
                                                </button>
                                            </template>
                                        </template>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="action-inner">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="confirmSetLabel">
                                {{$t('保存')}}
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideSetLabel">
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
    import axios from 'axios'
    import Clipboard from 'clipboard'
    import { catchErrorHandler } from '@open/common/util'
    import LoadingCell from '../cluster/loading-cell'
    import nodeSearcher from '../cluster/searcher'

    export default {
        components: {
            LoadingCell,
            nodeSearcher
        },
        data () {
            return {
                ingStatus: [
                    // 初始化中
                    'initializing',
                    // 初始化中
                    'so_initializing',
                    // 移除中
                    'removing',
                    // 初始化中
                    'initial_checking',
                    // 初始化中
                    'uninitialized'
                ],
                failStatus: [
                    // 初始化失败
                    'initial_failed',
                    // 初始化失败
                    'so_init_failed',
                    // 初始化失败
                    'check_failed',
                    // 初始化失败
                    'bke_failed',
                    // 初始化失败
                    'schedule_failed',
                    // 删除失败
                    'delete_failed',
                    // 删除失败
                    'remove_failed'
                ],
                showLoading: false,
                pageLoading: false,
                nodeList: [],
                curPageData: [],
                // for search
                nodeListTmp: [],
                pageConf: {
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                // 已选择的 nodeList
                checkedNodeList: [],
                // 单行 node
                curRowNode: {},
                setLabelConf: {
                    isShow: false,
                    title: this.$t('设置标签'),
                    width: 750,
                    loading: false
                },
                // 设置标签的参数
                labelList: [{ key: '', value: '' }],
                // 节点列表是否全选
                isCheckAllNode: false,
                // 是否显示混合值的提示
                showMixinTip: false,
                enableSetLabel: false,
                exceptionCode: null,
                cancelLoop: false,
                timer: null,
                clusterList: [],
                curSelectedClusterName: 'all',
                curSelectedClusterId: 'all',
                alreadySelectedNums: 0,
                searchParams: [],
                clipboardInstance: null
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            labelDocUrl () {
                const curProject = this.$store.state.curProject
                return curProject.kind === 1 ? this.PROJECT_CONFIG.doc.nodeLabelK8s : this.PROJECT_CONFIG.doc.nodeLabelMesos
            },
            isEn () {
                return this.$store.state.isEn
            }
        },
        watch: {
            'checkedNodeList.length' (len) {
                this.enableSetLabel = !!len
                this.alreadySelectedNums = len
            }
        },
        beforeDestroy () {
            clearTimeout(this.timer) && (this.timer = null)
            this.cancelLoop = true

            this.clipboardInstance && this.clipboardInstance.destroy()
            if (this.clipboardInstance && this.clipboardInstance.off) {
                this.clipboardInstance.off('success')
            }
        },
        destroyed () {
            clearTimeout(this.timer) && (this.timer = null)
            this.cancelLoop = true

            this.clipboardInstance && this.clipboardInstance.destroy()
            if (this.clipboardInstance && this.clipboardInstance.off) {
                this.clipboardInstance.off('success')
            }
        },
        async created () {
            this.pageConf.curPage = 1
            this.pageLoading = true
            await this.fetchData()
        },
        methods: {
            /**
             * 获取所有的集群
             */
            async getClusters () {
                try {
                    const res = await this.$store.dispatch('cluster/getClusterList', this.projectId)

                    const list = res.data.results || []
                    this.$store.commit('cluster/forceUpdateClusterList', list)

                    this.clusterList.splice(0, this.clusterList.length, ...list)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 切换集群条件
             *
             * @param {Object} cluster 集群
             */
            changeCluster (cluster) {
                setTimeout(() => {
                    this.$refs.toggleFilterDropdownMenu && this.$refs.toggleFilterDropdownMenu.hide()
                }, 0)
                this.curSelectedClusterName = cluster.name
                this.curSelectedClusterId = cluster.cluster_id
                this.pageConf.curPage = 1
                this.searchNodeList()
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
                this.pageChange()
            },

            /**
             * 格式化日志
             *
             * @param {string} log 日志内容
             *
             * @return {strin} 格式化后的日志内容
             */
            formatLog (log) {
                // 换行
                log = log.replace(/##/ig, '<p class="html-tag"></p>').replace(/\|/ig, '<p class="html-tag"></p>')
                // 着色
                log = log.replace(/(Failed)/ig, '<span class="biz-danger-text">$1</span>')
                log = log.replace(/(OK)/ig, '<span class="biz-success-text">$1</span>')
                return log
            },

            /**
             * 查询节点列表数据
             *
             * @param {boolean} isPolling 是否是轮询
             */
            async fetchData (isPolling) {
                if (!isPolling) {
                    this.showLoading = true
                    await this.getClusters()
                }
                try {
                    const res = await this.$store.dispatch('cluster/getAllNodeList', {
                        projectId: this.projectId
                    })

                    const data = res.data || {}

                    const list = data.results || []
                    const nodeList = []
                    list.forEach(item => {
                        item.transformLabels = []
                        item.labels.forEach((label, index) => {
                            const labelKey = Object.keys(label)[0]
                            const labelVal = label[labelKey]
                            item.transformLabels.push({
                                key: labelKey,
                                value: labelVal
                            })
                        })

                        item.isExpandLabels = false
                        // 是否显示标签的展开按钮
                        item.showExpand = false
                        nodeList.push(item)
                    })

                    this.isCheckAllNode = false

                    this.nodeList.splice(0, this.nodeList.length, ...nodeList)
                    this.nodeListTmp.splice(0, this.nodeListTmp.length, ...nodeList)

                    if (this.curSelectedClusterName !== 'all') {
                        const newNodeList = []
                        newNodeList.splice(0, 0, ...this.nodeListTmp.filter(
                            node => node.cluster_name === this.curSelectedClusterName
                        ))

                        this.nodeList.splice(0, this.nodeList.length, ...newNodeList)
                    }

                    // this.initPageConf()
                    // this.curPageData = this.getDataByPage(this.pageConf.curPage)
                    if (this.$refs.searcher
                        && this.$refs.searcher.searchParams
                        && this.$refs.searcher.searchParams.length
                    ) {
                        this.searchNodeList(this.pageConf.curPage)
                    } else {
                        this.initPageConf()
                        this.curPageData = this.getDataByPage(this.pageConf.curPage)
                    }

                    setTimeout(() => {
                        this.curPageData.forEach((item, index) => {
                            const real = this.$refs[`${this.pageConf.curPage}-real${index}`]
                            if (real && real[0]) {
                                // .labels-inner 高度 24px, margin-bottom 5px
                                if (real[0].offsetHeight > 24 + 5) {
                                    item.showExpand = true
                                }
                            }
                        })
                    }, 0)

                    const checkNodeIdList = this.checkedNodeList.map(node => node.id)
                    this.nodeList.forEach(node => {
                        if (node.permissions && node.permissions.edit && node.status === 'normal') {
                            node.isChecked = checkNodeIdList.indexOf(node.id) > -1
                        }
                    })

                    // 当前页选中的
                    const selectedNodeList = this.curPageData.filter(node => node.isChecked === true)
                    // 当前页合法的
                    const validList = this.curPageData.filter(
                        node => node.permissions && node.permissions.edit && node.status === 'normal'
                    )
                    this.isCheckAllNode = selectedNodeList.length === validList.length

                    if (this.cancelLoop) {
                        clearTimeout(this.timer)
                        this.timer = null
                    } else {
                        this.timer = setTimeout(() => {
                            this.fetchData(true)
                        }, 10000)
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.pageLoading = false
                    this.showLoading = false
                }
            },

            /**
             * 初始化翻页条
             */
            initPageConf () {
                const total = this.nodeList.length
                this.pageConf.total = total
                this.pageConf.show = true
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
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
                if (endIndex > this.nodeList.length) {
                    endIndex = this.nodeList.length
                }
                const data = this.nodeList.slice(startIndex, endIndex)
                return data
            },

            /**
             * 翻页回调
             *
             * @param {number} page 当前页
             */
            pageChange (page = 1) {
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData.splice(0, this.curPageData.length, ...data)

                // 当前页选中的
                const selectedNodeList = this.curPageData.filter(node => node.isChecked === true)

                // 当前页合法的
                const validList = this.curPageData.filter(
                    node => node.permissions && node.permissions.edit && node.status === 'normal'
                )

                this.isCheckAllNode = selectedNodeList.length === validList.length

                setTimeout(() => {
                    this.curPageData.forEach((item, index) => {
                        const real = this.$refs[`${this.pageConf.curPage}-real${index}`]
                        if (real && real[0]) {
                            // .labels-inner 高度 24px, margin-bottom 5px
                            if (real[0].offsetHeight > 24 + 5) {
                                item.showExpand = true
                            }
                        }
                    })
                }, 0)
            },

            /**
             * 展开或收起当前行的标签
             *
             * @param {Object} node 当前行 node 对象
             * @param {number} index 当前行 node 对象索引
             */
            toggleLabel (node, index) {
                node.isExpandLabels = !node.isExpandLabels
                this.$set(this.curPageData, index, node)
            },

            /**
             * 清除 searcher 搜索条件
             */
            clearSearchParams () {
                this.$refs.searcher.clear()
                this.getSearchParams()
            },

            /**
             * 手动刷新表格数据
             */
            async refresh () {
                this.showLoading = true
                this.curSelectedClusterName = 'all'
                this.curSelectedClusterId = 'all'
                this.clearSearchParams()
                await this.fetchData()
            },

            /**
             * 延迟
             *
             * @param {Number} ms 毫秒数
             */
            timeout (ms) {
                return new Promise(resolve => setTimeout(resolve, ms))
            },

            /**
             * 获取 searcher 的参数
             *
             * @return {Object} 参数
             */
            getSearchParams () {
                const searchParams = (this.$refs.searcher && this.$refs.searcher.searchParams) || []
                const ipParams = searchParams.filter(item => item.id === 'ip').map(
                    item => item.valueArr.join(',')
                ).join(',')

                const labelsParams = searchParams.filter(item => item.id === 'labels')
                const labels = []
                labelsParams.forEach(label => {
                    label.valueArr.forEach(item => {
                        labels.push({
                            [`${label.key}`]: item
                        })
                    })
                })
                return { ipParams, labels }
            },

            /**
             * nodeList 搜索
             */
            async searchNodeList (page = 1) {
                this.showLoading = true
                await this.timeout(1000)
                this.showLoading = false

                const newNodeList = []
                if (this.curSelectedClusterName === 'all') {
                    newNodeList.splice(0, 0, ...this.nodeListTmp)
                } else {
                    newNodeList.splice(0, 0, ...this.nodeListTmp.filter(
                        node => node.cluster_name === this.curSelectedClusterName
                    ))
                }

                const searchParams = this.getSearchParams()
                const ipParams = searchParams.ipParams || ''
                const ipList = ipParams
                    ? searchParams.ipParams.split(',')
                    : []

                const sLabels = searchParams.labels
                const len = sLabels.length

                const results = []

                // 没有搜索条件，那么就是全部
                if (!ipList.length && !len) {
                    results.splice(0, 0, ...newNodeList)
                } else {
                    const resultMap = {}
                    if (ipList.length) {
                        newNodeList.forEach(node => {
                            ipList.forEach(ip => {
                                if (String(node.inner_ip || '').toLowerCase().indexOf(ip) > -1) {
                                    resultMap[node.inner_ip] = node
                                }
                            })
                        })
                    } else {
                        newNodeList.forEach(node => {
                            resultMap[node.inner_ip] = node
                        })
                    }

                    Object.keys(resultMap).forEach(ip => {
                        for (let i = 0; i < len; i++) {
                            if (!resultMap[ip].labels.filter(
                                label => JSON.stringify(label) === JSON.stringify(sLabels[i])).length
                            ) {
                                delete resultMap[ip]
                                continue
                            }
                        }
                    })
                    Object.keys(resultMap).forEach(key => {
                        results.push(resultMap[key])
                    })
                }

                this.nodeList.splice(0, this.nodeList.length, ...results)

                this.pageConf.curPage = page

                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)

                const checkNodeIdList = this.checkedNodeList.map(node => node.id)
                this.curPageData.forEach(item => {
                    if (item.permissions && item.permissions.edit && item.status === 'normal') {
                        item.isChecked = checkNodeIdList.indexOf(item.id) > -1
                    }
                })

                // 当前页选中的
                const selectedNodeList = this.curPageData.filter(node => node.isChecked === true)

                // 当前页合法的
                const validList = this.curPageData.filter(
                    node => node.permissions && node.permissions.edit && node.status === 'normal'
                )

                this.isCheckAllNode = selectedNodeList.length === validList.length
            },

            /**
             * 节点列表行选中
             *
             * @param {Object} e 事件对象
             */
            nodeRowClick (e) {
                let target = e.target
                while (target.nodeName.toLowerCase() !== 'tr') {
                    target = target.parentNode
                }
                const checkboxNode = target.querySelector('input[type="checkbox"]')
                checkboxNode && checkboxNode.click()
            },

            /**
             * 节点列表全选
             */
            checkAllNode (e) {
                const isChecked = e.target.checked
                this.curPageData.forEach(node => {
                    if (node.permissions && node.permissions.edit && node.status === 'normal') {
                        node.isChecked = isChecked
                    }
                })
                const checkedNodeList = []
                checkedNodeList.splice(0, 0, ...this.checkedNodeList)
                // 用于区分是否已经选择过
                const hasCheckedList = checkedNodeList.map(item => item.id)
                if (isChecked) {
                    const checkedList = this.curPageData.filter(
                        node => node.permissions && node.permissions.edit && node.status === 'normal' && !hasCheckedList.includes(node.id)
                    )
                    checkedNodeList.push(...checkedList)
                    this.checkedNodeList.splice(0, this.checkedNodeList.length, ...checkedNodeList)
                } else {
                    // 当前页所有合法的 node id 集合
                    const validIdList = this.curPageData.filter(
                        node => node.permissions && node.permissions.edit && node.status === 'normal'
                    ).map(node => node.id)

                    const newCheckedNodeList = []
                    this.checkedNodeList.forEach(checkedNode => {
                        if (validIdList.indexOf(checkedNode.id) < 0) {
                            newCheckedNodeList.push(JSON.parse(JSON.stringify(checkedNode)))
                        }
                    })
                    this.checkedNodeList.splice(0, this.checkedNodeList.length, ...newCheckedNodeList)
                }
            },

            /**
             * 节点列表每一行的 checkbox 点击
             *
             * @param {Object} node 当前节点即当前行
             */
            checkNode (node) {
                this.$nextTick(() => {
                    // 当前页选中的
                    const selectedNodeList = this.curPageData.filter(node => node.isChecked === true)
                    // 当前页合法的
                    const validList = this.curPageData.filter(
                        node => node.permissions && node.permissions.edit && node.status === 'normal'
                    )
                    this.isCheckAllNode = selectedNodeList.length === validList.length

                    const checkedNodeList = []
                    if (node.isChecked) {
                        checkedNodeList.splice(0, checkedNodeList.length, ...this.checkedNodeList)
                        if (!this.checkedNodeList.filter(checkedNode => checkedNode.id === node.id).length) {
                            checkedNodeList.push(node)
                        }
                    } else {
                        this.checkedNodeList.forEach(checkedNode => {
                            if (checkedNode.id !== node.id) {
                                checkedNodeList.push(JSON.parse(JSON.stringify(checkedNode)))
                            }
                        })
                    }
                    this.checkedNodeList.splice(0, this.checkedNodeList.length, ...checkedNodeList)
                })
            },

            /**
             * 复制 IP
             *
             * @param {string} idx 复制的标识
             */
            copyIp (idx) {
                this.$refs.copyIpDropdownMenu && this.$refs.copyIpDropdownMenu.hide()

                let successMsg = ''
                // 复制所选 ip
                if (idx === 'selected') {
                    this.clipboardInstance = new Clipboard('.copy-ip-dropdown .selected', {
                        text: trigger => this.checkedNodeList.map(checkedNode => checkedNode.inner_ip).join('\n')
                    })
                    successMsg = this.$t('复制 {len} 个IP成功', { len: this.checkedNodeList.length })
                } else if (idx === 'cur-page') {
                    // 复制当前页 IP
                    this.clipboardInstance = new Clipboard('.copy-ip-dropdown .cur-page', {
                        text: trigger => this.curPageData.map(checkedNode => checkedNode.inner_ip).join('\n')
                    })
                    successMsg = this.$t('复制当前页IP成功')
                } else if (idx === 'all') {
                    // 复制所有 IP
                    this.clipboardInstance = new Clipboard('.copy-ip-dropdown .all', {
                        text: trigger => this.nodeList.map(checkedNode => checkedNode.inner_ip).join('\n')
                    })
                    successMsg = this.$t('复制所有IP成功')
                }
                this.clipboardInstance.on('success', e => {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'success',
                        message: successMsg
                    })
                })
            },

            /**
             * 显示设置节点标签 sideslider
             */
            async showSetLabel () {
                if (!this.checkedNodeList.length) {
                    this.bkMessageInstance && this.bkMessageInstance.close()
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择节点')
                    })
                    return
                }

                try {
                    this.setLabelConf.isShow = true
                    this.setLabelConf.loading = true
                    const res = await this.$store.dispatch('cluster/getNodeLabel', {
                        projectId: this.projectId,
                        nodeIds: this.checkedNodeList.map(checkedNode => checkedNode.id)
                    })

                    const labels = res.data || {}
                    const list = Object.keys(labels)
                    const labelList = []
                    if (list.length) {
                        list.forEach((key, index) => {
                            const isMixin = labels[key] === '*****-----$$$$$'
                            if (isMixin) {
                                this.showMixinTip = true
                            }
                            const value = isMixin ? '' : labels[key]
                            labelList.push({
                                key,
                                fromData: 1,
                                value: value,
                                // 是否是混合值
                                isMixin: isMixin
                            })
                        })
                    }
                    labelList.push({ key: '', value: '' })
                    this.labelList.splice(0, this.labelList.length, ...labelList)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    setTimeout(() => {
                        this.setLabelConf.loading = false
                    }, 300)
                }
            },

            /**
             * 单行里的显示设置节点标签 sideslider
             *
             * @param {Object} node 当前节点对象
             */
            async showSetLabelInRow (node) {
                if (!node.permissions.view) {
                    const type = `cluster_${node.cluster_env === 'stag' ? 'test' : 'prod'}`
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: node.cluster_id,
                        resource_name: node.cluster_name,
                        resource_type: type
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                try {
                    this.setLabelConf.isShow = true
                    this.setLabelConf.loading = true
                    const res = await this.$store.dispatch('cluster/getNodeLabel', {
                        projectId: this.projectId,
                        nodeIds: node.id
                    })

                    const labels = res.data || {}
                    const list = Object.keys(labels)
                    const labelList = []
                    if (list.length) {
                        list.forEach((key, index) => {
                            const isMixin = labels[key] === '*****-----$$$$$'
                            if (isMixin) {
                                this.showMixinTip = true
                            }
                            const value = isMixin ? '' : labels[key]
                            labelList.push({
                                key,
                                fromData: 1,
                                value: value,
                                // 是否是混合值
                                isMixin: isMixin
                            })
                        })
                    }
                    labelList.push({ key: '', value: '' })
                    this.labelList.splice(0, this.labelList.length, ...labelList)

                    this.curRowNode = Object.assign({}, node)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    setTimeout(() => {
                        this.setLabelConf.loading = false
                    }, 300)
                }
            },

            /**
             * sideslder 里添加 label 按钮
             */
            addLabel () {
                const labelList = []
                labelList.splice(0, labelList.length, ...this.labelList)
                labelList.push({ key: '', value: '' })
                this.labelList.splice(0, this.labelList.length, ...labelList)
            },

            /**
             * sideslder 里删除 label 按钮
             *
             * @param {Object} label 当前 label 对象
             * @param {number} index 当前 label 对象索引
             */
            delLabel (label, index) {
                const labelList = []
                labelList.splice(0, labelList.length, ...this.labelList)
                labelList.splice(index, 1)
                this.labelList.splice(0, this.labelList.length, ...labelList)
            },

            /**
             * 设置标签 sideslder 确认按钮
             */
            async confirmSetLabel () {
                const labelList = []
                labelList.splice(0, labelList.length, ...this.labelList)
                const len = labelList.length
                const labelInfo = {}
                for (let i = 0; i < len; i++) {
                    const key = labelList[i].key.trim()
                    const value = labelList[i].value.trim()
                    if (labelInfo[key]) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('键值【{key}】重复，请重新填写', { key: key })
                        })
                        return
                    }

                    // if (!/^[a-z0-9A-Z][\w.-]{0,61}[a-z0-9A-Z]$/.test(key)) {
                    //     this.$bkMessage({
                    //         theme: 'error',
                    //         message: '键不符合规则，以字母数字开头结尾，只能包含".", "-"的大于1位不超过63位的字符串'
                    //     })
                    //     return
                    // }

                    // if (!/^[a-z0-9A-Z][\w.-]{0,61}[a-z0-9A-Z]$/.test(value)) {
                    //     this.$bkMessage({
                    //         theme: 'error',
                    //         message: '值不符合规则，以字母数字开头结尾，只能包含".", "-"的大于1位不超过63位的字符串'
                    //     })
                    //     return
                    // }

                    if (key) {
                        labelInfo[key] = labelList[i].isMixin && value === '' ? '*****-----$$$$$' : value
                    }
                }

                const nodeIdList = []

                if (this.curRowNode) {
                    nodeIdList.push(this.curRowNode.id)
                } else {
                    if (this.checkedNodeList.length) {
                        nodeIdList.push(...this.checkedNodeList.map(checkedNode => checkedNode.id))
                    }
                }

                try {
                    this.setLabelConf.loading = true
                    await this.$store.dispatch('cluster/updateLabel', {
                        projectId: this.projectId,
                        node_id_list: nodeIdList,
                        node_label_info: labelInfo
                    })

                    this.hideSetLabel()
                    this.checkedNodeList.splice(0, this.checkedNodeList.length, ...[])
                    setTimeout(() => {
                        this.curRowNode = null
                        this.fetchData()
                    }, 200)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.setLabelConf.loading = false
                }
            },

            /**
             * 设置标签 sideslder 取消按钮
             */
            hideSetLabel () {
                this.curRowNode = null
                this.setLabelConf.isShow = false
                this.labelList.splice(0, this.labelList.length, ...[])
            },

            /**
             * 进入节点详情页面
             *
             * @param {Object} node 节点信息
             */
            async goNodeOverview (node) {
                if (!node.permissions.view) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: node.cluster_id,
                        resource_name: node.cluster_name,
                        resource_type: `cluster_${node.cluster_env === 'stag' ? 'test' : 'prod'}`
                    })
                }

                this.$router.push({
                    name: 'clusterNodeOverview',
                    params: {
                        projectId: node.project_id,
                        projectCode: node.project_code,
                        nodeId: node.inner_ip,
                        clusterId: node.cluster_id,
                        backTarget: 'nodeMain'
                    }
                })
            },

            /**
             * 跳转到 clusterOverview
             *
             * @param {Object} node 当前节点对象
             */
            async goClusterOverview (node) {
                if (!node.permissions.view) {
                    const type = `cluster_${node.cluster_env === 'stag' ? 'test' : 'prod'}`
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: node.cluster_id,
                        resource_name: node.cluster_name,
                        resource_type: type
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.$store.commit('cluster/forceUpdateCurCluster', {})
                this.$router.push({
                    name: 'clusterOverview',
                    params: {
                        projectId: node.project_id,
                        projectCode: node.project_code,
                        clusterId: node.cluster_id,
                        backTarget: 'nodeMain'
                    }
                })
            },

            /**
             * 跳转到 clusterNode
             *
             * @param {Object} node 当前节点对象
             */
            async goClusterNode (node) {
                if (!node.permissions.view) {
                    const type = `cluster_${node.cluster_env === 'stag' ? 'test' : 'prod'}`
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: node.cluster_id,
                        resource_name: node.cluster_name,
                        resource_type: type
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.$store.commit('cluster/forceUpdateCurCluster', {})
                this.$router.push({
                    name: 'clusterNode',
                    params: {
                        projectId: node.project_id,
                        projectCode: node.project_code,
                        clusterId: node.cluster_id,
                        backTarget: 'nodeMain'
                    },
                    query: {
                        inner_ip: node.inner_ip
                    }
                })
            },

            /**
             * 节点导出
             */
            async exportNode () {
                // const link = document.createElement('a')
                // link.style.display = 'none'
                // link.href = `${DEVOPS_BCS_API_URL}/api/projects/${this.projectId}/nodes/export/?cluster_id=`
                //     + `${this.curSelectedClusterId === 'all' ? '' : this.curSelectedClusterId}`
                // document.body.appendChild(link)
                // link.click()

                const url = `${DEVOPS_BCS_API_URL}/api/projects/${this.projectId}/nodes/export/`

                const response = await axios({
                    url: url,
                    method: 'post',
                    responseType: 'blob', // 这句话很重要
                    data: {
                        cluster_id: this.curSelectedClusterId === 'all' ? '' : this.curSelectedClusterId
                    }
                })

                if (response.status !== 200) {
                    console.log('系统异常，请稍候再试')
                    return
                }

                const blob = new Blob([response.data], { type: response.headers['content-type'] })
                const a = window.document.createElement('a')
                const downUrl = window.URL.createObjectURL(blob)
                let filename = 'download.xls'
                const contentDisposition = response.headers['content-disposition']
                if (contentDisposition && contentDisposition.indexOf('filename=') !== -1) {
                    filename = contentDisposition.split('filename=')[1]
                    a.href = downUrl
                    a.download = filename || 'download.xls'
                    a.click()
                    window.URL.revokeObjectURL(downUrl)
                }
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
