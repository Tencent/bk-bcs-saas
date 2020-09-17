<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-service-title">
                Service
                <span class="biz-tip f12 ml10">{{$t('请通过模板集创建Service')}}</span>
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
                        <button class="bk-button bk-default" @click.stop.prevent="removeServices" v-if="curPageData.length">
                            <span>{{$t('批量删除')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="$t('输入关键字，按Enter搜索')"
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="getServiceList"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>

                <div class="biz-service">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table has-table-hover biz-table biz-service-table">
                            <thead>
                                <tr>
                                    <th style="width: 50px;">
                                        <label class="bk-form-checkbox">
                                            <input
                                                type="checkbox"
                                                name="check-all-user"
                                                :checked="isCheckCurPageAll"
                                                @click="toogleCheckCurPage"
                                                :disabled="!serviceList.length" />
                                        </label>
                                    </th>
                                    <th style="padding-left: 30px;">{{$t('Service名称')}}</th>
                                    <th style="min-width: 100px;">{{$t('所属集群')}}</th>
                                    <th>{{$t('命名空间')}}</th>
                                    <th>{{$t('来源')}}</th>
                                    <th style="min-width: 100px;">{{$t('更新时间')}}</th>
                                    <th style="min-width: 100px;">{{$t('创建时间')}}</th>
                                    <th>{{$t('更新人')}}</th>
                                    <th style="width: 125px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curPageData.length">
                                    <tr v-for="(service, index) in curPageData" :key="service._id">
                                        <td>
                                            <label class="bk-form-checkbox">
                                                <input
                                                    type="checkbox"
                                                    name="check-variable"
                                                    :disabled="!service.can_delete || !service.permissions.use"
                                                    v-model="service.isChecked"
                                                    @click="rowClick" />
                                            </label>
                                        </td>
                                        <td style="padding-left: 30px;">
                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="service.status === 'updating'" style="margin-left: -20px;">
                                                <div class="rotate rotate1"></div>
                                                <div class="rotate rotate2"></div>
                                                <div class="rotate rotate3"></div>
                                                <div class="rotate rotate4"></div>
                                                <div class="rotate rotate5"></div>
                                                <div class="rotate rotate6"></div>
                                                <div class="rotate rotate7"></div>
                                                <div class="rotate rotate8"></div>
                                            </div>
                                            <a href="javascript: void(0)" class="bk-text-button biz-table-title biz-resource-title" @click.stop.prevent="showServiceDetail(service, index)">{{service.resourceName ? service.resourceName : '--'}}</a>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="service.clusterId || '--'" placement="top">
                                                <p class="biz-text-wrapper">{{service.cluster_name ? service.cluster_name : '--'}}</p>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            {{service.namespace ? service.namespace : '--'}}
                                        </td>
                                        <td>
                                            {{service.source_type ? service.source_type : '--'}}
                                        </td>
                                        <td>
                                            {{service.updateTime ? formatDate(service.updateTime) : '--'}}
                                        </td>
                                        <td>
                                            {{service.createTime ? formatDate(service.createTime) : '--'}}
                                        </td>
                                        <td>
                                            {{service.updator ? service.updator : '--'}}
                                        </td>
                                        <td>
                                            <template v-if="service.can_update">
                                                <a href="javascript:void(0);" :class="['bk-text-button']" @click="showUpdateServicePanel(service)">{{$t('更新')}}</a>
                                            </template>

                                            <template v-else>
                                                <bk-tooltip :content="service.can_update_msg" placement="left">
                                                    <a href="javascript:void(0);" :class="['bk-text-button is-disabled']">{{$t('更新')}}</a>
                                                </bk-tooltip>
                                            </template>

                                            <template v-if="service.can_delete">
                                                <a href="javascript:void(0);" :class="['bk-text-button ml15']" @click="removeService(service)">{{$t('删除')}}</a>
                                            </template>
                                            <template v-else>
                                                <bk-tooltip :content="service.can_delete_msg" placement="left" style="margin-left: 15px;">
                                                    <a href="javascript:void(0);" :class="['bk-text-button is-disabled']">{{$t('删除')}}</a>
                                                </bk-tooltip>
                                            </template>

                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="9">
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
                            @page-change="pageChangeHandler">
                        </bk-paging>
                        <div class="already-selected-nums" v-if="alreadySelectedNums">{{$t('已选')}} {{alreadySelectedNums}} {{$t('条')}}</div>
                    </div>
                </div>
            </template>

            <bk-sideslider
                v-if="curServiceDetail"
                :quick-close="false"
                :is-show.sync="updateServiceSliderConf.isShow"
                :title="updateServiceSliderConf.title"
                :width="'700'">
                <div class="p30 pr10" slot="content" v-bkloading="{ isLoading: isDetailLoading }">
                    <div class="bk-form bk-form-vertical">
                        <div class="bk-form-item">
                            <label class="bk-label">{{$t('名称')}}：</label>
                            <div class="bk-form-content">
                                <input
                                    type="text"
                                    class="bk-form-input"
                                    placeholder="请输入"
                                    v-model="curServiceDetail.name"
                                    disabled="disabled"
                                    style="width: 600px;" />
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">{{$t('关联应用')}}：</label>
                            <div class="bk-form-content" style="width: 600px;">
                                <bk-selector
                                    :placeholder="$t('请选择要关联的Application')"
                                    :setting-key="'app_id'"
                                    :multi-select="true"
                                    :display-key="'app_name'"
                                    :selected.sync="curServiceDetail.config.webCache.link_app"
                                    :list="applicationList"
                                    :init-prevent-trigger="true"
                                    :is-link="true"
                                    @item-selected="selectAppsHandler">
                                </bk-selector>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">{{$t('权重设置')}}(%)：<p :class="['biz-tip', { 'bk-danger': isWeightError }]">{{curTotalPercent}}%</p></label>
                            <div class="bk-form-content">
                                <template v-if="curServiceDetail.config.webCache.link_app_weight.length">
                                    <div class="bk-form-input-group is-addon-left mr10" v-for="(app, index) in curServiceDetail.config.webCache.link_app_weight" :key="index">
                                        <span class="input-group-addon">
                                            {{app.name}}
                                        </span>

                                        <bk-number-input
                                            :value.sync="app.weight"
                                            :min="0"
                                            :max="100"
                                            :hide-operation="true"
                                            :ex-style="{ 'width': '25px' }"
                                            :placeholder="$t('输入')"
                                            @change="checkTotalPercent">
                                        </bk-number-input>
                                    </div>

                                </template>
                                <template v-else>
                                    <p class="mt5">{{$t('请关联相应的Application')}}</p>
                                </template>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">{{$t('Service类型')}}：</label>
                            <div class="bk-form-content">
                                <bk-selector
                                    style="width: 600px;"
                                    :disabled="true"
                                    :placeholder="$t('请选择')"
                                    :setting-key="'id'"
                                    :display-key="'name'"
                                    :selected.sync="curServiceDetail.config.spec.type"
                                    :list="serviceTypeList">
                                </bk-selector>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">IP：</label>
                            <div class="bk-form-content" style="width: 600px;">
                                <input type="text" class="bk-form-input" :placeholder="$t('请输入')" disabled :value="curServiceDetail.config.spec.clusterIP ? curServiceDetail.config.spec.clusterIP.join(',') : '--'">
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">{{$t('端口映射')}}：</label>
                            <div class="bk-form-content">
                                <div class="biz-keys-list mb10">
                                    <template v-if="curServiceDetail.config.webCache.link_app.length">
                                        <template v-if="appPortList.length && curServicePortMap.length">
                                            <table class="biz-simple-table">
                                                <thead>
                                                    <tr>
                                                        <th style="width: 100px;">{{$t('端口名称')}}</th>
                                                        <th style="width: 90px;">{{$t('协议')}}</th>
                                                        <th style="width: 90px;">{{$t('目标端口')}}</th>
                                                        <th style="width: 90px;">{{$t('服务端口')}}</th>
                                                        <th style="width: 100px;">{{$t('域名')}}</th>
                                                        <th style="width: 90px;">{{$t('路径')}}</th>
                                                        <th></th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr v-for="(port, index) in curServicePortMap" :key="index">
                                                        <td>
                                                            <bk-selector
                                                                :placeholder="$t('端口名称')"
                                                                :setting-key="'name'"
                                                                :display-key="'name'"
                                                                :selected.sync="port.name"
                                                                :filter-list="curServicePortList"
                                                                :list="appPortList"
                                                                :allow-clear="true"
                                                                :init-prevent-trigger="true"
                                                                :is-link="true"
                                                                style="width: 100px;"
                                                                @clear="clearPortHandler(port)"
                                                                @item-selected="selectPortHandler(port)">
                                                            </bk-selector>
                                                        </td>
                                                        <td>
                                                            <input type="text" class="bk-form-input" disabled :value="getProtocalByName(port.name)" style="width: 90px;" />
                                                        </td>
                                                        <td>
                                                            <input type="text" class="bk-form-input" disabled :value="getTargetPortByName(port.name)" style="width: 90px;" />
                                                        </td>
                                                        <td>
                                                            <bk-number-input
                                                                :value.sync="port.servicePort"
                                                                :min="1"
                                                                :max="65535"
                                                                :hide-operation="true"
                                                                :ex-style="{ 'width': '90px' }"
                                                                :placeholder="$t('服务端口')">
                                                            </bk-number-input>
                                                        </td>
                                                        <td>
                                                            <input type="text" class="bk-form-input" placeholder="域名" v-model="port.domainName" :disabled="port.protocol !== 'HTTP'" style="width: 100px;" />
                                                        </td>
                                                        <td>
                                                            <input type="text" class="bk-form-input" :placeholder="$t('路径')" style="width: 90px;" v-model="port.path" :disabled="port.protocol !== 'HTTP'" />
                                                        </td>
                                                        <td>
                                                            <button class="action-btn" @click.stop.prevent="addPort" v-show="curServicePortMap.length < appPortList.length">
                                                                <i class="bk-icon icon-plus"></i>
                                                            </button>
                                                            <button class="action-btn" @click.stop.prevent="removePort(port, index)" v-show="curServicePortMap.length > 1">
                                                                <i class="bk-icon icon-minus"></i>
                                                            </button>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </template>
                                        <template v-else>
                                            <p class="mt5">
                                                <router-link :to="{ name: 'mesosTemplatesetApplication', params: { templateId: curServiceDetail.template_id } }" class="bk-text-button">{{$t('点此')}}</router-link>{{$t('去模板集配置端口映射信息')}}
                                            </p>
                                        </template>
                                    </template>
                                    <template v-else>
                                        <p class="mt5">{{$t('请关联相应的Application')}}</p>
                                    </template>
                                </div>
                            </div>
                        </div>
                        <!-- mesos service 现阶段不允许随便更新label及关联lb，需要禁用掉相关内容更新 -->
                        <div class="bk-form-item" style="display: none;">
                            <label class="bk-label">{{$t('标签管理')}}：</label>
                            <div class="bk-form-content">
                                <bk-keyer
                                    :key-list.sync="curLabelList"
                                    ref="labelKeyer"
                                    @change="updateLabelList">
                                </bk-keyer>
                            </div>
                        </div>
                        <!-- mesos service 现阶段不允许随便更新label及关联lb，需要禁用掉相关内容更新 -->
                        <div class="bk-form-item" style="display: none;">
                            <div class="bk-form-content" style="margin-left: 130px">
                                <label class="bk-form-checkbox">
                                    <input
                                        type="checkbox"
                                        v-model="curServiceDetail.config.isLinkLoadBalance"
                                        :disabled="isLoadBalanceEdited" />
                                    <i class="bk-checkbox-text">{{$t('关联LoadBalance')}}</i>
                                </label>
                                <span class="biz-tip ml5 bk-danger" style="display: inline-block;" v-if="curServiceDetail.config.isLinkLoadBalance && !loadBalanceList.length && !isDetailLoading">{{$t('没有相关联的 LoadBalance，请先到 网络 -> LoadBalance 页面关联')}}!</span>
                                <div style="width: 360px;">
                                    <bk-selector
                                        v-if="curServiceDetail.config.isLinkLoadBalance"
                                        :placeholder="$t('请选择')"
                                        :disabled="isLoadBalanceEdited"
                                        :setting-key="'lb_name'"
                                        :display-key="'lb_name'"
                                        :selected.sync="curServiceDetail.lb_name"
                                        :list="loadBalanceList">
                                    </bk-selector>
                                </div>
                            </div>
                        </div>
                        <!-- mesos service 现阶段不允许随便更新label及关联lb，需要禁用掉相关内容更新 -->
                        <div class="bk-form-item" v-if="curServiceDetail.config.isLinkLoadBalance" style="display: none;">
                            <label class="bk-label" style="width: 130px;">{{$t('负载均衡算法')}}：</label>
                            <div class="bk-form-content" style="margin-left: 130px;">
                                <div class="bk-dropdown-box" style="width: 360px;">
                                    <bk-selector
                                        :placeholder="$t('请选择')"
                                        :disabled="isLoadBalanceEdited"
                                        :setting-key="'id'"
                                        :display-key="'name'"
                                        :selected.sync="algorithmIndex"
                                        :list="algorithmList"
                                        @item-selected="selectAlgorithmHandler">
                                    </bk-selector>
                                </div>
                            </div>
                        </div>
                        <div class="bk-form-item mt25">
                            <button :class="['bk-button bk-primary', { 'is-loading': isDetailSaving }]" @click.stop.prevent="saveServiceDetail">{{$t('保存并更新')}}</button>
                            <button class="bk-button bk-default" @click.stop.prevent="hideServiceSlider">{{$t('取消')}}</button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>

            <bk-sideslider
                v-if="curService"
                :quick-close="true"
                :is-show.sync="serviceSlider.isShow"
                :title="serviceSlider.title"
                :width="'800'">
                <div class="p30" slot="content" v-bkloading="{ isLoading: isEndpointLoading }">
                    <p class="data-title">
                        {{$t('基础信息')}}
                    </p>
                    <div class="biz-metadata-box">
                        <div class="data-item" style="width: 260px;">
                            <p class="key">{{$t('选择器')}}：</p>
                            <p class="value" v-bktooltips="{ direction: 'top', content: selector }">
                                {{selector}}
                            </p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('类型')}}：</p>
                            <p class="value">{{curService.data.spec.type}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">Service IP：</p>
                            <p class="value">{{curService.data.spec && curService.data.spec.clusterIP ? curService.data.spec.clusterIP.join(',') : '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">Service Domain：</p>
                            <p class="value">--</p>
                        </div>
                    </div>
                    <p class="data-title">
                        {{$t('端口映射')}}
                    </p>
                    <table class="bk-table biz-data-table">
                        <thead>
                            <tr>
                                <th>{{$t('端口索引')}}</th>
                                <th>{{$t('服务端口')}}</th>
                                <th>{{$t('目标端口')}}</th>
                                <th>{{$t('域名')}}</th>
                                <th>{{$t('路径')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curService.data.spec.ports.length">
                                <tr v-for="(port, index) in curService.data.spec.ports" :key="index">
                                    <td>{{port.name ? port.name : '--'}}</td>
                                    <td>{{port.servicePort ? port.servicePort : '--'}}</td>
                                    <td>
                                        {{port.targetPort ? port.targetPort : '--'}}
                                    </td>
                                    <td>
                                        {{port.domainName ? port.domainName : '--'}}
                                    </td>
                                    <td>
                                        {{port.path ? port.path : '--'}}
                                    </td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="5">
                                        <div class="biz-app-list">
                                            <div class="bk-message-box" style="min-height: auto;">
                                                <p class="message empty-message" style="margin: 30px; font-size: 14px;">{{$t('无数据')}}</p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <p class="data-title">
                        Endpoints
                    </p>
                    <table class="bk-table biz-data-table">
                        <thead>
                            <tr>
                                <th>{{$t('名称')}}</th>
                                <!-- <th>状态</th> -->
                                <th>Pod IP</th>
                                <th>Node IP</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="endpoints.length">
                                <tr v-for="(point, index) in endpoints" :key="index">
                                    <td>{{point.targetRef.name ? point.targetRef.name : '--'}}</td>
                                    <!-- <td>Running</td> -->
                                    <td>
                                        {{point.containerIP ? point.containerIP : '--'}}
                                    </td>
                                    <td>
                                        {{point.nodeIP ? point.nodeIP : '--'}}
                                    </td>
                                </tr>
                            </template>

                            <template v-else>
                                <tr>
                                    <td colspan="4">
                                        <div class="biz-app-list">
                                            <div class="bk-message-box" style="min-height: auto;">
                                                <p class="message empty-message" style="margin: 30px; font-size: 14px;">{{$t('无数据')}}</p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <div class="actions">
                        <span class="show-labels-btn bk-button bk-button-small bk-primary">{{$t('标签')}}</span>
                    </div>
                    <div class="point-box">
                        <template v-if="labelList.length">
                            <ul class="key-list">
                                <li v-for="(label, index) in labelList" :key="index">
                                    <span class="key">{{label[0]}}</span>
                                    <span class="value">{{label[1]}}</span>
                                </li>
                            </ul>
                        </template>
                        <template v-else>
                            <div class="bk-message-box" style="min-height: auto;">
                                <p class="message empty-message" style="margin: 30px; font-size: 14px;">{{$t('无数据')}}</p>
                            </div>
                        </template>
                    </div>
                </div>
            </bk-sideslider>

            <bk-dialog
                :is-show="batchDialogConfig.isShow"
                :width="550"
                :has-header="false"
                :quick-close="false"
                @confirm="deleteServices(batchDialogConfig.data)"
                @cancel="batchDialogConfig.isShow = false">
                <div slot="content">
                    <div class="biz-batch-wrapper">
                        <p class="batch-title">{{$t('确定要删除以下Service？')}}</p>
                        <ul class="batch-list">
                            <li v-for="(item, index) of batchDialogConfig.list" :key="index">{{item}}</li>
                        </ul>
                    </div>
                </div>
            </bk-dialog>
        </div>
    </div>
</template>

<script>
    import mixin from './mixin'
    import { catchErrorHandler, formatDate } from '@open/common/util'

    export default {
        mixins: [mixin],
        data () {
            return {
                formatDate: formatDate,
                isInitLoading: true,
                isPageLoading: false,
                exceptionCode: null,
                isEndpointLoading: true,
                searchKeyword: '',
                searchScope: '',
                curPageData: [],
                applicationList: [],
                appIds: [],
                curService: null,
                curVersion: 0,
                curServiceDetail: null,
                isDetailLoading: true,
                curTotalPercent: 0,
                isLoadBalanceEdited: false,
                isDetailSaving: false,
                statusTimer: [],
                pageConf: {
                    total: 0,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                isWeightError: true,
                serviceSlider: {
                    title: '',
                    isShow: false
                },
                updateServiceSliderConf: {
                    title: this.$t('更新Service'),
                    isShow: false
                },
                isLabelsShow: false,
                serviceTypeList: [
                    {
                        id: 'ClusterIP',
                        name: 'ClusterIP'
                    },
                    {
                        id: 'None',
                        name: 'None'
                    }
                ],
                serviceType: -1,
                ports: [
                    {
                        name: '',
                        protocol: 'http',
                        nodePort: '',
                        domainName: '',
                        path: '',
                        servicePort: ''
                    }
                ],
                protocolIndex: -1,
                protocolList: [
                    {
                        id: 'HTTP',
                        name: 'HTTP'
                    },
                    {
                        id: 'TCP',
                        name: 'TCP'
                    },
                    {
                        id: 'UDP',
                        name: 'UDP'
                    }
                ],
                appPortList: [],
                algorithmList: [
                    {
                        id: 'roundrobin',
                        name: 'roundrobin'
                    },
                    {
                        id: 'source',
                        name: 'source'
                    },
                    {
                        id: 'leastconn',
                        name: 'leastconn'
                    }
                ],
                curServicePortMap: [],
                algorithmIndex: -1,
                loadBalanceList: [],
                alreadySelectedNums: 0
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            curServicePortList () {
                const results = []
                const ports = this.curServicePortMap
                ports.forEach(item => {
                    results.push(item.name)
                })
                return results
            },
            isClusterDataReady () {
                return this.$store.state.cluster.isClusterDataReady
            }
        },
        watch: {
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
                            
                            this.getServiceList()
                        }, 1000)
                    }
                }
            }
        },
        created () {
            this.initPageConf()
            // this.getServiceList()
        },
        beforeDestroy () {
            this.serviceList = []
        },
        beforeRouteLeave () {
            this.serviceList = []
        },
        methods: {
            /**
             * service兼容处理
             * @param  {object} service sertice
             */
            formatService (service) {
                // 数据兼容处理
                if (!service.app_id) {
                    service.app_id = {}
                }

                if (!service.config.webCache) {
                    service.config.webCache = {}
                }

                if (!service.config.webCache.link_app) {
                    service.config.webCache.link_app = []
                    service.config.webCache.link_app_weight = []
                }

                if (!service.config.spec.ports.length) {
                    service.config.spec.ports.push({
                        'name': '',
                        'protocol': 'http',
                        'domainName': '',
                        'path': '',
                        'servicePort': ''
                    })
                }
            },

            /**
             * 显示更新侧面板
             * @param  {object} service service
             */
            async showUpdateServicePanel (service) {
                if (!service.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: service.namespace_id,
                        resource_name: service.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                const projectId = this.projectId
                const namespace = service.namespace
                const clusterId = service.clusterId
                const serviceId = service.resourceName

                this.curService = service
                this.isDetailLoading = true
                this.updateServiceSliderConf.isShow = true

                try {
                    const res = await this.$store.dispatch('network/getServiceDetail', {
                        projectId,
                        namespace,
                        clusterId,
                        serviceId
                    })
                    const service = res.data.service[0]
                    const appIds = []

                    service.config.webCache.link_app_weight.forEach(item => {
                        appIds.push(item.id)
                    })

                    this.formatService(service)

                    this.isLoadBalanceEdited = service.config.isLinkLoadBalance
                    this.curServiceDetail = service
                    this.curVersion = service.version
                    this.getApplications(this.curVersion)
                    this.getLoadBalanceList(service.namespace_id)
                    this.updateServiceSliderConf.isShow = true
                    this.checkTotalPercent()
                    this.getPorts(appIds)
                    this.curServicePortMap = this.curServiceDetail.config.spec.ports
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.updateServiceSliderConf.isShow = false
                } finally {
                    this.isDetailLoading = false
                }
            },

            /**
             * 选择端口
             * @param  {[type]} port [description]
             * @return {[type]}      [description]
             */
            selectPortHandler (port) {
                const name = port.name
                this.appPortList.forEach(item => {
                    if (item.name === name) {
                        port.protocol = item.protocol
                        port.nodePort = item.target_port

                        // 清空
                        port.domainName = ''
                        port.path = ''
                        port.servicePort = ''
                    }
                })
            },

            /**
             * 清空端口数据
             * @param  {object} port port
             */
            clearPortHandler (port) {
                port.id = ''
                port.name = ''
                port.protocol = ''
                port.nodePort = ''
                port.domainName = ''
                port.path = ''
                port.servicePort = ''
            },

            /**
             * 添加端口映射
             */
            addPort () {
                const ports = this.curServicePortMap
                ports.push({
                    'name': '',
                    'protocol': 'http',
                    'domainName': '',
                    'path': '',
                    'servicePort': ''
                })
            },

            /**
             * 删除端口映射
             * @param  {object} port  端口
             * @param  {number} index 索引
             */
            removePort (port, index) {
                const ports = this.curServicePortMap
                ports.splice(index, 1)
            },

            /**
             * 关联应用回调处理
             * @param  {number} index 应用索引
             * @param  {object} data  应用
             */
            selectAppsHandler (index, data) {
                const appIds = []
                this.curServiceDetail.app_id = {}
                this.curServiceDetail.config.webCache.link_app_weight = []
                data.forEach(item => {
                    appIds.push(item.app_id)
                    this.curServiceDetail.config.webCache.link_app_weight.push({
                        id: item.app_id,
                        name: item.app_name,
                        weight: 0
                    })
                })
                this.getPorts(appIds)
                this.checkTotalPercent()
            },

            /**
             * 获取协议
             * @param  {string} name 协议名称
             * @return {string} protocol
             */
            getProtocalByName (name) {
                const result = this.appPortList.find(item => item.name === name)
                return result ? result.protocol : ''
            },

            /**
             * 获取目标端口
             * @param  {string} name 端口名称
             * @return {string} target_port
             */
            getTargetPortByName (name) {
                const result = this.appPortList.find(item => item.name === name)
                return result ? result.target_port : ''
            },

            /**
             * 获取应用的端口列表
             * @param  {array} apps 应用id数组
             */
            async getPorts (apps) {
                const projectId = this.projectId
                const version = this.curVersion

                try {
                    const res = await this.$store.dispatch('network/getPortsByApps', { projectId, version, apps })
                    const ports = res.data.filter(item => {
                        return item.name && item.protocol && item.target_port
                    })
                    const keys = []

                    ports.forEach(port => {
                        keys.push(port.name)
                        port.domainName = ''
                        port.path = ''
                        port.servicePort = ''
                    })

                    this.appPortList.splice(0, this.appPortList.length, ...ports)

                    // 重新拉取后，再匹配用户已经选择的端口是否在列表中
                    this.curServiceDetail.config.spec.ports.filter(item => {
                        if (!item.name) {
                            return true
                        } else if (keys.includes(item.name)) {
                            return true
                        } else {
                            return false
                        }
                    })

                    // 如果没数据，default：添加一项
                    if (!this.curServicePortMap.length) {
                        this.addPort()
                    }
                } catch (e) {
                    this.appPortList.splice(0, this.appPortList.length)
                }
            },

            /**
             * 检查权重是否满足100%
             * return {boolean} 是否符合
             */
            checkTotalPercent () {
                this.curTotalPercent = 0
                this.curServiceDetail.config.webCache.link_app_weight.forEach(item => {
                    this.curTotalPercent += item.weight
                })
                if (this.curTotalPercent !== 100) {
                    this.isWeightError = true
                    return false
                }
                this.isWeightError = false
                return true
            },

            /**
             * 获取LB列表
             * @param  {number} namespace 命名空间ID
             */
            async getLoadBalanceList (namespace) {
                const projectId = this.projectId
                this.loadBalanceList = []
                if (!namespace) return

                try {
                    const res = await this.$store.dispatch('network/getLoadBalanceByNamespace', { projectId, namespace })
                    this.loadBalanceList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取Applications
             * @param  {number} version 版本号
             */
            async getApplications (version) {
                this.applicationList = []
                const projectId = this.projectId

                try {
                    const res = await this.$store.dispatch('network/getApplicationsByVersion', { projectId, version })
                    this.applicationList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 显示service详情侧面板
             * @param  {object} service service
             * @param  {number} index 索引
             */
            async showServiceDetail (service, index) {
                if (!service.permissions.view) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: service.namespace_id,
                        resource_name: service.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.serviceSlider.title = service.resourceName
                this.curService = service
                this.serviceSlider.isShow = true
                this.getServiceData(service)
            },

            /**
             * 获取service列表
             */
            async getServiceList () {
                const projectId = this.projectId
                const params = {
                    cluster_id: this.searchScope
                }

                try {
                    this.isPageLoading = true
                    await this.$store.dispatch('network/getServiceList', {
                        projectId,
                        params
                    })
                    setTimeout(() => {
                        this.initPageConf()
                        this.curPageData = this.getDataByPage(this.pageConf.curPage)

                        // 如果有搜索关键字，继续显示过滤后的结果
                        if (this.searchKeyword) {
                            this.searchService()
                        }
                    }, 200)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isPageLoading = false
                        this.isInitLoading = false
                    }, 400)
                }
            },

            /**
             * 获取service
             * @param  {object} service service
             * @param  {number} index 索引
             */
            async getServiceData (service) {
                const projectId = this.projectId
                const clusterId = service.clusterId
                const namespace = service.namespace
                const name = service.resourceName

                this.isEndpointLoading = true

                try {
                    const res = await this.$store.dispatch('network/getEndpoints', {
                        projectId,
                        clusterId,
                        namespace,
                        name
                    })
                    if (res.data.length) {
                        const service = res.data[0]
                        this.curService.data.metadata.labels = service.data.metadata.labels
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isEndpointLoading = false
                }
            },

            /**
             * 清空搜索
             */
            clearSearch () {
                this.searchKeyword = ''
                this.searchService()
            },

            /**
             * 选择负载均衡回调
             * @param  {number} index 索引
             * @param  {object} data  数据
             */
            selectAlgorithmHandler (index, data) {
                if (!this.curServiceDetail.config.metadata.lb_labels) {
                    this.curServiceDetail.config.metadata.lb_labels = {}
                }
                this.curServiceDetail.config.metadata.lb_labels.BCSBALANCE = index
            },

            /**
             * 搜索service
             */
            searchService () {
                const keyword = this.searchKeyword.trim()
                const keyList = ['resourceName', 'namespace', 'cluster_name']
                let list = JSON.parse(JSON.stringify(this.$store.state.network.serviceList))
                const results = []

                if (this.searchScope) {
                    list = list.filter(item => {
                        return item.clusterId === this.searchScope
                    })
                }

                list.forEach(item => {
                    item.isChecked = false
                    for (const key of keyList) {
                        if (item[key].indexOf(keyword) > -1) {
                            results.push(item)
                            return true
                        }
                    }
                })

                this.serviceList.splice(0, this.serviceList.length, ...results)
                this.pageConf.curPage = 1
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.serviceList.length
                this.pageConf.total = total
                this.pageConf.curPage = 1
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
            },

            /**
             * 重新加载当面页数据
             * @return {[type]} [description]
             */
            reloadCurPage () {
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 获取分页数据
             * @param  {number} page 第几页
             * @return {object} data 数据
             */
            getDataByPage (page) {
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                this.isPageLoading = true
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.serviceList.length) {
                    endIndex = this.serviceList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.serviceList.slice(startIndex, endIndex)
            },

            /**
             * 页数改变回调
             * @param  {number} page 第几页
             */
            pageChangeHandler (page = 1) {
                // this.clearSelectServices()
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                // this.curPageData = JSON.parse(JSON.stringify(data))
                this.curPageData = data
            },

            /**
             * 更新Label列表
             * @param  {array} list 列表 [{key, value}...]
             * @param  {object} data 对象 {key:value...}
             */
            updateLabelList (list, data) {
                if (!this.curServiceDetail.config.webCache) {
                    this.curServiceDetail.config.webCache = {}
                }
                this.curServiceDetail.config.webCache.labelListCache = list
            },

            /**
             * 检查提交的数据
             * @return {boolean} true/false 是否合法
             */
            checkData () {
                const appId = this.curServiceDetail.config.webCache.link_app
                const pathReg = /\/((?!\.)[\w\d\-./~]+)+/

                if (!appId.length) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请关联相应的Application')
                    })
                    return false
                }

                if (!this.checkTotalPercent()) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('权重的值为大于等于0的整数，且所有权重相加为100')
                    })
                    return false
                }

                const ports = this.curServicePortMap

                // 端口映射检查
                for (const item of ports) {
                    if (item.name) {
                        if (!item.servicePort) {
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: this.$t('服务端口不能为空')
                            })
                            return false
                        }
                        if (parseInt(item.servicePort) < 1 || parseInt(item.servicePort) > 65535) {
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: this.$t('服务端口范围为1-65535')
                            })
                            return false
                        }
                        if (item.path && !pathReg.test(item.path)) {
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: this.$t('请填写正确的路径')
                            })
                            return false
                        }
                    }
                }

                if (this.curServiceDetail.config.isLinkLoadBalance && !this.curServiceDetail.lb_name) {
                    this.$bkMessage({
                        theme: 'error',
                        delay: 5000,
                        message: this.$t('请选择需要关联的LoadBalance')
                    })
                    return false
                }

                return true
            },

            /**
             * 格式化数据
             */
            formatData () {
                // 键值转换
                const labels = this.$refs.labelKeyer.getKeyObject()
                this.curServiceDetail.config.metadata.labels = labels

                this.curServiceDetail.app_id = {}
                this.curServiceDetail.config.webCache.link_app_weight.forEach(item => {
                    this.curServiceDetail.app_id[item.id] = item.weight
                })
                this.curServiceDetail.config.spec.ports = this.curServicePortMap
            },

            /**
             * 保存service
             */
            async saveServiceDetail () {
                if (this.checkData()) {
                    this.formatData()
                    const projectId = this.projectId
                    const clusterId = this.curServiceDetail.cluster_id
                    const namespace = this.curServiceDetail.namespace
                    const serviceId = this.curServiceDetail.name
                    const data = this.curServiceDetail

                    if (this.isDetailSaving) {
                        return false
                    }

                    if (!data.config.spec.clusterIP) {
                        data.config.spec.clusterIP = []
                    }

                    this.isDetailSaving = true

                    try {
                        await this.$store.dispatch('network/saveServiceDetail', {
                            projectId,
                            clusterId,
                            namespace,
                            serviceId,
                            data
                        })

                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('操作成功'),
                            hasCloseIcon: true,
                            delay: 3000
                        })
                        this.getServiceList()
                        this.updateServiceSliderConf.isShow = false
                    } catch (e) {
                        catchErrorHandler(e, this)
                    } finally {
                        this.isDetailSaving = false
                    }
                }
            },

            /**
             * 隐藏service侧面板
             */
            hideServiceSlider () {
                this.updateServiceSliderConf.isShow = false
            }
        }
    }
</script>

<style scoped>
    @import '../service.css';
</style>
