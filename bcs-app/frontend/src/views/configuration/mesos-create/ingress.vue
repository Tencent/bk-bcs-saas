<template>
    <div class="biz-content">
        <biz-header ref="commonHeader"
            @exception="exceptionHandler"
            @saveIngressSuccess="saveIngressSuccess"
            @switchVersion="initResource">
        </biz-header>
        <template>
            <div class="biz-content-wrapper biz-confignation-wrapper" v-bkloading="{ isLoading: isTemplateSaving }">
                <app-exception
                    v-if="exceptionCode && !isDataLoading"
                    :type="exceptionCode.code"
                    :text="exceptionCode.msg">
                </app-exception>
                <div class="biz-tab-box" v-else v-show="!isDataLoading">
                    <biz-tabs @tab-change="tabResource" ref="commonTab"></biz-tabs>

                    <div class="biz-tab-content" v-bkloading="{ isLoading: isTabChanging }">
                        <template v-if="!ingresss.length">
                            <p class="biz-template-tip f12 mb10">
                                {{$t('Ingress是用来管理从CLB访问集群内服务的对象，可将集群内部Service通过CLB向外暴露，并设置CLB端口的详细参数，CloudLoadbalancer负责实施Ingress')}}
                            </p>
                            <div class="biz-guide-box mt0" style="padding: 140px 30px;">
                                <bk-button type="primary" @click.stop.prevent="addLocalIngress">
                                    <i class="bcs-icon bcs-icon-plus"></i>
                                    <span style="margin-left: 0;">{{$t('添加')}}Ingress</span>
                                </bk-button>
                            </div>
                        </template>

                        <template v-else>
                            <div class="biz-configuration-topbar">
                                <p class="biz-template-tip f12 mb10">
                                    {{$t('Ingress是用来管理从CLB访问集群内服务的对象，可将集群内部Service通过CLB向外暴露，并设置CLB端口的详细参数，CloudLoadbalancer负责实施Ingress')}}
                                </p>
                                <div class="biz-list-operation">
                                    <div class="item" v-for="(ingress, index) in ingresss" :key="ingress.id">
                                        <bk-button :class="['bk-button', { 'bk-primary': curIngress.id === ingress.id }]" @click.stop="setCurIngress(ingress, index)">
                                            {{(ingress && ingress.config.metadata.name) || $t('未命名')}}
                                            <span class="biz-update-dot" v-show="ingress.isEdited"></span>
                                        </bk-button>
                                        <span class="bcs-icon bcs-icon-close" @click.stop="removeIngress(ingress, index)"></span>
                                    </div>

                                    <bcs-popover ref="ingressTooltip" :content="$t('添加Ingress')" placement="top">
                                        <bk-button class="bk-button bk-default is-outline is-icon" @click.stop="addLocalIngress">
                                            <i class="bcs-icon bcs-icon-plus"></i>
                                        </bk-button>
                                    </bcs-popover>
                                </div>
                            </div>

                            <div class="biz-configuration-content" style="position: relative;">
                                <div class="bk-form biz-configuration-form">
                                    <a href="javascript:void(0);" class="bk-text-button from-json-btn" @click.stop.prevent="showJsonPanel"></a>

                                    <!-- <bk-sideslider
                                        :is-show.sync="toJsonDialogConf.isShow"
                                        :title="toJsonDialogConf.title"
                                        :width="toJsonDialogConf.width"
                                        :quick-close="false"
                                        class="biz-app-rule-tojson-sideslider"
                                        @hidden="closeToJson">
                                        <div slot="content" style="position: relative;">
                                            <div class="biz-log-box" :style="{ height: `${winHeight - 60}px` }" v-bkloading="{ isLoading: toJsonDialogConf.loading }">
                                                <bk-button class="bk-button bk-primary save-json-btn" @click.stop.prevent="saveApplicationJson">{{$t('导入')}}</bk-button>
                                                <bk-button class="bk-button bk-default hide-json-btn" @click.stop.prevent="hideApplicationJson">{{$t('取消')}}</bk-button>
                                                <ace
                                                    :value="editorConfig.value"
                                                    :width="editorConfig.width"
                                                    :height="editorConfig.height"
                                                    :lang="editorConfig.lang"
                                                    :read-only="editorConfig.readOnly"
                                                    :full-screen="editorConfig.fullScreen"
                                                    @init="editorInitAfter">
                                                </ace>
                                            </div>
                                        </div>
                                    </bk-sideslider> -->

                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 130px;">{{$t('名称')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <input
                                                type="text"
                                                :class="['bk-form-input',{ 'is-danger': errors.has('ingressName') }]"
                                                :placeholder="$t('请输入64个以内的字符')"
                                                style="width: 310px;"
                                                maxlength="64"
                                                v-model="curIngress.config.metadata.name"
                                                name="ingressName"
                                                v-validate="{ required: true, regex: /^[a-z]{1}[a-z0-9-]{0,63}$/ }">
                                            <div class="bk-form-tip" v-if="errors.has('ingressName')">
                                                <p class="bk-tip-text">{{$t('名称必填，以字母开头，只能含小写字母、数字、连字符(-)')}}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="bk-form-item">
                                        <div class="bk-form-content" style="margin-left: 0;">
                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 130px;">{{$t('区域')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 130px;">
                                                    <bk-selector
                                                        style="width: 310px;"
                                                        :placeholder="$t('请选择')"
                                                        :selected.sync="curIngress.config.metadata.labels['io.tencent.bcs.clb.region']"
                                                        :list="regionList"
                                                        :searchable="true"
                                                        :setting-key="'region'"
                                                        :search-key="'region_name'"
                                                        :display-key="'region_name'"
                                                        :is-link="true"
                                                        @item-selected="handlerRegionSelect">
                                                    </bk-selector>
                                                </div>
                                            </div>

                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 201px;">CLB：</label>
                                                <div class="bk-form-content" style="margin-left: 201px;">
                                                    <bk-selector
                                                        style="width: 310px;"
                                                        :placeholder="$t('请选择')"
                                                        :selected.sync="curIngress.config.metadata.labels['bmsf.tencent.com/clbname']"
                                                        :list="clbList">
                                                    </bk-selector>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="biz-part-header">
                                    <div class="bk-button-group">
                                        <div class="item" v-for="(rule, index) in curIngress.config.webCache.rules" :key="index">
                                            <bk-button
                                                :class="['bk-button bk-default is-outline', { 'is-selected': curRuleIndex === index }]"
                                                @click.stop="setCurRule(rule, index)">
                                                {{rule.name || $t('未命名')}}
                                            </bk-button>
                                            <span
                                                class="bcs-icon bcs-icon-close-circle"
                                                @click.stop="removeRule(index)"
                                                v-if="curIngress.config.webCache.rules.length > 1">
                                            </span>
                                        </div>
                                        <bcs-popover
                                            ref="ruleTooltip"
                                            placement="top"
                                            :content="$t('添加规则')">
                                            <bk-button
                                                type="button"
                                                class="bk-button bk-default is-outline is-icon"
                                                @click.stop.prevent="addLocalRule">
                                                <i class="bcs-icon bcs-icon-plus"></i>
                                            </bk-button>
                                        </bcs-popover>
                                    </div>
                                </div>

                                <div class="bk-form biz-configuration-form pb15">
                                    <div class="biz-span">
                                        <span class="title">{{$t('基础信息')}}</span>
                                    </div>
                                    <div class="bk-form-item">
                                        <div class="bk-form-content" style="margin-left: 0;">
                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 135px;">{{$t('类型')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bk-selector
                                                        style="width: 182px;"
                                                        :placeholder="$t('请选择')"
                                                        :selected.sync="curRule.type"
                                                        :list="typeList">
                                                    </bk-selector>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="bk-form-item">
                                        <div class="bk-form-content" style="margin-left: 0;">
                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 135px;">{{$t('Service名称')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bk-selector
                                                        style="width: 182px;"
                                                        :placeholder="$t('请选择')"
                                                        :setting-key="'name'"
                                                        :selected.sync="curRule.serviceName"
                                                        :list="serviceList"
                                                        @item-selected="handleServiceNameChange">
                                                    </bk-selector>
                                                </div>
                                            </div>

                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 135px;">{{$t('协议')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bk-selector
                                                        style="width: 182px;"
                                                        :placeholder="$t('请选择')"
                                                        :disabled="curRule.type === 'service' && !curRule.serviceName"
                                                        :setting-key="'id'"
                                                        :selected.sync="curRule.serviceType"
                                                        :list="curProtocol.protocolList"
                                                        @item-selected="handleProtocolChange">
                                                    </bk-selector>
                                                </div>
                                            </div>

                                            <div class="bk-form-inline-item is-required" v-if="isServiceType">
                                                <label class="bk-label" style="width: 135px;">{{$t('端口')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bk-selector
                                                        style="width: 182px;"
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
                                                <label class="bk-label" style="width: 135px;">{{$t('域名')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bkbcs-input
                                                        style="width: 182px;"
                                                        :placeholder="$t('请输入')"
                                                        :value.sync="curRule.host"
                                                        :disabled="isServiceType">
                                                    </bkbcs-input>
                                                </div>
                                            </div>

                                            <div class="bk-form-inline-item">
                                                <label class="bk-label" style="width: 135px;">{{$t('路径')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bkbcs-input
                                                        style="width: 182px;"
                                                        :placeholder="$t('请输入')"
                                                        :value.sync="curRule.path"
                                                        :disabled="isServiceType">
                                                    </bkbcs-input>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="bk-form-item">
                                        <div class="bk-form-content" style="margin-left: 0;">
                                            <div class="bk-form-inline-item is-required" v-if="isServiceType">
                                                <label class="bk-label" style="width: 135px;">{{$t('监听CLB端口')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bkbcs-input
                                                        type="number"
                                                        :placeholder="'1-65535'"
                                                        style="width: 182px;"
                                                        :min="1"
                                                        :max="65535"
                                                        :value.sync="curRule.clbPort"
                                                        :list="varList">
                                                    </bkbcs-input>
                                                </div>
                                            </div>

                                            <div class="bk-form-inline-item">
                                                <label class="bk-label" style="width: 135px;">{{$t('会话保持时间')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <div class="bk-form-input-group">
                                                        <bkbcs-input
                                                            type="number"
                                                            :placeholder="'30-3600'"
                                                            style="width: 146px;"
                                                            :min="0"
                                                            :max="3600"
                                                            :value.sync="curRule.sessionTime"
                                                            :list="varList"
                                                            @change="handleSessionTimeChange">
                                                        </bkbcs-input>
                                                        <span class="input-group-addon">
                                                            {{$t('秒')}}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="bk-form-inline-item">
                                                <label class="bk-label" style="width: 135px;">{{$t('负载均衡策略')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bk-selector
                                                        style="width: 182px;"
                                                        :placeholder="$t('请选择')"
                                                        :setting-key="'id'"
                                                        :selected.sync="curRule.lbPolicy.strategy"
                                                        :list="strategyList">
                                                    </bk-selector>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="bk-form-item" v-if="!isServiceType">
                                        <div class="bk-form-content" style="margin-left: 0;">
                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 135px;">{{$t('CLB起始端口')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bkbcs-input
                                                        type="number"
                                                        :placeholder="$t('请输入')"
                                                        style="width: 182px;"
                                                        :max="32000"
                                                        :value.sync="curRule.startPort">
                                                    </bkbcs-input>
                                                </div>
                                            </div>
                                            
                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 135px;">{{$t('起始索引')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bkbcs-input
                                                        type="number"
                                                        :placeholder="$t('请输入')"
                                                        style="width: 182px;"
                                                        :min="0"
                                                        :value.sync="curRule.startIndex">
                                                    </bkbcs-input>
                                                </div>
                                            </div>
                                            
                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 135px;">{{$t('终止索引')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                    <bkbcs-input
                                                        type="number"
                                                        :placeholder="$t('请输入')"
                                                        style="width: 182px;"
                                                        :min="0"
                                                        :value.sync="curRule.endIndex">
                                                    </bkbcs-input>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="bk-form-item">
                                        <div class="bk-form-content" style="margin-left: 0;">
                                            <div class="bk-form-inline-item">
                                                <label class="bk-label" style="width: 135px;">{{$t('健康检查策略')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 135px;">
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
                                                                        <bkbcs-input
                                                                            type="number"
                                                                            style="width: 150px;"
                                                                            :placeholder="'2-60'"
                                                                            :min="2"
                                                                            :max="60"
                                                                            :value.sync="curRule.healthCheck.timeout"
                                                                            :list="varList">
                                                                        </bkbcs-input>
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
                                                                        <!-- 处理限制为30 -->
                                                                        <bkbcs-input
                                                                            type="number"
                                                                            style="width: 150px;"
                                                                            :placeholder="'5-300'"
                                                                            :min="5"
                                                                            :max="300"
                                                                            :value.sync="curRule.healthCheck.intervalTime"
                                                                            :list="varList">
                                                                        </bkbcs-input>
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
                                                                        <bkbcs-input
                                                                            type="number"
                                                                            style="width: 150px;"
                                                                            :placeholder="'2-10'"
                                                                            :min="2"
                                                                            :max="10"
                                                                            :value.sync="curRule.healthCheck.healthNum"
                                                                            :list="varList">
                                                                        </bkbcs-input>
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
                                                                        <bkbcs-input
                                                                            type="number"
                                                                            style="width: 150px;"
                                                                            :placeholder="'2-10'"
                                                                            :min="2"
                                                                            :max="10"
                                                                            :value.sync="curRule.healthCheck.unHealthNum"
                                                                            :list="varList">
                                                                        </bkbcs-input>
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
                                                                    <bkbcs-input
                                                                        style="width: 182px;"
                                                                        :placeholder="$t('请输入')"
                                                                        :value.sync="curRule.healthCheck.httpCheckPath"
                                                                        :list="varList">
                                                                    </bkbcs-input>
                                                                </div>
                                                            </div>

                                                            <div class="bk-form-inline-item">
                                                                <label class="bk-label" style="width: 200px;">{{$t('健康状态码')}}：</label>
                                                                <div class="bk-form-content" style="margin-left: 200px;">
                                                                    <bkbcs-input
                                                                        type="number"
                                                                        style="width: 182px;"
                                                                        :placeholder="$t('请输入')"
                                                                        :min="0"
                                                                        :value.sync="curRule.healthCheck.httpCode"
                                                                        :list="varList">
                                                                    </bkbcs-input>
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
                                                                <label class="bk-label" style="width: 92px;">{{$t('认证模式')}}：</label>
                                                                <div class="bk-form-content" style="margin-left: 92px;">
                                                                    <bk-selector
                                                                        style="width: 140px;"
                                                                        :placeholder="$t('请选择')"
                                                                        :setting-key="'id'"
                                                                        :selected.sync="curRule.tls.mode"
                                                                        :list="tlsModeList"
                                                                        @item-selected="handleModeSelect">
                                                                    </bk-selector>
                                                                </div>
                                                            </div>

                                                            <div class="bk-form-inline-item">
                                                                <label class="bk-label" style="width: 100px;">{{$t('证书ID')}}：</label>
                                                                <div class="bk-form-content" style="margin-left: 100px;">
                                                                    <bkbcs-input
                                                                        style="width: 140px;"
                                                                        :placeholder="$t('请输入')"
                                                                        :value.sync="curRule.tls.certId"
                                                                        :list="varList">
                                                                    </bkbcs-input>
                                                                </div>
                                                            </div>

                                                            <div class="bk-form-inline-item" v-if="curRule.tls.mode === 'mutual'">
                                                                <label class="bk-label" style="width: 140px;">{{$t('客户端证书ID')}}：</label>
                                                                <div class="bk-form-content" style="margin-left: 140px;">
                                                                    <bkbcs-input
                                                                        style="width: 140px;"
                                                                        :placeholder="$t('请输入')"
                                                                        :key="curRule.tls.mode"
                                                                        :value.sync="curRule.tls.certCaId"
                                                                        :list="varList">
                                                                    </bkbcs-input>
                                                                    <bcs-popover
                                                                        :content="$t('如果mode=mutual，客户端证书ID为必填项')"
                                                                        placement="top">
                                                                        <span class="bk-badge">
                                                                            <i class="bcs-icon bcs-icon-question-circle"></i>
                                                                        </span>
                                                                    </bcs-popover>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </section>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </template>
    </div>
</template>

<script>
    import ingressParams from '@open/json/ingress.json'
    import ruleParams from '@open/json/ingress-rule.json'
    import { catchErrorHandler } from '@open/common/util'
    import header from './header.vue'
    import tabs from './tabs.vue'
    import _ from 'lodash'
    export default {
        async beforeRouteLeave (to, from, next) {
            // 修改模板集信息
            // await this.$refs.commonHeader.saveTemplate()
            clearInterval(this.compareTimer)
            this.updateIngressDatas()
            next(true)
        },
        components: {
            'biz-header': header,
            'biz-tabs': tabs
        },
        data () {
            return {
                isTabChanging: false,
                winHeight: 0,
                curRuleIndex: 0,
                exceptionCode: null,
                isDataLoading: true,
                isDataSaveing: false,
                curIngressCache: Object.assign({}, ingressParams),
                compareTimer: 0, // 定时器，查看用户是否有修改
                curIngress: ingressParams,
                curRule: ingressParams.config.webCache.rules[0],
                content: 'hello',
                curKeyIndex: 0,
                curKeyParams: null,
                toJsonDialogConf: {
                    isShow: false,
                    title: '',
                    timer: null,
                    width: 800,
                    loading: false
                },
                editorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'json',
                    readOnly: false,
                    fullScreen: false,
                    value: '',
                    editor: null
                },
                clbList: [],
                serviceList: [],
                typeList: [
                    {
                        id: 'service',
                        name: this.$t('service转发')
                    },
                    {
                        id: 'port',
                        name: this.$t('端口段映射')
                    }
                ],
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
                regionList: []
            }
        },
        computed: {
            varList () {
                return this.$store.state.variable.varList
            },
            isTemplateSaving () {
                return this.$store.state.mesosTemplate.isTemplateSaving
            },
            curTemplate () {
                return this.$store.state.mesosTemplate.curTemplate
            },
            applications () {
                return this.$store.state.mesosTemplate.applications
            },
            deployments () {
                return this.$store.state.mesosTemplate.deployments
            },
            curVersion () {
                return this.$store.state.mesosTemplate.curVersion
            },
            services () {
                return this.$store.state.mesosTemplate.services
            },
            configmaps () {
                return this.$store.state.mesosTemplate.configmaps
            },
            secrets () {
                return this.$store.state.mesosTemplate.secrets
            },
            ingresss () {
                return this.$store.state.mesosTemplate.ingresss
            },
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            templateId () {
                return this.$route.params.templateId
            },
            curProtocol () {
                if (this.curRule.type === 'port') {
                    return {
                        protocolList: [{
                            id: 'TCP',
                            name: 'TCP'
                        }, {
                            id: 'UDP',
                            name: 'UDP'
                        }, {
                            id: 'HTTP',
                            name: 'HTTP'
                        }]
                    }
                }
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
            },
            isServiceType () {
                return this.curRule.type === 'service'
            }
        },
        watch: {
            curIngress () {
                this.curRuleIndex = 0
                this.curRule = this.curIngress.config.webCache.rules[0]
            }
        },
        mounted () {
            this.$refs.commonHeader.initTemplate((data) => {
                this.initResource(data)
                this.initServiceList()
                this.getRegions()
                this.isDataLoading = false
            })
            this.winHeight = window.innerHeight
        },
        methods: {
            exceptionHandler (exceptionCode) {
                this.isDataLoading = false
                this.exceptionCode = exceptionCode
            },
            editorInit () {
            },
            setCurIngress (ingress) {
                // 切换到当前项
                this.curIngress = ingress

                clearInterval(this.compareTimer)
                clearTimeout(this.setTimer)
                this.setTimer = setTimeout(() => {
                    if (!this.curIngress.cache) {
                        this.curIngress.cache = JSON.parse(JSON.stringify(ingress))
                    }
                    this.watchChange()
                }, 500)
            },
            watchChange () {
                this.compareTimer = setInterval(() => {
                    const appCopy = JSON.parse(JSON.stringify(this.curIngress))

                    const cacheCopy = JSON.parse(JSON.stringify(this.curIngress.cache))
                    // 删除无用属性
                    delete appCopy.isEdited
                    delete appCopy.cache
                    delete appCopy.id

                    delete cacheCopy.isEdited
                    delete cacheCopy.cache
                    delete cacheCopy.id

                    const appStr = JSON.stringify(appCopy)
                    const cacheStr = JSON.stringify(cacheCopy)

                    if (String(this.curIngress.id).indexOf('local_') > -1) {
                        this.curIngress.isEdited = true
                    } else if (appStr !== cacheStr) {
                        this.curIngress.isEdited = true
                    } else {
                        this.curIngress.isEdited = false
                    }
                }, 1000)
            },
            removeLocalIngress (service, index) {
                // 是否删除当前项
                if (this.curIngress.id === service.id) {
                    if (index === 0 && this.ingresss[index + 1]) {
                        this.setCurIngress(this.ingresss[index + 1])
                    } else if (this.ingresss[0]) {
                        this.setCurIngress(this.ingresss[0])
                    }
                }
                this.ingresss.splice(index, 1)
            },
            removeIngress (ingress, index) {
                const self = this
                const projectId = this.projectId
                const version = this.curVersion
                const ingressId = ingress.id

                this.$bkInfo({
                    title: this.$t('确认删除'),
                    content: this.$createElement('p', { style: { 'text-align': 'left' } }, `${this.$t('删除Ingress')}：${ingress.config.metadata.name || this.$t('未命名')}`),
                    confirmFn () {
                        if (ingressId.indexOf && ingressId.indexOf('local_') > -1) {
                            self.removeLocalIngress(ingress, index)
                        } else {
                            self.$store.dispatch('mesosTemplate/removeIngress', { ingressId, version, projectId }).then(res => {
                                const data = res.data

                                self.removeLocalIngress(ingress, index)

                                if (data.version) {
                                    self.$store.commit('mesosTemplate/updateCurVersion', data.version)
                                    self.$store.commit('mesosTemplate/updateBindVersion', true)
                                }
                            }, res => {
                                const message = res.message
                                self.$bkMessage({
                                    theme: 'error',
                                    message: message
                                })
                            })
                        }
                    }
                })
            },
            initServiceList () {
                const templateId = this.templateId
                const projectId = this.projectId
                const version = this.curTemplate.latest_version_id

                this.$store.dispatch('mesosTemplate/getServicesByVersion', {
                    projectId,
                    templateId,
                    version
                }).then(res => {
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
                }, res => {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                })
            },
            addLocalIngress () {
                const ingress = JSON.parse(JSON.stringify(ingressParams))
                const index = this.ingresss.length + 1
                const now = +new Date()
                ingress.id = 'local_' + now
                ingress.isEdited = true
                ingress.config.metadata.name = 'ingress-' + index
                this.ingresss.push(ingress)
                this.setCurIngress(ingress)
                this.$refs.ingressTooltip && (this.$refs.ingressTooltip.visible = false)
                this.$store.commit('mesosTemplate/updateIngresss', this.ingresss)
            },
            saveIngressSuccess (params) {
                this.ingresss.forEach(item => {
                    if (params.responseData.id === item.id || params.preId === item.id) {
                        item.cache = JSON.parse(JSON.stringify(item))
                    }
                })
                if (params.responseData.id === this.curIngress.id || params.preId === this.curIngress.id) {
                    this.updateLocalData(params.resource)
                }
            },
            updateLocalData (data) {
                if (data.id) {
                    this.curIngress.id = data.id
                }
                if (data.version) {
                    this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                }

                this.$store.commit('mesosTemplate/updateIngresss', this.ingresss)

                setTimeout(() => {
                    this.ingresss.forEach(item => {
                        if (item.id === data.id) {
                            this.setCurIngress(item)
                        }
                    })
                }, 500)
            },
            updateIngressDatas () {
                const keyObj = {}
                const keys = this.curIngress.ingressKeyList
                if (keys) {
                    for (const item of keys) {
                        keyObj[item.key] = {
                            content: item.content
                        }
                    }
                    this.curIngress.config.datas = keyObj
                }
            },
            initResource (data) {
                if (data.ingresss && data.ingresss.length) {
                    this.setCurIngress(data.ingresss[0], 0)
                } else if (data.ingress && data.ingress.length) {
                    this.setCurIngress(data.ingress[0], 0)
                }
            },
            async tabResource (type, target) {
                this.isTabChanging = true
                await this.$refs.commonHeader.saveTemplate()
                await this.$refs.commonHeader.autoSaveResource(type)
                this.$refs.commonTab.goResource(target)
            },
            showJsonPanel () {
                this.toJsonDialogConf.title = this.curIngress.config.metadata.name + '.json'
                const appConfig = JSON.parse(JSON.stringify(this.curIngress.config))
                delete appConfig.webCache

                const jsonStr = JSON.stringify(appConfig, null, 4)
                this.editorConfig.value = jsonStr
                this.toJsonDialogConf.isShow = true
            },
            editorInitAfter (editor) {
                this.editorConfig.editor = editor
                this.editorConfig.editor.setStyle('biz-app-rule-tojson-ace')
            },
            setFullScreen () {
                this.editorConfig.fullScreen = !this.editorConfig.fullScreen
            },
            cancelFullScreen () {
                this.editorConfig.fullScreen = false
            },
            closeToJson () {
                this.toJsonDialogConf.isShow = false
                this.toJsonDialogConf.title = ''
                this.editorConfig.value = ''
            },
            getAppParamsKeys (obj, result) {
                for (const key in obj) {
                    if (key === 'datas') continue

                    if (Object.prototype.toString.call(obj) === '[object Array]') {
                        this.getAppParamsKeys(obj[key], result)
                    } else if (Object.prototype.toString.call(obj) === '[object Object]') {
                        if (!result.includes(key)) {
                            result.push(key)
                        }
                        this.getAppParamsKeys(obj[key], result)
                    }
                }
            },
            setCurRule (rule, index) {
                this.curRule = rule
                this.curRuleIndex = index
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
                rules.push(rule)
                this.setCurRule(rule, index)
                this.$refs.ruleTooltip.visible = false
            },
            checkJson (jsonObj) {
                const editor = this.editorConfig.editor
                const appParams = ingressParams.config
                const appParamKeys = [
                    'id'
                ]
                const jsonParamKeys = []
                this.getAppParamsKeys(appParams, appParamKeys)
                this.getAppParamsKeys(jsonObj, jsonParamKeys)

                // application查看无效字段
                for (const key of jsonParamKeys) {
                    if (!appParamKeys.includes(key)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: `${key}${this.$t('为无效字段')}`
                        })
                        const reg = new RegExp(`"${key}"`, 'ig')
                        const match = editor.find(reg)
                        if (match) {
                            editor.moveCursorTo(match.end.row, match.end.column)
                        }
                        return false
                    }
                }
                return true
            },
            hideApplicationJson () {
                this.toJsonDialogConf.isShow = false
            },
            saveApplicationJson () {
                const editor = this.editorConfig.editor
                const json = editor.getValue()
                let appObj = null
                if (!json) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入JSON')
                    })
                    return false
                }

                try {
                    appObj = JSON.parse(json)
                } catch (err) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入合法的JSON')
                    })
                    return false
                }

                const annot = editor.getSession().getAnnotations()
                if (annot && annot.length) {
                    editor.gotoLine(annot[0].row, annot[0].column, true)
                    return false
                }

                const newConfObj = _.merge({}, ingressParams.config, appObj)
                const jsonFromat = this.formatJson(newConfObj)
                this.curIngress.config = jsonFromat
                this.toJsonDialogConf.isShow = false
            },
            formatJson (jsonObj) {
                return jsonObj
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
            handleSessionTimeChange (value) {
                // sessionTime 为 0 表示关闭，取值范围 30 - 3600
                if (value > 0 && value < 30) {
                    this.curRule.sessionTime = 30
                }
            },
            handleModeSelect () {
                this.curRule.tls.certCaId = ''
            },
            /**
             * 获取区域列表
             */
            async getRegions () {
                const projectId = this.projectId

                try {
                    const res = await this.$store.dispatch('network/getRegions', { projectId })
                    this.regionList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            }
        }
    }
</script>

<style scoped>
    @import './ingress.css';
</style>
