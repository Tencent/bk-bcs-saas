<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-topbar-title">
                Ingress
                <span class="biz-tip f12 ml10">{{$t('请通过模板集创建Ingress')}}</span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper p0" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <template v-if="!isInitLoading">
                <div class="biz-panel-header">
                    <div class="right">
                        <bk-data-searcher
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="searchIngress"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>

                <div class="biz-resource">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table has-table-hover biz-table biz-resource-table">
                            <thead>
                                <tr>
                                    <th style="width: 10px;">
                                    </th>
                                    <th style="width: 300px;">{{$t('名称')}}</th>
                                    <th style="width: 300px;">{{$t('所属集群')}}</th>
                                    <th style="width: 300px;">{{$t('命名空间')}}</th>
                                    <th style="width: 300px;">{{$t('CLB')}}</th>
                                    <th style="width: 300px;">{{$t('更新时间')}}</th>
                                    <th style="width: 100px">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="ingressList.length">
                                    <tr v-for="(ingress, index) in curPageData" :key="index">
                                        <td>
                                            <div
                                                class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning"
                                                v-if="ingress.status === 'updating'">
                                                <div class="rotate rotate1"></div>
                                                <div class="rotate rotate2"></div>
                                                <div class="rotate rotate3"></div>
                                                <div class="rotate rotate4"></div>
                                                <div class="rotate rotate5"></div>
                                                <div class="rotate rotate6"></div>
                                                <div class="rotate rotate7"></div>
                                                <div class="rotate rotate8"></div>
                                            </div>
                                        </td>
                                        <td>
                                            <a href="javascript: void(0)" class="bk-text-button biz-table-title biz-resource-title" @click.stop.prevent="showIngressDetail(ingress, index)">{{ingress.name}}</a>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="ingress.cluster_id || '--'" placement="top">
                                                <p class="biz-text-wrapper">{{ingress.cluster_name ? ingress.cluster_name : '--'}}</p>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            {{ingress.namespace || '--'}}
                                        </td>
                                        <td>
                                            {{ingress.config.metadata.labels['bmsf.tencent.com/clbname'] || '--'}}
                                        </td>
                                        <td>
                                            {{ingress.update_time ? formatDate(ingress.update_time) : '--'}}
                                        </td>
                                        <td>
                                            <li style="width: 200px;">
                                                <a @click.stop="showIngressEditDialog(ingress)" class="biz-operate">{{$t('编辑')}}</a>
                                                <a @click.stop="showIngressDetail(ingress)" class="biz-operate">{{$t('查看')}}</a>
                                                <a @click.stop="removeIngress(ingress)" class="biz-operate">{{$t('删除')}}</a>
                                            </li>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="6">
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
                :quick-close="true"
                :is-show.sync="ingressSlider.isShow"
                :title="ingressSlider.title"
                :width="'800'">
                <div class="pt20 pr30 pl30 pb20" slot="content">
                    <label class="biz-title">{{$t('基本信息')}}</label>
                    <table class="bk-table biz-data-table has-table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 270px;">{{$t('名称')}}</th>
                                <th>{{$t('所属集群')}}</th>
                                <th>{{$t('命名空间')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{{curIngress.name || '--'}}</td>
                                <td>{{curIngress.cluster_name || '--'}}</td>
                                <td>{{curIngress.namespace || '--'}}</td>
                            </tr>
                        </tbody>
                    </table>

                    <label class="biz-title">{{$t('规则')}}</label>
                    <table class="bk-table biz-data-table has-table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 200px;">{{$t('Service名称')}}</th>
                                <th style="width: 200px;">{{$t('协议')}}</th>
                                <th style="width: 200px;">{{$t('服务端口')}}</th>
                                <th style="width: 200px;">{{$t('监听CLB端口')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curIngress.rules && curIngress.rules.length">
                                <tr v-for="(rule, index) in curIngress.rules" :key="index">
                                    <td>{{rule.serviceName || '--'}}</td>
                                    <td>{{rule.protocol || '--'}}</td>
                                    <td>{{rule.servicePort || '--'}}</td>
                                    <td>{{rule.clbPort || '--'}}</td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="4">
                                        <p style="padding: 10px; text-align: center;">{{$t('无数据')}}</p>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                    <div class="actions">
                        <button class="show-labels-btn bk-button bk-button-small bk-primary">{{$t('显示标签')}}</button>
                    </div>

                    <div class="point-box">
                        <template v-if="curIngress.labels && curIngress.labels.length">
                            <ul class="key-list">
                                <li v-for="(label, index) of curIngress.labels" :key="index">
                                    <span class="key">{{label.key}}</span>
                                    <span class="value">{{label.value || '--'}}</span>
                                </li>
                            </ul>
                        </template>
                        <template v-else>
                            <p class="biz-no-data">{{$t('无数据')}}</p>
                        </template>
                    </div>
                </div>
            </bk-sideslider>

            <bk-sideslider
                :is-show.sync="ingressEditSlider.isShow"
                :title="ingressEditSlider.title"
                :width="'1020'">
                <div class="p0 pl20" slot="content">
                    <div class="biz-configuration-content" style="position: relative;">
                        <div class="bk-form biz-configuration-form">
                            <div class="bk-form-item is-required">
                                <label class="bk-label" style="width: 130px;">{{$t('名称')}}：</label>
                                <div class="bk-form-content" style="margin-left: 130px;">
                                    <input
                                        type="text"
                                        class="bk-form-input"
                                        :placeholder="$t('请输入30个以内的字符')"
                                        :disabled="true"
                                        style="width: 300px;"
                                        maxlength="30"
                                        v-model="curIngress.config.metadata.name">
                                </div>
                            </div>

                            <div class="bk-form-item" v-if="ingressEditSlider.isShow">
                                <div class="bk-form-content" style="margin-left: 0;">
                                    <div class="bk-form-inline-item">
                                        <label class="bk-label" style="width: 130px;">{{$t('区域')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-selector
                                                style="width: 300px;"
                                                :placeholder="$t('请选择')"
                                                :selected.sync="curIngress.config.metadata.labels['io.tencent.bcs.clb.region']"
                                                :list="regionList"
                                                :is-link="true"
                                                @item-selected="handlerRegionSelect">
                                            </bk-selector>
                                        </div>
                                    </div>

                                    <div class="bk-form-inline-item">
                                        <label class="bk-label" style="width: 176px;">CLB：</label>
                                        <div class="bk-form-content" style="margin-left: 176px;">
                                            <template v-if="clbList.length">
                                                <bk-selector
                                                    style="width: 300px;"
                                                    :placeholder="$t('请选择')"
                                                    :selected.sync="curIngress.config.metadata.labels['bmsf.tencent.com/clbname']"
                                                    :list="clbList">
                                                </bk-selector>
                                            </template>
                                            <template v-else>
                                                <bk-input
                                                    style="width: 300px;"
                                                    v-model="curIngress.config.metadata.labels['bmsf.tencent.com/clbname']"
                                                    :disabled="true">
                                                </bk-input>
                                            </template>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="biz-part-header">
                            <div class="bk-button-group">
                                <div class="item" v-for="(rule, index) in curIngress.config.webCache.rules" :key="index">
                                    <button
                                        :class="['bk-button bk-default is-outline', { 'is-selected': curRuleIndex === index }]"
                                        @click.stop="setCurRule(rule, index)">
                                        {{rule.name || $t('未命名')}}
                                    </button>
                                    <span
                                        class="bk-icon icon-close-circle"
                                        @click.stop="removeRule(index)"
                                        v-if="curIngress.config.webCache.rules.length > 1">
                                    </span>
                                </div>
                                <button
                                    type="button"
                                    class="bk-button bk-default is-outline is-icon"
                                    @click.stop.prevent="addLocalRule">
                                    <i class="bk-icon icon-plus"></i>
                                </button>
                            </div>
                        </div>

                        <div class="bk-form biz-configuration-form pb15" :key="curRule.name">
                            <div class="biz-span">
                                <span class="title">{{$t('基础信息')}}</span>
                            </div>
                            <div class="bk-form-item">
                                <div class="bk-form-content" style="margin-left: 0;">
                                    <div class="bk-form-inline-item is-required">
                                        <label class="bk-label" style="width: 130px;">{{$t('Service名称')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-selector
                                                style="width: 170px;"
                                                :placeholder="$t('请选择')"
                                                :setting-key="'name'"
                                                :selected.sync="curRule.serviceName"
                                                :list="serviceList"
                                                @item-selected="handleServiceNameChange">
                                            </bk-selector>
                                        </div>
                                    </div>

                                    <div class="bk-form-inline-item is-required">
                                        <label class="bk-label" style="width: 130px;">{{$t('协议')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-selector
                                                style="width: 170px;"
                                                :placeholder="$t('请选择')"
                                                :disabled="!curRule.serviceName"
                                                :setting-key="'id'"
                                                :selected.sync="curRule.serviceType"
                                                :list="curProtocol.protocolList"
                                                @item-selected="handleProtocolChange">
                                            </bk-selector>
                                        </div>
                                    </div>

                                    <div class="bk-form-inline-item is-required">
                                        <label class="bk-label" style="width: 130px;">{{$t('端口')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-selector
                                                style="width: 170px;"
                                                :placeholder="$t('请选择')"
                                                :disabled="!curRule.serviceType"
                                                :setting-key="'servicePort'"
                                                :display-key="'servicePort'"
                                                :selected.sync="curRule.servicePort"
                                                :list="curProtocol[curRule.serviceType] || []"
                                                @item-selected="handlePortChange">
                                            </bk-selector>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="bk-form-item" v-if="curRule.serviceType === 'HTTP'">
                                <div class="bk-form-content" style="margin-left: 0;">
                                    <div class="bk-form-inline-item">
                                        <label class="bk-label" style="width: 130px;">{{$t('域名')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-input
                                                style="width: 170px;"
                                                :placeholder="$t('请输入')"
                                                :value.sync="curRule.host"
                                                :disabled="true">
                                            </bk-input>
                                        </div>
                                    </div>

                                    <div class="bk-form-inline-item">
                                        <label class="bk-label" style="width: 130px;">{{$t('路径')}}</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-input
                                                style="width: 170px;"
                                                :placeholder="$t('请输入')"
                                                :value.sync="curRule.path"
                                                :disabled="true">
                                            </bk-input>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="bk-form-item">
                                <div class="bk-form-content" style="margin-left: 0;">
                                    <div class="bk-form-inline-item is-required">
                                        <label class="bk-label" style="width: 130px;">{{$t('监听CLB端口')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-input
                                                type="number"
                                                :placeholder="'1-65535'"
                                                style="width: 170px;"
                                                :min="1"
                                                :max="65535"
                                                :value.sync="curRule.clbPort"
                                                :list="varList">
                                            </bk-input>
                                        </div>
                                    </div>

                                    <div class="bk-form-inline-item">
                                        <label class="bk-label" style="width: 130px;">{{$t('会话保持时间')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div class="bk-form-input-group">
                                                <bk-input
                                                    type="number"
                                                    :placeholder="'30-3600'"
                                                    style="width: 134px;"
                                                    :min="30"
                                                    :max="3600"
                                                    :value.sync="curRule.sessionTime"
                                                    :list="varList">
                                                </bk-input>
                                                <span class="input-group-addon">
                                                    {{$t('秒')}}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="bk-form-inline-item">
                                        <label class="bk-label" style="width: 130px;">{{$t('负载均衡策略')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-selector
                                                style="width: 170px;"
                                                :placeholder="$t('请选择')"
                                                :setting-key="'id'"
                                                :selected.sync="curRule.lbPolicy.strategy"
                                                :list="strategyList">
                                            </bk-selector>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="bk-form-item">
                                <div class="bk-form-content" style="margin-left: 0;">
                                    <div class="bk-form-inline-item">
                                        <label class="bk-label" style="width: 130px;">{{$t('健康检查策略')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div
                                                class="ingress-switcher-wrapper"
                                                @click="toggleHealcheckEnable">
                                                <bk-switcher
                                                    class="mt10 mr5"
                                                    :selected="curRule.healthCheck.enabled"
                                                    size="small">
                                                </bk-switcher>
                                            </div>
                                            
                                            <span class="f12 mt10 vm" style="display: inline-block;">{{curRule.healthCheck.enabled ? $t('已启用') : $t('未启用')}}</span>

                                            <section class="ingress-block" v-if="curRule.healthCheck.enabled">
                                                <div class="bk-form-content" style="margin-left: 0;">
                                                    <div class="bk-form-inline-item">
                                                        <label class="bk-label" style="width: 130px;">{{$t('响应超时时间')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 130px;">
                                                            <div class="bk-form-input-group">
                                                                <bk-input
                                                                    type="number"
                                                                    style="width: 150px;"
                                                                    :placeholder="'2-60'"
                                                                    :min="2"
                                                                    :max="60"
                                                                    :value.sync="curRule.healthCheck.timeout"
                                                                    :list="varList">
                                                                </bk-input>
                                                                <span class="input-group-addon">
                                                                    {{$t('秒')}}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class="bk-form-inline-item">
                                                        <label class="bk-label" style="width: 200px;">{{$t('探测间隔时间')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 200px;">
                                                            <div class="bk-form-input-group">
                                                                <bk-input
                                                                    type="number"
                                                                    style="width: 150px;"
                                                                    :placeholder="'5-300'"
                                                                    :min="5"
                                                                    :max="300"
                                                                    :value.sync="curRule.healthCheck.intervalTime"
                                                                    :list="varList">
                                                                </bk-input>
                                                                <span class="input-group-addon">
                                                                    {{$t('秒')}}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div class="bk-form-content" style="margin-left: 0;">
                                                    <div class="bk-form-inline-item">
                                                        <label class="bk-label" style="width: 130px;">{{$t('健康阈值')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 130px;">
                                                            <div class="bk-form-input-group">
                                                                <bk-input
                                                                    type="number"
                                                                    style="width: 150px;"
                                                                    :placeholder="'2-10'"
                                                                    :min="2"
                                                                    :max="10"
                                                                    :value.sync="curRule.healthCheck.healthNum"
                                                                    :list="varList">
                                                                </bk-input>
                                                                <span class="input-group-addon">
                                                                    {{$t('次')}}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class="bk-form-inline-item">
                                                        <label class="bk-label" style="width: 200px;">{{$t('不健康阈值')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 200px;">
                                                            <div class="bk-form-input-group">
                                                                <bk-input
                                                                    type="number"
                                                                    style="width: 150px;"
                                                                    :placeholder="'2-10'"
                                                                    :min="2"
                                                                    :max="10"
                                                                    :value.sync="curRule.healthCheck.unHealthNum"
                                                                    :list="varList">
                                                                </bk-input>
                                                                <span class="input-group-addon">
                                                                    {{$t('次')}}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div class="bk-form-content" style="margin-left: 0;">
                                                    <div class="bk-form-inline-item">
                                                        <label class="bk-label" style="width: 130px;">{{$t('探测路径')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 130px;">
                                                            <bk-input
                                                                style="width: 186px;"
                                                                :placeholder="$t('请输入')"
                                                                :value.sync="curRule.healthCheck.httpCheckPath"
                                                                :list="varList">
                                                            </bk-input>
                                                        </div>
                                                    </div>

                                                    <div class="bk-form-inline-item">
                                                        <label class="bk-label" style="width: 200px;">{{$t('健康状态码')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 200px;">
                                                            <bk-input
                                                                type="number"
                                                                style="width: 186px;"
                                                                :placeholder="$t('请输入')"
                                                                :min="0"
                                                                :value.sync="curRule.healthCheck.httpCode"
                                                                :list="varList">
                                                            </bk-input>
                                                        </div>
                                                    </div>
                                                </div>
                                            </section>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="bk-form-item" v-if="curRule.serviceType === 'HTTP'">
                                <div class="bk-form-content" style="margin-left: 0;">
                                    <div class="bk-form-inline-item">
                                        <label class="bk-label" style="width: 130px;">{{$t('开启Https')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div
                                                class="ingress-switcher-wrapper"
                                                @click="toggleHttpsEnable">
                                                <bk-switcher
                                                    class="mt10 mr5"
                                                    :selected="curRule.httpsEnabled"
                                                    size="small">
                                                </bk-switcher>
                                            </div>
                                            <span class="f12 mt10 vm" style="display: inline-block;">{{curRule.httpsEnabled ? $t('已启用') : $t('未启用')}}</span>

                                            <section class="ingress-block" v-if="curRule.httpsEnabled">
                                                <div class="bk-form-content" style="margin-left: 0;">
                                                    <div class="bk-form-inline-item">
                                                        <label class="bk-label" style="width: 90px;">{{$t('认证模式')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 90px;">
                                                            <bk-selector
                                                                style="width: 130px;"
                                                                :placeholder="$t('请选择')"
                                                                :setting-key="'id'"
                                                                :selected.sync="curRule.tls.mode"
                                                                :list="tlsModeList"
                                                                @item-selected="handleModeSelect">
                                                            </bk-selector>
                                                        </div>
                                                    </div>

                                                    <div class="bk-form-inline-item">
                                                        <label class="bk-label" style="width: 90px;">{{$t('证书ID')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 90px;">
                                                            <bk-input
                                                                style="width: 130px;"
                                                                :placeholder="$t('请输入')"
                                                                :value.sync="curRule.tls.certId"
                                                                :list="varList">
                                                            </bk-input>
                                                        </div>
                                                    </div>

                                                    <div class="bk-form-inline-item" v-if="curRule.tls.mode === 'mutual'">
                                                        <label class="bk-label" style="width: 130px;">{{$t('客户端证书ID')}}：</label>
                                                        <div class="bk-form-content" style="margin-left: 130px;">
                                                            <bk-input
                                                                style="width: 130px;"
                                                                :placeholder="$t('请输入')"
                                                                :key="curRule.tls.mode"
                                                                :value.sync="curRule.tls.certCaId"
                                                                :list="varList">
                                                            </bk-input>
                                                            <bk-tooltip
                                                                :content="$t('客户端证书的 ID，如果 mode=mutual，监听器如果不填写此项则必须上传客户端证书，包括 certClientCaName，certCilentCaContent')"
                                                                placement="top">
                                                                <span class="bk-badge">
                                                                    <i class="bk-icon icon-question"></i>
                                                                </span>
                                                            </bk-tooltip>
                                                        </div>
                                                    </div>
                                                </div>
                                            </section>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="biz-span mb50"></div>
                        <div class="ingress-action mt20" style="margin-left: 130px;">
                            <button class="bk-button bk-primary mr10" style="min-width: 80px;" @click="handleUpdateIngress">{{$t('更新')}}</button>
                            <button class="bk-button bk-default" @click="handleCancelUpdate">{{$t('取消')}}</button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>

            <bk-dialog
                :is-show="batchDialogConfig.isShow"
                :width="550"
                :has-header="false"
                :quick-close="false"
                @confirm="deleteIngresses(batchDialogConfig.data)"
                @cancel="batchDialogConfig.isShow = false">
                <div slot="content">
                    <div class="biz-batch-wrapper">
                        <p class="batch-title">{{$t('确定要删除以下Ingress？')}}</p>
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
    import { catchErrorHandler, formatDate } from '@open/common/util'
    import ingressParams from '@open/json/ingress.json'
    import ruleParams from '@open/json/ingress-rule.json'
    import _ from 'lodash'

    export default {
        data () {
            return {
                formatDate: formatDate,
                isInitLoading: true,
                isPageLoading: false,
                searchKeyword: '',
                searchScope: '',
                curPageData: [],
                curIngress: ingressParams,
                pageConf: {
                    total: 1,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                ingressSlider: {
                    title: '',
                    isShow: false
                },
                ingressEditSlider: {
                    title: '',
                    isShow: false
                },
                addSlider: {
                    title: '',
                    isShow: false
                },
                batchDialogConfig: {
                    isShow: false,
                    list: [],
                    data: []
                },
                namespace: '',
                alreadySelectedNums: 0,
                curRuleIndex: 0,
                curRule: JSON.parse(JSON.stringify(ruleParams)),
                clbList: [],
                serviceList: [],
                strategyList: [
                    {
                        id: 'wrr',
                        name: 'wrr'
                    },
                    {
                        id: 'least_conn',
                        name: 'least_conn'
                    }
                ],
                tlsModeList: [
                    {
                        id: 'unidirectional',
                        name: 'unidirectional'
                    },
                    {
                        id: 'mutual',
                        name: 'mutual'
                    }
                ],
                regionList: [
                    {
                        name: '上海',
                        id: 'ap-shanghai'
                    },
                    {
                        name: '南京',
                        id: 'ap-nanjing'
                    },
                    {
                        name: '天津',
                        id: 'ap-tianjin'
                    },
                    {
                        name: '广州',
                        id: 'ap-guangzhou'
                    },
                    {
                        name: '深圳',
                        id: 'ap-shenzhen'
                    },
                    {
                        name: '杭州',
                        id: 'ap-hangzhou'
                    },
                    {
                        name: '济南',
                        id: 'ap-jinan'
                    },
                    {
                        name: '福州',
                        id: 'ap-fuzhou'
                    },
                    {
                        name: '重庆',
                        id: 'ap-chongqing'
                    },
                    {
                        name: '香港',
                        id: 'ap-hongkong'
                    },
                    {
                        name: '新加坡',
                        id: 'ap-singapore'
                    },
                    {
                        name: '首尔',
                        id: 'ap-seoul'
                    },
                    {
                        name: '孟买',
                        id: 'ap-mumbai'
                    },
                    {
                        name: '法兰克福',
                        id: 'ap-frankfurt'
                    },
                    {
                        name: '硅谷',
                        id: 'ap-siliconvalley'
                    }
                ]
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            curProject () {
                return this.$store.state.curProject
            },
            searchScopeList () {
                const clusterList = this.$store.state.cluster.clusterList
                const results = clusterList.map(item => {
                    return {
                        id: item.cluster_id,
                        name: item.name
                    }
                })

                results.length && results.unshift({
                    id: '',
                    name: this.$t('全部集群')
                })

                return results
            },
            projectId () {
                return this.$route.params.projectId
            },
            ingressList () {
                const list = this.$store.state.resource.ingressList
                list.forEach(ingress => {
                    const rules = []
                    let index = 1
                    ingress.isChecked = false
                    ingress.config.webCache = {
                        rules: []
                    }
                    // 通过client导入的，labels没有区域字段
                    const labels = ingress.config.metadata.labels
                    if (!labels.hasOwnProperty('io.tencent.bcs.clb.region')) {
                        labels['io.tencent.bcs.clb.region'] = ''
                    }

                    // 将数据扁平化
                    for (const key in ingress.config.spec) {
                        const types = ingress.spec[key]
                        types.forEach(item => {
                            // 将少的字段通过和模板json合并补全
                            ruleParams.sessionTime = ''
                            const newItem = _.merge({}, ruleParams, item)
                            if (key.toUpperCase() === 'HTTPS') {
                                newItem.serviceType = 'HTTP'
                                newItem.httpsEnabled = true
                            } else {
                                newItem.serviceType = key.toUpperCase()
                                newItem.httpsEnabled = false
                            }
                            
                            newItem.name = `rule-${index}`
                            ingress.config.webCache.rules.push(newItem)
                            index++
                        })
                    }
                })

                return JSON.parse(JSON.stringify(list))
            },
            varList () {
                return this.$store.state.variable.varList
            },
            curProtocol () {
                const serviceName = this.curRule.serviceName
                const emptyObj = {
                    protocolList: [],
                    TCP: [],
                    HTTP: [],
                    UDP: [],
                    HTTPS: []
                }
                const matchItem = this.serviceList.find(service => {
                    return service.name === serviceName
                })
                return matchItem || emptyObj
            }
        },
        watch: {
            curIngress () {
                this.curRuleIndex = 0
                this.curRule = this.curIngress.config.webCache.rules[0]
            }
        },
        created () {
            this.initPageConf()
            this.getIngressList()
        },
        methods: {
            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.getIngressList()
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
                this.pageChangeHandler()
            },

            /**
             * 确认批量删除
             */
            async removeIngresses () {
                const data = []
                const names = []

                this.ingressList.forEach(item => {
                    if (item.isChecked) {
                        data.push({
                            cluster_id: item.cluster_id,
                            namespace: item.namespace,
                            name: item.name
                        })
                        names.push(`${item.cluster_name} / ${item.namespace} / ${item.resourceName}`)
                    }
                })

                if (!data.length) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择要删除的Ingress')
                    })
                    return false
                }

                this.batchDialogConfig.list = names
                this.batchDialogConfig.data = data
                this.batchDialogConfig.isShow = true
            },

            /**
             * 批量删除
             * @param  {object} data ingresses
             */
            async deleteIngresses (data) {
                const me = this
                const projectId = this.projectId

                this.batchDialogConfig.isShow = false
                this.isPageLoading = true
                try {
                    await this.$store.dispatch('resource/deleteMesosIngresses', {
                        projectId,
                        data
                    })
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除成功')
                    })
                    // 稍晚一点加载数据，接口不一定立即清除
                    setTimeout(() => {
                        me.getIngressList()
                    }, 500)
                } catch (e) {
                    // 4004，已经被删除过，但接口不能立即清除，再重新拉数据，防止重复删除
                    if (e.code === 4004) {
                        me.isPageLoading = true
                        setTimeout(() => {
                            me.getIngressList()
                        }, 500)
                    } else {
                        this.isPageLoading = false
                    }
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 确认删除ingress
             * @param  {object} ingress ingress
             */
            async removeIngress (ingress) {
                if (!ingress.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: ingress.namespace_id,
                        resource_name: ingress.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                const me = this
                me.$bkInfo({
                    title: ``,
                    clsName: 'biz-remove-dialog max-size',
                    content: me.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除Ingress')}【${ingress.cluster_name} / ${ingress.namespace} / ${ingress.name}】？`),
                    confirmFn () {
                        me.deleteIngress(ingress)
                    }
                })
            },

            /**
             * 删除ingress
             * @param  {object} ingress ingress
             */
            async deleteIngress (ingress) {
                const me = this
                const projectId = me.projectId
                const clusterId = ingress.cluster_id
                const namespace = ingress.namespace
                const name = ingress.name

                this.isPageLoading = true
                try {
                    await this.$store.dispatch('resource/deleteMesosIngress', {
                        projectId,
                        clusterId,
                        namespace,
                        name
                    })
                    me.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除成功')
                    })
                    // 稍晚一点加载数据，接口不一定立即清除
                    setTimeout(() => {
                        me.getIngressList()
                    }, 500)
                } catch (e) {
                    this.isPageLoading = false
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 显示ingress详情
             * @param  {object} ingress object
             * @param  {number} index 索引
             */
            async showIngressDetail (ingress, index) {
                if (!ingress.permissions.view) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'view',
                        resource_code: ingress.namespace_id,
                        resource_name: ingress.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                const rules = []
                const labels = []

                for (const key in ingress.config.spec) {
                    const types = ingress.spec[key]
                    types.forEach(item => {
                        item.protocol = key
                        rules.push(item)
                    })
                }

                for (const key in ingress.config.metadata.labels) {
                    labels.push({
                        key: key,
                        value: ingress.config.metadata.labels[key]
                    })
                }

                ingress.rules = rules
                ingress.labels = labels
                this.ingressSlider.title = ingress.name
                this.curIngress = ingress
                this.ingressSlider.isShow = true
            },

            /**
             * 清除选择，在分页改变时触发
             */
            clearSelectIngress () {
                this.curPageData.forEach((item) => {
                    item.isChecked = false
                })
            },

            /**
             * 获取Ingresslist
             */
            async getIngressList () {
                const projectId = this.projectId
                try {
                    await this.$store.dispatch('resource/getMesosIngressList', projectId)
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)
                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchScope || this.searchKeyword) {
                        this.searchIngress()
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
             * 清除搜索
             */
            clearSearch () {
                this.searchKeyword = ''
                this.searchIngress()
            },

            /**
             * 搜索Ingress
             */
            searchIngress () {
                const keyword = this.searchKeyword.trim()
                const keyList = ['name', 'namespace', 'cluster_name']
                let list = JSON.parse(JSON.stringify(this.$store.state.resource.ingressList))
                const results = []

                if (this.searchScope) {
                    list = list.filter(item => {
                        return item.cluster_id === this.searchScope
                    })
                }

                list.forEach(item => {
                    item.isChecked = false
                    for (const key of keyList) {
                        if (item[key] && item[key].indexOf(keyword) > -1) {
                            results.push(item)
                            return true
                        }
                    }
                })

                this.ingressList.splice(0, this.ingressList.length, ...results)
                this.pageConf.curPage = 1
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.ingressList.length
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
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
                if (page < 1) {
                    this.pageConf.curPage = page = 1
                }
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                this.isPageLoading = true
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.ingressList.length) {
                    endIndex = this.ingressList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.ingressList.slice(startIndex, endIndex)
            },

            /**
             * 页数改变回调
             * @param  {number} page 第几页
             */
            pageChangeHandler (page = 1) {
                this.pageConf.curPage = page

                const data = this.getDataByPage(page)
                this.curPageData = data
            },

            /**
             * 每行的多选框点击事件
             */
            rowClick () {
                this.$nextTick(() => {
                    this.alreadySelectedNums = this.ingressList.filter(item => item.isChecked).length
                })
            },

            async showIngressEditDialog (ingress) {
                if (!ingress.permissions.edit) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'edit',
                        resource_code: ingress.namespace_id,
                        resource_name: ingress.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }
  
                this.curIngress = ingress
                this.ingressEditSlider.isShow = true
                this.ingressEditSlider.title = ingress.name
                this.initServiceList()
            },

            async handlerRegionSelect (data, params, isInitTrigger) {
                const region = data
                const projectId = this.projectId
                try {
                    const res = await this.$store.dispatch('network/getCloudLoadBalanceNames', { projectId, region })
                    this.clbList = []
                    res.data.forEach(item => {
                        this.clbList.push({
                            id: item,
                            name: item
                        })
                    })
                    if (!isInitTrigger) {
                        this.curIngress.config.metadata.labels['bmsf.tencent.com/clbname'] = ''
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            toggleHttpsEnable () {
                this.curRule.httpsEnabled = !this.curRule.httpsEnabled
            },
            toggleHealcheckEnable () {
                this.curRule.healthCheck.enabled = !this.curRule.healthCheck.enabled
            },
            handlePortChange (index, data) {
                if (this.curRule.serviceType === 'HTTP') {
                    this.curRule.host = data.domainName
                    this.curRule.path = data.path
                }
            },
            handleServiceNameChange () {
                this.curRule.serviceType = ''
                this.curRule.servicePort = ''
                this.curRule.host = ''
                this.curRule.path = '/'
            },
            handleProtocolChange () {
                this.curRule.servicePort = ''
                this.curRule.host = ''
                this.curRule.path = '/'

                this.curRule.httpsEnabled = false
                this.tls = {
                    mode: 'unidirectional',
                    certId: ''
                }
            },

            async initServiceList () {
                const templateId = this.templateId
                const projectId = this.projectId
                const version = this.curIngress.config.metadata.labels['io.tencent.bcs.latest.version.id']

                if (!version) {
                    this.serviceList = []
                    return false
                }

                try {
                    const res = await this.$store.dispatch('mesosTemplate/getServicesByVersion', {
                        projectId,
                        templateId,
                        version
                    })
                    res.data.forEach(item => {
                        const protocolList = []
                        item.protocolList = []
                        item.port.forEach(port => {
                            const protocol = port.protocol
                            protocolList.push(protocol)
                            if (!item[protocol]) {
                                item[protocol] = []
                            }
                            item[protocol].push(port)
                        })
                        const uniqueList = [...new Set(protocolList)]
                        uniqueList.forEach(protocol => {
                            item.protocolList.push({
                                id: protocol,
                                name: protocol
                            })
                        })
                    })
                    this.serviceList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            removeRule (index) {
                const rules = this.curIngress.config.webCache.rules
                rules.splice(index, 1)
                if (this.curRuleIndex === index) {
                    this.curRuleIndex = 0
                } else if (this.curRuleIndex > index) {
                    this.curRuleIndex = this.curRuleIndex - 1
                }
                this.curRule = rules[this.curRuleIndex]
            },

            addLocalRule () {
                const rule = JSON.parse(JSON.stringify(ruleParams))
                const rules = this.curIngress.config.webCache.rules
                const index = rules.length

                rule.name = 'rule-' + (index + 1)
                rule.namespace = this.curIngress.namespace
                rules.push(rule)
                this.setCurRule(rule, index)
            },

            setCurRule (rule, index) {
                this.curRule = rule
                this.curRuleIndex = index
            },

            checkIngressData (ingress) {
                const ingressName = ingress.config.metadata.name
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,29}$/
                let megPrefix = `"${ingressName}"${this.$t('中')}`

                if (ingressName === '') {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }

                if (!nameReg1.test(ingressName)) {
                    megPrefix += this.$t('名称：')
                    this.$bkMessage({
                        theme: 'error',
                        message: megPrefix + this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符'),
                        delay: 8000
                    })
                    return false
                }

                // if (!ingress.config.metadata.labels['io.tencent.bcs.clb.region']) {
                //     megPrefix += this.$t('区域：')
                //     this.$bkMessage({
                //         theme: 'error',
                //         message: this.$t('请选择区域')
                //     })
                //     return false
                // }

                if (!ingress.config.metadata.labels['bmsf.tencent.com/clbname']) {
                    megPrefix += this.$t('CLB')
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择CLB')
                    })
                    return false
                }
                
                const rules = ingress.config.webCache.rules
                for (const rule of rules) {
                    if (!rule.serviceName) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的Service名称：请选择Service名称', rule),
                            delay: 8000
                        })
                        return false
                    }

                    if (!rule.serviceType) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的协议：请选择协议', rule),
                            delay: 8000
                        })
                        return false
                    }

                    if (!rule.servicePort) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的端口：请选择端口', rule),
                            delay: 8000
                        })
                        return false
                    }

                    if (!rule.clbPort) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的监听CLB端口：请输入监听CLB端口', rule),
                            delay: 8000
                        })
                        return false
                    }

                    if (rule.sessionTime && (rule.sessionTime < 30 || rule.sessionTime > 3600)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('规则"{name}"的会话保持时间：会话保持时间范围为30-3600', rule),
                            delay: 8000
                        })
                        return false
                    }
                }

                return true
            },

            formatIngressData (ingress) {
                const params = JSON.parse(JSON.stringify(ingress))
                const spec = params.config.spec
                spec.tcp = []
                spec.udp = []
                spec.http = []
                spec.https = []
                params.config.webCache.rules.forEach(data => {
                    const rule = JSON.parse(JSON.stringify(data))

                    if (rule.sessionTime === '') {
                        delete rule.sessionTime
                    }
                    switch (rule.serviceType) {
                        case 'TCP':
                            delete rule.serviceType
                            delete rule.tls
                            delete rule.host
                            delete rule.path
                            delete rule.healthCheck.httpCode
                            delete rule.healthCheck.httpCheckPath
                            delete rule.httpsEnabled
                            spec.tcp.push(rule)
                            break

                        case 'UDP':
                            delete rule.serviceType
                            delete rule.tls
                            delete rule.host
                            delete rule.path
                            delete rule.healthCheck.httpCode
                            delete rule.healthCheck.httpCheckPath
                            delete rule.httpsEnabled
                            spec.udp.push(rule)
                            break

                        case 'HTTP':
                            delete rule.serviceType
                            if (rule.httpsEnabled) {
                                delete rule.httpsEnabled
                                spec.https.push(rule)
                            } else {
                                delete rule.httpsEnabled
                                delete rule.tls
                                spec.http.push(rule)
                            }
                            break

                        case 'HTTPS':
                            delete rule.serviceType
                            delete rule.httpsEnabled
                            spec.https.push(rule)
                            break
                    }
                })
                delete params.isEdited
                delete params.cache
                return params
            },

            handleUpdateIngress () {
                if (this.checkIngressData(this.curIngress)) {
                    const ingress = this.formatIngressData(this.curIngress)
                    this.updateIngress(ingress)
                }
            },

            handleCancelUpdate () {
                this.ingressEditSlider.isShow = false
            },

            async updateIngress (ingress) {
                const me = this
                const projectId = me.projectId
                const clusterId = ingress.cluster_id
                const namespace = ingress.namespace
                const name = ingress.name
                try {
                    await this.$store.dispatch('resource/updateMesosIngress', {
                        projectId,
                        clusterId,
                        namespace,
                        name,
                        data: ingress
                    })
                    me.$bkMessage({
                        theme: 'success',
                        message: this.$t('更新成功')
                    })
                    this.ingressEditSlider.isShow = false
                    // 稍晚一点加载数据，接口不一定立即清除
                    setTimeout(() => {
                        me.getIngressList()
                    }, 500)
                } catch (e) {
                    this.isPageLoading = false
                    catchErrorHandler(e, this)
                }
            },
            handleModeSelect () {
                this.curRule.tls.certCaId = ''
            }
        }
    }
</script>

<style scoped>
    @import '../../ingress.css';
</style>
