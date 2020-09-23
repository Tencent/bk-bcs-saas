<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-crd-instance-title">
                <a href="javascript:void(0);" class="bk-icon icon-arrows-left back" @click="goBack"></a>
                {{$t('日志采集规则')}}
                <span class="biz-tip f12 ml10">({{$t('集群名称')}}：{{clusterName}})</span>
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
                        <button class="bk-button bk-primary" @click.stop.prevent="createLoadBlance">
                            <i class="bk-icon icon-plus" style="top: -1px;"></i>
                            <span>{{$t('新建规则')}}</span>
                        </button>
                    </div>
                    <div class="right search-wrapper">
                        <div class="left">
                            <bk-selector
                                style="width: 135px;"
                                :searchable="true"
                                :placeholder="$t('命名空间')"
                                :selected.sync="searchParams.namespace"
                                :list="nameSpaceList"
                                :setting-key="'name'"
                                :display-key="'name'"
                                :allow-clear="true"
                                @clear="clusterClear">
                            </bk-selector>
                        </div>
                        <div class="left">
                            <bk-selector
                                style="width: 135px;"
                                :placeholder="$t('应用类型')"
                                :selected.sync="searchParams.workload_type"
                                :list="appTypes"
                                :setting-key="'id'"
                                :display-key="'name'"
                                :allow-clear="true"
                                @clear="clusterClear">
                            </bk-selector>
                        </div>
                        <div class="left">
                            <bk-input
                                style="width: 135px;"
                                :placeholder="$t('应用名')"
                                :value.sync="searchParams.workload_name">
                            </bk-input>
                        </div>
                        <div class="left">
                            <bk-button type="primary" :title="$t('查询')" icon="search" @click="handleSearch">
                                {{$t('查询')}}
                            </bk-button>
                        </div>
                    </div>
                </div>

                <div class="biz-crd-instance">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table has-table-hover biz-table biz-crd-instance-table">
                            <thead>
                                <tr>
                                    <th style="min-width: 220px;">{{$t('名称')}}</th>
                                    <th style="min-width: 220px;">{{$t('集群')}} / {{$t('命名空间')}}</th>
                                    <th style="min-width: 100px;">{{$t('日志源')}}</th>
                                    <th style="min-width: 200px;">{{$t('应用信息')}}</th>
                                    <th style="min-width: 250px;">{{$t('容器名')}} / {{$t('日志信息')}}</th>
                                    <th style="min-width: 250px;">{{$t('操作记录')}}</th>
                                    <th style="min-width: 90px;">{{$t('状态')}}</th>
                                    <th style="min-width: 140px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="crdInstanceList.length">
                                    <tr v-for="(crdInstance, index) in curPageData" :key="index">
                                        <td style="width: 200px; padding-left: 30px;">
                                            <a href="javascript: void(0)" class="bk-text-button biz-table-title biz-resource-title" @click.stop.prevent="editCrdInstance(crdInstance, true)">{{crdInstance.name || '--'}}</a>
                                        </td>
                                        <td>
                                            <p>{{$t('所属集群')}}：{{clusterName}}</p>
                                            <p>{{$t('命名空间')}}：{{crdInstance.namespace || '--'}}</p>
                                        </td>
                                        <td>{{crdInstance.config_type === 'custom' ? $t('指定容器') : $t('所有容器')}}</td>
                                        <td>
                                            <template v-if="crdInstance.config_type === 'custom'">
                                                <p>{{$t('类型')}}：{{crdInstance.crd_data.workload.type}}</p>
                                                <p>{{$t('名称')}}：{{crdInstance.crd_data.workload.name || '--'}}</p>
                                            </template>
                                            <template v-else>
                                                --
                                            </template>
                                        </td>
                                        <td>
                                            <template v-if="crdInstance.config_type === 'custom'">
                                                <bk-tooltip placement="top" :delay="500">
                                                    <p class="path-text" v-for="(conf, confIndex) of crdInstance.crd_data.workload.container_confs" :key="confIndex" style="display: block;">
                                                        {{conf.name}}：{{conf.log_paths[0] || '--'}}
                                                        <template v-if="conf.log_paths.length > 1">...</template>
                                                    </p>
                                                    <div slot="content">
                                                        <p v-for="(conf, confIndex) of crdInstance.crd_data.workload.container_confs" :key="confIndex">
                                                            {{conf.name}}：{{conf.log_paths.join(';') || '--'}}
                                                        </p>
                                                    </div>
                                                </bk-tooltip>
                                            </template>
                                            <template v-else>
                                                --
                                            </template>
                                        </td>
                                        <td>
                                            <p>{{$t('更新人')}}：{{crdInstance.operator || '--'}}</p>
                                            <p>{{$t('更新时间')}}：{{crdInstance.updated || '--'}}</p>
                                        </td>
                                        <td>{{crdInstance.bind_success ? $t('正常') : $t('异常')}}</td>
                                        <td>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="editCrdInstance(crdInstance)">{{$t('更新')}}</a>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="removeCrdInstance(crdInstance)">{{$t('删除')}}</a>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="7">
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
                            @page-change="handlerPageChange">
                        </bk-paging>
                    </div>
                </div>
            </template>

            <bk-sideslider
                style="z-index: 150;"
                :quick-close="false"
                :is-show.sync="crdInstanceSlider.isShow"
                :title="crdInstanceSlider.title"
                :width="800">
                <div class="p30" slot="content">
                    <div class="bk-form bk-form-vertical">
                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 346px;">
                                    <label class="bk-label">{{$t('名称')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            :placeholder="$t('请输入')"
                                            :value.sync="curCrdInstanceName"
                                            :disabled="true">
                                        </bk-input>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 352px;">
                                    <label class="bk-label">{{$t('所属集群')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请输入')"
                                            :setting-key="'cluster_id'"
                                            :display-key="'name'"
                                            :selected.sync="clusterId"
                                            :list="clusterList"
                                            :disabled="true">
                                        </bk-selector>
                                    </div>
                                </div>

                                <div class="bk-form-inline-item is-required" style="width: 352px; margin-left: 25px;">
                                    <label class="bk-label">{{$t('命名空间')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :searchable="true"
                                            :placeholder="$t('请选择')"
                                            :selected.sync="curCrdInstance.namespace"
                                            :setting-key="'name'"
                                            :list="nameSpaceList"
                                            :disabled="curCrdInstance.id">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item is-required mb5">
                            <label class="bk-label">{{$t('日志源')}}：</label>
                            <div class="bk-form-content">
                                <label class="bk-form-radio">
                                    <input type="radio" value="custom" name="cluster-type-radio" v-model="curCrdInstance.config_type" :disabled="curCrdInstance.id">
                                    <i class="bk-radio-text">{{$t('指定容器')}}</i>
                                </label>
                                <label class="bk-form-radio">
                                    <input type="radio" value="default" name="cluster-type-radio" v-model="curCrdInstance.config_type" :disabled="curCrdInstance.id">
                                    <i class="bk-radio-text">{{$t('所有容器')}}</i>
                                </label>
                            </div>
                        </div>

                        <section class="log-wrapper" v-if="curCrdInstance.config_type === 'default'">
                            <div class="bk-form-content log-flex">
                                <div class="bk-form-inline-item">
                                    <div class="log-form">
                                        <div class="label">{{$t('标准输出')}}：</div>
                                        <div class="content" style="width: 110px;">
                                            <label class="bk-form-checkbox" style="width: auto;">
                                                <input type="checkbox" value="true" name="cluster-classify-checkbox" checked disabled>
                                                <i class="bk-checkbox-text">{{$t('是否采集')}}</i>
                                                <i class="bk-icon icon-question-circle" v-bktooltips.right="$t('如果不勾选，将不采集此容器的标准输出')"></i>
                                            </label>
                                        </div>
                                    </div>
                                </div>

                                <div class="bk-form-inline-item">
                                    <div class="log-form">
                                        <div class="label" style="width: 110px;">{{$t('标准采集ID')}}：</div>
                                        <div class="content">
                                            <bk-input
                                                style="width: 80px;"
                                                type="number"
                                                :min="0"
                                                :placeholder="$t('请输入')"
                                                :value.sync="curCrdInstance.std_data_id"
                                                :disabled="!curCrdInstance.is_std_custom">
                                            </bk-input>
                                            <label class="bk-form-checkbox" style="width: auto;">
                                                <input class="ml5" type="checkbox" name="cluster-classify-checkbox" v-model="curCrdInstance.is_std_custom">
                                                <i class="bk-checkbox-text">{{$t('是否自定义')}}</i>
                                                <i class="bk-icon icon-question-circle" v-bktooltips.left="$t('采集id对应数据平台的data id，不勾选平台将分配默认的data id进行日志的清洗和入库。如果有特别的清洗和计算要求，用户可以填写自己的data id')"></i>
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>

                        <section class="log-wrapper" v-if="curCrdInstance.config_type === 'custom'">
                            <div class="bk-form-item">
                                <div class="bk-form-content log-flex mb15">
                                    <div class="bk-form-inline-item">
                                        <div class="log-form no-flex">
                                            <div class="label">{{$t('应用类型')}}：</div>
                                            <div class="content">
                                                <bk-selector
                                                    style="width: 330px;"
                                                    :placeholder="$t('应用类型')"
                                                    :selected.sync="curCrdInstance.workload.type"
                                                    :list="appTypes"
                                                    :setting-key="'id'"
                                                    :display-key="'name'"
                                                    :allow-clear="true"
                                                    :disabled="curCrdInstance.id">
                                                </bk-selector>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="bk-form-inline-item">
                                        <div class="log-form no-flex">
                                            <div class="label">{{$t('应用名称')}}：</div>
                                            <div class="content">
                                                <bk-input
                                                    style="width: 330px;"
                                                    :placeholder="$t('请输入应用名称，支持正则匹配')"
                                                    :value.sync="curCrdInstance.workload.name"
                                                    :disabled="curCrdInstance.id">
                                                </bk-input>
                                            </div>
                                        </div>
                                    </div>

                                </div>
                            </div>

                            <div class="bk-form-item">
                                <div class="bk-form-content log-flex mb10">
                                    <div class="log-form no-flex">
                                        <div class="label">{{$t('采集路径')}}：</div>
                                        <div class="content">
                                            <section class="log-inner-wrapper mb10" v-for="(containerConf, index) of curCrdInstance.workload.container_confs" :key="index">
                                                <div class="bk-form-content log-flex mb10">
                                                    <div class="bk-form-inline-item">
                                                        <div class="log-form">
                                                            <div class="label">{{$t('容器名')}}：</div>
                                                            <div class="content">
                                                                <bk-input
                                                                    style="width: 223px;"
                                                                    :placeholder="$t('请输入')"
                                                                    :value.sync="containerConf.name">
                                                                </bk-input>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div class="bk-form-content log-flex mb10">
                                                    <div class="bk-form-inline-item">
                                                        <div class="log-form">
                                                            <div class="label">{{$t('标准输出')}}：</div>
                                                            <div class="content" style="width: 223px;">
                                                                <label class="bk-form-checkbox" style="width: auto;">
                                                                    <input type="checkbox" name="cluster-classify-checkbox" value="true" v-model="containerConf.stdout">
                                                                    <i class="bk-checkbox-text">{{$t('是否采集')}}</i>
                                                                    <i class="bk-icon icon-question-circle" v-bktooltips.right="$t('如果不勾选，将不采集此容器的标准输出')"></i>
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class="bk-form-inline-item">
                                                        <div class="log-form">
                                                            <div class="label" style="width: 110px;">{{$t('标准采集ID')}}：</div>
                                                            <div class="content">
                                                                <bk-input
                                                                    style="width: 80px;"
                                                                    type="number"
                                                                    :min="0"
                                                                    :placeholder="$t('请输入')"
                                                                    :value.sync="containerConf.std_data_id"
                                                                    :disabled="!containerConf.is_std_custom">
                                                                </bk-input>
                                                                <label class="bk-form-checkbox" style="width: auto;">
                                                                    <input class="ml5" type="checkbox" name="cluster-classify-checkbox" v-model="containerConf.is_std_custom">
                                                                    <i class="bk-checkbox-text">{{$t('是否自定义')}}</i>
                                                                    <i class="bk-icon icon-question-circle" v-bktooltips.left="$t('采集id对应数据平台的data id，不勾选平台将分配默认的data id进行日志的清洗和入库。如果有特别的清洗和计算要求，用户可以填写自己的data id')"></i>
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
        
                                                <div class="bk-form-content log-flex">
                                                    <div class="bk-form-inlineitem">
                                                        <div class="log-form" style="width: 345px;">
                                                            <div class="label">{{$t('文件路径')}}：</div>
                                                            <div class="content log-path-wrapper" style="width: 223px;">
                                                                <textarea class="bk-form-textarea" v-model="containerConf.log_paths_str" style="width: 223px;" :placeholder="$t('多个以;分隔')"></textarea>
                                                                
                                                                <bk-tooltip placement="top" :delay="500">
                                                                    <i class="path-tip bk-icon icon-question-circle"></i>
                                                                    <div slot="content">
                                                                        <p>1. 请填写文件的绝对路径，不支持目录</p>
                                                                        <p>2. 支持通配符，但通配符仅支持文件级别的</p>
                                                                        <p>有效的示例: /data/log/*/*.log, /data/test.log, /data/log/log.*</p>
                                                                        <p>无效的示例: /data/log/*, /data/log</p>
                                                                    </div>
                                                                </bk-tooltip>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class="bk-form-inline-item">
                                                        <div class="log-form">
                                                            <div class="label" style="width: 110px;">{{$t('文件采集ID')}}：</div>
                                                            <div class="content">
                                                                <bk-input
                                                                    style="width: 80px;"
                                                                    type="number"
                                                                    :min="0"
                                                                    :placeholder="$t('请输入')"
                                                                    :value.sync="containerConf.file_data_id"
                                                                    :disabled="!containerConf.is_file_custom">
                                                                </bk-input>
                                                                <label class="bk-form-checkbox" style="width: auto;">
                                                                    <input class="ml5" type="checkbox" name="cluster-classify-checkbox" v-model="containerConf.is_file_custom">
                                                                    <i class="bk-checkbox-text">{{$t('是否自定义')}}</i>
                                                                    <i class="bk-icon icon-question-circle" v-bktooltips.left="$t('采集id对应数据平台的data id，不勾选平台将分配默认的data id进行日志的清洗和入库。如果有特别的清洗和计算要求，用户可以填写自己的data id')"></i>
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <i class="bk-icon icon-close log-close" @click="removeContainerConf(containerConf, index)" v-if="curCrdInstance.workload.container_confs.length > 1"></i>
                                            </section>

                                            <button class="log-block-btn mt10" @click="addContainerConf">
                                                <i class="bk-icon icon-plus"></i>
                                                {{$t('点击增加')}}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>

                        <div class="bk-form-item mt5" style="overflow: hidden;">
                            <label class="bk-label">{{$t('附加日志标签')}}：</label>
                        </div>

                        <div class="log-wrapper">
                            <bk-keyer
                                :key-list.sync="curLogLabelList"
                                :var-list="varList"
                                @change="updateLogLabels">
                            </bk-keyer>
                            <label class="bk-form-checkbox mt5" style="width: auto;">
                                <input type="checkbox" v-model="curCrdInstance.add_pod_labels_b" name="cluster-classify-checkbox">
                                <i class="bk-checkbox-text">{{$t('是否自动添加Pod中的labels')}}</i>
                            </label>
                        </div>

                        <div class="bk-form-item mt15">
                            <!-- <div class="log-tip">
                                <i class="bk-icon icon-info-circle-shape"></i>
                                <p class="desc">{{$t('日志采集规则要先于应用下发，否则下发后，对应的应用需要重建才能使采集任务生效')}}</p>
                            </div> -->
                            <button :class="['bk-button bk-primary', { 'is-loading': isDataSaveing }]" @click.stop.prevent="saveCrdInstance">{{curCrdInstance.id ? $t('更新') : $t('创建')}}</button>
                            <button class="bk-button bk-default" @click.stop.prevent="hideCrdInstanceSlider">{{$t('取消')}}</button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>

            <bk-sideslider
                :quick-close="true"
                :is-show.sync="detailSliderConf.isShow"
                :title="detailSliderConf.title"
                :width="'700'">
                <div class="p30" slot="content">
                    <p class="data-title">
                        {{$t('基础信息')}}
                    </p>
                    <div class="biz-metadata-box vertical mb20">
                        <div class="data-item">
                            <p class="key">{{$t('所属集群')}}：</p>
                            <p class="value">{{clusterName || '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('命名空间')}}：</p>
                            <p class="value">{{curCrdInstance.namespace || '--'}}</p>
                        </div>
                        <div class="data-item">
                            <p class="key">{{$t('规则名称')}}：</p>
                            <p class="value">{{curCrdInstance.name || '--'}}</p>
                        </div>
                    </div>
                    <p class="data-title">
                        {{$t('日志源信息')}}
                    </p>

                    <div class="biz-metadata-box vertical mb0">
                        <div class="data-item">
                            <p class="key">{{$t('日志源类型')}}：</p>
                            <p class="value">{{curCrdInstance.config_type === 'custom' ? $t('指定容器') : $t('所有容器')}}</p>
                        </div>
                        <template v-if="curCrdInstance.config_type === 'custom'">
                            <div class="data-item">
                                <p class="key">{{$t('应用类型')}}：</p>
                                <p class="value">{{curCrdInstance.workload.type || '--'}}</p>
                            </div>
                            <div class="data-item">
                                <p class="key">{{$t('应用名称')}}：</p>
                                <p class="value">{{curCrdInstance.workload.name || '--'}}</p>
                            </div>

                            <div class="data-item">
                                <p class="key">{{$t('采集路径')}}：</p>
                                <div class="value">
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <div class="data-item">
                                <p class="key">{{$t('是否采集')}}：</p>
                                <p class="value">{{$t('是')}}</p>
                            </div>
                            <div class="data-item">
                                <p class="key">{{$t('标准采集ID')}}：</p>
                                <p class="value">{{curCrdInstance.std_data_id || '--'}} ({{curCrdInstance.is_std_custom ? '自定义' : '默认'}})</p>
                            </div>
                        </template>
                    </div>

                    <div class="biz-metadata-box mb0 mt5" style="border: none;" v-if="curCrdInstance.config_type === 'custom'">
                        <table class="bk-table bk-log-table">
                            <thead>
                                <tr>
                                    <th style="width: 130px;">{{$t('容器名')}}</th>
                                    <th style="width: 200px;">{{$t('标准输出')}}</th>
                                    <th>{{$t('文件路径')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(containerConf, index) of curCrdInstance.workload.container_confs" :key="index">
                                    <td>
                                        {{containerConf.name || '--'}}
                                    </td>
                                    <td>
                                        {{$t('采集ID')}}：{{containerConf.std_data_id || '--'}} ({{containerConf.is_std_custom ? $t('自定义') : $t('默认')}})<br />
                                        {{$t('是否采集')}}：{{containerConf.stdout ? $t('是') : $t('否')}}
                                    </td>
                                    <td>
                                        <p>{{$t('采集ID')}}：{{containerConf.file_data_id || '--'}} ({{containerConf.is_file_custom ? $t('自定义') : $t('默认')}})</p>
                                        <div class="log-key-value">
                                            <div style="width: 38px;">{{$t('路径')}}：</div>
                                            <ul class="log-path-list" v-if="containerConf.log_paths.length">
                                                <li v-for="path of containerConf.log_paths" :key="path" v-if="path">{{path}}</li>
                                            </ul>
                                            <span v-else>--</span>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'
    import bkKeyer from '@open/components/keyer'

    export default {
        components: {
            bkKeyer
        },
        data () {
            return {
                isInitLoading: true,
                isPageLoading: false,
                exceptionCode: null,
                curPageData: [],
                isDataSaveing: false,
                prmissions: {},
                pageConf: {
                    total: 0,
                    totalPage: 1,
                    pageSize: 5,
                    curPage: 1,
                    show: true
                },
                crdInstanceSlider: {
                    title: this.$t('新建规则'),
                    isShow: false
                },
                searchParams: {
                    clusterIndex: 0,
                    namespace: 0,
                    workload_type: 0,
                    workload_name: ''
                },
                appTypes: [
                    {
                        id: 'Deployment',
                        name: 'Deployment'
                    },
                    {
                        id: 'DaemonSet',
                        name: 'DaemonSet'
                    },
                    {
                        id: 'Job',
                        name: 'Job'
                    },
                    {
                        id: 'StatefulSet',
                        name: 'StatefulSet'
                    },
                    {
                        id: 'GameStatefulSet',
                        name: 'GameStatefulSet'
                    }
                ],
                searchScope: '',
                nameSpaceList: [],
                curLabelList: [
                    {
                        key: '',
                        value: ''
                    }
                ],

                dbTypes: [
                    {
                        id: 'mysql',
                        name: 'mysql'
                    },
                    {
                        id: 'spider',
                        name: 'spider'
                    }
                ],

                curCrdInstance: {
                    'crd_kind': 'BcsLog',
                    'cluster_id': '',
                    'namespace': '',
                    'namespace_id': 0,
                    'config_type': 'custom',
                    'app_id': '',
                    'std_data_id': '',
                    'is_std_custom': false,
                    'stdout': true,
                    'labels': {},
                    'add_pod_labels': 'false',
                    'add_pod_labels_b': false,
                    'workload': {
                        'name': '',
                        'type': '',
                        'container_confs': [
                            {
                                'name': '',
                                'std_data_id': '',
                                'file_data_id': '',
                                'stdout': 'true',
                                'log_paths': [],
                                'log_paths_str': '',
                                'is_std_custom': false,
                                'is_file_custom': false
                            }
                        ]
                    }
                },
                detailSliderConf: {
                    isShow: false,
                    title: ''
                },
                crdKind: 'BcsLog',
                defaultStdDataId: 0,
                defaultFileDataId: 0
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            varList () {
                return this.$store.state.variable.varList
            },
            projectId () {
                return this.$route.params.projectId
            },
            crdInstanceList () {
                const list = Object.assign([], this.$store.state.crdInstanceList)
                list.forEach(item => {
                    if (item.config_type === 'custom') {
                        item.crd_data.workload.isExpand = false
                        item.crd_data.workload.container_confs.forEach(conf => {
                            if (!conf.log_paths) {
                                conf.log_paths = []
                            }
                        })
                    }
                })
                return list
            },
            clusterList () {
                return this.$store.state.cluster.clusterList
            },
            curProject () {
                return this.$store.state.curProject
            },
            clusterId () {
                return this.$route.params.clusterId
            },
            clusterName () {
                const cluster = this.clusterList.find(item => {
                    return item.cluster_id === this.clusterId
                })
                return cluster ? cluster.name : ''
            },
            searchScopeList () {
                const clusterList = this.$store.state.cluster.clusterList
                let results = []
                if (clusterList.length) {
                    results = []
                    clusterList.forEach(item => {
                        results.push({
                            id: item.cluster_id,
                            name: item.name
                        })
                    })
                }

                return results
            },
            curCrdInstanceName () {
                // 编辑状态，使用bcslog_name
                if (this.curCrdInstance.id && this.curCrdInstance.bcslog_name) {
                    return this.curCrdInstance.bcslog_name
                } else if (this.curCrdInstance.config_type === 'default') {
                    return 'default-std-log'
                } else {
                    const app = this.curCrdInstance.workload
                    if (app['type'] && app['name']) {
                        return `${app['type']}-${app['name']}-log`.toLowerCase()
                    } else {
                        return 'log'
                    }
                }
            },
            curLogLabelList () {
                const keyList = []
                const labels = this.curCrdInstance.labels || {}
                for (const key in labels) {
                    keyList.push({
                        key: key,
                        value: labels[key]
                    })
                }
                if (!keyList.length) {
                    keyList.push({
                        key: '',
                        value: ''
                    })
                }
                return keyList
            }
        },
        watch: {
            crdInstanceList () {
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },
            curPageData () {
                this.curPageData.forEach(item => {
                    if (item.clb_status && item.clb_status !== 'Running') {
                        this.getCrdInstanceStatus(item)
                    }
                })
            },
            curCrdInstance: {
                deep: true,
                handler () {
                    if (this.curCrdInstance.config_type === 'custom') {
                        const containerConfs = this.curCrdInstance.workload.container_confs
                        containerConfs.forEach(conf => {
                            if (!conf.is_std_custom) {
                                conf.std_data_id = this.defaultStdDataId
                            }
                            if (!conf.is_file_custom) {
                                conf.file_data_id = this.defaultFileDataId
                            }
                        })
                    } else {
                        if (!this.curCrdInstance.is_std_custom) {
                            this.curCrdInstance.std_data_id = this.defaultStdDataId
                        }
                    }
                }
            }
        },
        created () {
            // 如果不是mesos类型的项目，无法访问页面，重定向回集群首页
            if (this.curProject && this.curProject.kind === PROJECT_MESOS) {
                this.$router.push({
                    name: 'clusterMain',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
                return false
            }

            this.getCrdInstanceList()
            this.getNameSpaceList()
            this.getLogInfo()
        },
        methods: {
            goBack () {
                this.$router.push({
                    name: 'logCrdcontroller',
                    params: {
                        projectId: this.projectId
                    }
                })
            },

            /**
             * 搜索列表
             */
            handleSearch () {
                this.pageConf.curPage = 1
                this.isPageLoading = true

                this.getCrdInstanceList()
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
                this.handlerPageChange()
            },

            /**
             * 新建
             */
            createLoadBlance () {
                this.curCrdInstance = {
                    'crd_kind': 'BcsLog',
                    'cluster_id': this.clusterId,
                    'namespace': '',
                    'namespace_id': 0,
                    'config_type': 'custom',
                    'app_id': this.curProject.cc_app_id,
                    'std_data_id': this.defaultStdDataId,
                    'is_std_custom': false,
                    'stdout': 'true',
                    'labels': {},
                    'add_pod_labels': 'false',
                    'add_pod_labels_b': false,
                    'workload': {
                        'name': '',
                        'type': '',
                        'container_confs': [
                            {
                                'name': '',
                                'std_data_id': this.defaultStdDataId,
                                'file_data_id': this.defaultFileDataId,
                                'stdout': 'true',
                                'log_paths': '',
                                'log_paths_str': '',
                                'is_std_custom': false,
                                'is_file_custom': false
                            }
                        ]
                    }
                }

                this.crdInstanceSlider.title = this.$t('新建规则')
                this.crdInstanceSlider.isShow = true
            },

            updateLogLabels (list, data) {
                this.curCrdInstance.labels = data
            },

            /**
             * 编辑
             * @param  {object} crdInstance crdInstance
             * @param  {number} index 索引
             */
            async editCrdInstance (crdInstance, isReadonly) {
                if (crdInstance.permissions && !crdInstance.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: crdInstance.namespace,
                        resource_name: crdInstance.namespace_name,
                        resource_type: 'namespace'
                    })
                }

                try {
                    const projectId = this.projectId
                    const clusterId = this.clusterId
                    const crdId = crdInstance.id
                    const res = await this.$store.dispatch('crdcontroller/getCrdInstanceDetail', {
                        projectId,
                        clusterId,
                        crdId
                    })

                    if (res.data.config_type === 'custom') {
                        res.data.workload.container_confs.forEach(conf => {
                            if (!conf.log_paths) {
                                conf.log_paths = []
                            }
                            conf.log_paths_str = conf.log_paths.join(';')
                            // 是否自定义
                            conf.is_std_custom = String(conf.std_data_id) !== String(this.defaultStdDataId)
                            conf.is_file_custom = String(conf.file_data_id) !== String(this.defaultFileDataId)

                            conf.stdout = conf.stdout === 'true'
                        })
                    } else {
                        res.data.is_std_custom = String(res.data.std_data_id) !== String(this.defaultStdDataId)
                    }
                    if (!res.data.hasOwnProperty('add_pod_labels')) {
                        res.data.add_pod_labels = 'false'
                    }
                    res.data.add_pod_labels_b = res.data.add_pod_labels === 'true'
                    this.curCrdInstance = res.data
                    this.curCrdInstance.id = crdId

                    if (isReadonly) {
                        this.detailSliderConf.title = `${this.curCrdInstance.name}`
                        this.detailSliderConf.isShow = true
                    } else {
                        this.crdInstanceSlider.title = this.$t('编辑规则')
                        this.crdInstanceSlider.isShow = true
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 删除
             * @param  {object} crdInstance crdInstance
             * @param  {number} index 索引
             */
            async removeCrdInstance (crdInstance, index) {
                if (crdInstance.permissions && !crdInstance.permissions.use) {
                    await this.$store.dispatch('getResourcePermissions', {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: crdInstance.namespace,
                        resource_name: crdInstance.namespace_name,
                        resource_type: 'namespace'
                    })
                }

                const self = this
                const projectId = this.projectId
                const clusterId = this.clusterId
                const crdId = crdInstance.id

                this.$bkInfo({
                    title: '',
                    clsName: 'biz-remove-dialog',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除')}【${crdInstance.name}】？`),
                    async confirmFn () {
                        self.isPageLoading = true
                        try {
                            await self.$store.dispatch('crdcontroller/deleteCrdInstance', { projectId, clusterId, crdId })
                            self.$bkMessage({
                                theme: 'success',
                                message: self.$t('删除成功')
                            })
                            self.getCrdInstanceList()
                        } catch (e) {
                            catchErrorHandler(e, this)
                        } finally {
                            self.isPageLoading = false
                        }
                    }
                })
            },

            /**
             * 获取
             * @param  {number} crdInstanceId id
             * @return {object} crdInstance crdInstance
             */
            getCrdInstanceById (crdInstanceId) {
                return this.crdInstanceList.find(item => {
                    return item.id === crdInstanceId
                })
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.crdInstanceList.length
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
            },

            /**
             * 重新加载当前页
             */
            reloadCurPage () {
                this.initPageConf()
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 获取页数据
             * @param  {number} page 页
             * @return {object} data lb
             */
            getDataByPage (page) {
                // 如果没有page，重置
                if (!page) {
                    this.pageConf.curPage = page = 1
                }
                let startIndex = (page - 1) * this.pageConf.pageSize
                let endIndex = page * this.pageConf.pageSize
                // this.isPageLoading = true
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.crdInstanceList.length) {
                    endIndex = this.crdInstanceList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.crdInstanceList.slice(startIndex, endIndex)
            },

            /**
             * 分页改变回调
             * @param  {number} page 页
             */
            handlerPageChange (page = 1) {
                this.isPageLoading = true
                this.pageConf.curPage = page
                const data = this.getDataByPage(page)
                this.curPageData = JSON.parse(JSON.stringify(data))
            },

            /**
             * 隐藏lb侧面板
             */
            hideCrdInstanceSlider () {
                this.crdInstanceSlider.isShow = false
            },

            /**
             * 加载数据
             */
            async getCrdInstanceList () {
                try {
                    const projectId = this.projectId

                    const params = {
                        cluster_id: this.clusterId,
                        crd_kind: this.crdKind
                    }

                    if (this.searchParams.namespace) {
                        params.namespace = this.searchParams.namespace
                    }

                    if (this.searchParams.workload_type) {
                        params.workload_type = this.searchParams.workload_type
                    }

                    if (this.searchParams.workload_name) {
                        params.workload_name = this.searchParams.workload_name
                    }

                    this.isPageLoading = true
                    await this.$store.dispatch('getBcsCrdsList', {
                        projectId,
                        params
                    })

                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isPageLoading = false
                        this.isInitLoading = false
                    }, 500)
                }
            },

            /**
             * 获取命名空间列表
             */
            async getNameSpaceList () {
                try {
                    const projectId = this.projectId
                    const clusterId = this.clusterId
                    const res = await this.$store.dispatch('crdcontroller/getNameSpaceListByCluster', { projectId, clusterId })
                    const list = res.data
                    list.forEach(item => {
                        item.isSelected = false
                    })
                    this.nameSpaceList.splice(0, this.nameSpaceList.length, ...list)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取日志信息
             */
            async getLogInfo () {
                try {
                    const projectId = this.projectId
                    const res = await this.$store.dispatch('getLogPlans', projectId)
                    this.defaultStdDataId = res.data.std_data_id
                    this.defaultFileDataId = res.data.file_data_id
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 选择/取消选择命名空间
             * @param  {object} nameSpace 命名空间
             * @param  {number} index 索引
             */
            toggleSelected (nameSpace, index) {
                nameSpace.isSelected = !nameSpace.isSelected
                this.nameSpaceList = JSON.parse(JSON.stringify(this.nameSpaceList))
            },

            /**
             * 检查提交的数据
             * @return {boolean} true/false 是否合法
             */
            checkData (params) {
                if (!params.namespace) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择命名空间'),
                        delay: 5000
                    })
                    return false
                }

                if (params.config_type === 'custom') {
                    if (!params.workload.type) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('请选择应用类型')
                        })
                        return false
                    }

                    if (!params.workload.name) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('请输入应用名称')
                        })
                        return false
                    }

                    try {
                        const reg = new RegExp(params.workload.name)
                        console.log(reg)
                    } catch (e) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('应用名称不合法')
                        })
                        return false
                    }

                    for (const conf of params.workload.container_confs) {
                        if (!conf.name) {
                            this.$bkMessage({
                                theme: 'error',
                                message: this.$t('请输入容器名')
                            })
                            return false
                        }

                        if (!conf.std_data_id) {
                            this.$bkMessage({
                                theme: 'error',
                                message: this.$t('请输入标准采集ID')
                            })
                            return false
                        }

                        // if (!conf.log_paths.length) {
                        //     this.$bkMessage({
                        //         theme: 'error',
                        //         message: this.$t('请输入文件路径')
                        //     })
                        //     return false
                        // }

                        if (!conf.file_data_id) {
                            this.$bkMessage({
                                theme: 'error',
                                message: this.$t('请输入文件采集ID')
                            })
                            return false
                        }
                    }
                } else {
                    if (!params.std_data_id) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('请输入标准采集ID')
                        })
                        return false
                    }
                }

                return true
            },

            showCrdInstanceDetail (data) {
                data.labels = []
                for (const key in data.pod_selector) {
                    data.labels.push({
                        key: key,
                        value: data.pod_selector[key]
                    })
                }
                this.curCrdInstance = data

                this.detailSliderConf.title = `${data.name}`
                this.detailSliderConf.isShow = true
            },

            /**
             * 格式化数据，符合接口需要的格式
             */
            formatData () {
                const params = JSON.parse(JSON.stringify(this.curCrdInstance))

                // 附加日志标签
                const labels = params.labels
                params.labels = {}
                if (params.labels) {
                    for (const key in labels) {
                        if (key) {
                            params.labels[key] = labels[key]
                        }
                    }
                }
                // 指定容器
                if (params.config_type === 'custom') {
                    params.workload.container_confs.forEach(conf => {
                        const paths = conf.log_paths_str.split(/[;|\n]/).filter(item => {
                            return !!item.trim()
                        }).map(item => {
                            return item.trim()
                        })

                        if (paths.length) {
                            conf.log_paths = paths
                        } else {
                            delete conf.log_paths
                        }
                        
                        // 接口接受'true'、'false'字符类型
                        conf.stdout = String(conf.stdout)
                    })
                    delete params.std_data_id
                    delete params.is_std_custom
                    delete params.stdout
                } else {
                    delete params.workload
                }
                params.add_pod_labels = String(params.add_pod_labels_b)
                delete params.add_pod_labels_b

                return params
            },

            /**
             * 保存新建的
             */
            async createCrdInstance (params) {
                const projectId = this.projectId
                const data = params
                this.isDataSaveing = true

                try {
                    await this.$store.dispatch('crdcontroller/addCrdInstance', { projectId, data })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('规则创建成功')
                    })
                    this.getCrdInstanceList()
                    this.hideCrdInstanceSlider()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }
            },

            /**
             * 保存更新的
             */
            async updateCrdInstance (params) {
                const projectId = this.projectId
                const data = params
                this.isDataSaveing = true

                data.crd_kind = this.crdKind
                try {
                    await this.$store.dispatch('crdcontroller/updateCrdInstance', { projectId, data })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('规则更新成功')
                    })
                    
                    this.hideCrdInstanceSlider()
                    // sideslider和loading层有样式冲突
                    setTimeout(() => {
                        this.getCrdInstanceList()
                    }, 500)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }
            },

            /**
             * 保存
             */
            saveCrdInstance () {
                const params = this.formatData()
                if (this.checkData(params) && !this.isDataSaveing) {
                    if (this.curCrdInstance.id > 0) {
                        this.updateCrdInstance(params)
                    } else {
                        this.createCrdInstance(params)
                    }
                }
            },

            handleNamespaceSelect (index, data) {
                this.curCrdInstance.namespace = data.name
            },

            changeLabels (labels, data) {
                // this.curCrdInstance.pod_selector = data
                this.curCrdInstance.labels = labels
            },

            addContainerConf () {
                this.curCrdInstance.workload.container_confs.push({
                    'name': '',
                    'std_data_id': this.defaultStdDataId,
                    'file_data_id': this.defaultFileDataId,
                    'stdout': 'true',
                    'log_paths': [],
                    'log_paths_str': '',
                    'is_file_custom': false,
                    'is_std_custom': false

                })
            },

            removeContainerConf (data, index) {
                this.curCrdInstance.workload.container_confs.splice(index, 1)
            },

            toggleExpand (crdInstance) {
                crdInstance.crd_data.workload.isExpand = !crdInstance.crd_data.workload.isExpand
            }
        }
    }
</script>

<style scoped>
    @import './log_list.css';
</style>
