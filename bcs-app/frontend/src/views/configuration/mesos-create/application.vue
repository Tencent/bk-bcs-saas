<template>
    <div class="biz-content">
        <biz-header ref="commonHeader"
            @exception="exceptionHandler"
            @saveApplicationSuccess="saveApplicationSuccess"
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
                    <biz-tabs @tabChange="tabResource"></biz-tabs>
                    <div class="biz-tab-content" v-bkloading="{ isLoading: isTabChanging }">
                        <div class="biz-configuration-topbar">
                            <div class="biz-list-operation">
                                <div class="item" v-for="(application, index) in applications" :key="application.id">
                                    <button :class="['bk-button', { 'bk-primary': curApplication.id === application.id }]" @click.stop="setCurApplication(application, index)">
                                        {{(application && application.config.metadata.name) || '未命名'}}
                                        <span class="biz-update-dot" v-show="application.isEdited"></span>
                                    </button>
                                    <span class="bk-icon icon-close" title="未保存" @click.stop="removeApplication(application, index)" v-if="applications.length > 1"></span>
                                </div>

                                <bk-tooltip ref="applicationTooltip" :content="'添加Application'" placement="top">
                                    <button class="bk-button bk-default is-outline is-icon" @click.stop="addLocalApplication">
                                        <i class="bk-icon icon-plus"></i>
                                    </button>
                                </bk-tooltip>
                            </div>
                        </div>
                        <div class="biz-configuration-content" style="position: relative;">
                            <!-- part1 start -->
                            <div class="bk-form biz-configuration-form">
                                <a href="javascript:void(0);" class="bk-text-button from-json-btn" @click.stop.prevent="showJsonPanel">导入JSON</a>

                                <bk-sideslider
                                    :is-show.sync="toJsonDialogConf.isShow"
                                    :title="toJsonDialogConf.title"
                                    :width="toJsonDialogConf.width"
                                    :quick-close="false"
                                    class="biz-app-container-tojson-sideslider"
                                    @hidden="closeToJson">
                                    <div slot="content" style="position: relative;">
                                        <div class="biz-log-box" :style="{ height: `${winHeight - 60}px` }" v-bkloading="{ isLoading: toJsonDialogConf.loading }">
                                            <bk-button class="bk-button bk-primary save-json-btn" @click.stop.prevent="saveApplicationJson">导入</bk-button>
                                            <bk-button class="bk-button bk-default hide-json-btn" @click.stop.prevent="hideApplicationJson">取消</bk-button>
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
                                </bk-sideslider>

                                <div class="bk-form-item">
                                    <div class="bk-form-item">
                                        <div class="bk-form-content" style="margin-left: 0;">
                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 105px;">应用名称：</label>
                                                <div class="bk-form-content" style="margin-left: 105px;">
                                                    <div class="bk-form-input-group">
                                                        <input type="text" :class="['bk-form-input',{ 'is-danger': errors.has('applicationName') }]" placeholder="请输入30个字符以内" style="width: 310px;" v-model="curApplication.config.metadata.name" maxlength="30" name="applicationName" v-validate="{ required: true, regex: /^[a-z]{1}[a-z0-9-]{0,29}$/ }">
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="bk-form-inline-item is-required">
                                                <label class="bk-label" style="width: 105px;">实例数量：</label>
                                                <div class="bk-form-content" style="margin-left: 105px;">
                                                    <div class="bk-form-input-group">
                                                        <bk-input
                                                            type="number"
                                                            placeholder="请输入"
                                                            style="width: 310px;"
                                                            :min="0"
                                                            :max="10000"
                                                            :value.sync="curApplication.config.spec.instance"
                                                            :list="varList"
                                                        >
                                                        </bk-input>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="bk-form-tip is-danger" style="margin-left: 105px;" v-if="errors.has('applicationName')">
                                                <p class="bk-tip-text">名称必填，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="bk-form-item">
                                    <label class="bk-label" style="width: 105px;">重要级别：</label>
                                    <div class="bk-form-content" style="margin-left: 105px;">
                                        <label class="bk-form-radio">
                                            <input type="radio" name="monitorlevel" value="important" v-model="curApplication.config.monitorLevel">
                                            <i class="bk-radio-text">重要</i>
                                        </label>
                                        <label class="bk-form-radio">
                                            <input type="radio" name="monitorlevel" value="general" v-model="curApplication.config.monitorLevel">
                                            <i class="bk-radio-text">一般</i>
                                        </label>
                                        <label class="bk-form-radio">
                                            <input type="radio" name="monitorlevel" value="unimportant" v-model="curApplication.config.monitorLevel">
                                            <i class="bk-radio-text">不重要</i>
                                        </label>
                                    </div>
                                </div>
                                <div class="bk-form-item">
                                    <label class="bk-label" style="width: 105px;">描述：</label>
                                    <div class="bk-form-content" style="margin-left: 105px;">
                                        <textarea class="bk-form-textarea" placeholder="请输入256个字符以内" v-model="curApplication.desc" maxlength="256"></textarea>
                                    </div>
                                </div>
                                <div class="bk-form-item">
                                    <div class="bk-form-content" style="margin-left: 105px;">
                                        <button :class="['bk-text-button f12 mb10 pl0', { 'rotate': isPartAShow }]" @click.stop.prevent="togglePartA">
                                            更多设置<i class="bk-icon icon-angle-double-down ml5"></i>
                                        </button>
                                        <bk-tab :type="'fill'" :active-name="'tab1'" :size="'small'" v-show="isPartAShow">
                                            <bk-tabpanel name="tab1" title="Restart策略">
                                                <div class="bk-form m20">
                                                    <div class="bk-form-item">
                                                        <label class="bk-label" style="width: 105px;">重启策略：</label>
                                                        <div class="bk-form-content" style="margin-left: 105px;">
                                                            <label class="bk-form-radio" v-for="(policy, index) in restartPolicy" :key="index">
                                                                <input type="radio" name="restartPolicy" :value="policy" v-model="curApplication.config.restartPolicy.policy">
                                                                <i class="bk-radio-text">{{policy}}</i>
                                                                <span v-if="policy === 'OnFailure'">(容器异常退出后，自动重新调度)</span>
                                                            </label>
                                                        </div>
                                                    </div>
                                                    <div class="bk-form-item" v-if="curApplication.config.restartPolicy.policy !== 'Never'">
                                                        <div class="bk-form-content" style="margin-left: 0;">
                                                            <div class="bk-form-inline-item">
                                                                <label class="bk-label" style="width: 105px;">重启间隔：</label>
                                                                <div class="bk-form-content" style="margin-left: 105px;">
                                                                    <div class="bk-form-input-group">
                                                                        <bk-input
                                                                            type="number"
                                                                            placeholder="请输入"
                                                                            style="width: 100px;"
                                                                            :min="0"
                                                                            :value.sync="curApplication.config.restartPolicy.interval"
                                                                            :list="varList"
                                                                        >
                                                                        </bk-input>
                                                                        <span class="input-group-addon">
                                                                            秒
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div class="bk-form-inline-item">
                                                                <label class="bk-label" style="width: 135px;">重启间隔步长：</label>
                                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                                    <div class="bk-form-input-group">
                                                                        <bk-input
                                                                            type="number"
                                                                            placeholder="请输入"
                                                                            style="width: 100px;"
                                                                            :min="0"
                                                                            :value.sync="curApplication.config.restartPolicy.backoff"
                                                                            :list="varList"
                                                                        >
                                                                        </bk-input>
                                                                        <span class="input-group-addon">
                                                                            秒
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div class="bk-form-inline-item">
                                                                <label class="bk-label" style="width: 135px;">最多重启次数：</label>
                                                                <div class="bk-form-content" style="margin-left: 135px;">
                                                                    <div class="bk-form-input-group">
                                                                        <bk-input
                                                                            type="number"
                                                                            placeholder="请输入"
                                                                            style="width: 100px;"
                                                                            :min="0"
                                                                            :value.sync="curApplication.config.restartPolicy.maxtimes"
                                                                            :list="varList"
                                                                        >
                                                                        </bk-input>
                                                                        <span class="input-group-addon">
                                                                            次
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </bk-tabpanel>
                                            <bk-tabpanel name="tab2" title="Kill策略">
                                                <div class="biz-tab-wrapper">
                                                    <div class="bk-form">
                                                        <div class="bk-form-item">
                                                            <label class="bk-label" style="width: 105px;">宽期限：</label>
                                                            <div class="bk-form-content" style="margin-left: 105px;">
                                                                <div class="bk-form-input-group">
                                                                    <bk-input
                                                                        type="number"
                                                                        placeholder="请输入"
                                                                        style="width: 100px;"
                                                                        :min="0"
                                                                        :value.sync="curApplication.config.killPolicy.gracePeriod"
                                                                        :list="varList"
                                                                    >
                                                                    </bk-input>
                                                                    <span class="input-group-addon">
                                                                        秒
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </bk-tabpanel>
                                            <bk-tabpanel name="tab3" title="备注">
                                                <div class="biz-tab-wrapper">
                                                    <bk-keyer :key-list.sync="curRemarkList" :var-list="varList" ref="remarkKeyer" @change="updateApplicationRemark"></bk-keyer>
                                                </div>
                                            </bk-tabpanel>
                                            <bk-tabpanel name="tab4" title="标签">
                                                <div class="biz-tab-wrapper">
                                                    <bk-keyer :key-list.sync="curLabelList" :var-list="varList" ref="labelKeyer" @change="updateApplicationLabel"></bk-keyer>
                                                </div>
                                            </bk-tabpanel>
                                            <bk-tabpanel name="tab5" title="调度约束">
                                                <div class="biz-tab-wrapper">
                                                    <table class="biz-simple-table">
                                                        <thead>
                                                            <tr>
                                                                <th style="width: 200px;">name</th>
                                                                <th style="width: 200px;">operator</th>
                                                                <th style="width: 250px;">value</th>
                                                                <th></th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            <tr class="bk-form" v-for="(item, index) in curApplication.config.constraint.intersectionItem" :key="index">
                                                                <td>
                                                                    <bk-combobox
                                                                        type="text"
                                                                        placeholder="请输入"
                                                                        style="width: 195px;"
                                                                        :value.sync="item.unionData[0].name"
                                                                        :display-key="'name'"
                                                                        :search-key="'name'"
                                                                        :setting-key="'id'"
                                                                        :list="constraintNameList"
                                                                        @input="selectConstraintName(...arguments, item)"
                                                                    >
                                                                    </bk-combobox>
                                                                </td>
                                                                <td>
                                                                    <template v-if="item.unionData[0].name !== 'ip-resources'">
                                                                        <bk-selector
                                                                            placeholder="请选择"
                                                                            :setting-key="'id'"
                                                                            :selected.sync="item.unionData[0].operate"
                                                                            :list="operatorList"
                                                                            @item-selected="selectOperate(item.unionData[0])">
                                                                        </bk-selector>
                                                                    </template>
                                                                    <template v-else>
                                                                        <bk-selector
                                                                            placeholder="请选择"
                                                                            :setting-key="'id'"
                                                                            :disabled="true"
                                                                            :selected.sync="item.unionData[0].operate"
                                                                            :list="operatorListForIP">
                                                                        </bk-selector>
                                                                    </template>
                                                                </td>
                                                                <td>
                                                                    <template v-if="item.unionData[0].name !== 'ip-resources'">
                                                                        <bk-input
                                                                            type="text"
                                                                            placeholder="多个值以管道符分隔"
                                                                            style="width: 250px;"
                                                                            :disabled="item.unionData[0].operate === 'UNIQUE'"
                                                                            :value.sync="item.unionData[0].arg_value"
                                                                            :list="varList"
                                                                        >
                                                                        </bk-input>
                                                                    </template>
                                                                    <template v-else>
                                                                        <bk-input
                                                                            type="number"
                                                                            placeholder="请输入"
                                                                            style="width: 250px;"
                                                                            :value.sync="item.unionData[0].arg_value"
                                                                            :list="varList"
                                                                        >
                                                                        </bk-input>
                                                                    </template>
                                                                </td>
                                                                <td>
                                                                    <div class="action-box">
                                                                        <button class="action-btn ml5" @click.stop.prevent="addConstraint()">
                                                                            <i class="bk-icon icon-plus"></i>
                                                                        </button>
                                                                        <button class="action-btn" @click.stop.prevent="removeConstraint(item, index)" v-show="curApplication.config.constraint.intersectionItem.length > 1">
                                                                            <i class="bk-icon icon-minus"></i>
                                                                        </button>
                                                                    </div>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </bk-tabpanel>
                                            <bk-tabpanel name="tab6" title="网络">
                                                <div class="biz-tab-wrapper">
                                                    <div class="bk-form">
                                                        <div class="bk-form-item">
                                                            <label class="bk-label" style="width: 105px;">网络模式：</label>
                                                            <div class="bk-form-content" style="margin-left: 105px;">
                                                                <div class="bk-dropdown-box" style="width: 200px;">
                                                                    <bk-selector
                                                                        placeholder="请选择"
                                                                        :setting-key="'id'"
                                                                        :display-key="'name'"
                                                                        :selected.sync="curApplication.config.spec.template.spec.networkMode"
                                                                        :list="netList"
                                                                        @item-selected="clearNetworkCustom">
                                                                    </bk-selector>
                                                                </div>
                                                                <transition name="fade">
                                                                    <input type="text" class="bk-form-input" style="width: 200px;" placeholder="自定义值" v-model="curApplication.config.spec.template.spec.custom_value" v-if="curApplication.config.spec.template.spec.networkMode === 'CUSTOM'">
                                                                </transition>
                                                            </div>
                                                        </div>
                                                        <div class="bk-form-item">
                                                            <label class="bk-label" style="width: 105px;">网络类型：</label>
                                                            <div class="bk-form-content" style="margin-left: 105px;">
                                                                <label class="bk-form-radio">
                                                                    <input type="radio" name="networkmodel" value="cni" v-model="curApplication.config.spec.template.spec.networkType" :disabled="curApplication.config.spec.template.spec.networkMode !== 'USER' && curApplication.config.spec.template.spec.networkMode !== 'CUSTOM'">
                                                                    <i class="bk-radio-text">cni</i>
                                                                </label>
                                                                <label class="bk-form-radio">
                                                                    <input type="radio" name="networkmodel" value="cnm" v-model="curApplication.config.spec.template.spec.networkType" :disabled="curApplication.config.spec.template.spec.networkMode === 'USER'">
                                                                    <i class="bk-radio-text">cnm</i>
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </bk-tabpanel>
                                        </bk-tab>
                                    </div>
                                </div>
                            </div>
                            <!-- part1 end -->

                            <!-- part2 start -->
                            <div class="biz-part-header" style="margin-left: 105px;">
                                <div class="bk-button-group">
                                    <div class="item" v-for="(container, index) in curApplication.config.spec.template.spec.containers" :key="index">
                                        <button :class="['bk-button bk-default is-outline', { 'is-selected': curContainerIndex === index }]" @click.stop="setCurContainer(container, index)">
                                            {{container.name || '未命名'}}
                                        </button>
                                        <span class="bk-icon icon-close-circle" @click.stop="removeContainer(index)" v-if="curApplication.config.spec.template.spec.containers.length > 1"></span>
                                    </div>
                                    <bk-tooltip ref="containerTooltip" :content="curApplication.config.spec.template.spec.containers.length >= 5 ? '最多添加5个' : '添加Container'" placement="top">
                                        <button type="button" class="bk-button bk-default is-outline is-icon" :disabled="curApplication.config.spec.template.spec.containers.length >= 5 " @click.stop.prevent="addLocalContainer">
                                            <i class="bk-icon icon-plus"></i>
                                        </button>
                                    </bk-tooltip>
                                </div>
                            </div>

                            <div class="bk-form biz-configuration-form pb15">
                                <div class="biz-span" style="margin-left: 105px;">
                                    <span class="title">基础信息</span>
                                </div>
                                <div class="bk-form-item is-required">
                                    <label class="bk-label" style="width: 105px;">容器名称：</label>
                                    <div class="bk-form-content" style="margin-left: 105px;">
                                        <input type="text" :class="['bk-form-input', { 'is-danger': errors.has('containerName') }]" placeholder="请输入30个字符以内" style="width: 310px;" v-model="curContainer.name" maxlength="30" name="containerName" v-validate="{ required: true, regex: /^[a-z]{1}[a-z0-9-]{0,29}$/ }">
                                    </div>
                                </div>
                                <div class="bk-form-item">
                                    <label class="bk-label" style="width: 105px;">描述：</label>
                                    <div class="bk-form-content" style="margin-left: 105px;">
                                        <textarea name="" id="" cols="30" rows="10" class="bk-form-textarea" placeholder="请输入256个字符以内" v-model="curContainer.desc" maxlength="256"></textarea>
                                    </div>
                                </div>
                                <div class="bk-form-item is-required">
                                    <label class="bk-label" style="width: 105px;">镜像及版本：</label>
                                    <div class="bk-form-content" style="margin-left: 105px;">
                                        <div class="bk-dropdown-box" style="width: 255px;" @click="initImageList">
                                            <bk-input
                                                type="text"
                                                placeholder="镜像"
                                                :display-key="'_name'"
                                                :setting-key="'_id'"
                                                :search-key="'_name'"
                                                :value.sync="curContainer.imageName"
                                                :list="varList"
                                                :is-link="true"
                                                :is-select-mode="true"
                                                :default-list="imageList"
                                                @item-selected="changeImage(...arguments, curContainer)">
                                            </bk-input>
                                        </div>
                                        <div class="bk-dropdown-box" style="width: 221px;">
                                            <bk-input
                                                type="text"
                                                placeholder="版本号"
                                                :display-key="'_name'"
                                                :setting-key="'_id'"
                                                :search-key="'_name'"
                                                :value.sync="curContainer.imageVersion"
                                                :list="varList"
                                                :is-select-mode="true"
                                                :default-list="imageVersionList"
                                                :disabled="!curContainer.imageName"
                                                @item-selected="setImageVersion">
                                            </bk-input>
                                        </div>

                                        <label class="bk-form-checkbox" style="margin-left: 10px;">
                                            <input type="checkbox" name="image-get" value="Always" v-model="isAlwayCheckImage" @click="changeImagePullPolicy">
                                            <i class="bk-checkbox-text">总是在创建之前拉取镜像</i>
                                        </label>
                                    </div>
                                </div>

                                <div class="biz-span" style="margin-left: 105px;">
                                    <span class="title">端口映射</span>
                                </div>

                                <div class="bk-form-item">
                                    <div class="bk-form-content" style="margin-left: 105px;">
                                        <table class="biz-simple-table">
                                            <thead>
                                                <tr>
                                                    <th style="width: 330px;">名称</th>
                                                    <th style="width: 135px;">协议</th>
                                                    <th style="width: 135px;">容器端口</th>
                                                    <th style="width: 135px;">主机端口</th>
                                                    <th></th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="(port, index) in curContainer.ports" :key="index">
                                                    <td>
                                                        <bk-input
                                                            type="text"
                                                            placeholder="名称"
                                                            maxlength="255"
                                                            :value.sync="port.name"
                                                            :list="varList"
                                                        >
                                                        </bk-input>
                                                    </td>
                                                    <td>
                                                        <template v-if="port.isLink">
                                                            <bk-tooltip :content="port.isLink" placement="top">
                                                                <bk-selector
                                                                    placeholder="协议"
                                                                    :setting-key="'id'"
                                                                    :disabled="true"
                                                                    :allow-clear="true"
                                                                    :selected.sync="port.protocol"
                                                                    :list="protocolList">
                                                                </bk-selector>
                                                            </bk-tooltip>
                                                        </template>
                                                        <template v-else>
                                                            <bk-selector
                                                                placeholder="协议"
                                                                :setting-key="'id'"
                                                                :allow-clear="true"
                                                                :selected.sync="port.protocol"
                                                                :list="protocolList">
                                                            </bk-selector>
                                                        </template>
                                                    </td>
                                                    <td>
                                                        <bk-input
                                                            type="number"
                                                            style="width: 135px"
                                                            placeholder="1-65535"
                                                            :min="1"
                                                            :max="65535"
                                                            :value.sync="port.containerPort"
                                                            :list="varList"
                                                        >
                                                        </bk-input>
                                                    </td>
                                                    <td>
                                                        <bk-input
                                                            type="number"
                                                            style="width: 135px"
                                                            placeholder="-1-65535"
                                                            :min="-1"
                                                            :max="65535"
                                                            :value.sync="port.hostPort"
                                                            :list="varList"
                                                        >
                                                        </bk-input>
                                                    </td>
                                                    <td>
                                                        <button class="action-btn ml5" @click.stop.prevent="addPort">
                                                            <i class="bk-icon icon-plus"></i>
                                                        </button>
                                                        <button class="action-btn" v-if="curContainer.ports.length > 1" @click.stop.prevent="removePort(port, index)">
                                                            <i class="bk-icon icon-minus"></i>
                                                        </button>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                <div class="biz-span" style="margin-left: 105px;">
                                    <div class="title">
                                        <button :class="['bk-text-button fb', { 'rotate': isPartBShow }]" @click.stop.prevent="togglePartB">
                                            更多设置<i class="bk-icon icon-angle-double-down f12 ml5 mb10 fb"></i>
                                        </button>
                                    </div>
                                </div>

                                <div style="margin-left: 105px;" v-show="isPartBShow">
                                    <bk-tab :type="'fill'" :active-name="'tab1'" :size="'small'">
                                        <bk-tabpanel name="tab1" title="命令">
                                            <div class="bk-form m20">
                                                <div class="bk-form-item">
                                                    <div class="bk-form-content" style="margin-left: 0;">
                                                        <div class="bk-form-item">
                                                            <label class="bk-label" style="width: 130px;">启动命令：</label>
                                                            <div class="bk-form-content" style="margin-left: 130px;">
                                                                <bk-input
                                                                    type="text"
                                                                    placeholder="例如/bin/bash"
                                                                    style="width: 520px;"
                                                                    :value.sync="curContainer.command"
                                                                    :list="varList"
                                                                >
                                                                </bk-input>
                                                            </div>
                                                        </div>
                                                        <div class="bk-form-item">
                                                            <label class="bk-label" style="width: 130px;">命令参数：</label>
                                                            <div class="bk-form-content" style="margin-left: 125px;">
                                                                <bk-input
                                                                    type="text"
                                                                    placeholder="多个参数用空格分隔"
                                                                    style="width: 520px;"
                                                                    :value.sync="curContainer.args_text"
                                                                    :list="varList"
                                                                >
                                                                </bk-input>
                                                            </div>
                                                        </div>
                                                        <div class="bk-form-item">
                                                            <label class="bk-label" style="width: 130px;">工作目录：</label>
                                                            <div class="bk-form-content" style="margin-left: 125px;">
                                                                <bk-input
                                                                    type="text"
                                                                    placeholder="例如/mywork"
                                                                    style="width: 520px;"
                                                                    :value.sync="curContainer.workingDir"
                                                                    :list="varList"
                                                                >
                                                                </bk-input>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="bk-form-item">
                                                    <label class="bk-label" style="width: 130px;">Docker参数：</label>
                                                    <div class="bk-form-content" style="margin-left: 130px;">
                                                        <bk-keyer :key-list.sync="curContainer.parameter_list" :var-list="varList"></bk-keyer>
                                                    </div>
                                                </div>
                                            </div>
                                        </bk-tabpanel>

                                        <bk-tabpanel name="tab2" title="挂载卷">
                                            <div class="bk-form m20">
                                                <table class="biz-simple-table">
                                                    <thead>
                                                        <tr>
                                                            <th>类型</th>
                                                            <th>挂载名</th>
                                                            <th>挂载源</th>
                                                            <th>容器目录</th>
                                                            <th>子路径</th>
                                                            <th style="width: 80px;"></th>
                                                            <th style="width: 80px;"></th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        <tr v-for="(volumeItem, index) in curContainer.volumes" :key="index">
                                                            <td>
                                                                <bk-selector
                                                                    placeholder="类型"
                                                                    :setting-key="'id'"
                                                                    :selected.sync="volumeItem.type"
                                                                    :list="mountTypeList"
                                                                    @item-selected="selectVolumeType(volumeItem)">
                                                                </bk-selector>
                                                            </td>
                                                            <td>
                                                                <template v-if="volumeItem.type === 'custom'">
                                                                    <bk-input
                                                                        type="text"
                                                                        placeholder="请输入"
                                                                        :value.sync="volumeItem.name"
                                                                        :list="varList"
                                                                    >
                                                                    </bk-input>
                                                                </template>
                                                                <template v-else>
                                                                    <bk-selector
                                                                        placeholder="请选择"
                                                                        :setting-key="'name'"
                                                                        :selected.sync="volumeItem.name"
                                                                        :list="getVolumeNameList(volumeItem.type)"
                                                                        @item-selected="setVolumeName(volumeItem)">
                                                                    </bk-selector>
                                                                </template>
                                                            </td>
                                                            <td>
                                                                <template v-if="volumeItem.type === 'custom'">
                                                                    <bk-input
                                                                        type="text"
                                                                        placeholder="例如：/a/b"
                                                                        style="width: 215px;"
                                                                        maxlength="512"
                                                                        :value.sync="volumeItem.volume.hostPath"
                                                                        :list="varList"
                                                                    >
                                                                    </bk-input>
                                                                </template>
                                                                <template v-else>
                                                                    <bk-selector
                                                                        placeholder="请选择"
                                                                        :setting-key="'id'"
                                                                        :selected.sync="volumeItem.volume.hostPath"
                                                                        :list="getVolumeSourceList(volumeItem.type, volumeItem.name)">
                                                                    </bk-selector>
                                                                </template>

                                                            </td>
                                                            <td>
                                                                <bk-input
                                                                    type="text"
                                                                    placeholder="例如：/a/b"
                                                                    maxlength="512"
                                                                    :value.sync="volumeItem.volume.mountPath"
                                                                    :list="varList"
                                                                >
                                                                </bk-input>
                                                            </td>
                                                            <td>
                                                                <bk-input
                                                                    type="text"
                                                                    placeholder="请输入"
                                                                    :value.sync="volumeItem.volume.subPath"
                                                                    :list="varList"
                                                                    :disabled="volumeItem.type !== 'custom'"
                                                                >
                                                                </bk-input>
                                                            </td>
                                                            <td>
                                                                <div class="biz-input-wrapper">
                                                                    <label class="bk-form-checkbox">
                                                                        <input type="checkbox" v-model="volumeItem.volume.readOnly">
                                                                        <i class="bk-checkbox-text">只读</i>
                                                                    </label>
                                                                </div>
                                                            </td>
                                                            <div class="action-box">
                                                                <button class="action-btn ml5" @click.stop.prevent="addVolumn()">
                                                                    <i class="bk-icon icon-plus"></i>
                                                                </button>
                                                                <button class="action-btn" @click.stop.prevent="removeVolumn(volumeItem, index)" v-show="curContainer.volumes.length > 1">
                                                                    <i class="bk-icon icon-minus"></i>
                                                                </button>
                                                            </div>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            </div>
                                        </bk-tabpanel>

                                        <bk-tabpanel name="tab3" title="环境变量">
                                            <div class="bk-form m20">
                                                <table class="biz-simple-table" style="width: 690px;">
                                                    <thead>
                                                        <tr>
                                                            <th style="width: 140px;">类型</th>
                                                            <th style="width: 220px;">变量键</th>
                                                            <th style="width: 220px;">变量值</th>
                                                            <th></th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        <tr v-for="(env, index) in curContainer.env_list" :key="index">
                                                            <td>
                                                                <bk-selector
                                                                    placeholder="类型"
                                                                    :setting-key="'id'"
                                                                    :selected.sync="env.type"
                                                                    :list="mountTypeList">
                                                                </bk-selector>
                                                            </td>
                                                            <td>
                                                                <bk-input
                                                                    type="text"
                                                                    placeholder="请输入"
                                                                    :value.sync="env.key"
                                                                    :list="varList"
                                                                    @paste="pasteKey(env, $event)"
                                                                >
                                                                </bk-input>
                                                            </td>
                                                            <td>
                                                                <template v-if="env.type === 'custom'">
                                                                    <bk-input
                                                                        type="text"
                                                                        placeholder="例如：/metadata/name"
                                                                        :value.sync="env.value"
                                                                        :list="varList"
                                                                    >
                                                                    </bk-input>
                                                                </template>
                                                                <template v-else-if="env.type === 'configmap'">
                                                                    <bk-selector
                                                                        placeholder="请选择"
                                                                        :setting-key="'id'"
                                                                        :selected.sync="env.value"
                                                                        :list="configmapKeyList">
                                                                    </bk-selector>
                                                                </template>
                                                                <template v-else>
                                                                    <bk-selector
                                                                        placeholder="请选择"
                                                                        :setting-key="'id'"
                                                                        :selected.sync="env.value"
                                                                        :list="secretKeyList">
                                                                    </bk-selector>
                                                                </template>
                                                            </td>
                                                            <td>
                                                                <div class="action-box">
                                                                    <button class="action-btn ml5" @click.stop.prevent="addEnv()">
                                                                        <i class="bk-icon icon-plus"></i>
                                                                    </button>
                                                                    <button class="action-btn" @click.stop.prevent="removeEnv(env, index)" v-show="curContainer.env_list.length > 1">
                                                                        <i class="bk-icon icon-minus"></i>
                                                                    </button>
                                                                </div>
                                                            </td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                                <p class="biz-tip">自定义类型可同时粘贴多行“键=值”的文本会自动添加多行记录</p>
                                            </div>
                                        </bk-tabpanel>

                                        <bk-tabpanel name="tab4" title="资源限制">
                                            <div class="bk-form m20">
                                                <div class="bk-form-item">
                                                    <label class="bk-label" style="width: 105px;">特权：</label>
                                                    <div class="bk-form-content" style="margin-left: 105px;">
                                                        <label class="bk-form-checkbox">
                                                            <input type="checkbox" v-model="curContainer.privileged">
                                                            <i class="bk-checkbox-text">可完全访问母机资源</i>
                                                        </label>
                                                    </div>
                                                </div>
                                                <div class="bk-form-item">
                                                    <label class="bk-label" style="width: 105px;">CPU限制：</label>
                                                    <div class="bk-form-content" style="margin-left: 105px;">
                                                        <div class="bk-form-input-group mr5">
                                                            <bk-input
                                                                type="number"
                                                                :min="0.001"
                                                                :is-decimals="true"
                                                                :max="128"
                                                                placeholder="请输入"
                                                                style="width: 100px;"
                                                                :value.sync="curContainer.resources.limits.cpu"
                                                                :list="varList"
                                                            >
                                                            </bk-input>
                                                            <span class="input-group-addon">
                                                                核
                                                            </span>
                                                        </div>
                                                        <bk-tooltip content="设置CPU上限，范围为0.001-128" placement="top">
                                                            <span class="bk-badge">
                                                                <i class="bk-icon icon-question"></i>
                                                            </span>
                                                        </bk-tooltip>
                                                        <div class="bk-form-input-group ml20 mr5">
                                                            <bk-input
                                                                type="number"
                                                                style="width: 100px;"
                                                                :min="0.001"
                                                                :is-decimals="true"
                                                                :max="curContainer.resources.limits.cpu ? curContainer.resources.limits.cpu : Number.MAX_VALUE"
                                                                placeholder="请输入"
                                                                :value.sync="curContainer.resources.requests.cpu"
                                                                :list="varList"
                                                            >
                                                            </bk-input>
                                                            <span class="input-group-addon">
                                                                核
                                                            </span>
                                                        </div>
                                                        <bk-tooltip content="设置CPU下限，范围为0.001-128" placement="top">
                                                            <span class="bk-badge">
                                                                <i class="bk-icon icon-question"></i>
                                                            </span>
                                                        </bk-tooltip>
                                                    </div>
                                                </div>
                                                <div class="bk-form-item">
                                                    <label class="bk-label" style="width: 105px;">内存限制：</label>
                                                    <div class="bk-form-content" style="margin-left: 105px;">
                                                        <div class="bk-form-input-group mr5">
                                                            <bk-input
                                                                type="number"
                                                                :is-decimals="true"
                                                                :min="0"
                                                                placeholder="请输入"
                                                                style="width: 100px;"
                                                                :value.sync="curContainer.resources.limits.memory"
                                                                :list="varList"
                                                            >
                                                            </bk-input>
                                                            <span class="input-group-addon">
                                                                M
                                                            </span>
                                                        </div>
                                                        <bk-tooltip content="设置内存上限" placement="top">
                                                            <span class="bk-badge">
                                                                <i class="bk-icon icon-question"></i>
                                                            </span>
                                                        </bk-tooltip>

                                                        <div class="bk-form-input-group ml20 mr5">
                                                            <bk-input
                                                                type="number"
                                                                style="width: 100px;"
                                                                :min="0"
                                                                :max="curContainer.resources.limits.memory ? curContainer.resources.limits.memory : Number.MAX_VALUE"
                                                                placeholder="请输入"
                                                                :value.sync="curContainer.resources.requests.memory"
                                                                :list="varList"
                                                            >
                                                            </bk-input>
                                                            <span class="input-group-addon">
                                                                M
                                                            </span>
                                                        </div>
                                                        <bk-tooltip content="设置内存下限" placement="top">
                                                            <span class="bk-badge">
                                                                <i class="bk-icon icon-question"></i>
                                                            </span>
                                                        </bk-tooltip>
                                                    </div>
                                                </div>
                                            </div>
                                        </bk-tabpanel>

                                        <bk-tabpanel name="tab5" title="健康检查">
                                            <div class="bk-form m20">
                                                <div class="bk-form-item">
                                                    <label class="bk-label" style="width: 120px;">类型：</label>
                                                    <div class="bk-form-content" style="margin-left: 120px">
                                                        <div class="bk-dropdown-box" style="width: 250px;">
                                                            <bk-selector
                                                                placeholder="请选择"
                                                                :setting-key="'id'"
                                                                :display-key="'name'"
                                                                :selected.sync="curContainer.healthChecks[0].type"
                                                                :list="healthCheckTypes">
                                                            </bk-selector>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div class="bk-form-item" v-show="curContainer.healthChecks[0].type && curContainer.healthChecks[0].type !== 'COMMAND'">
                                                    <label class="bk-label" style="width: 120px;">端口名称：</label>
                                                    <div class="bk-form-content" style="margin-left: 120px;">
                                                        <div class="bk-dropdown-box" style="width: 250px;">
                                                            <bk-selector
                                                                placeholder="请选择"
                                                                :setting-key="'name'"
                                                                :display-key="'name'"
                                                                :selected="portName"
                                                                :list="portList"
                                                                @item-selected="portNameSelect">
                                                            </bk-selector>
                                                        </div>
                                                        <span class="biz-guard-tip ml10 bk-default" v-if="!portList.length">请先配置完整的端口映射</span>
                                                    </div>
                                                </div>

                                                <div class="bk-form-item" v-show="curContainer.healthChecks[0].type && (curContainer.healthChecks[0].type === 'HTTP' || curContainer.healthChecks[0].type === 'REMOTE_HTTP')">
                                                    <div class="bk-form-content" style="margin-left: 0">
                                                        <div class="bk-form-inline-item">
                                                            <label class="bk-label" style="width: 120px;">请求路径：</label>
                                                            <div class="bk-form-content" style="margin-left: 120px;">
                                                                <bk-input
                                                                    type="text"
                                                                    placeholder="例如：/healthcheck"
                                                                    style="width: 675px;"
                                                                    :value.sync="curContainer.healthChecks[0].http.path"
                                                                    :list="varList"
                                                                >
                                                                </bk-input>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div class="bk-form-item" v-show="curContainer.healthChecks[0].type && curContainer.healthChecks[0].type === 'COMMAND'">
                                                    <div class="bk-form-content" style="margin-left: 0">
                                                        <div class="bk-form-inline-item">
                                                            <label class="bk-label" style="width: 120px;">检查命令：</label>
                                                            <div class="bk-form-content" style="margin-left: 120px;">
                                                                <bk-input
                                                                    type="text"
                                                                    placeholder="例如：/tmp/check.sh"
                                                                    style="width: 670px;"
                                                                    :value.sync="curContainer.healthChecks[0].command.value"
                                                                    :list="varList"
                                                                >
                                                                </bk-input>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div class="bk-form-item" v-show="curContainer.healthChecks[0].type && curContainer.healthChecks[0].type === 'REMOTE_HTTP'">
                                                    <div class="bk-form-content" style="margin-left: 0">
                                                        <div class="bk-form-inline-item">
                                                            <label class="bk-label" style="width: 120px;">设置Header：</label>
                                                            <div class="bk-form-content" style="margin-left: 120px;">
                                                                <bk-keyer ref="headerKeyer" :key-list.sync="healCheckHttpHeaders" :var-list="varList"></bk-keyer>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <template v-if="curContainer.healthChecks[0].type">
                                                    <button :class="['bk-text-button mt10 f12 mb10', { 'rotate': isPartCShow }]" style="margin-left: 114px;" @click.stop.prevent="togglePartC">
                                                        高级设置<i class="bk-icon icon-angle-double-down ml5"></i>
                                                    </button>
                                                    <div v-show="isPartCShow">
                                                        <div class="bk-form-item" v-show="curContainer.healthChecks[0].type">
                                                            <div class="bk-form-content" style="margin-left: 0">
                                                                <div class="bk-form-inline-item">
                                                                    <label class="bk-label" style="width: 120px;">初始化超时：</label>
                                                                    <div class="bk-form-content" style="margin-left: 120px;">
                                                                        <div class="bk-form-input-group">
                                                                            <bk-input
                                                                                type="number"
                                                                                placeholder="请输入"
                                                                                style="width: 100px;"
                                                                                :min="0"
                                                                                :value.sync="curContainer.healthChecks[0].delaySeconds"
                                                                                :list="varList"
                                                                            >
                                                                            </bk-input>
                                                                            <span class="input-group-addon">
                                                                                秒
                                                                            </span>
                                                                        </div>
                                                                    </div>
                                                                </div>

                                                                <div class="bk-form-inline-item">
                                                                    <label class="bk-label" style="width: 130px;">检查间隔：</label>
                                                                    <div class="bk-form-content" style="margin-left: 130px;">
                                                                        <div class="bk-form-input-group">
                                                                            <bk-input
                                                                                type="number"
                                                                                placeholder="请输入"
                                                                                style="width: 100px;"
                                                                                :min="0"
                                                                                :value.sync="curContainer.healthChecks[0].intervalSeconds"
                                                                                :list="varList"
                                                                            >
                                                                            </bk-input>
                                                                            <span class="input-group-addon">
                                                                                秒
                                                                            </span>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                <div class="bk-form-inline-item">
                                                                    <label class="bk-label" style="width: 130px;">检查超时：</label>
                                                                    <div class="bk-form-content" style="margin-left: 130px;">
                                                                        <div class="bk-form-input-group">
                                                                            <bk-input
                                                                                type="number"
                                                                                placeholder="请输入"
                                                                                style="width: 100px;"
                                                                                :min="0"
                                                                                :value.sync="curContainer.healthChecks[0].timeoutSeconds"
                                                                                :list="varList"
                                                                            >
                                                                            </bk-input>
                                                                            <span class="input-group-addon">
                                                                                秒
                                                                            </span>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div class="bk-form-item" v-show="curContainer.healthChecks[0].type">
                                                            <div class="bk-form-content" style="margin-left: 0">
                                                                <div class="bk-form-inline-item">
                                                                    <label class="bk-label" style="width: 120px;">不健康阈值：</label>
                                                                    <div class="bk-form-content" style="margin-left: 120px;">
                                                                        <div class="bk-form-input-group">
                                                                            <bk-input
                                                                                type="number"
                                                                                placeholder="请输入"
                                                                                style="width: 80px;"
                                                                                :min="0"
                                                                                :value.sync="curContainer.healthChecks[0].consecutiveFailures"
                                                                                :list="varList">
                                                                            </bk-input>
                                                                            <span class="input-group-addon">
                                                                                次失败
                                                                            </span>
                                                                            <bk-tooltip content="健康检查连续失败的次数，达到次数后会重新调度容器" placement="top">
                                                                                <span class="bk-badge ml5">
                                                                                    <i class="bk-icon icon-question" style="cursor: pointer;"></i>
                                                                                </span>
                                                                            </bk-tooltip>
                                                                        </div>
                                                                    </div>
                                                                </div>

                                                                <div class="bk-form-inline-item">
                                                                    <label class="bk-label" style="width: 107px;">健康阈值：</label>
                                                                    <div class="bk-form-content" style="margin-left: 107px;">
                                                                        <div class="bk-form-input-group">
                                                                            <bk-input
                                                                                type="number"
                                                                                placeholder="请输入"
                                                                                style="width: 80px;"
                                                                                :min="0"
                                                                                :value.sync="curContainer.healthChecks[0].gracePeriodSeconds"
                                                                                :list="varList"
                                                                            >
                                                                            </bk-input>
                                                                            <span class="input-group-addon">
                                                                                秒
                                                                            </span>
                                                                            <bk-tooltip content="启动之后，该时间内的健康检查失败会被忽略" placement="top">
                                                                                <span class="bk-badge ml5">
                                                                                    <i class="bk-icon icon-question" style="cursor: pointer;"></i>
                                                                                </span>
                                                                            </bk-tooltip>
                                                                        </div>
                                                                    </div>
                                                                </div>

                                                            </div>
                                                        </div>
                                                    </div>
                                                </template>

                                            </div>
                                        </bk-tabpanel>
                                    </bk-tab>
                                </div>

                            </div>
                            <!-- part2 end -->
                        </div>
                    </div>
                </div>

            </div>
        </template>
    </div>
</template>

<script>
    import bkKeyer from '@open/components/keyer'
    import applicationParams from '@open/json/application.json'
    import containerParams from '@open/json/container.json'
    import ace from '@open/components/ace-editor'
    import bkCombobox from '@open/components/bk-combobox'
    import header from './header.vue'
    import tabs from './tabs.vue'
    import _ from 'lodash'

    export default {
        components: {
            ace,
            'bk-keyer': bkKeyer,
            'biz-header': header,
            'biz-tabs': tabs,
            bkCombobox
        },
        data () {
            return {
                isTabChanging: false,
                imagePublish: '',
                curImageData: {},
                winHeight: 0,
                exceptionCode: null,
                isDataLoading: true,
                isDataSaveing: false,
                isPartAShow: false, // 第一个更多设置
                isPartBShow: false, // 第二个更多设置
                isPartCShow: false, // 第三个更多设置
                imageIndex: -1,
                versionIndex: -1,
                appJsonValidator: null,
                isEditName: false,
                isEditDesc: false,
                appParamKeys: [],
                keyList: [],
                isLoadingImageList: true,
                applicationJsonCache: null,
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
                netList: [
                    {
                        id: 'HOST',
                        name: 'HOST'
                    },
                    {
                        id: 'BRIDGE',
                        name: 'BRIDGE'
                    },
                    {
                        id: 'NONE',
                        name: 'NONE'
                    },
                    {
                        id: 'USER',
                        name: 'USER'
                    },
                    {
                        id: 'CUSTOM',
                        name: '自定义'
                    }
                ],
                constraintNameList: [
                    {
                        id: 'hostname',
                        name: 'hostname'
                    },
                    {
                        id: 'InnerIP',
                        name: 'InnerIP'
                    }
                ],
                operatorList: [
                    {
                        id: 'CLUSTER',
                        name: 'CLUSTER'
                    },
                    {
                        id: 'GROUPBY',
                        name: 'GROUPBY'
                    },
                    {
                        id: 'LIKE',
                        name: 'LIKE'
                    },
                    {
                        id: 'UNLIKE',
                        name: 'UNLIKE'
                    },
                    {
                        id: 'UNIQUE',
                        name: 'UNIQUE'
                    },
                    {
                        id: 'MAXPER',
                        name: 'MAXPER'
                    }
                ],
                operatorListForIP: [
                    {
                        id: 'GREATER',
                        name: 'GREATER'
                    }
                ],
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
                mountTypeList: [
                    {
                        id: 'custom',
                        name: '自定义'
                    },
                    {
                        id: 'configmap',
                        name: 'Configmap'
                    },
                    {
                        id: 'secret',
                        name: 'Secret'
                    }
                ],
                metricIndex: [],
                configmapList: [],
                configmapKeyList: [],
                secretKeyList: [],
                secretList: [],
                curApplicationId: 0,
                curApplicationCache: JSON.parse(JSON.stringify(applicationParams)),
                compareTimer: 0, // 定时器，查看用户是否有修改
                setTimer: 0,
                curApplication: applicationParams,
                curContainerIndex: 0,
                curContainer: applicationParams.config.spec.template.spec.containers[0],
                isAlwayCheckImage: false,
                editTemplate: {
                    name: '',
                    desc: ''
                },
                imageList: [],
                imageVersionList: [],
                restartPolicy: ['Never', 'Always', 'OnFailure'],
                healthCheckTypes: [
                    {
                        id: '',
                        name: '无'
                    },
                    {
                        id: 'HTTP',
                        name: 'HTTP'
                    },
                    {
                        id: 'REMOTE_HTTP',
                        name: 'REMOTE_HTTP'
                    },
                    {
                        id: 'TCP',
                        name: 'TCP'
                    },
                    {
                        id: 'REMOTE_TCP',
                        name: 'REMOTE_TCP'
                    }
                    // {
                    //     id: 'COMMAND',
                    //     name: 'COMMAND'
                    // }
                ],
                logList: [
                    {
                        value: ''
                    }
                ]
            }
        },
        computed: {
            varList () {
                const list = this.$store.state.variable.varList
                list.forEach(item => {
                    item._id = item.key
                    item._name = item.key
                })
                return list
            },
            metricList () {
                return this.$store.state.mesosTemplate.metricList
            },
            versionList () {
                const list = this.$store.state.mesosTemplate.versionList
                return list
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
            services () {
                return this.$store.state.mesosTemplate.services
            },
            configmaps () {
                return this.$store.state.mesosTemplate.configmaps
            },
            secrets () {
                return this.$store.state.mesosTemplate.secrets
            },
            portName () {
                const healthParams = this.curContainer.healthChecks[0]
                const type = healthParams.type
                if (type === 'HTTP' || type === 'REMOTE_HTTP') {
                    return healthParams.http.portName
                } else if (type === 'TCP' || type === 'REMOTE_TCP') {
                    return healthParams.tcp.portName
                } else if (type === 'COMMAND') {
                    return healthParams.command.portName
                } else {
                    return ''
                }
            },
            curVersion () {
                return this.$store.state.mesosTemplate.curVersion
            },
            templateId () {
                return this.$route.params.templateId
            },
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            portList () {
                let results = []
                const ports = this.curContainer.ports

                if (ports && ports.length) {
                    results = ports.filter(port => {
                        return port.name && (port.hostPort !== '') && port.protocol && port.containerPort
                    })
                    return results
                } else {
                    return []
                }
            },
            curLabelList () {
                const keyList = []
                const labels = this.curApplication.config.metadata.labels
                // 如果有缓存直接使用
                if (this.curApplication.config.webCache && this.curApplication.config.webCache.labelListCache) {
                    return this.curApplication.config.webCache.labelListCache
                }
                for (const [key, value] of Object.entries(labels)) {
                    keyList.push({
                        key: key,
                        value: value
                    })
                }
                if (!keyList.length) {
                    keyList.push({
                        key: '',
                        value: ''
                    })
                }
                return keyList
            },
            curLogLabelList () {
                const keyList = []
                const labels = this.curApplication.config.customLogLabel
                // 如果有缓存直接使用
                if (this.curApplication.config.webCache && this.curApplication.config.webCache.logLabelListCache) {
                    return this.curApplication.config.webCache.logLabelListCache
                }
                for (const [key, value] of Object.entries(labels)) {
                    keyList.push({
                        key: key,
                        value: value
                    })
                }
                if (!keyList.length) {
                    keyList.push({
                        key: '',
                        value: ''
                    })
                }
                return keyList
            },
            curRemarkList () {
                const list = []
                // 如果有缓存直接使用
                if (this.curApplication.config.webCache && this.curApplication.config.webCache.remarkListCache) {
                    return this.curApplication.config.webCache.remarkListCache
                }
                const annotations = this.curApplication.config.metadata.annotations
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
            curEnvList () {
                const list = []
                const envs = this.curContainer.env
                envs.forEach(env => {
                    for (const [key, value] of Object.entries(env)) {
                        list.push({
                            key: key,
                            value: value
                        })
                    }
                })
                return list
            },
            healCheckHttpHeaders () {
                let list = []
                const headers = this.curContainer.healthChecks[0].http.headers
                if (headers) {
                    for (const [key, value] of Object.entries(headers)) {
                        list.push({
                            key: key,
                            value: value
                        })
                    }
                } else {
                    this.curContainer.healthChecks[0].http.headers = {}
                    list = []
                }
                if (!list.length) {
                    list.push({
                        key: '',
                        value: ''
                    })
                }
                return list
            }
        },
        watch: {
            'curContainer' () {
                if (this.curContainer.imagePullPolicy === 'Always') {
                    this.isAlwayCheckImage = true
                } else {
                    this.isAlwayCheckImage = false
                }

                if (!this.curContainer.ports.length) {
                    this.addPort()
                } else {
                    this.curContainer.ports.forEach(item => {
                        const projectId = this.projectId
                        const version = this.curVersion
                        const portId = item.id
                        if (portId) {
                            this.$store.dispatch('mesosTemplate/checkPortIsLink', { projectId, version, portId }).then(res => {
                                item.isLink = ''
                            }, res => {
                                const message = res.message || res.data.data || ''
                                const msg = message.split(',')[0]
                                if (msg) {
                                    item.isLink = msg + '，不能修改协议！'
                                } else {
                                    item.isLink = ''
                                }
                            })
                        } else {
                            item.isLink = ''
                        }
                    })
                }

                if (!this.curContainer.volumes.length) {
                    this.curContainer.volumes.push({
                        'volume': {
                            'hostPath': '',
                            'mountPath': '',
                            'subPath': '',
                            'readOnly': false
                        },
                        'type': 'custom',
                        'name': ''
                    })
                }
            },
            'curApplication' () {
                this.curContainerIndex = 0
                this.curContainer = this.curApplication.config.spec.template.spec.containers[0]
            },
            'curApplication.config.spec.template.spec.networkMode' (val) {
                if (val === 'USER') {
                    this.curApplication.config.spec.template.spec.networkType = 'cni'
                } else if (val !== 'CUSTOM') {
                    this.curApplication.config.spec.template.spec.networkType = 'cnm'
                }
            },
            'curVersion' (val) {
                this.initVolumeConfigmaps()
                this.initVloumeSelectets()
            }
        },
        async beforeRouteLeave (to, from, next) {
            // 修改模板集信息
            // await this.$refs.commonHeader.saveTemplate()
            clearInterval(this.compareTimer)
            clearTimeout(this.setTimer)
            next(true)
        },
        mounted () {
            this.isDataLoading = true
            this.$refs.commonHeader.initTemplate((data) => {
                this.initResource(data)
                this.isDataLoading = false
            })
            this.winHeight = window.innerHeight
            this.initImageList()
            this.initVolumeConfigmaps()
            this.initVloumeSelectets()
            this.initMetricList()

            const Validator = require('jsonschema').Validator
            this.appJsonValidator = new Validator()
        },
        methods: {
            getAppParamsKeys (obj, result) {
                for (const key in obj) {
                    if (key === 'labels') continue
                    if (key === 'annotations') continue
                    if (key === 'updatePolicy') continue
                    if (key === 'set') continue
                    if (key === 'customLogLabel') continue

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
            checkJson (jsonObj) {
                const editor = this.editorConfig.editor
                const appParams = applicationParams.config
                const appParamKeys = [
                    'id',
                    'containerPort',
                    'hostPort',
                    'name',
                    'protocol',
                    'isLink',
                    'isDisabled',
                    'env',
                    'secrets',
                    'configmaps',
                    'apiVersion',
                    'updatePolicy',
                    'imagePullUser',
                    'imagePullPasswd',
                    'selector',
                    'namespace',
                    'updateDelay',
                    'MaxRetries',
                    'maxFailovers',
                    'action',
                    'scalar',
                    'module'
                ]
                const jsonParamKeys = []
                this.getAppParamsKeys(appParams, appParamKeys)
                this.getAppParamsKeys(jsonObj, jsonParamKeys)

                // application查看无效字段
                for (const key of jsonParamKeys) {
                    if (!appParamKeys.includes(key)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: `${key}为无效字段！`
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
                const cParams = containerParams
                let appObj = null
                if (!json) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入JSON!'
                    })
                    return false
                }

                try {
                    appObj = JSON.parse(json)
                } catch (err) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入合法的JSON!'
                    })
                }

                const annot = editor.getSession().getAnnotations()
                if (annot && annot.length) {
                    editor.gotoLine(annot[0].row, annot[0].column, true)
                    return false
                }

                const curAppContainers = this.curApplication.config.spec.template.spec.containers
                const containers = appObj.spec.template.spec.containers
                let index = 0
                for (let container of containers) {
                    // 处理container命名
                    if (!container.name) {
                        if (curAppContainers[index]) {
                            container.name = curAppContainers[index].name
                        } else {
                            container.name = 'container-' + (index + 1)
                        }
                    }
                    if (!container.logListCache) {
                        container.logListCache = [{
                            value: ''
                        }]
                    }
                    if (container.args && container.args.length) {
                        container.args_text = container.args.join(' ')
                    }
                    if (!container.args_text) {
                        container.args_text = ''
                    }
                    if (container.resources && container.resources.limits && container.resources.limits.cpu) {
                        container.resources.limits.cpu = Number(container.resources.limits.cpu)
                    }
                    if (container.resources && container.resources.limits && container.resources.limits.memory) {
                        container.resources.limits.memory = Number(container.resources.limits.memory)
                    }
                    container = _.merge({}, cParams, container)
                    index++
                }

                const newConfObj = _.merge({}, this.curApplication.config, appObj)
                const jsonFromat = this.formatJson(newConfObj)
                this.curApplication.config = jsonFromat
                this.toJsonDialogConf.isShow = false
                if (this.curApplication.config.spec.template.spec.containers.length) {
                    const container = this.curApplication.config.spec.template.spec.containers[0]
                    this.setCurContainer(container, 0)
                }
            },
            formatJson (jsonObj) {
                // constraint 调度约束
                // 转换调度约束
                const constraint = jsonObj.constraint.intersectionItem
                constraint.forEach(item => {
                    const data = item.unionData[0]
                    const operate = data.operate

                    data.type = 4
                    data.arg_value = ''
                    if (!data.text) {
                        data.text = {
                            value: ''
                        }
                    }
                    if (!data.set) {
                        data.set = {
                            item: []
                        }
                    }

                    if (data.text && data.text.value) {
                        data.arg_value = data.text.value
                    }
                    switch (operate) {
                        case 'UNIQUE':
                            data.arg_value = ''
                            break
                        case 'MAXPER':
                            data.type = 3
                            break
                        case 'CLUSTER':
                            data.type = 4
                            if (data.set && data.set.item && data.set.item.length) {
                                data.arg_value = data.set.item.join('|')
                            }
                            break
                        case 'GROUPBY':
                            data.type = 4
                            if (data.set && data.set.item && data.set.item) {
                                data.arg_value = data.set.item.join('|')
                            }
                            break
                        case 'LIKE':
                            if (data.set && data.set.item && data.set.item.length) {
                                data.type = 4
                                data.arg_value = data.set.item.join('|')
                            } else {
                                data.type = 3
                            }
                            break
                        case 'UNLIKE':
                            if (data.set && data.set.item && data.set.item.length) {
                                data.type = 4
                                data.arg_value = data.set.item.join('|')
                            } else {
                                data.type = 3
                            }
                            break
                        case 'GREATER':
                            data.type = 1
                            data.arg_value = data.scalar.value
                            break
                    }
                })

                // 备注
                const annotations = jsonObj.metadata.annotations
                if (annotations) {
                    const list = []
                    for (const key in annotations) {
                        list.push({
                            key: key,
                            value: annotations[key]
                        })
                    }
                    jsonObj.webCache.remarkListCache = list
                }

                // 标签
                const labels = jsonObj.metadata.labels
                if (labels) {
                    const list = []
                    for (const key in labels) {
                        list.push({
                            key: key,
                            value: labels[key]
                        })
                    }
                    jsonObj.webCache.labelListCache = list
                }

                // 日志采集
                const customLogLabel = jsonObj.customLogLabel
                if (customLogLabel) {
                    const list = []
                    for (const key in customLogLabel) {
                        list.push({
                            key: key,
                            value: customLogLabel[key]
                        })
                    }
                    jsonObj.webCache.logLabelListCache = list
                }

                // container env
                const containers = jsonObj.spec.template.spec.containers
                containers.forEach(container => {
                    // 环境变量
                    if (container.env) {
                        const envs = container.env
                        container.env_list = []
                        envs.forEach(item => {
                            container.env_list.push({
                                type: 'custom',
                                key: item.name,
                                value: item.value
                            })
                        })
                        if (!container.env_list.length) {
                            container.env_list.push({
                                type: 'custom',
                                key: '',
                                value: ''
                            })
                        }
                    }

                    // 端口
                    if (container.ports) {
                        const ports = container.ports
                        ports.forEach((item, index) => {
                            item.isLink = ''
                            if (!item.id) {
                                item.id = +new Date() + index
                            }
                        })
                    }

                    // volumes
                    if (container.volumes) {
                        const volumes = container.volumes
                        volumes.forEach(item => {
                            if (item.type !== 'configmap' && item.type !== 'secret') {
                                item.type = 'custom'
                            }
                        })
                    }

                    // 命令参数
                    if (container.parameters && container.parameters.length > 0) {
                        container.parameters.forEach(item => {
                            container.parameter_list.push(item)
                        })
                    } else {
                        container.parameters = []
                        container.parameter_list = [{
                            key: '',
                            value: ''
                        }]
                    }

                    const healthchecksParams = [
                        {
                            type: '',
                            delaySeconds: 10,
                            intervalSeconds: 60,
                            timeoutSeconds: 10,
                            consecutiveFailures: 0,
                            gracePeriodSeconds: 10,
                            command: {
                                portName: '',
                                value: ''
                            },
                            http: {
                                port: '',
                                portName: '',
                                scheme: 'http',
                                path: '',
                                headers: {}
                            },
                            tcp: {
                                port: '',
                                portName: ''
                            }
                        }
                    ]
                    if (container.healthChecks) {
                        container.healthChecks = _.merge(healthchecksParams, container.healthChecks)
                    } else {
                        container.healthChecks = healthchecksParams
                    }
                })
                return jsonObj
            },
            formatLocalToServerData (data) {
                data.spec.template.containers.forEach(container => {
                    // delete 命令参数
                    if (container.args_text.trim().length) {
                        container.args = container.args_text.split(' ')
                    } else {
                        container.args = []
                    }
                    delete container.args_text

                    // 环境变量
                    if (container.env_list) {
                        const envList = container.env_list
                        container.env = []
                        envList.forEach(item => {
                            container.env.push({
                                name: item.name,
                                value: item.value
                            })
                        })
                    }
                    delete container.env_list
                })
            },
            formatServerToLocalData (data) {
                // container env
                const containers = data.spec.template.spec.containers
                containers.forEach(container => {
                    // 环境变量
                    if (container.env) {
                        const envs = container.env
                        container.env_list = []
                        envs.forEach(item => {
                            container.env_list.push({
                                type: 'custom',
                                key: item.name,
                                value: item.value
                            })
                        })
                    }

                    // 端口
                    if (container.ports) {
                        const ports = container.ports
                        ports.forEach(item => {
                            item.isLink = ''
                            item.id = +new Date()
                        })
                    }

                    // volumes
                    if (container.volumes) {
                        const volumes = container.volumes
                        volumes.forEach(item => {
                            item.type = 'custom'
                        })
                    }
                })
            },
            getKeyList (list) {
                let results = []
                results = list.filter(item => {
                    return item.key && item.value
                })
                return results
            },
            tranListToObject (list) {
                const results = this.getKeyList(list)
                if (results.length === 0) {
                    return {}
                } else {
                    const obj = {}
                    results.forEach(item => {
                        if (item.key && item.value) {
                            obj[item.key] = item.value
                        }
                    })
                    return obj
                }
            },
            showJsonPanel () {
                this.toJsonDialogConf.title = this.curApplication.config.metadata.name + '.json'
                const appConfig = JSON.parse(JSON.stringify(this.curApplication.config))

                // 转换调度约束
                const constraint = appConfig.constraint.intersectionItem
                constraint.forEach(item => {
                    const data = item.unionData[0]
                    const operate = data.operate
                    switch (operate) {
                        case 'UNIQUE':
                            delete data.type
                            delete data.set
                            delete data.text
                            break
                        case 'MAXPER':
                            data.type = 3
                            data.text = {
                                'value': data.arg_value
                            }
                            delete data.set
                            break
                        case 'GREATER':
                            data.type = 1
                            delete data.set
                            delete data.text
                            data.scalar = {
                                'value': data.arg_value
                            }
                            break
                        case 'CLUSTER':
                            data.type = 4
                            if (data.arg_value.trim().length) {
                                data.set = {
                                    'item': data.arg_value.split('|')
                                }
                            } else {
                                data.set = {
                                    'item': []
                                }
                            }

                            delete data.text
                            break
                        case 'GROUPBY':
                            data.type = 4
                            if (data.arg_value.trim().length) {
                                data.set = {
                                    'item': data.arg_value.split('|')
                                }
                            } else {
                                data.set = {
                                    'item': []
                                }
                            }
                            delete data.text
                            break
                        case 'LIKE':
                            if (data.arg_value.indexOf('|') > -1) {
                                data.type = 4
                                if (data.arg_value.trim().length) {
                                    data.set = {
                                        'item': data.arg_value.split('|')
                                    }
                                } else {
                                    data.set = {
                                        'item': []
                                    }
                                }
                                delete data.text
                            } else {
                                data.type = 3
                                data.text = {
                                    'value': data.arg_value
                                }
                                delete data.set
                            }
                            break
                        case 'UNLIKE':
                            if (data.arg_value.indexOf('|') > -1) {
                                data.type = 4
                                if (data.arg_value.trim().length) {
                                    data.set = {
                                        'item': data.arg_value.split('|')
                                    }
                                } else {
                                    data.set = {
                                        'item': []
                                    }
                                }
                                delete data.text
                            } else {
                                data.type = 3
                                data.text = {
                                    'value': data.arg_value
                                }
                                delete data.set
                            }
                            break
                    }
                })
                delete appConfig.webCache

                const jsonStr = JSON.stringify(appConfig, null, 4)
                this.applicationJsonCache = jsonStr
                this.editorConfig.value = jsonStr
                this.toJsonDialogConf.isShow = true
            },
            editorInitAfter (editor) {
                this.editorConfig.editor = editor
                this.editorConfig.editor.setStyle('biz-app-container-tojson-ace')
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
            initResource (data) {
                if (data.applications && data.applications.length) {
                    this.setCurApplication(data.applications[0], 0)
                } else if (data.application && data.application.length) {
                    this.setCurApplication(data.application[0], 0)
                } else {
                    this.addLocalApplication()
                }
            },
            tabResource (type) {
                this.isTabChanging = true
                this.$refs.commonHeader.saveTemplate()
                this.$refs.commonHeader.autoSaveResource(type)
            },
            exceptionHandler (exceptionCode) {
                this.isDataLoading = false
                this.exceptionCode = exceptionCode
            },
            portNameSelect (selected, data) {
                const healthParams = this.curContainer.healthChecks[0]
                const type = healthParams.type
                if (type === 'HTTP' || type === 'REMOTE_HTTP') {
                    healthParams.http.portName = selected
                } else if (type === 'TCP' || type === 'REMOTE_TCP') {
                    healthParams.tcp.portName = selected
                } else if (type === 'COMMAND') {
                    healthParams.command.portName = selected
                }
            },
            toggleRouter (target) {
                this.$router.push({
                    name: target,
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode,
                        templateId: this.templateId
                    }
                })
            },
            changeImagePullPolicy () {
                // 判断改变前的状态
                if (!this.isAlwayCheckImage) {
                    this.curContainer.imagePullPolicy = 'Always'
                } else {
                    this.curContainer.imagePullPolicy = 'IfNotPresent'
                }
            },
            addLocalApplication () {
                const application = JSON.parse(JSON.stringify(applicationParams))
                const index = this.applications.length
                const now = +new Date()
                const applicationName = 'application-' + (index + 1)
                const containerName = 'container-1'

                application.id = 'local_' + now
                application.isEdited = true

                application.config.metadata.name = applicationName
                application.config.spec.template.spec.containers[0].name = containerName
                this.applications.push(application)

                this.setCurApplication(application, index)
                this.$refs.applicationTooltip.visible = false
            },
            setCurApplication (application, index) {
                this.curApplication = application
                this.curApplicationId = application.id

                clearInterval(this.compareTimer)
                clearTimeout(this.setTimer)
                this.setTimer = setTimeout(() => {
                    if (!this.curApplication.cache) {
                        this.curApplication.cache = JSON.parse(JSON.stringify(application))
                    }
                    this.watchChange()
                }, 500)
            },
            watchChange () {
                this.compareTimer = setInterval(() => {
                    const appCopy = JSON.parse(JSON.stringify(this.curApplication))
                    const cacheCopy = JSON.parse(JSON.stringify(this.curApplication.cache))
                    // 删除无用属性
                    delete appCopy.isEdited
                    delete appCopy.cache
                    delete appCopy.id
                    appCopy.config.spec.template.spec.containers.forEach(item => {
                        item.ports.forEach(port => {
                            delete port.isLink
                        })
                    })

                    delete cacheCopy.isEdited
                    delete cacheCopy.cache
                    delete cacheCopy.id
                    cacheCopy.config.spec.template.spec.containers.forEach(item => {
                        item.ports.forEach(port => {
                            delete port.isLink
                        })
                    })

                    const appStr = JSON.stringify(appCopy)
                    const cacheStr = JSON.stringify(cacheCopy)

                    if (String(this.curApplication.id).indexOf('local_') > -1) {
                        this.curApplication.isEdited = true
                    } else if (appStr !== cacheStr) {
                        this.curApplication.isEdited = true
                    } else {
                        this.curApplication.isEdited = false
                    }
                }, 1000)
            },
            setCurContainer (container, index) {
                // this.imageVersionList = []
                // 保存当前container数据
                const httpHeaders = this.$refs.headerKeyer.getKeyObject()
                this.curContainer.healthChecks[0].http.headers = httpHeaders
                // 切换container
                this.curContainer = container
                this.curContainerIndex = index
            },
            removeContainer (index) {
                const containers = this.curApplication.config.spec.template.spec.containers
                containers.splice(index, 1)
                if (this.curContainerIndex === index) {
                    this.curContainerIndex = 0
                } else if (this.curContainerIndex > index) {
                    this.curContainerIndex = this.curContainerIndex - 1
                }
                this.curContainer = containers[this.curContainerIndex]
            },
            addLocalContainer () {
                const container = JSON.parse(JSON.stringify(containerParams))
                const containers = this.curApplication.config.spec.template.spec.containers
                const index = containers.length
                container.name = 'container-' + (index + 1)
                containers.push(container)
                this.setCurContainer(container, index)
                this.$refs.containerTooltip.visible = false
            },
            removeLocalApplication (application, index) {
                // 是否删除当前项
                if (this.curApplication.id === application.id) {
                    if (index === 0 && this.applications[index + 1]) {
                        this.setCurApplication(this.applications[index + 1])
                    } else if (this.applications[0]) {
                        this.setCurApplication(this.applications[0])
                    }
                }
                this.applications.splice(index, 1)
            },
            removeApplication (application, index) {
                const self = this
                const projectId = this.projectId
                const version = this.curVersion
                const applicationId = application.id
                this.$bkInfo({
                    title: '确认',
                    content: this.$createElement('p', { style: { 'text-align': 'center' } }, `删除Application：${application.config.metadata.name || '未命名'}`),
                    confirmFn () {
                        if (applicationId.indexOf && applicationId.indexOf('local_') > -1) {
                            self.removeLocalApplication(application, index)
                        } else {
                            self.$store.dispatch('mesosTemplate/removeApplication', { applicationId, version, projectId }).then(res => {
                                const data = res.data
                                self.removeLocalApplication(application, index)

                                if (data.version) {
                                    self.$store.commit('mesosTemplate/updateCurVersion', data.version)
                                    self.$store.commit('mesosTemplate/updateBindVersion', true)
                                    // self.$refs.commonHeader.saveVersion(data.version) // 保存到默认版本
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
            togglePartA () {
                this.isPartAShow = !this.isPartAShow
            },
            togglePartB () {
                this.isPartBShow = !this.isPartBShow
            },
            togglePartC () {
                this.isPartCShow = !this.isPartCShow
            },
            initTemplate () {
                this.initApplicationList()
            },
            initApplicationList () {
                setTimeout(() => {
                    if (!this.applications.length) {
                        this.addLocalApplication()
                    }
                }, 1000)
            },
            saveApplicationSuccess (params) {
                this.applications.forEach(item => {
                    if (params.responseData.id === item.id || params.preId === item.id) {
                        item.cache = JSON.parse(JSON.stringify(item))
                    }
                })
                if (params.responseData.id === this.curApplication.id || params.preId === this.curApplication.id) {
                    this.updateLocalData(params.resource)
                }
            },
            updateLocalData (data) {
                this.curApplicationCache = JSON.parse(JSON.stringify(this.curApplication))
                this.curApplication.isEdited = false
                if (data.id) {
                    this.curApplication.id = data.id
                    this.curApplicationId = data.id
                }
                if (data.version) {
                    this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                }

                this.$store.commit('mesosTemplate/updateApplications', this.applications)
                setTimeout(() => {
                    this.applications.forEach(item => {
                        if (item.id === data.id) {
                            this.setCurApplication(item)
                        }
                    })
                }, 500)
            },
            createFirstApplication (data) {
                const templateId = this.templateId
                const projectId = this.projectId
                this.$store.dispatch('mesosTemplate/addFirstApplication', { projectId, templateId, data }).then(res => {
                    const data = res.data
                    this.$bkMessage({
                        theme: 'success',
                        message: '数据保存成功！'
                    })
                    this.updateLocalData(data)
                    this.isDataSaveing = false
                    if (templateId === 0 || templateId === '0') {
                        this.$router.push({
                            name: 'mesosTemplatesetApplication',
                            params: {
                                projectId: this.projectId,
                                projectCode: this.projectCode,
                                templateId: data.template_id
                            }
                        })
                    }
                }, res => {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
            },
            updateApplication (data) {
                const version = this.curVersion
                const projectId = this.projectId
                const applicationId = this.curApplicationId
                this.$store.dispatch('mesosTemplate/updateApplication', { projectId, version, data, applicationId }).then(res => {
                    const data = res.data
                    this.$bkMessage({
                        theme: 'success',
                        message: '数据保存成功！'
                    })
                    this.updateLocalData(data)
                    this.isDataSaveing = false
                }, res => {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                    this.isDataSaveing = false
                })
            },
            createApplication (data) {
                const version = this.curVersion
                const projectId = this.projectId
                this.$store.dispatch('mesosTemplate/addApplication', { projectId, version, data }).then(res => {
                    const data = res.data
                    this.$bkMessage({
                        theme: 'success',
                        message: '数据保存成功！'
                    })

                    this.updateLocalData(data)
                    this.isDataSaveing = false
                }, res => {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                    this.isDataSaveing = false
                })
            },
            removeVolumn (item, index) {
                const volumes = this.curContainer.volumes
                volumes.splice(index, 1)
            },
            addVolumn () {
                const volumes = this.curContainer.volumes
                volumes.push({
                    'volume': {
                        'hostPath': '',
                        'mountPath': '',
                        'subPath': '',
                        'readOnly': false
                    },
                    'type': 'custom',
                    'name': ''
                })
            },
            removeEnv (item, index) {
                const envList = this.curContainer.env_list
                envList.splice(index, 1)
            },
            addEnv () {
                const envList = this.curContainer.env_list
                envList.push({
                    'type': 'custom',
                    'key': '',
                    'value': ''
                })
            },
            pasteKey (item, event) {
                const cache = item.key
                this.paste(event)
                item.key = cache
                setTimeout(() => {
                    item.key = cache
                }, 0)
            },
            paste (event) {
                const clipboard = event.clipboardData
                const text = clipboard.getData('Text')
                const envList = this.curContainer.env_list
                if (text) {
                    const items = text.split('\n')
                    items.forEach(item => {
                        const arr = item.split('=')
                        envList.push({
                            type: 'custom',
                            key: arr[0],
                            value: arr[1]
                        })
                    })
                }
                setTimeout(() => {
                    this.formatEnvListData()
                }, 10)

                return false
            },
            formatEnvListData () {
                // 去掉空值
                if (this.curContainer.env_list.length) {
                    const results = []
                    const keyObj = {}
                    const length = this.curContainer.env_list.length
                    this.curContainer.env_list.forEach((item, i) => {
                        if (item.key || item.value) {
                            if (!keyObj[item.key]) {
                                results.push(item)
                                keyObj[item.key] = true
                            }
                        }
                    })
                    const patchLength = results.length - length
                    if (patchLength > 0) {
                        for (let i = 0; i < patchLength; i++) {
                            results.push({
                                type: 'custom',
                                key: '',
                                value: ''
                            })
                        }
                    }
                    this.curContainer.env_list.splice(0, this.curContainer.env_list.length, ...results)
                }
            },
            removeConstraint (item, index) {
                const constraint = this.curApplication.config.constraint.intersectionItem
                constraint.splice(index, 1)
            },
            getVolumeNameList (type) {
                if (type === 'configmap') {
                    return this.configmapList
                } else if (type === 'secret') {
                    return this.secretList
                }
            },
            getVolumeSourceList (type, name) {
                if (!name) return []
                if (type === 'configmap') {
                    const list = this.configmapList
                    for (const item of list) {
                        if (item.name === name) {
                            return item.childList
                        }
                    }
                    return []
                } else if (type === 'secret') {
                    const list = this.secretList
                    for (const item of list) {
                        if (item.name === name) {
                            return item.childList
                        }
                    }
                    return []
                }
                return []
            },
            addConstraint () {
                const constraint = this.curApplication.config.constraint.intersectionItem
                constraint.push({
                    unionData: [
                        {
                            name: 'hostname',
                            operate: 'CLUSTER',
                            type: 4,
                            arg_value: '',
                            text: {
                                value: ''
                            },
                            set: {
                                item: []
                            }
                        }
                    ]
                })
            },

            selectConstraintName (data, item) {
                if (data === 'ip-resources') {
                    item.unionData[0].operate = 'GREATER'
                    item.unionData[0].arg_value = ''
                }
            },
            selectOperate (data) {
                const operate = data.operate
                if (operate === 'UNIQUE') {
                    data.type = 0
                    data.arg_value = ''
                }
            },
            checkData () {
                const appName = this.curApplication.config.metadata.name
                const instance = this.curApplication.config.spec.instance
                const nameReg1 = /^[a-z]{1}[a-z0-9-]{0,29}$/
                const nameReg2 = /^[a-zA-Z]{1}[a-zA-Z0-9-_]{0,29}$/
                const pathReg = /\/((?!\.)[\w\d\-./~]+)+/

                if (appName === '') {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入应用名称！'
                    })
                    return false
                }
                if (!nameReg1.test(appName)) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '应用名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                        delay: 8000
                    })
                    return false
                }

                if (instance === '') {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入实例数量！'
                    })
                    return false
                }

                const containers = this.curApplication.config.spec.template.spec.containers

                for (const container of containers) {
                    // 检查container name
                    if (!container.name) {
                        this.$bkMessage({
                            theme: 'error',
                            message: `容器名称不能为空！`
                        })
                        return false
                    }

                    if (!nameReg1.test(container.name)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: '容器名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符',
                            delay: 8000
                        })
                        return false
                    }

                    // 检查container镜像设置
                    if (!container.image) {
                        this.$bkMessage({
                            theme: 'error',
                            delay: 5000,
                            message: `容器${container.name}的镜像及版本配置：请设置所属的镜像及版本！`
                        })
                        return false
                    }

                    // 端口映射检查
                    const portNameCache = {}
                    for (const item of container.ports) {
                        if (item.name || item.protocol || item.containerPort || (item.hostPort !== '')) {
                            if (!item.name) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: `容器${container.name}的端口映射配置：名称不能为空！`
                                })
                                return false
                            }
                            if (!nameReg2.test(item.name)) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: `容器${container.name}的端口映射配置：名称错误，只能包含：字母、数字、连字符(-)、下划线(_)，必须是字母开头，长度小于30个字符`,
                                    delay: 8000
                                })
                                return false
                            }
                            if (portNameCache[item.name]) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: `容器${container.name}的端口映射配置：端口名称不可重复！`,
                                    delay: 8000
                                })
                                return false
                            } else {
                                portNameCache[item.name] = true
                            }
                            if (!item.protocol) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: `容器${container.name}的端口映射配置：协议不能为空！`
                                })
                                return false
                            }
                            if (!item.containerPort) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: `容器${container.name}的端口映射配置：容器端口不能为空！`
                                })
                                return false
                            }
                            if (parseInt(item.containerPort) < 1 || parseInt(item.containerPort) > 65535) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: `容器${container.name}的端口映射配置：容器端口范围为1-65535！`
                                })
                                return false
                            }
                            if (item.hostPort === '') {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: `容器${container.name}的端口映射配置：主机端口不能为空！`
                                })
                                return false
                            }
                            if ((parseInt(item.hostPort) < 31000 && parseInt(item.hostPort) !== 0) || parseInt(item.hostPort) > 32000) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: `容器${container.name}的端口映射配置：主机端口范围为31000-32000或者0！`
                                })
                                return false
                            }
                        }
                    }

                    // 检查container volumes
                    if (container.volumes.length) {
                        for (const item of container.volumes) {
                            if (item.name || item.volume.hostname || item.volume.mountPath || item.volume.subPath) {
                                if (!item.name) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: `容器${container.name}的挂载卷配置：挂载名不能为空！`
                                    })
                                    return false
                                }
                                if (!nameReg2.test(item.name)) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: `容器${container.name}的挂载卷配置：挂载名错误，只能包含：字母、数字、连字符(-)、下划线(_)，必须是字母开头，长度小于30个字符`,
                                        delay: 8000
                                    })
                                    return false
                                }
                                if (!item.volume.hostPath) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: `容器${container.name}的挂载卷配置：挂载源不能为空！`,
                                        delay: 5000
                                    })
                                    return false
                                }
                                if (!item.volume.mountPath) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        message: `容器${container.name}的挂载卷配置：容器目录不能为空！`,
                                        delay: 5000
                                    })
                                    return false
                                }
                                if (!pathReg.test(item.volume.mountPath)) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: `容器${container.name}的挂载卷配置：容器目录不正确！`
                                    })
                                    return false
                                }
                            }
                        }
                    }

                    // 环境变量检查
                    const envList = container.env_list
                    for (const env of envList) {
                        if (env.key || env.value) {
                            if (!env.key) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: `容器${container.name}的环境变量配置：键不能为空！`,
                                    delay: 5000
                                })
                                return false
                            }
                            if (!env.value) {
                                this.$bkMessage({
                                    theme: 'error',
                                    message: `容器${container.name}的环境变量配置：值不能为空！`,
                                    delay: 5000
                                })
                                return false
                            }
                        }
                    }

                    // 资源限制
                    if (container.resources.limits.cpu !== undefined) {
                        if (container.resources.limits.cpu < 0.001) {
                            this.$bkMessage({
                                theme: 'error',
                                message: `容器${container.name}的资源限制配置：CPU限制不能少于0.001！`,
                                delay: 5000
                            })
                            return false
                        }
                        if (container.resources.limits.cpu > 128) {
                            this.$bkMessage({
                                theme: 'error',
                                message: `容器${container.name}的资源限制配置：CPU限制不能大于128！`,
                                delay: 5000
                            })
                            return false
                        }
                    }

                    // 健康检查
                    const healthChecks = container.healthChecks[0]
                    if (healthChecks.type) {
                        switch (healthChecks.type) {
                            case 'HTTP':
                            case 'REMOTE_HTTP':
                                if (!healthChecks.http.portName) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: `容器${container.name}的健康检查配置：端口名称不能为空！`
                                    })
                                    return false
                                }
                                break
                            case 'TCP':
                            case 'REMOTE_TCP':
                                if (!healthChecks.tcp.portName) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: `容器${container.name}的健康检查配置：端口名称不能为空！`
                                    })
                                    return false
                                }
                                break
                            case 'COMMAND':
                                if (!healthChecks.command.portName) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: `容器${container.name}的健康检查配置：端口名称不能为空！`
                                    })
                                    return false
                                }
                                if (!healthChecks.command.value) {
                                    this.$bkMessage({
                                        theme: 'error',
                                        delay: 5000,
                                        message: `容器${container.name}的健康检查配置：检查命令不能为空！`
                                    })
                                    return false
                                }
                                break
                        }
                    }

                    if (container.logListCache.length) {
                        for (const log of container.logListCache) {
                            if (log.value && !pathReg.test(log.value)) {
                                this.$bkMessage({
                                    theme: 'error',
                                    delay: 5000,
                                    message: `容器${container.name}的非标准日志采集配置：日志绝对路径不正确！`
                                })
                                return false
                            }
                        }
                    }
                }

                return true
            },
            updateApplicationRemark (list, data) {
                if (!this.curApplication.config.webCache) {
                    this.curApplication.config.webCache = {}
                }
                this.curApplication.config.metadata.annotations = data
                this.curApplication.config.webCache.remarkListCache = list
            },
            updateApplicationLabel (list, data) {
                if (!this.curApplication.config.webCache) {
                    this.curApplication.config.webCache = {}
                }
                this.curApplication.config.metadata.labels = data
                this.curApplication.config.webCache.labelListCache = list
            },
            updateApplicationLogLabel (list, data) {
                if (!this.curApplication.config.webCache) {
                    this.curApplication.config.webCache = {}
                }
                this.curApplication.config.customLogLabel = data
                this.curApplication.config.webCache.logLabelListCache = list
            },
            formatData () {
                const params = JSON.parse(JSON.stringify(this.curApplication))
                params.template = {
                    name: this.curTemplate.name,
                    desc: this.curTemplate.desc
                }
                delete params.isEdited
                // 键值转换
                const remarkKeyList = this.$refs.remarkKeyer.getKeyObject()
                const labelKeyList = this.$refs.labelKeyer.getKeyObject()

                params.config.metadata.labels = labelKeyList
                params.config.metadata.annotations = remarkKeyList

                // 转换调度约束
                const constraint = params.config.constraint.intersectionItem
                constraint.forEach(item => {
                    const data = item.unionData[0]
                    const operate = data.operate
                    switch (operate) {
                        case 'UNIQUE':
                            delete data.type
                            delete data.set
                            delete data.text
                            break
                        case 'MAXPER':
                            data.type = 3
                            data.text = {
                                'value': data.arg_value
                            }
                            delete data.set
                            break
                        case 'CLUSTER':
                            data.type = 4
                            if (data.arg_value.trim().length) {
                                data.set = {
                                    'item': data.arg_value.split('|')
                                }
                            } else {
                                data.set = {
                                    'item': []
                                }
                            }

                            delete data.text
                            break
                        case 'GROUPBY':
                            data.type = 4
                            if (data.arg_value.trim().length) {
                                data.set = {
                                    'item': data.arg_value.split('|')
                                }
                            } else {
                                data.set = {
                                    'item': []
                                }
                            }
                            delete data.text
                            break
                        case 'LIKE':
                            if (data.arg_value.indexOf('|') > -1) {
                                data.type = 4
                                if (data.arg_value.trim().length) {
                                    data.set = {
                                        'item': data.arg_value.split('|')
                                    }
                                } else {
                                    data.set = {
                                        'item': []
                                    }
                                }
                                delete data.text
                            } else {
                                data.type = 3
                                data.text = {
                                    'value': data.arg_value
                                }
                                delete data.set
                            }
                            break
                        case 'UNLIKE':
                            if (data.arg_value.indexOf('|') > -1) {
                                data.type = 4
                                if (data.arg_value.trim().length) {
                                    data.set = {
                                        'item': data.arg_value.split('|')
                                    }
                                } else {
                                    data.set = {
                                        'item': []
                                    }
                                }
                                delete data.text
                            } else {
                                data.type = 3
                                data.text = {
                                    'value': data.arg_value
                                }
                                delete data.set
                            }
                            break
                    }
                })

                // 转换命令参数和环境变量
                const containers = params.config.spec.template.spec.containers
                containers.forEach(container => {
                    if (container.args_text.trim().length) {
                        container.args = container.args_text.split(' ')
                    } else {
                        container.args = []
                    }

                    container.resources.limits.cpu = parseFloat(container.resources.limits.cpu)

                    // docker参数
                    const parameterList = container.parameter_list
                    container.parameters = []
                    parameterList.forEach(param => {
                        if (param.key && param.value) {
                            container.parameters.push(param)
                        }
                    })

                    // 端口
                    const ports = container.ports
                    const validatePorts = []
                    ports.forEach(item => {
                        if (item.containerPort && (item.hostPort !== undefined) && item.name && item.protocol) {
                            validatePorts.push({
                                id: item.id,
                                containerPort: item.containerPort,
                                hostPort: item.hostPort,
                                protocol: item.protocol,
                                name: item.name
                            })
                        }
                    })
                    container.ports = validatePorts

                    // volumes
                    const volumes = container.volumes
                    let validateVolumes = []
                    validateVolumes = volumes.filter(item => {
                        return item.volume.hostPath && item.volume.mountPath && item.name
                    })
                    container.volumes = validateVolumes

                    // logpath
                    const paths = []
                    const logList = container.logListCache
                    logList.forEach(item => {
                        if (item.value) {
                            paths.push(item.value)
                        }
                    })
                    container.logPathList = paths
                })
                return params
            },
            saveApplication () {
                if (!this.checkData()) {
                    return false
                }
                if (this.isDataSaveing) {
                    return false
                } else {
                    this.isDataSaveing = true
                }
                const data = this.formatData()
                if (this.curVersion) {
                    if (this.curApplicationId.indexOf && this.curApplicationId.indexOf('local') > -1) {
                        this.createApplication(data)
                    } else {
                        this.updateApplication(data)
                    }
                } else {
                    this.createFirstApplication(data)
                }
            },
            initImageList () {
                this.isLoadingImageList = true
                const projectId = this.projectId
                this.$store.dispatch('mesosTemplate/getImageList', { projectId }).then(res => {
                    const data = res.data
                    data.forEach(item => {
                        item._id = item.value
                        item._name = item.name
                    })
                    this.imageList.splice(0, this.imageList.length, ...data)
                    this.$store.commit('mesosTemplate/updateImageList', this.imageList)
                    this.isLoadingImageList = false
                }, res => {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        delay: 10000
                    })
                    this.isLoadingImageList = false
                })
            },
            setImageVersion (value, data) {
                /**
                 *   根据imagename的 is_pub:
                 *   1) true:
                 *   image = imageBase + imageName + ':' + imageVersion
                 *   2)false:
                 *   image = imageBase + imageName + ':' + imageVersion
                 *   内部版：
                 *   3)无 [用户填写变量的情况]
                 *   image = imageBase +  'paas/' + projectCode + '/' + imageName + ':' + imageVersion
                 *   企业版：
                 *   3) image = imageBase + '/' + projectCode + '/' + imageName + ':' + imageVersion
                 */
                // 镜像和版本都是通过下拉选择
                const projectCode = this.projectCode
                // curImageData不是空对象
                if (JSON.stringify(this.curImageData) !== '{}') {
                    if (data.text && data.value) {
                        this.curContainer.imageVersion = data.text
                        this.curContainer.image = data.value
                    } else if (this.curImageData.is_pub !== undefined) {
                        // 镜像是下拉，版本是变量
                        // image = imageBase + imageName + ':' + imageVersion
                        const imageName = this.curContainer.imageName
                        this.curContainer.imageVersion = value
                        this.curContainer.image = `${DEVOPS_ARTIFACTORY_HOST}/${imageName}:${value}`
                    } else {
                        // 镜像和版本是变量
                        // image = imageBase +  'paas/' + projectCode + '/' + imageName + ':' + imageVersion
                        const imageName = this.curContainer.imageName
                        this.curContainer.imageVersion = value
                        this.curContainer.image = `${DEVOPS_ARTIFACTORY_HOST}/${projectCode}/${imageName}:${value}`
                    }
                }
            },
            changeImage (value, data, isInitTrigger) {
                const projectId = this.projectId
                const imageId = data.value
                const isPub = data.is_pub
                this.curImageData = data
                // 如果不是输入变量
                if (isPub !== undefined) {
                    this.$store.dispatch('mesosTemplate/getImageVertionList', { projectId, imageId, isPub }).then(res => {
                        const data = res.data
                        data.forEach(item => {
                            item._id = item.text
                            item._name = item.text
                        })
                        this.imageVersionList.splice(0, this.imageVersionList.length, ...data)
                        // 非首次关联触发，默认选择第一项或清空
                        if (isInitTrigger) return

                        if (this.imageVersionList.length) {
                            const imageInfo = this.imageVersionList[0]
                            this.curContainer.image = imageInfo.value
                            this.curContainer.imageVersion = imageInfo.text
                        } else {
                            this.curContainer.image = ''
                        }
                    }, res => {
                        const message = res.message
                        this.$bkMessage({
                            theme: 'error',
                            message: message
                        })
                    })
                } else if (!isInitTrigger) {
                    this.imageVersionList = []
                    this.curContainer.image = ''

                    this.curContainer.imageVersion = ''
                }
            },
            addPort () {
                const id = +new Date()
                const params = {
                    id: id,
                    containerPort: '',
                    hostPort: '',
                    name: '',
                    protocol: '',
                    isLink: false
                }

                this.curContainer.ports.push(params)
            },
            addLog () {
                this.curContainer.logListCache.push({
                    value: ''
                })
            },
            removeLog (log, index) {
                this.curContainer.logListCache.splice(index, 1)
            },
            changeProtocol (item) {
                const projectId = this.projectId
                const version = this.curVersion
                const portId = item.id
                this.$store.dispatch('mesosTemplate/checkPortIsLink', { projectId, version, portId }).then(res => {
                }, res => {
                    const message = res.message || res.data.data
                    const msg = message.split(',')[0]
                    this.$bkMessage({
                        theme: 'error',
                        message: msg + '，不能修改协议！'
                    })
                })
            },
            removePort (item, index) {
                const projectId = this.projectId
                const version = this.curVersion
                const portId = item.id
                this.$store.dispatch('mesosTemplate/checkPortIsLink', { projectId, version, portId }).then(res => {
                    this.curContainer.ports.splice(index, 1)
                }, res => {
                    const message = res.message || res.data.data
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                })
            },
            selectVolumeType (volumeItem) {
                volumeItem.name = ''
                volumeItem.volume.hostPath = ''
                volumeItem.volume.mountPath = ''
                volumeItem.volume.subPath = ''
                const data = Object.assign([], this.curContainer.volumes)
                this.curContainer.volumes.splice(0, this.curContainer.volumes.length, ...data)
            },
            setVolumeName (volumeItem) {
                volumeItem.volume.hostPath = ''
            },
            initVolumeConfigmaps () {
                const version = this.curVersion
                if (!version) {
                    return false
                }
                const projectId = this.projectId

                this.$store.dispatch('mesosTemplate/getConfigmaps', { projectId, version }).then(res => {
                    const data = res.data
                    const keyList = []

                    data.forEach(item => {
                        const list = []
                        const name = item.name
                        const keys = item.keys
                        keys.forEach(key => {
                            const params = {
                                id: name + '.' + key,
                                name: name + '.' + key
                            }
                            list.push(params)
                            keyList.push(params)
                        })
                        item.childList = list
                    })
                    this.configmapKeyList.splice(0, this.configmapKeyList.length, ...keyList)
                    this.configmapList.splice(0, this.configmapList.length, ...data)
                }, res => {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                })
            },
            initVloumeSelectets () {
                const version = this.curVersion
                if (!version) {
                    return false
                }
                const projectId = this.projectId

                this.$store.dispatch('mesosTemplate/getSecrets', { projectId, version }).then(res => {
                    const data = res.data
                    const keyList = []
                    data.forEach(item => {
                        const list = []
                        const name = item.name
                        const keys = item.keys
                        keys.forEach(key => {
                            const params = {
                                id: name + '.' + key,
                                name: name + '.' + key
                            }
                            list.push(params)
                            keyList.push(params)
                        })

                        item.childList = list
                    })
                    this.secretKeyList.splice(0, this.secretKeyList.length, ...keyList)
                    this.secretList.splice(0, this.secretList.length, ...data)
                }, res => {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                })
            },
            initMetricList () {
                const projectId = this.projectId
                this.$store.dispatch('mesosTemplate/getMetricList', projectId)
            },
            initVloumeKeys (index, data) {
                const list = data.childList
                this.secretKeyList.splice(0, this.secretKeyList.length, ...list)
            },
            clearNetworkCustom () {
                this.curApplication.config.spec.template.spec.custom_value = ''
            }
        }
    }
</script>

<style scoped>
    @import './application.css';
</style>
