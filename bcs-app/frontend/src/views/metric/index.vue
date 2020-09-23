<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-app-title">
                <!-- Metric管理{{$t('test', { vari1: 1, vari2: 2 })}} -->
                {{$t('Metric管理')}}
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
                <div class="biz-panel-header biz-metric-manage-create" style="padding: 27px 30px 22px 20px;">
                    <div class="left">
                        <bk-button type="primary" :title="$t('新建Metric')" @click="showCreateMetric">
                            <i class="bk-icon icon-plus"></i>
                            <span class="text">{{$t('新建Metric')}}</span>
                        </bk-button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="$t('输入名称，按Enter搜索')"
                            :search-key.sync="searchKeyWord"
                            @search="searchMetric"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>
                <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                    <table class="bk-table has-table-hover biz-table biz-metric-manage-table">
                        <thead>
                            <tr>
                                <th style="width: 260px; text-align: left;padding-left: 36px;">
                                    {{$t('名称')}}
                                </th>
                                <th style="width: 100px;">{{$t('端口')}}</th>
                                <th style="width: 350px;">URI</th>
                                <th style="width: 270px;">{{$t('采集频率(秒/次)')}}</th>
                                <th style="width: 600px; text-align: right; padding-right: 100px;">{{$t('操作')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curPageData.length">
                                <tr v-for="(item, index) in curPageData" :key="index">
                                    <td style="text-align: left;padding-left: 36px;">
                                        <bk-tooltip placement="top" :delay="500">
                                            <p class="item-name biz-table-title">{{item.name || '--'}}</p>
                                            <template slot="content">
                                                <p style="text-align: left; white-space: normal;word-break: break-all;" cla>{{item.name || '--'}}</p>
                                            </template>
                                        </bk-tooltip>
                                    </td>
                                    <td>
                                        {{item.port || '--'}}
                                    </td>
                                    <td>
                                        <bk-tooltip placement="top" :delay="500">
                                            <p class="item-uri">{{item.uri || '--'}}</p>
                                            <template slot="content">
                                                <p style="text-align: left; white-space: normal;word-break: break-all;">{{item.uri || '--'}}</p>
                                            </template>
                                        </bk-tooltip>
                                    </td>
                                    <td>{{item.frequency || '--'}}</td>
                                    <td class="act">
                                        <a href="javascript:void(0);" class="bk-text-button" @click="checkMetricInstance(item)">{{$t('查看实例')}}</a>
                                        <template v-if="!item.status || item.status === 'normal'">
                                            <a href="javascript:void(0);" class="bk-text-button" @click="pauseAndResume(item, 'pause', [])">{{$t('暂停')}}</a>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="editMetric(item)">{{$t('更新')}}</a>
                                        </template>
                                        <template v-else>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="pauseAndResume(item, 'resume', [])">{{$t('恢复')}}</a>
                                        </template>
                                        <a href="javascript:void(0);" class="bk-text-button" @click="deleteMetric(item)">{{$t('删除')}}</a>
                                        <!-- 数据平台不能直接跳转到字段设置页面，先去掉 -->
                                        <!-- <a class="bk-text-button" href="javascript:void(0)" @click="go(item, item.uri_fields_info)" target="_blank">字段设置</a> -->
                                        <a class="bk-text-button" href="javascript:void(0)" @click="go(item, item.uri_data_clean)" target="_blank">{{$t('数据清洗')}}</a>
                                    </td>
                                </tr>
                            </template>
                            <template v-else-if="!curPageData.length && !isInitLoading">
                                <tr class="no-hover">
                                    <td colspan="5">
                                        <div class="bk-message-box">
                                            <p class="message empty-message">{{$t('无数据')}}</p>
                                        </div>
                                    </td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr class="no-hover">
                                    <td colspan="5">
                                        <div class="bk-message-box">
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
                </div>
            </template>
        </div>

        <bk-sideslider
            :is-show.sync="createMetricConf.isShow"
            :title="createMetricConf.title"
            :width="createMetricConf.width"
            :quick-close="false"
            class="biz-metric-manage-create-sideslider"
            @hidden="hideCreateMetric">
            <template slot="content">
                <div class="wrapper" style="position: relative;" v-bkloading="{ isLoading: isCreatingOrEditing, opacity: 0.8, title: creatingOrEditingStr }">
                    <form class="bk-form bk-form-vertical create-form">
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <label class="bk-label label">{{$t('名称')}}：<span class="red">*</span></label>
                                <div class="bk-form-content">
                                    <input type="text" v-model="createParams.name" class="bk-form-input text-input-half" :placeholder="$t('请输入')" maxlength="253" />
                                </div>
                            </div>
                            <div class="right">
                                <label class="bk-label label">{{$t('端口')}}：<span class="red">*</span></label>
                                <div class="bk-form-content">
                                    <bk-number-input
                                        class="text-input-half"
                                        :value.sync="createParams.port"
                                        :min="1"
                                        :max="65535"
                                        :debounce-timer="0"
                                        :placeholder="$t('请输入')">
                                    </bk-number-input>
                                </div>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label label">
                                URI：<span class="red">*</span>
                            </label>
                            <div class="bk-form-content">
                                <input type="text" v-model="createParams.url" class="bk-form-input text-input" :placeholder="$t('请输入')" />
                            </div>
                        </div>
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <label class="bk-label label">{{$t('采集频率')}}：<span class="red">*</span></label>
                                <div class="bk-form-content">
                                    <bk-number-input
                                        class="text-input-half has-suffix"
                                        :value.sync="createParams.frequency"
                                        :min="0"
                                        :max="999999999"
                                        :debounce-timer="0"
                                        :placeholder="$t('请输入')">
                                    </bk-number-input>
                                    <span class="suffix">
                                        {{$t('秒/次')}}
                                    </span>
                                </div>
                            </div>
                            <div class="right">
                                <label class="bk-label label">{{$t('单次采集超时时间（秒）')}}：<span class="red">*</span></label>
                                <div class="bk-form-content">
                                    <bk-number-input
                                        class="text-input-half has-suffix"
                                        :value.sync="createParams.timeout"
                                        :min="0"
                                        :debounce-timer="0"
                                        :placeholder="$t('请输入')">
                                    </bk-number-input>
                                    <span class="suffix">
                                        {{$t('秒')}}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="bk-form-item prometheus-item">
                            <div class="prometheus-header">
                                <label class="bk-label label">{{$t('Prometheus格式设置')}}</label>
                                <label class="bk-form-checkbox">
                                    <input type="checkbox" name="metric-type" value="prometheus" v-model="createParams.metricType">
                                </label>
                            </div>

                            <div class="prometheus-keys" v-show="createParams.metricType">
                                <label class="bk-label label">
                                    {{$t('附加数据')}}：
                                </label>
                                <bk-keyer
                                    class="prometheus-keylist"
                                    ref="constKeyer"
                                    :key-placeholder="$t('键')"
                                    :value-placeholder="$t('值')"
                                    :tip="$t('小提示：同时粘贴多行“键=值”的文本会自动添加多行记录')"
                                    :key-list.sync="createParams.constLabels"
                                ></bk-keyer>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label label">
                                Http Header：
                            </label>
                            <div class="bk-form-content">
                                <bk-keyer
                                    class="http-header"
                                    ref="labelKeyer"
                                    :key-list.sync="createParams.httpHeader"
                                    :key-placeholder="$t('键')"
                                    :value-placeholder="$t('值')"
                                    :tip="$t('小提示：同时粘贴多行“键=值”的文本会自动添加多行记录')"
                                ></bk-keyer>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label label">Http Method：</label>
                            <div class="bk-form-content scroll-order-form-item">
                                <label class="bk-form-radio">
                                    <input type="radio" value="GET" name="radio" checked="checked" v-model="createParams.httpMethod">
                                    <i class="bk-radio-text">GET</i>
                                </label>
                                <label class="bk-form-radio" style="margin-right: 7px;">
                                    <input type="radio" value="POST" name="radio" v-model="createParams.httpMethod">
                                    <i class="bk-radio-text">POST</i>
                                </label>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label label">
                                {{$t('Http参数')}}：
                            </label>
                            <div class="bk-form-content">
                                <template v-if="createParams.httpMethod === 'GET'">
                                    <bk-keyer
                                        class="http-header"
                                        ref="labelKeyer"
                                        :key-list.sync="createParams.httpBodyGet"
                                        :key-placeholder="$t('键')"
                                        :value-placeholder="$t('值')"
                                        :tip="$t('小提示：同时粘贴多行“键=值”的文本会自动添加多行记录')"
                                    ></bk-keyer>
                                </template>
                                <template v-else>
                                    <textarea v-model="createParams.httpBodyPost" class="bk-form-textarea" :placeholder="$t('请输入')"></textarea>
                                </template>
                            </div>
                        </div>
                        <div class="action-inner">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="confirmCreateMetric">
                                {{$t('创建')}}
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideCreateMetric">
                                {{$t('取消')}}
                            </button>
                        </div>
                    </form>
                </div>
            </template>
        </bk-sideslider>

        <bk-sideslider
            :is-show.sync="editMetricConf.isShow"
            :title="editMetricConf.title"
            :width="editMetricConf.width"
            :quick-close="false"
            class="biz-metric-manage-create-sideslider"
            @hidden="hideEditMetric">
            <template slot="content">
                <div class="wrapper" style="position: relative;" v-bkloading="{ isLoading: isCreatingOrEditing, opacity: 0.8, title: creatingOrEditingStr }">
                    <form class="bk-form bk-form-vertical create-form">
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <label class="bk-label label">{{$t('名称')}}：<span class="red">*</span></label>
                                <div class="bk-form-content">
                                    <input type="text" disabled="disabled" v-model="editParams.name" class="bk-form-input text-input-half" :placeholder="$t('请输入')" maxlength="32" />
                                </div>
                            </div>
                            <div class="right">
                                <label class="bk-label label">{{$t('端口')}}：<span class="red">*</span></label>
                                <div class="bk-form-content">
                                    <bk-number-input
                                        class="text-input-half"
                                        :value.sync="editParams.port"
                                        :min="1"
                                        :max="65535"
                                        :debounce-timer="0"
                                        :placeholder="$t('请输入')">
                                    </bk-number-input>
                                </div>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label label">
                                URI：<span class="red">*</span>
                            </label>
                            <div class="bk-form-content">
                                <input type="text" v-model="editParams.url" class="bk-form-input text-input" :placeholder="$t('请输入')" />
                            </div>
                        </div>
                        <div class="bk-form-item flex-item">
                            <div class="left">
                                <label class="bk-label label">{{$t('采集频率')}}：<span class="red">*</span></label>
                                <div class="bk-form-content">
                                    <bk-number-input
                                        class="text-input-half has-suffix"
                                        :value.sync="editParams.frequency"
                                        :min="0"
                                        :max="999999999"
                                        :debounce-timer="0"
                                        :placeholder="$t('请输入')">
                                    </bk-number-input>
                                    <span class="suffix">
                                        {{$t('秒/次')}}
                                    </span>
                                </div>
                            </div>
                            <div class="right">
                                <label class="bk-label label">{{$t('单次采集超时时间（秒）')}}：<span class="red">*</span></label>
                                <div class="bk-form-content">
                                    <bk-number-input
                                        class="text-input-half has-suffix"
                                        :value.sync="editParams.timeout"
                                        :min="0"
                                        :debounce-timer="0"
                                        :placeholder="$t('请输入')">
                                    </bk-number-input>
                                    <span class="suffix">
                                        {{$t('秒')}}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item prometheus-item">
                            <div class="prometheus-header">
                                <label class="bk-label label">{{$t('Prometheus格式设置')}}</label>
                                <label class="bk-form-checkbox">
                                    <bk-tooltip placement="left" :transfer="true">
                                        <div slot="content" style="white-space: normal;">
                                            <div style="width: 230px;">
                                                <!-- 在创建的时候已经按{{editParams.metricType ? 'Prometheus' : '普通'}}类型在数据平台申请dataid，不能更改 -->
                                                {{$t('在创建的时候已经按{metricType}类型在数据平台申请dataid，不能更改', { metricType: editParams.metricType ? 'Prometheus' : $t('普通') })}}
                                            </div>
                                        </div>
                                        <input type="checkbox" name="metric-type" value="prometheus" v-model="editParams.metricType" disabled="disabled">
                                    </bk-tooltip>
                                </label>
                            </div>

                            <div class="prometheus-keys" v-show="editParams.metricType">
                                <label class="bk-label label">
                                    {{$t('附加数据')}}：
                                </label>
                                <bk-keyer
                                    class="prometheus-keylist"
                                    ref="constKeyer"
                                    :key-list.sync="editParams.constLabels"
                                    :key-placeholder="$t('键')"
                                    :value-placeholder="$t('值')"
                                    :tip="$t('小提示：同时粘贴多行“键=值”的文本会自动添加多行记录')"
                                ></bk-keyer>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label label">
                                Http Header：
                            </label>
                            <div class="bk-form-content">
                                <bk-keyer
                                    class="http-header"
                                    ref="labelKeyer"
                                    :key-list.sync="editParams.httpHeader"
                                    :key-placeholder="$t('键')"
                                    :value-placeholder="$t('值')"
                                    :tip="$t('小提示：同时粘贴多行“键=值”的文本会自动添加多行记录')"
                                ></bk-keyer>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label label">Http Method：</label>
                            <div class="bk-form-content scroll-order-form-item">
                                <label class="bk-form-radio">
                                    <input type="radio" value="GET" name="radio" checked="checked" v-model="editParams.httpMethod">
                                    <i class="bk-radio-text">GET</i>
                                </label>
                                <label class="bk-form-radio" style="margin-right: 7px;">
                                    <input type="radio" value="POST" name="radio" v-model="editParams.httpMethod">
                                    <i class="bk-radio-text">POST</i>
                                </label>
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label label">
                                {{$t('Http参数')}}：
                            </label>
                            <div class="bk-form-content">
                                <template v-if="editParams.httpMethod === 'GET'">
                                    <bk-keyer
                                        class="http-header"
                                        ref="labelKeyer"
                                        :key-list.sync="editParams.httpBodyGet"
                                        :key-placeholder="$t('键')"
                                        :value-placeholder="$t('值')"
                                        :tip="$t('小提示：同时粘贴多行“键=值”的文本会自动添加多行记录')"
                                    ></bk-keyer>
                                </template>
                                <template v-else>
                                    <textarea v-model="editParams.httpBodyPost" class="bk-form-textarea" :placeholder="$t('请输入')"></textarea>
                                </template>
                            </div>
                        </div>
                        <div class="action-inner">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="confirmEditMetric">
                                {{$t('更新')}}
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hideEditMetric">
                                {{$t('取消')}}
                            </button>
                        </div>
                    </form>
                </div>
            </template>
        </bk-sideslider>

        <bk-dialog
            :is-show.sync="instanceDialogConf.isShow"
            :width="instanceDialogConf.width"
            :content="instanceDialogConf.content"
            :has-header="instanceDialogConf.hasHeader"
            :has-footer="false"
            :close-icon="instanceDialogConf.closeIcon"
            :ext-cls="'biz-metric-manage-dialog'">
            <div slot="content">
                <div style="margin: -20px;">
                    <div class="bk-dialog-tool">
                        <i class="bk-dialog-close bk-icon icon-close" @click="hideInstanceDialog"></i>
                    </div>
                    <div class="instance-title">
                        {{curInstanceMetric.name}}{{$t('实例')}}
                    </div>
                    <div style="min-height: 100px;" v-bkloading="{ isLoading: isMetricInstanceLoading }">
                        <table class="bk-table has-table-hover biz-table biz-metric-instance-table" :style="{ borderBottomWidth: curMetricInstancePageData.length ? '1px' : 0 }" v-show="!isMetricInstanceLoading">
                            <thead>
                                <tr>
                                    <th style="padding-left: 30px;">{{$t('关联命名空间')}}</th>
                                    <th>{{$t('关联应用')}}</th>
                                    <th style="width: 150px;">{{$t('应用类型')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curMetricInstancePageData.length">
                                    <tr v-for="(instance, index) in curMetricInstancePageData" :key="index">
                                        <td style="padding-left: 30px;">
                                            {{instance.namespace}}
                                        </td>
                                        <td>
                                            {{instance.name}}
                                        </td>
                                        <td>
                                            {{instance.category}}
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
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
                    <div class="biz-page-box" v-if="!isMetricInstanceLoading && metricInstancePageConf.show && curMetricInstancePageData.length">
                        <bk-paging
                            :size="'small'"
                            :cur-page.sync="metricInstancePageConf.curPage"
                            :total-page="metricInstancePageConf.totalPage"
                            @page-change="metricInstancePageChange">
                        </bk-paging>
                    </div>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>

<script>
    import bkKeyer from '@open/components/keyer'

    export default {
        components: {
            'bk-keyer': bkKeyer
        },
        data () {
            return {
                permissions: {},
                winHeight: 0,
                searchKeyWord: '',
                isInitLoading: true,
                isPageLoading: false,
                bkMessageInstance: null,
                exceptionCode: null,
                dataList: [],
                dataListTmp: [],
                curPageData: [],
                metricInstancePageConf: {
                    totalPage: 1,
                    pageSize: 5,
                    curPage: 1,
                    show: true
                },
                isMetricInstanceLoading: true,
                curMetricInstancePageData: [],
                instanceDialogConf: {
                    isShow: false,
                    width: 690,
                    hasHeader: false,
                    closeIcon: false
                },
                pageConf: {
                    // 总数
                    total: 0,
                    // 总页数
                    totalPage: 1,
                    // 每页多少条
                    pageSize: 5,
                    // 当前页
                    curPage: 1,
                    // 是否显示翻页条
                    show: false
                },
                createMetricConf: {
                    isShow: false,
                    title: this.$t('新建Metric'),
                    timer: null,
                    width: 644,
                    loading: false
                },
                // 创建的参数
                createParams: {
                    name: '',
                    port: '',
                    url: '',
                    timeout: 30,
                    metricType: false,
                    frequency: 60,
                    httpMethod: 'GET',
                    httpHeader: [{ key: '', value: '' }],
                    httpBodyGet: [{ key: '', value: '' }],
                    constLabels: [{ key: '', value: '' }],
                    httpBodyPost: ''
                },
                // 编辑的参数
                editMetricConf: {
                    isShow: false,
                    title: this.$t('新建Metric'),
                    timer: null,
                    width: 644,
                    loading: false
                },
                curInstanceMetric: {
                    name: ''
                },
                // 编辑的参数
                editParams: {
                    curMetric: null,
                    name: '',
                    port: '',
                    url: '',
                    metricType: false,
                    timeout: 30,
                    frequency: 60,
                    httpMethod: 'GET',
                    httpHeader: [],
                    httpBodyGet: [],
                    constLabels: [],
                    httpBodyPost: ''
                },
                isCreatingOrEditing: false,
                creatingOrEditingStr: ''
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            isEn () {
                return this.$store.state.isEn
            }
        },
        mounted () {
            this.winHeight = window.innerHeight
            this.fetchData()
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
                this.initPageConf()
                this.pageChange()
            },

            /**
             * 搜索框清除事件
             */
            clearSearch () {
                this.searchKeyWord = ''
                this.searchMetric(true)
            },

            /**
             * 重置添加 metric 的参数
             */
            resetCreateParams () {
                this.createParams = Object.assign({}, {
                    name: '',
                    port: '',
                    url: '',
                    metricType: false,
                    timeout: 30,
                    frequency: 60,
                    httpMethod: 'GET',
                    httpHeader: [{ key: '', value: '' }],
                    httpBodyGet: [{ key: '', value: '' }],
                    constLabels: [{ key: '', value: '' }],
                    httpBodyPost: ''
                })
            },

            /**
             * 搜索
             *
             * @param {boolean} resetPage 是否重置 curPage 为 1
             * @param {Boolean} notLoading 是否不需要 loading
             */
            searchMetric (resetPage, notLoading = false) {
                let results = []
                if (this.searchKeyWord === '') {
                    this.dataList.splice(0, this.dataList.length, ...this.dataListTmp)
                } else {
                    results = this.dataListTmp.filter(m => {
                        return m.name.indexOf(this.searchKeyWord) > -1
                    })
                    this.dataList.splice(0, this.dataList.length, ...results)
                }
                if (resetPage) {
                    this.pageConf.curPage = 1
                }
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage, notLoading)
            },

            /**
             * 获取 metric 列表数据
             */
            async fetchData () {
                try {
                    const res = await this.$store.dispatch('metric/getMetricList', {
                        projectId: this.projectId
                    })
                    this.permissions = JSON.parse(JSON.stringify(res.permissions || {}))
                    this.dataList.splice(0, this.dataList.length, ...(res.data || []))
                    this.dataListTmp.splice(0, this.dataListTmp.length, ...(res.data || []))
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 初始化弹层翻页条
             */
            initPageConf () {
                const total = this.dataList.length
                if (total <= this.pageConf.pageSize) {
                    this.pageConf.show = false
                } else {
                    this.pageConf.show = true
                }
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize) || 1
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
            },

            /**
             * 获取当前这一页的数据
             *
             * @param {number} page 当前页
             * @param {Boolean} notLoading 是否不需要 loading
             *
             * @return {Array} 当前页数据
             */
            getDataByPage (page, notLoading = false) {
                // 如果没有page，重置
                if (!page) {
                    this.pageConf.curPage = page = 1
                }
                this.isPageLoading = !notLoading
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.dataList.length) {
                    endIndex = this.dataList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.dataList.slice(startIndex, endIndex)
            },

            /**
             * 手动刷新表格数据
             */
            refresh () {
                this.pageConf.curPage = 1
                this.searchKeyWord = ''
                this.fetchData()
            },

            /**
             * 创建 Metric 确定按钮
             */
            async confirmCreateMetric () {
                const me = this
                const name = me.createParams.name.trim()
                const port = me.createParams.port
                const url = me.createParams.url.trim()
                const timeout = me.createParams.timeout
                const frequency = me.createParams.frequency
                const httpMethod = me.createParams.httpMethod.trim()

                if (!name) {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return
                }

                if (name.length < 3) {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('名称不得小于三个字符')
                    })
                    return
                }

                if (url.length < 2) {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('URI不得小于两个字符')
                    })
                    return
                }

                if (port === null || port === undefined || port === '') {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入端口')
                    })
                    return
                }

                if (!url) {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入URI')
                    })
                    return
                }

                if (frequency === null || frequency === undefined || frequency === '') {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入采集频率')
                    })
                    return
                }

                if (timeout === '' || timeout === null || timeout === undefined) {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入单次采集超时时间')
                    })
                    return
                }

                const params = {
                    projectId: me.projectId,
                    name: name,
                    port: port,
                    uri: url,
                    metric_type: '',
                    timeout: timeout,
                    frequency: frequency,
                    const_labels: {},
                    http_method: httpMethod
                }

                if (me.createParams.metricType) {
                    params.metric_type = 'prometheus'
                }

                const headers = {}
                me.createParams.httpHeader.forEach(item => {
                    if (item.key) {
                        headers[item.key] = item.value
                    }
                })
                if (Object.keys(headers).length) {
                    params.http_headers = headers
                }

                const constLabels = {}
                me.createParams.constLabels.forEach(item => {
                    if (item.key) {
                        constLabels[item.key] = item.value
                    }
                })
                if (Object.keys(constLabels).length && params.metric_type) {
                    params.const_labels = constLabels
                }

                if (httpMethod === 'POST') {
                    if (me.createParams.httpBodyPost.trim()) {
                        params.http_body = me.createParams.httpBodyPost
                    }
                } else {
                    const bodys = {}
                    me.createParams.httpBodyGet.forEach(item => {
                        if (item.key) {
                            bodys[item.key] = item.value
                        }
                    })
                    if (Object.keys(bodys).length) {
                        params.http_body = JSON.stringify(bodys)
                    }
                }

                try {
                    me.isCreatingOrEditing = true
                    me.creatingOrEditingStr = this.$t('创建Metric中，请稍候...')
                    await me.$store.dispatch('metric/createMetric', params)

                    const res = await me.$store.dispatch('metric/getMetricList', {
                        projectId: me.projectId
                    })
                    me.dataList.splice(0, me.dataList.length, ...(res.data || []))
                    me.dataListTmp.splice(0, me.dataListTmp.length, ...(res.data || []))
                    me.pageConf.curPage = 1
                    me.searchKeyWord = ''
                    me.initPageConf()
                    // me.curPageData = me.getDataByPage(me.pageConf.curPage, true)

                    me.searchMetric(false, true)
                    me.hideCreateMetric()
                    me.isCreatingOrEditing = false
                    me.creatingOrEditingStr = ''
                } catch (e) {
                    console.error(e)
                    me.isCreatingOrEditing = false
                    me.creatingOrEditingStr = ''
                    me.bkMessageInstance = me.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 显示创建 metric sideslider
             */
            async showCreateMetric () {
                if (!this.permissions.create) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'create',
                        resource_type: 'metric'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.resetCreateParams()
                this.createMetricConf.isShow = true
            },

            /**
             * 隐藏创建 metric sideslider
             */
            hideCreateMetric () {
                this.createMetricConf.isShow = false
                this.isCreatingOrEditing = false
                this.creatingOrEditingStr = ''
            },

            /**
             * 跳转到 字段设置或数据清洗 页面
             *
             * @param {Object} metric 当前 metric 对象
             * @param {string} url 要跳转的 url
             */
            async go (metric, url) {
                if (!metric.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: metric.id,
                        resource_name: metric.name,
                        resource_type: 'metric'
                    })
                }
                window.open(url)
            },

            /**
             * 显示编辑 metric sideslider
             *
             * @param {Object} metric 当前 metric 对象
             */
            async editMetric (metric) {
                if (!metric.permissions.edit) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'edit',
                        resource_code: metric.id,
                        resource_name: metric.name,
                        resource_type: 'metric'
                    })
                }

                this.editMetricConf.isShow = true
                this.editMetricConf.title = this.$t(`更新【{metricName}】`, { metricName: metric.name })

                this.editParams.curMetric = metric
                this.editParams.name = metric.name
                this.editParams.port = metric.port
                this.editParams.url = metric.uri
                this.editParams.timeout = metric.timeout
                this.editParams.metricType = !!metric.metric_type
                this.editParams.frequency = metric.frequency
                this.editParams.httpMethod = metric.http_method
                const headersKeyList = Object.keys(metric.http_headers)
                if (headersKeyList.length) {
                    headersKeyList.forEach(key => {
                        this.editParams.httpHeader.push({
                            key: key,
                            value: metric.http_headers[key]
                        })
                    })
                } else {
                    this.editParams.httpHeader.push({
                        key: '',
                        value: ''
                    })
                }

                const constLabelsKeys = Object.keys(metric.const_labels)
                if (constLabelsKeys.length) {
                    constLabelsKeys.forEach(key => {
                        this.editParams.constLabels.push({
                            key: key,
                            value: metric.const_labels[key]
                        })
                    })
                } else {
                    this.editParams.constLabels.push({
                        key: '',
                        value: ''
                    })
                }

                if (this.editParams.httpMethod === 'POST') {
                    this.editParams.httpBodyPost = metric.http_body
                    this.editParams.httpBodyGet.push({
                        key: '',
                        value: ''
                    })
                } else {
                    const bodyKeyList = Object.keys(metric.http_body)
                    if (bodyKeyList.length) {
                        bodyKeyList.forEach(key => {
                            this.editParams.httpBodyGet.push({
                                key: key,
                                value: metric.http_body[key]
                            })
                        })
                    } else {
                        this.editParams.httpBodyGet.push({
                            key: '',
                            value: ''
                        })
                    }
                }
            },

            /**
             * 编辑 Metric 确定按钮
             */
            async confirmEditMetric () {
                const me = this
                const name = me.editParams.name.trim()
                const port = me.editParams.port
                const url = me.editParams.url.trim()
                const timeout = me.editParams.timeout
                const frequency = me.editParams.frequency
                const httpMethod = me.editParams.httpMethod.trim()

                if (!name) {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return
                }

                if (name.length < 3) {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('名称不得小于三个字符')
                    })
                    return
                }

                if (port === null || port === undefined || port === '') {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入端口')
                    })
                    return
                }

                if (!url) {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入URI')
                    })
                    return
                }

                if (frequency === null || frequency === undefined || frequency === '') {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入采集频率')
                    })
                    return
                }

                if (timeout === null || timeout === undefined || timeout === '') {
                    me.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入单次采集超时时间')
                    })
                    return
                }

                const params = {
                    projectId: me.projectId,
                    metricId: me.editParams.curMetric.id,
                    name: name,
                    port: port,
                    uri: url,
                    metric_type: '',
                    timeout: timeout,
                    const_labels: {},
                    frequency: frequency,
                    http_method: httpMethod
                }

                if (me.editParams.metricType) {
                    params.metric_type = 'prometheus'
                }

                const constLabels = {}
                me.editParams.constLabels.forEach(item => {
                    if (item.key) {
                        constLabels[item.key] = item.value
                    }
                })
                if (Object.keys(constLabels).length && params.metric_type) {
                    params.const_labels = constLabels
                }

                if (me.editParams.httpHeader.length === 1
                    && me.editParams.httpHeader[0].key === ''
                    && me.editParams.httpHeader[0].value === ''
                ) {
                    params.http_headers = ''
                } else {
                    const headers = {}
                    me.editParams.httpHeader.forEach(item => {
                        if (item.key) {
                            headers[item.key] = item.value
                        }
                    })
                    if (Object.keys(headers).length) {
                        params.http_headers = headers
                    }
                }

                if (httpMethod === 'POST') {
                    // if (me.editParams.httpBodyPost.trim()) {
                    //     params.http_body = me.editParams.httpBodyPost
                    // }
                    params.http_body = me.editParams.httpBodyPost.trim() || ''
                } else {
                    if (me.editParams.httpBodyGet.length === 1
                        && me.editParams.httpBodyGet[0].key === ''
                        && me.editParams.httpBodyGet[0].value === ''
                    ) {
                        params.http_body = '{}'
                    } else {
                        const bodys = {}
                        me.editParams.httpBodyGet.forEach(item => {
                            if (item.key) {
                                bodys[item.key] = item.value
                            }
                        })
                        if (Object.keys(bodys).length) {
                            params.http_body = JSON.stringify(bodys)
                        }
                    }
                }

                try {
                    me.isCreatingOrEditing = true
                    me.creatingOrEditingStr = this.$t('更新Metric中，请稍候...')
                    await me.$store.dispatch('metric/editMetric', params)

                    const res = await me.$store.dispatch('metric/getMetricList', {
                        projectId: me.projectId
                    })
                    me.dataList.splice(0, me.dataList.length, ...(res.data || []))
                    me.dataListTmp.splice(0, me.dataListTmp.length, ...(res.data || []))
                    me.initPageConf()
                    me.searchMetric(false, true)
                    me.hideEditMetric()
                    me.isCreatingOrEditing = false
                    me.creatingOrEditingStr = ''
                } catch (e) {
                    console.error(e)
                    me.isCreatingOrEditing = false
                    me.creatingOrEditingStr = ''
                    me.bkMessageInstance = me.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 隐藏创建 metric sideslider
             */
            hideEditMetric () {
                this.editParams = Object.assign({}, {
                    curMetric: null,
                    name: '',
                    port: '',
                    url: '',
                    timeout: 30,
                    metricType: false,
                    frequency: 60,
                    httpMethod: 'GET',
                    httpHeader: [],
                    httpBodyGet: [],
                    constLabels: [],
                    httpBodyPost: ''
                })
                this.editMetricConf.isShow = false
            },

            initMetricInstancePageConf () {
                const total = this.metricInstanceList.length
                this.metricInstancePageConf.totalPage = Math.ceil(total / this.metricInstancePageConf.pageSize)
            },
            reloadMetricInstanceCurPage () {
                this.initMetricInstancePageConf()
                if (this.metricInstancePageConf.curPage > this.metricInstancePageConf.totalPage) {
                    this.metricInstancePageConf.curPage = this.metricInstancePageConf.totalPage
                }
                this.curMetricInstancePageData = this.getDataByPage(this.metricInstancePageConf.curPage)
            },
            getMetricInstanceDataByPage (page) {
                let startIndex = (page - 1) * this.metricInstancePageConf.pageSize
                let endIndex = page * this.metricInstancePageConf.pageSize
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.metricInstanceList.length) {
                    endIndex = this.metricInstanceList.length
                }
                const data = this.metricInstanceList.slice(startIndex, endIndex)
                return data
            },
            metricInstancePageChange (page) {
                this.metricInstancePageConf.curPage = page
                const data = this.getMetricInstanceDataByPage(page)
                this.curMetricInstancePageData = JSON.parse(JSON.stringify(data))
            },

            hideInstanceDialog () {
                this.instanceDialogConf.isShow = false
            },

            /**
             * 查看 metric 实例
             *
             * @param {Object} metric 当前 metric 对象
             */
            async checkMetricInstance (metric) {
                // if (!metric.permissions.view) {
                //     let params = {
                //         project_id: this.projectId,
                //         policy_code: 'view',
                //         resource_code: metric.id,
                //         resource_name: metric.name,
                //         resource_type: 'metric'
                //     }
                //     await this.$store.dispatch('getResourcePermissions', params)
                // }
                this.curInstanceMetric = metric
                this.isMetricInstanceLoading = true
                this.instanceDialogConf.isShow = true
                try {
                    const res = await this.$store.dispatch('metric/checkMetricInstance', {
                        projectId: this.projectId,
                        metricId: metric.id
                    })
                    this.metricInstanceList = res.data
                    this.metricInstancePageConf.curPage = 1
                    this.initMetricInstancePageConf()
                    this.curMetricInstancePageData = this.getMetricInstanceDataByPage(this.metricInstancePageConf.curPage)
                    this.isMetricInstanceLoading = false
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * 删除 metric
             *
             * @param {Object} metric 当前 metric 对象
             */
            async deleteMetric (metric) {
                if (!metric.permissions.delete) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'delete',
                        resource_code: metric.id,
                        resource_name: metric.name,
                        resource_type: 'metric'
                    })
                }

                const me = this
                me.$bkInfo({
                    title: ``,
                    clsName: 'biz-remove-dialog',
                    content: me.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除Metric')}【${metric.name}】？`),
                    async confirmFn () {
                        try {
                            me.$bkLoading({
                                title: me.$createElement('span', me.$t('删除Metric中，请稍候'))
                            })

                            await me.$store.dispatch('metric/deleteMetric', {
                                projectId: me.projectId,
                                metricId: metric.id
                            })

                            const res = await me.$store.dispatch('metric/getMetricList', {
                                projectId: me.projectId
                            })

                            me.dataList.splice(0, me.dataList.length, ...(res.data || []))
                            me.dataListTmp.splice(0, me.dataListTmp.length, ...(res.data || []))
                            me.pageConf.curPage = 1
                            me.searchKeyWord = ''
                            me.initPageConf()
                            me.curPageData = me.getDataByPage(me.pageConf.curPage)
                            // me.searchMetric(true)
                            me.$bkLoading.hide()
                        } catch (e) {
                            console.error(e)
                            me.$bkLoading.hide()
                            me.bkMessageInstance = me.$bkMessage({
                                theme: 'error',
                                message: e.message || e.data.msg || e.statusText
                            })
                        }
                    }
                })
            },

            /**
             * 暂停/恢复 metric
             *
             * @param {Object} metric 当前 metric 对象
             * @param {string} idx 暂停/恢复 标识
             * @param {Array} namespaceIdList 命名空间 id 集合
             */
            async pauseAndResume (metric, idx, namespaceIdList = []) {
                if (!metric.permissions.delete) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'delete',
                        resource_code: metric.id,
                        resource_name: metric.name,
                        resource_type: 'metric'
                    })
                }

                const idxStr = idx === 'pause' ? this.$t('暂停') : this.$t('恢复')
                const opType = idx === 'pause' ? 'pause' : 'resume'

                const me = this
                me.$bkInfo({
                    // title: `确认${idxStr}【${metric.name}】？`,
                    title: this.$t(`确认{action}【{metricName}】？`, { action: idxStr, metricName: metric.name }),
                    async confirmFn () {
                        try {
                            me.$bkLoading({
                                // title: me.$createElement('span', `${idxStr}Metric中，请稍候...`)
                                title: me.$createElement('span', me.$t(`{action}Metric中，请稍候`, { action: idxStr }))
                            })

                            await me.$store.dispatch('metric/pauseAndResumeMetric', {
                                projectId: me.projectId,
                                metricId: metric.id,
                                op_type: opType,
                                ns_id_list: namespaceIdList
                            })

                            const res = await me.$store.dispatch('metric/getMetricList', {
                                projectId: me.projectId
                            })

                            me.dataList.splice(0, me.dataList.length, ...(res.data || []))
                            me.dataListTmp.splice(0, me.dataListTmp.length, ...(res.data || []))
                            me.pageConf.curPage = 1
                            me.searchKeyWord = ''
                            me.initPageConf()
                            me.curPageData = me.getDataByPage(me.pageConf.curPage)
                            // me.searchMetric(true)
                            me.$bkLoading.hide()
                        } catch (e) {
                            console.error(e)
                            me.$bkLoading.hide()
                            me.bkMessageInstance = me.$bkMessage({
                                theme: 'error',
                                message: e.message || e.data.msg || e.statusText
                            })
                        }
                    }
                })
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
