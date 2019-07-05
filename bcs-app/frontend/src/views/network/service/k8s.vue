<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-service-title">
                Service
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
                            <span>批量删除</span>
                        </button>
                        <button style="opacity: 0">
                            <span>.</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="'输入关键字，按Enter搜索'"
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="searchService"
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
                                            <input type="checkbox" name="check-all-user" :checked="isCheckCurPageAll" @click="toogleCheckCurPage" :disabled="!serviceList.length">
                                        </label>
                                    </th>
                                    <th style="padding-left: 30px;">Service名称</th>
                                    <th style="min-width: 100px;">所属集群</th>
                                    <th>命名空间</th>
                                    <th>来源</th>
                                    <th style="min-width: 100px;">更新时间</th>
                                    <th style="min-width: 100px;">创建时间</th>
                                    <th>更新人</th>
                                    <th style="width: 125px;">操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="serviceList.length">
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
                                                {{service.cluster_name ? service.cluster_name : '--'}}
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
                                                <a href="javascript:void(0);" :class="['bk-text-button']" @click="showUpdateServicePanel(service)">更新</a>
                                            </template>
                                            <template v-else>
                                                <bk-tooltip :content="service.can_update_msg" placement="left">
                                                    <a href="javascript:void(0);" :class="['bk-text-button is-disabled']">更新</a>
                                                </bk-tooltip>
                                            </template>
                                            <template v-if="service.can_delete">
                                                <a href="javascript:void(0);" :class="['bk-text-button ml15']" @click="removeService(service)">删除</a>
                                            </template>
                                            <template v-else>
                                                <bk-tooltip :content="service.can_delete_msg" placement="left" style="margin-left: 15px;">
                                                    <a href="javascript:void(0);" :class="['bk-text-button is-disabled']">删除</a>
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
                                                    <p class="message empty-message" v-if="!isInitLoading">无数据</p>
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
                            :total="pageConf.total"
                            :page-size="pageConf.pageSize"
                            @change="changePageSize">
                        </bk-page-counter>
                        <bk-paging
                            :cur-page.sync="pageConf.curPage"
                            :total-page="pageConf.totalPage"
                            @page-change="pageChangeHandler">
                        </bk-paging>
                        <div class="already-selected-nums" v-if="alreadySelectedNums">已选{{alreadySelectedNums}}条</div>
                    </div>
                </div>
            </template>

            <bk-sideslider
                v-if="curServiceDetail"
                :quick-close="false"
                :is-show.sync="updateServiceSliderConf.isShow"
                :title="updateServiceSliderConf.title"
                :width="'700'">
                <div class="p30" slot="content" v-bkloading="{ isLoading: isDetailLoading }" style="overflow: hidden;">
                    <div class="bk-form bk-form-vertical">
                        <div class="bk-form-item">
                            <label class="bk-label">名称：</label>
                            <div class="bk-form-content">
                                <input
                                    type="text"
                                    class="bk-form-input"
                                    placeholder="请输入"
                                    v-model="curServiceDetail.name"
                                    disabled style="width: 600px;" />
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">关联应用：</label>
                            <div class="bk-form-content" style="width: 600px;">
                                <bk-selector
                                    placeholder="请选择要关联的Application"
                                    :setting-key="'deploy_tag'"
                                    :multi-select="true"
                                    :display-key="'deploy_name'"
                                    :selected.sync="curServiceDetail.config.webCache.link_app"
                                    :list="applicationList"
                                    :init-prevent-trigger="true"
                                    :is-link="true"
                                    @item-selected="selectAppsHandler">
                                </bk-selector>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">关联标签：</label>
                            <div class="bk-form-content key-tip-wrapper" style="width: 705px;">
                                <ul class="key-list" v-if="appLabels.length && !isLabelsLoading">
                                    <li v-for="(label, index) in appLabels" @click="selectLabel(label)" :key="index">
                                        <span class="key">
                                            <label class="bk-form-checkbox bk-checkbox-small pb0 pt0">
                                                <input type="checkbox" name="linkapp" :checked="label.isSelected">
                                            </label>
                                        </span>
                                        <span class="value">{{label.key}}:{{label.value}}</span>
                                    </li>
                                </ul>
                                <div v-else-if="!isLabelsLoading" class="key-tip">
                                    {{curServiceDetail.config.webCache.link_app ? '关联的应用没有公共的标签（注：Key、Value都相同的标签为公共标签）' : '请先关联应用'}}
                                </div>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">Service类型：</label>
                            <div class="bk-form-content">
                                <bk-selector
                                    style="width: 360px;"
                                    :disabled="true"
                                    placeholder="请选择"
                                    :setting-key="'id'"
                                    :display-key="'name'"
                                    :selected.sync="curServiceDetail.config.spec.type"
                                    :list="serviceTypeList">
                                </bk-selector>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">端口映射：</label>
                            <div class="bk-form-content">
                                <div class="biz-keys-list mt10">
                                    <template v-if="curServiceDetail.config.webCache.link_app.length">
                                        <template v-if="appPortList.length && curServiceDetail.config.spec.ports.length">
                                            <table class="biz-simple-table">
                                                <thead>
                                                    <tr>
                                                        <th style="width: 100px;">端口名称</th>
                                                        <th style="width: 100px;">端口</th>
                                                        <th style="width: 120px;">协议</th>
                                                        <th style="width: 120px;">目标端口</th>
                                                        <th style="width: 100px;">NodePort</th>
                                                        <th></th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr v-for="(port, index) in curServiceDetail.config.spec.ports" :key="index">
                                                        <td>
                                                            <input type="text" class="bk-form-input" style="width: 100px;" placeholder="请输入" v-model="port.name">
                                                        </td>
                                                        <td>
                                                            <bk-number-input
                                                                :value.sync="port.port"
                                                                :min="1"
                                                                :max="65535"
                                                                :hide-operation="true"
                                                                :ex-style="{ 'width': '100px' }"
                                                                :placeholder="'请输入'">
                                                            </bk-number-input>
                                                        </td>
                                                        <td>
                                                            <bk-selector
                                                                placeholder="协议"
                                                                :setting-key="'id'"
                                                                :allow-clear="true"
                                                                :selected.sync="port.protocol"
                                                                :list="protocolList">
                                                            </bk-selector>
                                                        </td>
                                                        <td>
                                                            <!-- {{appPortList}} -->
                                                            <bk-selector
                                                                placeholder="请输入"
                                                                :setting-key="'name'"
                                                                :display-key="'name'"
                                                                :selected.sync="port.targetPort"
                                                                :allow-clear="true"
                                                                :filter-list="curServicePortList"
                                                                :is-link="true"
                                                                :init-prevent-trigger="true"
                                                                :list="appPortList"
                                                                @clear="clearPortHandler(port)">
                                                            </bk-selector>
                                                        </td>
                                                        <td>
                                                            <bk-number-input
                                                                :disabled="curServiceDetail.config.spec.type !== 'NodePort'"
                                                                :value.sync="port.nodePort"
                                                                :min="0"
                                                                :max="32767"
                                                                :hide-operation="true"
                                                                :ex-style="{ 'width': '100px' }"
                                                                :placeholder="'请输入'">
                                                            </bk-number-input>
                                                        </td>
                                                        <td>
                                                            <button class="action-btn" @click.stop.prevent="addPort" v-show="curServiceDetail.config.spec.ports.length < appPortList.length">
                                                                <i class="bk-icon icon-plus"></i>
                                                            </button>
                                                            <button class="action-btn" @click.stop.prevent="removePort(port, index)" v-show="curServiceDetail.config.spec.ports.length > 1">
                                                                <i class="bk-icon icon-minus"></i>
                                                            </button>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </template>
                                        <template v-else>
                                            <p class="mt5">
                                                <router-link :to="{ name: 'k8sTemplatesetDeployment', params: { templateId: curServiceDetail.template_id } }" class="bk-text-button">点此</router-link>去模板集配置端口映射信息
                                            </p>
                                        </template>
                                    </template>
                                    <template v-else>
                                        <p class="mt5">请关联相应的应用</p>
                                    </template>
                                </div>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label">标签管理：</label>
                            <div class="bk-form-content">
                                <bk-keyer :key-list.sync="curLabelList" ref="labelKeyer" @change="updateLabelList"></bk-keyer>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <label class="bk-label">备注管理：</label>
                            <div class="bk-form-content">
                                <bk-keyer :key-list.sync="curRemarkList" ref="labelKeyer" @change="updateRemarkList"></bk-keyer>
                            </div>
                        </div>

                        <div class="bk-form-item mt25">
                            <button :class="['bk-button bk-primary', { 'is-loading': isDetailSaving }]" @click.stop.prevent="saveServiceDetail">保存并更新</button>
                            <button class="bk-button bk-default" @click.stop.prevent="hideServiceSlider">取消</button>
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
                        基础信息
                    </p>
                    <div class="biz-metadata-box">
                        <div class="data-item" style="width: 260px;">
                            <p class="key">选择器：</p>
                            <p class="value" v-bktooltips="{ direction: 'top', content: selector }">
                                {{selector ? selector : '--'}}
                            </p>
                        </div>
                        <div class="data-item">
                            <p class="key">类型：</p>
                            <p class="value">{{curService.data.spec.type}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">Service IP：</p>
                            <p class="value">{{curService.data.spec && curService.data.spec.clusterIP ? curService.data.spec.clusterIP : '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">Service Domain：</p>
                            <p class="value">--</p>
                        </div>
                    </div>
                    <p class="data-title">
                        端口映射
                    </p>
                    <table class="bk-table biz-data-table">
                        <thead>
                            <tr>
                                <th>端口名称</th>
                                <th>端口</th>
                                <th>协议</th>
                                <th>目标端口</th>
                                <th>NodePort</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curService.data.spec.ports && curService.data.spec.ports.length">
                                <tr v-for="(port, index) in curService.data.spec.ports" :key="index">
                                    <td>{{port.name ? port.name : '--'}}</td>
                                    <td>{{port.port ? port.port : '--'}}</td>
                                    <td>
                                        {{port.protocol ? port.protocol : '--'}}
                                    </td>
                                    <td>
                                        {{port.targetPort ? port.targetPort : '--'}}
                                    </td>
                                    <td>
                                        {{port.nodePort ? port.nodePort : '--'}}
                                    </td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="5">
                                        <div class="biz-app-list">
                                            <div class="bk-message-box" style="min-height: auto;">
                                                <p class="message empty-message" style="margin: 30px; font-size: 14px;">无数据</p>
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
                                <th>名称</th>
                                <th>Pod IP</th>
                                <th>Node IP</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="endpoints.length">
                                <tr v-for="(point, index) in endpoints" :key="index">
                                    <td>{{point.targetRef.name ? point.targetRef.name : '--'}}</td>
                                    <td>
                                        {{point.ip ? point.ip : '--'}}
                                    </td>
                                    <td>
                                        {{point.nodeName ? getNodeIpByName(point.nodeName) : '--'}}
                                    </td>
                                </tr>
                            </template>

                            <template v-else>
                                <tr>
                                    <td colspan="4">
                                        <div class="biz-app-list">
                                            <div class="bk-message-box" style="min-height: auto;">
                                                <p class="message empty-message" style="margin: 30px; font-size: 14px;">无数据</p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <div class="actions">
                        <span class="show-labels-btn bk-button bk-button-small bk-primary">标签</span>
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
                                <p class="message empty-message" style="margin: 30px; font-size: 14px;">无数据</p>
                            </div>
                        </template>
                    </div>
                </div>
            </bk-sideslider>

            <bk-dialog
                :is-show="batchDialogConfig.isShow"
                :width="400"
                :has-header="false"
                :quick-close="false"
                @confirm="deleteServices(batchDialogConfig.data)"
                @cancel="batchDialogConfig.isShow = false">
                <div slot="content">
                    <div class="biz-batch-wrapper">
                        <p class="batch-title">确定要删除以下Service？</p>
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
                appLabels: [],
                appIds: [],
                curService: null,
                curVersion: 0,
                curServiceDetail: null,
                isDetailLoading: true,
                curTotalPercent: 0,
                isLoadBalanceEdited: false,
                isDetailSaving: false,
                isLabelsLoading: true,
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
                    title: '更新Service',
                    isShow: false
                },
                isLabelsShow: false,
                serviceTypeList: [
                    {
                        id: 'ClusterIP',
                        name: 'ClusterIP'
                    },
                    {
                        id: 'NodePort',
                        name: 'NodePort'
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
                loadBalanceList: []
            }
        },
        computed: {
            applicationList () {
                return this.$store.state.k8sTemplate.linkApplications
            },
            curRemarkList () {
                const list = []
                const annotations = this.curServiceDetail.config.metadata.annotations
                // 如果有缓存直接使用
                if (this.curServiceDetail.config.webCache && this.curServiceDetail.config.webCache.remarkListCache) {
                    return this.curServiceDetail.config.webCache.remarkListCache
                }
                for (const [key, value] of Object.entries(annotations)) {
                    list.push({
                        key: key,
                        value: value
                    })
                }
                if (!list.length) {
                    list.push({
                        key: '',
                        value: ''
                    })
                }
                return list
            },
            curServicePortList () {
                const results = []
                const ports = this.curServiceDetail.config.spec.ports
                ports.forEach(item => {
                    results.push(item.targetPort)
                })
                return results
            }
        },
        created () {
            this.initPageConf()
            this.getServiceList()
        },
        methods: {
            /**
             * 选择标签
             * @param  {object} labels 标签
             */
            selectLabel (labels) {
                labels.isSelected = !labels.isSelected
                this.curServiceDetail.config.webCache.link_labels = []
                this.curServiceDetail.config.selector = {}
                this.appLabels.forEach(label => {
                    if (label.isSelected) {
                        this.curServiceDetail.config.webCache.link_labels.push(label.id)
                        this.curServiceDetail.config.selector[label.key] = label.value
                    }
                })
            },

            /**
             * 通过nodeName获取nodeIP eg: ip-10-235-46-109-n-bcs-k8s-15007
             * @param {string} nodeName
             * @return {string} nodeIP
             */
            getNodeIpByName (nodeName) {
                const reg = /ip-(.+)-n\w*/
                const match = nodeName.match(reg)
                let ip = '--'
                if (match && match[1]) {
                    ip = match[1].replace(/-/g, '.')
                }
                return ip
            },

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
                    service.config.webCache = {
                        link_app: [],
                        link_labels: []
                    }
                }

                if (!service.config.webCache.link_app.length) {
                    service.config.webCache.link_app = []
                    service.deploy_tag_list.forEach(item => {
                        service.config.webCache.link_app.push(item)
                    })
                }

                if (!service.config.spec.ports) {
                    service.config.spec.ports = []
                }
                if (service.config.spec.ports && !service.config.spec.ports.length) {
                    service.config.spec.ports.push({
                        'id': '',
                        'name': '',
                        'port': '',
                        'protocol': 'TCP',
                        'targetPort': '',
                        'nodePort': ''
                    })
                } else {
                    service.config.spec.ports.forEach(port => {
                        if (!port.nodePort) {
                            port.nodePort = ''
                        }
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
                this.isDetailLoading = true
                this.curService = service
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

                    this.formatService(service)

                    service.config.webCache.link_app.forEach(item => {
                        appIds.push(item)
                    })

                    this.isLoadBalanceEdited = service.config.isLinkLoadBalance
                    this.curServiceDetail = service
                    this.curVersion = service.version
                    this.getApplications(this.curVersion)
                    this.updateServiceSliderConf.isShow = true
                    this.isDetailLoading = false
                    this.getPorts(appIds)
                    this.getLabels(appIds)
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.updateServiceSliderConf.isShow = false
                } finally {
                    this.isDetailLoading = false
                }
            },

            /**
             * 清空端口数据
             * @param  {object} port port
             */
            clearPortHandler (port) {
                port.targetPort = ''
            },

            /**
             * 添加端口映射
             */
            addPort () {
                const ports = this.curServiceDetail.config.spec.ports
                const port = {
                    'id': '',
                    'name': '',
                    'port': '',
                    'protocol': 'TCP',
                    'targetPort': '',
                    'nodePort': ''
                }
                ports.push(port)
            },

            /**
             * 删除端口映射
             * @param  {object} port  端口
             * @param  {number} index 索引
             */
            removePort (port, index) {
                const ports = this.curServiceDetail.config.spec.ports
                ports.splice(index, 1)
            },

            /**
             * 关联应用回调处理
             * @param  {number} index 应用索引
             * @param  {object} data  应用
             */
            selectAppsHandler (index, data) {
                this.getPorts(index)
                this.getLabels(index)
            },

            /**
             * 获取Labels
             * @param  {array} apps 应用ids
             */
            async getLabels (apps) {
                this.isLabelsLoading = true
                const projectId = this.projectId
                const version = this.curVersion

                try {
                    const res = await this.$store.dispatch('k8sTemplate/getLabelsByDeployments', {
                        projectId,
                        version,
                        apps
                    })

                    const labels = []
                    for (const key in res.data) {
                        const params = {
                            id: key + ':' + res.data[key],
                            key: key,
                            value: res.data[key],
                            isSelected: false
                        }
                        if (this.curServiceDetail.config.webCache.link_labels && this.curServiceDetail.config.webCache.link_labels.indexOf(params.id) > -1) {
                            params.isSelected = true
                        }
                        labels.push(params)
                    }
                    this.appLabels.splice(0, this.appLabels.length, ...labels)
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.appLabels.splice(0, this.appLabels.length)
                } finally {
                    this.isLabelsLoading = false
                }
            },

            /**
             * 获取应用的端口列表
             * @param  {array} apps 应用id数组
             */
            async getPorts (apps) {
                const projectId = this.projectId
                const version = this.curVersion

                try {
                    const res = await this.$store.dispatch('k8sTemplate/getPortsByDeployments', {
                        projectId,
                        version,
                        apps
                    })

                    const ports = res.data.filter(item => {
                        return item.name
                    })
                    const keys = []
                    let results = []
                    ports.forEach(port => {
                        keys.push(port.id)
                    })
                    this.appPortList.splice(0, this.appPortList.length, ...ports)

                    // 重新拉取后，再匹配用户已经选择的端口是否在列表中
                    results = this.curServiceDetail.config.spec.ports.filter(item => {
                        if (!item.id) {
                            return true
                        } else if (keys.includes(item.id)) {
                            return true
                        } else {
                            return false
                        }
                    })
                    this.curServiceDetail.config.spec.ports.splice(0, this.curServiceDetail.config.spec.ports.length, ...results)

                    // 如果没数据，default：添加一项
                    if (!this.curServiceDetail.config.spec.ports.length) {
                        this.addPort()
                    }
                } catch (e) {
                    this.curServiceDetail.config.spec.ports.splice(0, this.appPortList.length)
                }
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
                const projectId = this.projectId

                try {
                    await this.$store.dispatch('k8sTemplate/getAppsByVersion', { projectId, version })
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

                try {
                    await this.$store.dispatch('network/getServiceList', projectId)
                    this.clearSelectServices()
                    this.initPageConf()
                    if (this.pageConf.curPage > this.pageConf.totalPage) {
                        this.pageConf.curPage = this.pageConf.totalPage
                    }
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)

                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchScope || this.searchKeyword) {
                        this.searchService()
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
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
             * 搜索service
             */
            searchService () {
                const keyword = this.searchKeyword.trim()
                const keyList = ['resourceName', 'namespace']
                const results = []
                let list = JSON.parse(JSON.stringify(this.$store.state.network.serviceList))

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
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
            },

            /**
             * 重新加载当面页数据
             * @return {[type]} [description]
             */
            reloadCurPage () {
                this.initPageConf()
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
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
             * 更新备注列表
             * @param  {array} list 列表 [{key, value}...]
             * @param  {object} data 对象 {key:value...}
             */
            updateRemarkList (list, data) {
                if (!this.curServiceDetail.config.webCache) {
                    this.curServiceDetail.config.webCache = {}
                }
                this.curServiceDetail.config.webCache.remarkListCache = list
            },

            /**
             * 检查提交的数据
             * @return {boolean} true/false 是否合法
             */
            checkData () {
                const service = this.curServiceDetail
                let megPrefix = ''
                if (service.config.spec.type === 'NodePort' && !service.deploy_tag_list.length) {
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + '请选择要关联的应用',
                        delay: 3000
                    })
                    return false
                }

                // 端口映射检查
                const ports = service.config.spec.ports
                const serviceIp = service.config.spec.clusterIP
                if (serviceIp !== 'None') {
                    let hasPort = false
                    for (const item of ports) {
                        if (item.name && item.port && item.targetPort) {
                            hasPort = true
                        }
                    }
                    if (!hasPort) {
                        megPrefix += '端口映射：'
                        this.$bkMessage({
                            theme: 'error',
                            delay: 8000,
                            message: megPrefix + 'ClusterIP不为None时，请配置相应的端口映射！'
                        })
                        return false
                    }
                }

                for (const item of ports) {
                    if (item.name || item.port || item.targetPort) {
                        if (item.name && !/^[a-z]{1}[a-z0-9-]{0,29}$/.test(item.name)) {
                            megPrefix += '端口映射：'
                            this.$bkMessage({
                                theme: 'error',
                                delay: 8000,
                                message: megPrefix + '端口名称以小写字母开头，只能包含：小写字母、数字、连字符(-)，长度小于30个字符！'
                            })
                            return false
                        }
                        if (!item.port) {
                            megPrefix += '端口映射：'
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: megPrefix + '端口不能为空！'
                            })
                            return false
                        }
                        if (!item.protocol) {
                            megPrefix += '端口映射：'
                            this.$bkMessage({
                                theme: 'error',
                                delay: 5000,
                                message: megPrefix + '请选择协议！'
                            })
                            return false
                        }
                        if (item.nodePort || item.nodePort === 0) {
                            if (item.nodePort < 30000 || item.nodePort > 32767) {
                                megPrefix += '端口映射：'
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: megPrefix + 'NodePort的范围为30000-32767'
                                })
                                return false
                            }
                        }
                    }
                }

                return true
            },

            /**
             * 格式化数据
             */
            formatData () {
                const params = JSON.parse(JSON.stringify(this.curServiceDetail))
                if (params.config.webCache.labelListCache) {
                    const keys = {}
                    params.config.webCache.labelListCache.forEach(item => {
                        keys[item.key] = item.value
                    })
                    params.config.metadata.labels = keys
                }
                if (params.config.webCache.remarkListCache) {
                    const keys = {}
                    params.config.webCache.remarkListCache.forEach(item => {
                        keys[item.key] = item.value
                    })
                    params.config.metadata.annotations = keys
                }
                return params
            },

            /**
             * 保存service
             */
            async saveServiceDetail () {
                if (this.checkData()) {
                    const data = this.formatData()
                    const projectId = this.projectId
                    const clusterId = this.curServiceDetail.cluster_id
                    const namespace = this.curServiceDetail.namespace
                    const serviceId = this.curServiceDetail.name

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
                            message: '操作成功！',
                            hasCloseIcon: true,
                            delay: 3000
                        })
                        this.getServiceList()
                        this.updateServiceSliderConf.isShow = false
                        this.isDetailSaving = false
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
