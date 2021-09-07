<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-loadbalance-title">
                LoadBalancer
                <span class="biz-tip ml10">{{$t('LB镜像升级，不影响已运行实例；如出现无法编辑或者启用的情况，请联系容器助手处理')}}</span>
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
                        <bk-button theme="primary" @click.stop.prevent="createLoadBlance">
                            <i class="bcs-icon bcs-icon-plus"></i>
                            <span>{{$t('新建LoadBalancer')}}</span>
                        </bk-button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="$t('输入关键字，按Enter搜索')"
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            :cluster-fixed="!!curClusterId"
                            @search="getLoadBalanceList"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>

                <div class="biz-loadbalance">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <bk-table
                            :size="'medium'"
                            :data="curPageData"
                            :pagination="pageConf"
                            v-bkloading="{ isLoading: isPageLoading && !isInitLoading }"
                            @page-limit-change="handlePageLimitChange"
                            @page-change="handlePageChange"
                            @select="handlePageSelect"
                            @select-all="handlePageSelectAll">
                            <bk-table-column :label="$t('名称')" :show-overflow-tooltip="true" min-width="200">
                                <template slot-scope="props">
                                    <a href="javascript:void(0)" class="bk-text-button" @click="goLoadBalanceDetail(props.row)">{{props.row.name || '--'}}</a>
                                    <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="loadBalanceFixStatus.includes(props.row.status)">
                                        <div class="rotate rotate1"></div>
                                        <div class="rotate rotate2"></div>
                                        <div class="rotate rotate3"></div>
                                        <div class="rotate rotate4"></div>
                                        <div class="rotate rotate5"></div>
                                        <div class="rotate rotate6"></div>
                                        <div class="rotate rotate7"></div>
                                        <div class="rotate rotate8"></div>
                                    </div>
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('所属集群')" min-width="150">
                                <template slot-scope="props">
                                    <bcs-popover :content="props.row.cluster_id" placement="top">
                                        <div class="cluster-name biz-text-wrapper">{{props.row.cluster_id}}</div>
                                    </bcs-popover>
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('网络类型')" min-width="130">
                                <template slot-scope="props">
                                    {{props.row.network_type || '--'}}
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('转发模式')" min-width="130">
                                <template slot-scope="props">
                                    {{props.row.forward_mode || '--'}}
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('状态')" min-width="160" :show-overflow-tooltip="false">
                                <template slot-scope="props">
                                    <span class="vm mr10">{{statusMap[props.row.status] || $t('未部署')}}</span>
                                    <div class="vm f12" style="display: inline-block;">
                                        <p v-bk-tooltips="props.row.deployment_message || props.row.deployment_status" v-if="props.row.deployment_status">
                                            Deployment: <span :class="`lb-text ${props.row.deployment_status.toLowerCase()}`">{{props.row.deployment_status}}</span>
                                        </p>
                                        <p v-bk-tooltips="props.row.application_message || props.row.application_status" v-if="props.row.application_status">
                                            Application: <span :class="`lb-text ${props.row.application_status.toLowerCase()}`">{{props.row.application_status}}</span>
                                        </p>
                                    </div>
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('操作')" width="200">
                                <template slot-scope="props">
                                    <template v-if="!props.row.status || props.row.status === 'not_deployed' || props.row.status === 'stopped'">
                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="runLoadBalance(props.row, index)">{{$t('启动')}}</a>
                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="editLoadBalance(props.row, index)">{{$t('编辑')}}</a>
                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="removeLoadBalance(props.row, index)">{{$t('删除')}}</a>
                                    </template>
                                    <template v-else-if="props.row.status === 'deployed'">
                                        <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="stopLoadBalance(props.row, index)">{{$t('停止')}}</a>
                                    </template>
                                </template>
                            </bk-table-column>
                        </bk-table>
                        <table class="bk-table has-table-hover biz-table biz-loadbalance-table" v-if="false">
                            <thead>
                                <tr>
                                    <th style="width: 160px;">{{$t('名称')}}</th>
                                    <th style="min-width: 100px;">{{$t('所属集群')}}</th>
                                    <th style="min-width: 100px;">{{$t('网络类型')}}</th>
                                    <th style="min-width: 100px;">{{$t('转发模式')}}</th>
                                    <th style="min-width: 100px;">{{$t('状态')}}</th>
                                    <th style="min-width: 220px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>

                                <template v-if="loadBalanceList.length">
                                    <tr v-for="(loadBalance, index) in curPageData" :key="index">
                                        <td>
                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="loadBalanceFixStatus.includes(loadBalance.status)" style="margin-left: -20px;">
                                                <div class="rotate rotate1"></div>
                                                <div class="rotate rotate2"></div>
                                                <div class="rotate rotate3"></div>
                                                <div class="rotate rotate4"></div>
                                                <div class="rotate rotate5"></div>
                                                <div class="rotate rotate6"></div>
                                                <div class="rotate rotate7"></div>
                                                <div class="rotate rotate8"></div>
                                            </div>
                                            <a href="javascript:void(0)" class="bk-text-button" @click="goLoadBalanceDetail(loadBalance)">{{loadBalance.name || '--'}}</a>
                                        </td>
                                        <td>
                                            <bcs-popover :content="loadBalance.cluster_id" placement="top">
                                                <div class="cluster-name biz-text-wrapper">{{loadBalance.cluster_id}}</div>
                                            </bcs-popover>
                                        </td>
                                        <td>{{loadBalance.network_type || '--'}}</td>
                                        <td>{{loadBalance.forward_mode || '--'}}</td>
                                        <td>
                                            <span class="vm mr10">{{statusMap[loadBalance.status] || $t('未部署')}}</span>
                                            <div class="vm f12" style="display: inline-block;">
                                                <p v-bk-tooltips.left="loadBalance.deployment_message || loadBalance.deployment_status" v-if="loadBalance.deployment_status">
                                                    Deployment: <span :class="`lb-text ${loadBalance.deployment_status.toLowerCase()}`">{{loadBalance.deployment_status}}</span>
                                                </p>
                                                <p v-bk-tooltips.left="loadBalance.application_message || loadBalance.application_status" v-if="loadBalance.application_status">
                                                    Application: <span :class="`lb-text ${loadBalance.application_status.toLowerCase()}`">{{loadBalance.application_status}}</span>
                                                </p>
                                            </div>
                                        </td>
                                        <td>
                                            <template v-if="!loadBalance.status || loadBalance.status === 'not_deployed' || loadBalance.status === 'stopped'">
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="runLoadBalance(loadBalance, index)">{{$t('启动')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="editLoadBalance(loadBalance, index)">{{$t('编辑')}}</a>
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="removeLoadBalance(loadBalance, index)">{{$t('删除')}}</a>
                                            </template>
                                            <template v-else-if="loadBalance.status === 'deployed'">
                                                <a href="javascript:void(0);" class="bk-text-button" @click.stop.prevent="stopLoadBalance(loadBalance, index)">{{$t('停止')}}</a>
                                            </template>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="7">
                                            <div class="biz-app-list">
                                                <div class="bk-message-box">
                                                    <bcs-exception type="empty" scene="part" v-if="!isInitLoading"></bcs-exception>
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                </div>
            </template>

            <bk-sideslider
                :quick-close="false"
                :is-show.sync="loadBalanceSlider.isShow"
                :title="loadBalanceSlider.title"
                :width="'630'"
                @shown="handlerShowSideslider"
                @hidden="handlerHideSideslider">
                <div class="pt30 pr0 pb30 pl30" slot="content">
                    <div class="bk-form bk-form-vertical" @click="handlerHideSideslider">
                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px;">
                                    <label class="bk-label">{{$t('名称')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-input
                                            :placeholder="$t('请输入30个以内的字符')"
                                            v-model="curLoadBalance.name"
                                            maxlength="30"
                                            :disabled="curLoadBalance.id" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px;">
                                    <label class="bk-label">{{$t('所属集群')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :field-type="'cluster'"
                                            :placeholder="$t('请输入')"
                                            :setting-key="'cluster_id'"
                                            :display-key="'longName'"
                                            :is-link="true"
                                            :selected.sync="curLoadBalance.cluster_id"
                                            :list="clusterList"
                                            :disabled="curLoadBalance.id"
                                            :init-prevent-trigger="true"
                                            @item-selected="handlerSelectCluster">
                                        </bk-selector>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item is-required" style="width: 260px; margin-left: 35px;">
                                    <label class="bk-label">{{$t('命名空间')}}：</label>
                                    <div class="bk-form-content">
                                        <bk-selector
                                            :placeholder="$t('请输入')"
                                            :setting-key="'name'"
                                            :display-key="'name'"
                                            :selected.sync="curLoadBalance.namespace"
                                            :list="nameSpaceList"
                                            :disabled="curLoadBalance.id">
                                        </bk-selector>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item is-required" style="width: 260px;">
                                    <label class="bk-label">{{$t('实例数量')}}：</label>
                                    <div class="bk-form-content">
                                        <bkbcs-input
                                            type="number"
                                            :placeholder="$t('请输入')"
                                            style="width: 260px;"
                                            :value.sync="curLoadBalance.instance_num">
                                        </bkbcs-input>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <label class="bk-label">{{$t('调度约束')}}：</label>
                                <div class="bk-form-content">
                                    <div class="biz-keys-list mb10">
                                        <div class="biz-key-item" v-for="(constraint, index) in curLoadBalance.constraint.IntersectionItem" :key="index">
                                            <div class="bk-dropdown-box">
                                                <bk-combobox
                                                    type="text"
                                                    :placeholder="$t('请输入')"
                                                    style="width: 130px;"
                                                    :value.sync="constraint.unionData[0].name"
                                                    :display-key="'name'"
                                                    :search-key="'name'"
                                                    :setting-key="'id'"
                                                    :list="constraintNameList">
                                                </bk-combobox>
                                            </div>
                                            <div class="bk-dropdown-box">
                                                <template v-if="constraint.unionData[0].name !== 'ip-resources'">
                                                    <bk-selector
                                                        :placeholder="$t('请输入')"
                                                        :setting-key="'id'"
                                                        :selected.sync="constraint.unionData[0].operate"
                                                        :list="operatorList"
                                                        @item-selected="handlerSelectOperate(constraint.unionData[0])">
                                                    </bk-selector>
                                                </template>
                                                <template v-else>
                                                    <bk-selector
                                                        :placeholder="$t('请输入')"
                                                        :setting-key="'id'"
                                                        :disabled="true"
                                                        :selected.sync="constraint.unionData[0].operate"
                                                        :list="operatorListForIP">
                                                    </bk-selector>
                                                </template>
                                            </div>

                                            <template v-if="constraint.unionData[0].name !== 'ip-resources'">
                                                <bkbcs-input
                                                    type="text"
                                                    :placeholder="$t('多个值以管道符分隔')"
                                                    style="width: 250px;"
                                                    :disabled="constraint.unionData[0].operate === 'UNIQUE'"
                                                    :value.sync="constraint.unionData[0].arg_value"
                                                    :list="varList">
                                                </bkbcs-input>
                                            </template>
                                            <template v-else>
                                                <bkbcs-input
                                                    type="number"
                                                    :placeholder="$t('请输入')"
                                                    style="width: 190px;"
                                                    :value.sync="constraint.unionData[0].arg_value"
                                                    :list="varList">
                                                </bkbcs-input>
                                            </template>
                                            <bk-button class="action-btn" @click.stop.prevent="addConstraint()">
                                                <i class="bcs-icon bcs-icon-plus"></i>
                                            </bk-button>
                                            <bk-button class="action-btn" @click.stop.prevent="removeConstraint(constraint, index)" v-show="curLoadBalance.constraint.IntersectionItem.length > 1">
                                                <i class="bcs-icon bcs-icon-minus"></i>
                                            </bk-button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <label class="bk-label mt10">{{$t('镜像及版本')}}：</label>
                        <div class="biz-expand-panel mt20 mb10" style="width: 560px; clear: both;">
                            <div class="panel" style="cursor: default;">
                                <div class="header">
                                    <span class="f12">{{$t('使用自定义镜像')}}：</span>
                                    <span @click="handleChangeImageMode">
                                        <bk-switcher
                                            :selected.sync="curLoadBalance.use_custom_image_url"
                                            size="small">
                                        </bk-switcher>
                                    </span>
                                    <span class="biz-tip ml5" style="font-weight: normal;">({{$t('启用后允许直接填写镜像信息')}})</span>
                                </div>
                                <div class="bk-form-item content">
                                    <div class="bk-form-item">
                                        <div class="bk-form-content">
                                            <div class="bk-form-inline-item is-required" style="width: 239px;">
                                                <label class="bk-label">{{$t('镜像地址')}}：</label>
                                                <div class="bk-form-content">
                                                    <bk-input :readonly="!curLoadBalance.use_custom_image_url" v-model="curLoadBalance.image_url" />
                                                </div>
                                            </div>
                                            <div class="bk-form-inline-item is-required" style="width: 235px; margin-left: 35px;">
                                                <label class="bk-label">{{$t('镜像版本')}}：</label>
                                                <div class="bk-form-content">
                                                    <template v-if="curLoadBalance.use_custom_image_url">
                                                        <bkbcs-input
                                                            type="text"
                                                            :placeholder="$t('版本号1')"
                                                            :value.sync="curLoadBalance.image_tag">
                                                        </bkbcs-input>
                                                    </template>
                                                    <template v-else>
                                                        <bkbcs-input
                                                            ref="imageVersion"
                                                            type="text"
                                                            :placeholder="$t('版本号1')"
                                                            :display-key="'_name'"
                                                            :setting-key="'_id'"
                                                            :search-key="'_name'"
                                                            :value.sync="curLoadBalance.image_tag"
                                                            :list="varList"
                                                            :is-select-mode="true"
                                                            :is-custom="true"
                                                            :default-list="imageVersionList">
                                                        </bkbcs-input>
                                                    </template>
                                                </div>
                                            </div>
                                        </div>

                                        <bk-checkbox class="mt5" name="image-get" v-model="curLoadBalance.use_custom_imagesecret">
                                            {{$t('添加镜像凭证')}}
                                        </bk-checkbox>

                                        <template v-if="curLoadBalance.use_custom_imagesecret">
                                            <div class="bk-form-item">
                                                <label class="bk-label" style="width: 150px;">ImagePullUser：</label>
                                                <div class="bk-form-content" style="margin-left: 150px;">
                                                    <bkbcs-input
                                                        type="text"
                                                        :placeholder="$t('请输入，格式是明文或secret语法(如secret::secret英文名称||user)')"
                                                        style="width: 515px;"
                                                        :value.sync="curLoadBalance.image_pull_user"
                                                        :list="varList">
                                                    </bkbcs-input>
                                                </div>
                                            </div>
                                            <div class="bk-form-item">
                                                <label class="bk-label" style="width: 150px;">ImagePullPasswd：</label>
                                                <div class="bk-form-content" style="margin-left: 150px;">
                                                    <bkbcs-input
                                                        type="text"
                                                        :placeholder="$t('请输入，格式是明文或secret语法(如secret::secret英文名称||pwd)')"
                                                        style="width: 515px;"
                                                        :value.sync="curLoadBalance.image_pull_password"
                                                        :list="varList">
                                                    </bkbcs-input>
                                                </div>
                                            </div>
                                        </template>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <label class="bk-label">{{$t('IP集')}}：</label>
                                <div class="bk-form-content">
                                    <textarea class="bk-form-textarea" :placeholder="$t('请输入IP，多个IP以空格或换行分隔')" v-model="curLoadBalance.ips" style="width: 558px;"></textarea>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <label class="bk-label">{{$t('挂载卷')}}：</label>
                                <div class="bk-form-content">
                                    <table class="biz-simple-table">
                                        <tbody>
                                            <tr v-for="(volumeItem, index) in curLoadBalance.volumes" :key="index">
                                                <td style="width: 170px;">
                                                    <bk-selector
                                                        :placeholder="$t('挂载名')"
                                                        :setting-key="'name'"
                                                        :selected.sync="volumeItem.name"
                                                        :list="configmapList">
                                                    </bk-selector>
                                                </td>
                                                <td style="width: 130px;">
                                                    <bkbcs-input
                                                        type="text"
                                                        :placeholder="$t('挂载源')"
                                                        maxlength="512"
                                                        :value.sync="volumeItem.volume.hostPath"
                                                        :list="varList">
                                                    </bkbcs-input>
                                                </td>
                                                <td style="width: 90px;">
                                                    <bkbcs-input
                                                        type="text"
                                                        :placeholder="$t('挂载目录')"
                                                        maxlength="512"
                                                        :value.sync="volumeItem.volume.mountPath"
                                                        :list="varList">
                                                    </bkbcs-input>
                                                </td>
                                                <td style="width: 70px;">
                                                    <bkbcs-input
                                                        type="text"
                                                        :placeholder="$t('用户')"
                                                        :value.sync="volumeItem.volume.user"
                                                        :list="varList">
                                                    </bkbcs-input>
                                                </td>
                                                <td style="width: 60px;">
                                                    <div class="biz-input-wrapper">
                                                        <bk-checkbox v-model="volumeItem.volume.readOnly">{{$t('只读')}}</bk-checkbox>
                                                    </div>
                                                </td>
                                                <div class="action-box">
                                                    <bk-button class="action-btn p0 mr5" @click.stop.prevent="addVolumn()">
                                                        <i class="bcs-icon bcs-icon-plus"></i>
                                                    </bk-button>
                                                    <bk-button class="action-btn p0" @click.stop.prevent="removeVolumn(volumeItem, index)" v-show="curLoadBalance.volumes.length > 1">
                                                        <i class="bcs-icon bcs-icon-minus"></i>
                                                    </bk-button>
                                                </div>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <label class="bk-label">{{$t('关联的Service的Label')}}：</label>
                                <div class="bk-form-content">
                                    <div class="biz-keys-list mb10">
                                        <div class="biz-key-item">
                                            <div class="bk-input-box bk-selector" style="width: 257px;">
                                                <bk-input :placeholder="$t('键')" :native-attributes="{ autocomplete: 'off' }" value="BCSGROUP" :disabled="true" style="width: 257px;" />
                                            </div>
                                            <span class="operator">=</span>
                                            <div class="bk-input-box bk-selector" style="width: 257px;">
                                                <bk-input :placeholder="$t('值')" :native-attributes="{ autocomplete: 'off' }" :readonly="true" style="width: 257px;" v-model="curLoadBalance.related_service_label" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <label class="bk-label mb10">{{$t('资源限制')}}：</label>
                        <div class="bk-form-item">
                            <div class="bk-form-content">
                                <div class="bk-form-inline-item" style="width: 270px;">
                                    <div class="bk-form-content">
                                        <label class="bk-label">CPU：</label>

                                        <div class="bk-form-input-group mr5">
                                            <span class="input-group-addon is-left">
                                                limits
                                            </span>
                                            <bkbcs-input
                                                type="number"
                                                :placeholder="$t('请输入')"
                                                style="width: 110px;"
                                                :value.sync="curLoadBalance.resources.limits.cpu">
                                            </bkbcs-input>
                                            <span class="input-group-addon">
                                                {{$t('核')}}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div class="bk-form-inline-item" style="width: 270px; margin-left: 20px;">
                                    <div class="bk-form-content">
                                        <label class="bk-label">{{$t('内存')}}：</label>
                                        <div class="bk-form-input-group mr5">
                                            <span class="input-group-addon is-left">
                                                limits
                                            </span>
                                            <bkbcs-input
                                                type="number"
                                                :placeholder="$t('请输入')"
                                                style="width: 110px;"
                                                :value.sync="curLoadBalance.resources.limits.memory">
                                            </bkbcs-input>
                                            <span class="input-group-addon">
                                                M
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="biz-span mr30">
                            <div class="title">
                                <button :class="['bk-text-button', { 'rotate': isShowMore }]" @click.stop.prevent="toggleMore">
                                    {{$t('更多设置')}}<i class="bcs-icon bcs-icon-angle-double-down f12 ml5 mb10 fb"></i>
                                </button>
                            </div>
                        </div>

                        <template v-if="isShowMore">
                            <label class="bk-label mt10">{{$t('网络设置')}}：</label>
                            <div class="biz-expand-panel mt20 mb10" style="width: 560px; clear: both;">
                                <div class="panel" style="cursor: default;">
                                    <div class="bk-form-item content">
                                        <div class="bk-form-item">
                                            <div class="bk-form-content">
                                                <div class="bk-form-inline-item is-required" style="width: 235px; ">
                                                    <label class="bk-label">{{$t('网络模式')}}：</label>
                                                    <div class="bk-form-content" style="width: 500px;">
                                                        <div class="bk-dropdown-box" style="width: 235px;">
                                                            <bk-selector
                                                                :placeholder="$t('请输入')"
                                                                :setting-key="'id'"
                                                                :display-key="'name'"
                                                                :selected.sync="curLoadBalance.network_mode"
                                                                :list="netList"
                                                                @item-selected="handlerSelectNetwork">
                                                            </bk-selector>
                                                        </div>
                                                        <transition name="fade">
                                                            <bk-input style="width: 220px;" :placeholder="$t('自定义值')" v-model="curLoadBalance.custom_value" v-if="curLoadBalance.network_mode === 'CUSTOM'" />
                                                        </transition>
                                                    </div>
                                                </div>
                                                <div class="bk-form-inline-item is-required" style="width: 235px; margin-left: 35px;" v-if="curLoadBalance.network_mode === 'BRIDGE'">
                                                    <label class="bk-label">{{$t('端口')}}：</label>
                                                    <div class="bk-form-content">
                                                        <bkbcs-input
                                                            type="number"
                                                            :placeholder="$t('请输入')"
                                                            style="width: 235px;"
                                                            :min="31000"
                                                            :max="32000"
                                                            :value.sync="curLoadBalance.host_port">
                                                        </bkbcs-input>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="bk-form-item">
                                            <div class="bk-form-content">
                                                <div class="bk-form-inline-item is-required" style="width: 235px; margin-right: 35px;">
                                                    <label class="bk-label">{{$t('转发模式')}}：</label>
                                                    <div class="bk-form-content">
                                                        <bk-radio-group v-model="curLoadBalance.forward_mode">
                                                            <bk-radio value="haproxy">haproxy</bk-radio>
                                                            <bk-radio value="nginx">nginx</bk-radio>
                                                        </bk-radio-group>
                                                    </div>
                                                </div>

                                                <div class="bk-form-inline-item is-required" style="width: 235px;">
                                                    <label class="bk-label">{{$t('网络类型')}}：</label>
                                                    <div class="bk-form-content">
                                                        <bk-radio-group v-model="curLoadBalance.network_type">
                                                            <bk-radio value="cni">cni</bk-radio>
                                                            <bk-radio value="cnm" :disabled="curLoadBalance.network_mode === 'USER'">cnm</bk-radio>
                                                        </bk-radio-group>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>

                        <div class="bk-form-item mt25">
                            <bk-button type="primary" :loading="isDataSaveing" @click.stop.prevent="saveLoadBalance">{{$t('保存')}}</bk-button>
                            <bk-button :disabled="isDataSaveing" @click.stop.prevent="hideLoadBalanceSlider">{{$t('取消')}}</bk-button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import bkCombobox from '@open/components/bk-combobox'
    import { catchErrorHandler } from '@open/common/util'

    export default {
        components: {
            bkCombobox
        },
        data () {
            return {
                isInitLoading: true,
                isPageLoading: false,
                exceptionCode: null,
                isNamespacePanelShow: false,
                isShowMore: false,
                curPageData: [],
                isAllDataLoad: false,
                isDataSaveing: false,
                prmissions: {},
                pageConf: {
                    count: 0,
                    totalPage: 1,
                    limit: 5,
                    current: 1,
                    show: true
                },
                mountTypeList: [
                    {
                        id: 'custom',
                        name: this.$t('自定义')
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
                loadBalanceSlider: {
                    title: this.$t('新建LoadBalancer'),
                    isShow: false
                },
                clusterIndex: 0,
                secretList: [],
                configmapList: [],
                constraintNameIndex: 'hostname',
                loadBalanceFixStatus: [
                    'deploying',
                    'stopping'
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
                statusTimer: {},
                imageVersionList: [],
                searchKeyword: '',
                searchScope: '',
                operatorIndex: -1,
                statusMap: {
                    'not_deployed': this.$t('未部署'),
                    'deploying': this.$t('部署中'),
                    'deployed': this.$t('已部署'),
                    'stopping': this.$t('停止中'),
                    'stopped': this.$t('已停止')
                },
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
                nameSpaceSelectedList: [],
                loadBalanceListCache: [],
                nameSpaceList: [],
                nameSpaceClusterList: [],
                globalImageId: 'paas/public/mesos/bcs-loadbalance',
                curLoadBalance: {
                    'name': '',
                    'cluster_id': '',
                    'namespace': '',
                    'ips': '',
                    'ip_list': [],
                    'instance_num': '',
                    'related_service_label': '',
                    'network_mode': 'BRIDGE',
                    'custom_value': '',
                    'network_type': 'cnm',
                    'volumes': [],
                    'configmaps': [],
                    'resources': {
                        'limits': {
                            'cpu': '1',
                            'memory': '1024'
                        }
                    },
                    'forward_mode': 'haproxy',
                    'use_custom_image_url': false,
                    'image_url': '/' + this.globalImageId,
                    'image_tag': '',
                    'use_custom_imagesecret': false,
                    'image_pull_user': '',
                    'image_pull_password': '',
                    'host_port': 31000,
                    'constraint': {
                        'IntersectionItem': [
                            {
                                'unionData': [
                                    {
                                        'name': 'hostname',
                                        'operate': 'CLUSTER',
                                        'type': 4,
                                        'arg_value': '',
                                        'text': {
                                            value: ''
                                        },
                                        'set': {
                                            item: []
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    'type': 'append'
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
                        id: 'FLANNEL',
                        name: 'FLANNEL'
                    },
                    {
                        id: 'MACVLAN',
                        name: 'MACVLAN'
                    },
                    {
                        id: 'CUSTOM',
                        name: this.$t('自定义')
                    }
                ]
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
            loadBalanceList () {
                const list = Object.assign([], this.$store.state.network.loadBalanceList)
                const keyword = this.searchKeyword.trim()
                const filterList = list.filter(item => {
                    if (item.name.indexOf(keyword) > -1 || item.cluster_id.indexOf(keyword) > -1 || item.ip_list.join(',').indexOf(keyword) > -1 || item.namespace.indexOf(keyword) > -1) {
                        return true
                    } else {
                        return false
                    }
                })
                const results = filterList.map(item => {
                    return {
                        ...item,
                        ...item.data
                    }
                })
                return results
            },
            clusterList () {
                const clusterList = this.$store.state.cluster.clusterList
                clusterList.forEach(cluster => {
                    cluster.longName = `${cluster.name}(${cluster.cluster_id})`
                })
                return clusterList
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
            curProject () {
                return this.$store.state.curProject
            },
            isClusterDataReady () {
                return this.$store.state.cluster.isClusterDataReady
            },
            curClusterId () {
                return this.$store.state.curClusterId
            }
        },
        watch: {
            'curLoadBalance.network_mode' (val) {
                if (val === 'USER') {
                    this.curLoadBalance.network_type = 'cni'
                } else if (val !== 'CUSTOM') {
                    this.curLoadBalance.network_type = 'cnm'
                }
            },
            'curLoadBalance.name' (val) {
                // 新建lb的时候，name和BCSGROUP联动
                if (this.curLoadBalance.id === undefined) {
                    this.curLoadBalance.related_service_label = val
                }
            },
            loadBalanceList () {
                this.curPageData = this.getDataByPage(this.pageConf.current)
            },
            curPageData () {
                this.curPageData.forEach(item => {
                    if (this.loadBalanceFixStatus.includes(item.status)) {
                        this.getLoadBalanceStatus(item)
                    }
                })
            },
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

                            this.getLoadBalanceList()
                            // this.getConfigmapList()
                        }, 1000)
                    }
                }
            },
            curClusterId () {
                this.searchScope = this.curClusterId
                this.getLoadBalanceList()
            }
        },

        created () {
            this.getImageTagList()
        },
        methods: {
            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.current = 1
                this.isPageLoading = true
                this.getLoadBalanceList()
            },

            /**
             * 获取镜像Tag列表
             */
            async getImageTagList (value, data, isInitTrigger) {
                const projectId = this.projectId
                const imageId = this.globalImageId
                const isPub = true

                try {
                    const res = await this.$store.dispatch('mesosTemplate/getImageVertionList', { projectId, imageId, isPub })
                    const data = res.data
                    data.forEach(item => {
                        item._id = item.text
                        item._name = item.text
                    })
                    this.imageVersionList.splice(0, this.imageVersionList.length, ...data)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 加载configmap列表数据
             */
            async getConfigmapList () {
                const projectId = this.projectId
                const params = {
                    cluster_id: this.curLoadBalance.cluster_id
                }
                try {
                    const res = await this.$store.dispatch('resource/getConfigmapList', {
                        projectId,
                        params
                    })
                    this.configmapList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 分页大小更改
             *
             * @param {number} pageSize pageSize
             */
            handlePageLimitChange (pageSize) {
                this.pageConf.limit = pageSize
                this.pageConf.current = 1
                this.initPageConf()
                this.handlePageChange()
            },

            /**
             * 切换页面时回调
             */
            leaveCallback () {
                for (const key of Object.keys(this.statusTimer)) {
                    clearInterval(this.statusTimer[key])
                }
                this.$store.commit('network/updateLoadBalanceList', [])
            },

            /**
             * 选择操作回调
             * @param  {object} data 操作
             */
            handlerSelectOperate (data) {
                const operate = data.operate
                if (operate === 'UNIQUE') {
                    data.type = 0
                    data.arg_value = ''
                }
            },

            /**
             * 查看LB详情
             * @param  {object} loadBalance loadBalance
             */
            async goLoadBalanceDetail (loadBalance) {
                const projectName = this.curProject.project_code
                const url = `${window.DEVOPS_HOST}/console/bcs/${projectName}/app/mesos/${loadBalance.name}/${loadBalance.namespace}/deployment?cluster_id=${loadBalance.cluster_id}`
                window.open(url)
            },

            /**
             * 删除调度约束
             * @param  {object} item 调度约束配置
             * @param  {number} index 索引
             */
            removeConstraint (item, index) {
                const constraint = this.curLoadBalance.constraint.IntersectionItem
                constraint.splice(index, 1)
            },

            /**
             * 添加调度约束
             */
            addConstraint () {
                const constraint = this.curLoadBalance.constraint.IntersectionItem
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

            /**
             * 新建LB
             */
            createLoadBlance () {
                this.nameSpaceSelectedList = []
                this.curLoadBalance = {
                    'name': '',
                    'cluster_id': '',
                    'namespace': '',
                    'ips': '',
                    'ip_list': [],
                    'instance_num': '',
                    'related_service_label': '',
                    'network_mode': 'BRIDGE',
                    'custom_value': '',
                    'network_type': 'cnm',
                    'volumes': [
                        {
                            'volume': {
                                'hostPath': '',
                                'mountPath': '',
                                'subPath': '',
                                'user': '',
                                'readOnly': false
                            },
                            'type': 'custom',
                            'name': ''
                        }
                    ],
                    'configmaps': [],
                    'resources': {
                        'limits': {
                            'cpu': '1',
                            'memory': '1024'
                        }
                    },
                    'forward_mode': 'haproxy',
                    'use_custom_image_url': false,
                    'image_url': '/' + this.globalImageId,
                    'image_tag': '',
                    'use_custom_imagesecret': false,
                    'image_pull_user': '',
                    'image_pull_password': '',
                    'host_port': 31000,
                    'constraint': {
                        'IntersectionItem': [
                            {
                                'unionData': [
                                    {
                                        'name': 'hostname',
                                        'operate': 'CLUSTER',
                                        'type': 4,
                                        'arg_value': '',
                                        'text': {
                                            value: ''
                                        },
                                        'set': {
                                            item: []
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    'type': 'append'
                }

                this.loadBalanceSlider.isShow = true
            },

            /**
             * 编辑LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async editLoadBalance (loadBalance, index) {
                const loadBalanceParams = Object.assign({}, loadBalance)
                this.nameSpaceSelectedList = []
                loadBalanceParams.ips = loadBalanceParams.ip_list.join('\n')
                loadBalanceParams.type = 'append'
                this.nameSpaceList.forEach(namespace => {
                    namespace.isSelected = false
                })

                loadBalanceParams.volumes = []
                if (!loadBalanceParams.configmaps) {
                    loadBalanceParams.configmaps = []
                }
                if (!loadBalanceParams.configmaps.length) {
                    loadBalanceParams.volumes.push({
                        'volume': {
                            'hostPath': '',
                            'mountPath': '',
                            'user': '',
                            'readOnly': false
                        },
                        'type': 'custom',
                        'name': ''
                    })
                } else {
                    loadBalanceParams.configmaps.forEach(configmap => {
                        configmap.items.forEach(item => {
                            loadBalanceParams.volumes.push({
                                'volume': {
                                    'hostPath': item.dataKey,
                                    'mountPath': item.keyOrPath,
                                    'user': item.user,
                                    'readOnly': item.readOnly
                                },
                                'type': 'custom',
                                'name': configmap.name
                            })
                        })
                    })
                }
                this.curLoadBalance = loadBalanceParams
                this.loadBalanceSlider.title = this.$t('编辑LoadBalancer')
                this.loadBalanceSlider.isShow = true
            },

            /**
             * 选择网络回调
             */
            handlerSelectNetwork () {
                this.curLoadBalance.custom_value = ''
            },

            /**
             * 启动LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async runLoadBalance (loadBalance, index) {
                // if (!loadBalance.permissions.use) {
                //     await this.$store.dispatch('getResourcePermissions', {
                //         project_id: this.projectId,
                //         policy_code: 'use',
                //         resource_code: loadBalance.namespace,
                //         resource_name: loadBalance.namespace_name,
                //         resource_type: 'namespace'
                //     })
                // }
                const self = this
                const projectId = this.projectId
                const loadBalanceId = loadBalance.name
                const clusterId = loadBalance.cluster_id
                const namespace = loadBalance.namespace

                this.$bkInfo({
                    title: this.$t('确认操作'),
                    content: `${this.$t('确定要启动此LoadBalancer')}: ${loadBalanceId}`,
                    async confirmFn () {
                        try {
                            await self.$store.dispatch('network/runMesosLoadBalance', {
                                projectId,
                                loadBalanceId,
                                clusterId,
                                namespace
                            })
                            self.$bkMessage({
                                theme: 'success',
                                message: self.$t('已经将配置文件下发到后台')
                            })
                            loadBalance.status = 'deploying'
                            loadBalance.deployment_status = ''
                            loadBalance.application_status = ''
                            self.getLoadBalanceStatus(loadBalance, index)
                        } catch (e) {
                            catchErrorHandler(e, self)
                            e.is_update && self.getLoadBalanceList()
                        }
                    }
                })
            },

            /**
             * 停止LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async stopLoadBalance (loadBalance, index) {
                // if (!loadBalance.permissions.use) {
                //     await this.$store.dispatch('getResourcePermissions', {
                //         project_id: this.projectId,
                //         policy_code: 'use',
                //         resource_code: loadBalance.namespace,
                //         resource_name: loadBalance.namespace_name,
                //         resource_type: 'namespace'
                //     })
                // }
                const self = this
                const projectId = this.projectId
                const loadBalanceId = loadBalance.name
                const clusterId = loadBalance.cluster_id
                const namespace = loadBalance.namespace

                this.$bkInfo({
                    title: this.$t('确认操作'),
                    content: `${this.$t('确定要停止此LoadBalancer')}: ${loadBalanceId}`,
                    async confirmFn () {
                        try {
                            await self.$store.dispatch('network/stopMesosLoadBalance', { projectId, loadBalanceId, clusterId, namespace })
                            loadBalance.status = 'stopping'
                            loadBalance.deployment_status = ''
                            loadBalance.application_status = ''
                            self.getLoadBalanceStatus(loadBalance, index)
                        } catch (e) {
                            catchErrorHandler(e, self)
                        }
                    }
                })
            },

            /**
             * 选择集群回调
             * @param  {number}  index 集群索引（ID）
             * @param  {object}  data 集群
             * @param  {boolean} isInitTrigger 是否在进入页面时触发
             */
            async handlerSelectCluster (index, data, isInitTrigger) {
                const projectId = this.projectId
                const clusterId = index
                if (!isInitTrigger) {
                    this.curLoadBalance.namespace = ''
                }
                this.nameSpaceList = []
                if (projectId && clusterId) {
                    try {
                        this.getConfigmapList()
                        const res = await this.$store.dispatch('network/getNameSpaceClusterList', { projectId, clusterId })
                        this.nameSpaceClusterList = res.data
                        this.nameSpaceList = res.data
                        this.nameSpaceList.forEach(item => {
                            item.isSelected = false
                        })
                        this.nameSpaceSelectedList = []
                    } catch (e) {
                        catchErrorHandler(e, this)
                    }
                } else {
                    this.nameSpaceClusterList = []
                }
            },

            /**
             * 删除LB
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            async removeLoadBalance (loadBalance, index) {
                // if (!loadBalance.permissions.use) {
                //     await this.$store.dispatch('getResourcePermissions', {
                //         project_id: this.projectId,
                //         policy_code: 'use',
                //         resource_code: loadBalance.namespace,
                //         resource_name: loadBalance.namespace_name,
                //         resource_type: 'namespace'
                //     })
                // }
                const self = this
                const projectId = this.projectId
                const loadBalanceId = loadBalance.name
                const clusterId = loadBalance.cluster_id
                const namespace = loadBalance.namespace
                this.$bkInfo({
                    title: this.$t('确认删除'),
                    clsName: 'biz-remove-dialog max-size',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除LoadBalancer')}【${loadBalance.cluster_id} / ${loadBalance.namespace} / ${loadBalanceId}】？`),
                    async confirmFn () {
                        self.isPageLoading = true
                        try {
                            await self.$store.dispatch('network/removeMesosLoadBalance', { projectId, loadBalanceId, namespace, clusterId })
                            self.$bkMessage({
                                theme: 'success',
                                message: self.$t('删除成功')
                            })
                            self.getLoadBalanceList()
                        } catch (e) {
                            catchErrorHandler(e, self)
                        } finally {
                            self.isPageLoading = false
                        }
                    }
                })
            },

            /**
             * 获取LB
             * @param  {number} loadBalanceId id
             * @return {object} loadBalance loadBalance
             */
            getLoadBalanceById (loadBalanceId) {
                return this.loadBalanceList.find(item => {
                    return item.id === loadBalanceId
                })
            },

            /**
             * 获取LB状态
             * @param  {object} loadBalance loadBalance
             * @param  {number} index 索引
             */
            getLoadBalanceStatus (loadBalance, index) {
                const projectId = this.projectId
                const loadBalanceId = loadBalance.name
                const clusterId = loadBalance.cluster_id
                const namespace = loadBalance.namespace
                const self = this

                clearInterval(this.statusTimer[loadBalance.id])

                this.statusTimer[loadBalance.id] = setInterval(async () => {
                    if (this.loadBalanceSlider.isShow) {
                        return
                    }
                    try {
                        const res = await this.$store.dispatch('network/getMesosLoadBalanceStatus', {
                            projectId,
                            clusterId,
                            namespace,
                            loadBalanceId
                        }, { getCloudLoadBalanceDetail: true })
                        const lb = res.data
                        if (!self.loadBalanceFixStatus.includes(lb.status)) {
                            clearInterval(self.statusTimer[loadBalance.id])
                        }
                    } catch (e) {
                        catchErrorHandler(e, this)
                    }
                }, 2000)
            },

            /**
             * 清空搜索
             */
            clearSearch () {
                this.searchKeyword = ''
                this.searchLoadBalance()
            },

            /**
             * 搜索LB
             */
            searchLoadBalance () {
                const keyword = this.searchKeyword.trim()
                let list = this.$store.state.network.loadBalanceList
                let results = []

                if (this.searchScope) {
                    list = list.filter(item => item.cluster_id === this.searchScope)
                }

                results = list.filter(item => {
                    if (item.name.indexOf(keyword) > -1 || item.cluster_id.indexOf(keyword) > -1 || item.ip_list.join(',').indexOf(keyword) > -1 || item.namespace.indexOf(keyword) > -1) {
                        return true
                    } else {
                        return false
                    }
                })
                this.loadBalanceList.splice(0, this.loadBalanceList.length, ...results)
                this.pageConf.current = 1
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.current)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.loadBalanceList.length
                this.pageConf.count = total
                this.pageConf.current = 1
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.limit)
            },

            /**
             * 重新加载当前页
             */
            reloadCurPage () {
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.current)
            },

            /**
             * 获取页数据
             * @param  {number} page 页
             * @return {object} data lb
             */
            getDataByPage (page) {
                // 如果没有page，重置
                if (!page) {
                    this.pageConf.current = page = 1
                }
                let startIndex = (page - 1) * this.pageConf.limit
                let endIndex = page * this.pageConf.limit
                // this.isPageLoading = true
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.loadBalanceList.length) {
                    endIndex = this.loadBalanceList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.loadBalanceList.slice(startIndex, endIndex)
            },

            /**
             * 分页改变回调
             * @param  {number} page 页
             */
            handlePageChange (page = 1) {
                this.isPageLoading = true
                this.pageConf.current = page
                const data = this.getDataByPage(page)
                this.curPageData = JSON.parse(JSON.stringify(data))
            },

            /**
             * 隐藏lb侧面板
             */
            hideLoadBalanceSlider () {
                this.loadBalanceSlider.isShow = false
            },

            /**
             * 显示命名空间选择面板
             */
            showNamespacePanel () {
                this.nameSpaceList.forEach(namespace => {
                    namespace.isSelected = false
                })
                this.nameSpaceSelectedList.forEach(item => {
                    this.nameSpaceList.forEach(namespace => {
                        if (namespace.id === item.id) {
                            namespace.isSelected = true
                        }
                    })
                })
                this.isNamespacePanelShow = true
            },

            /**
             * 确认选择命名空间
             */
            confirmSelected () {
                const ids = []
                const resutls = []
                this.nameSpaceList.forEach(item => {
                    if (item.isSelected) {
                        resutls.push(item)
                        ids.push(item.id)
                    }
                })
                this.nameSpaceSelectedList = resutls
                this.curLoadBalance.ns_id_list = ids
                this.isNamespacePanelShow = false
            },

            /**
             * 隐藏创建LB侧栏回调
             */
            handlerHideSideslider () {
                this.isNamespacePanelShow = false
                // 重启状态轮询
                this.curPageData.forEach(item => {
                    if (this.loadBalanceFixStatus.includes(item.status)) {
                        this.getLoadBalanceStatus(item)
                    }
                })
            },

            /**
             * 显示创建LB侧栏回调
             */
            handlerShowSideslider () {
                // 清除状态轮询
                for (const key in this.statusTimer) {
                    clearInterval(this.statusTimer[key])
                }
            },

            /**
             * 加载LB数据
             */
            async getLoadBalanceList () {
                try {
                    const project = this.curProject
                    const params = {
                        cluster_id: this.searchScope
                    }
                    this.isPageLoading = true
                    await this.$store.dispatch('network/getMesosLoadBalanceList', {
                        project,
                        params
                    })
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.current)
                    this.isAllDataLoad = true
                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchKeyword) {
                        this.searchLoadBalance()
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isPageLoading = false
                        this.isInitLoading = false
                    }, 200)
                }
            },

            /**
             * 获取命名空间列表
             */
            async getNameSpaceList () {
                try {
                    const res = await this.$store.dispatch('network/getNameSpaceList', this.projectId)
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
             * 获取集群列表
             */
            async getClusterList () {
                try {
                    await this.$store.dispatch('network/getClusterList', this.projectId)
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
                const appNameReg = /^[a-z]{1}[a-z0-9-]{0,29}$/
                // const ipReg = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)($|(?!\.$)\.)){4}$/
                if (params.name === '') {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入名称')
                    })
                    return false
                }
                if (!appNameReg.test(params.name)) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，必须是字母开头，长度小于30个字符'),
                        delay: 5000
                    })
                    return false
                }

                if (!params.cluster_id) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择所属集群'),
                        delay: 5000
                    })
                    return false
                }

                if (!params.namespace) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择命名空间'),
                        delay: 5000
                    })
                    return false
                }

                if (!params.image_tag) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择镜像版本'),
                        delay: 5000
                    })
                    return false
                }

                // 镜像凭证
                if (params.use_custom_imagesecret) {
                    if (!params.image_pull_user) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('请填写镜像凭证ImagePullUser'),
                            delay: 5000
                        })
                        return false
                    }
                    if (!params.image_pull_password) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('请填写镜像凭证ImagePullPasswd'),
                            delay: 5000
                        })
                        return false
                    }
                }

                if (params.ip_list.length) {
                    // for (const ip of params.ip_list) {
                    //     if (!ipReg.test(ip)) {
                    //         this.$bkMessage({
                    //             theme: 'error',
                    //             message: this.$t('请输入正确IP地址'),
                    //             delay: 3000
                    //         })
                    //         return false
                    //     }
                    // }
                    if (params.ip_list.length !== Number(params.instance_num)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('IP数量和实例数量不相等'),
                            delay: 3000
                        })
                        return false
                    }
                }

                if (!params.instance_num) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请填写实例数量'),
                        delay: 5000
                    })
                    return false
                }

                if (!params.related_service_label) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入关联的Service的Label'),
                        delay: 5000
                    })
                    return false
                }

                // if (!params.eth_value) {
                //     this.$bkMessage({
                //         theme: 'error',
                //         message: this.$t('请填写网卡'),
                //         delay: 5000
                //     })
                //     return false
                // }

                if (params.network_mode === 'BRIDGE' && !params.host_port) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('BRIDGE网络模式下，端口必填'),
                        delay: 5000
                    })
                    return false
                }

                return true
            },

            /**
             * 格式化数据，符合接口需要的格式
             */
            formatData () {
                const params = JSON.parse(JSON.stringify(this.curLoadBalance))
                // 转换ips
                const ips = params.ips
                if (ips) {
                    params.ip_list = ips.split(/\n|\s+/)
                } else {
                    params.ip_list = []
                }

                // 转换调度约束
                const constraint = params.constraint.IntersectionItem
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

                // 镜像凭证
                if (!params.use_custom_imagesecret) {
                    delete params.image_pull_user
                    delete params.image_pull_password
                }

                // 挂载卷
                const volumes = params.volumes
                const configmaps = []
                volumes.forEach(volumeItem => {
                    const match = configmaps.find(item => item.name === volumeItem.name)
                    if (match) {
                        match.items.push({
                            'type': 'file',
                            'dataKey': volumeItem.volume.hostPath,
                            'dataKeyAlias': volumeItem.volume.hostPath,
                            'keyOrPath': volumeItem.volume.mountPath,
                            'readOnly': volumeItem.volume.readOnly,
                            'user': volumeItem.volume.user
                        })
                    } else if (volumeItem.name) {
                        configmaps.push({
                            'name': volumeItem.name,
                            'items': [
                                {
                                    'type': 'file',
                                    'dataKey': volumeItem.volume.hostPath,
                                    'dataKeyAlias': volumeItem.volume.hostPath,
                                    'keyOrPath': volumeItem.volume.mountPath,
                                    'readOnly': volumeItem.volume.readOnly,
                                    'user': volumeItem.volume.user
                                }
                            ]
                        })
                    }
                })

                // 资源限制
                params.resources.limits.cpu = String(params.resources.limits.cpu)
                params.resources.limits.memory = String(params.resources.limits.memory)

                // 网络
                if (params.network_mode !== 'BRIDGE') {
                    delete params.host_port
                }
                if (params.network_mode !== 'CUSTOM') {
                    delete params.custom_value
                }

                params.configmaps = configmaps
                return params
            },

            /**
             * 保存新建的LB
             */
            async createLoadBalance (data) {
                if (this.isDataSaveing) {
                    return false
                }
                const projectId = this.projectId
                this.isDataSaveing = true
                try {
                    await this.$store.dispatch('network/addMesosLoadBalance', { projectId, data })
                    this.searchScope = data.cluster_id
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('数据保存成功')
                    })
                    this.getLoadBalanceList()
                    this.hideLoadBalanceSlider()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }
            },

            /**
             * 保存更新的LB
             */
            async updateLoadBalance (data) {
                if (this.isDataSaveing) {
                    return false
                }

                const projectId = this.projectId
                const loadBalanceId = data.name
                const clusterId = data.cluster_id
                const namespace = data.namespace
                this.isDataSaveing = true

                try {
                    await this.$store.dispatch('network/updateMesosLoadBalance', {
                        projectId,
                        clusterId,
                        loadBalanceId,
                        namespace,
                        data
                    })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('数据保存成功')
                    })
                    this.getLoadBalanceList()
                    this.hideLoadBalanceSlider()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isDataSaveing = false
                }
            },

            /**
             * 保存LB
             */
            saveLoadBalance () {
                setTimeout(() => {
                    const params = this.formatData()
                    if (this.checkData(params)) {
                        if (this.curLoadBalance.id > 0) {
                            this.updateLoadBalance(params)
                        } else {
                            this.createLoadBalance(params)
                        }
                    }
                }, 500)
            },

            /**
             * 获取变量列表
             */
            async getVarList () {
                try {
                    await this.$store.dispatch('variable/getVarList', this.projectId)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            handleChangeImageMode () {
                this.curLoadBalance.use_custom_image_url = !this.curLoadBalance.use_custom_image_url
                // 使用默认
                if (!this.curLoadBalance.use_custom_image_url) {
                    this.curLoadBalance.image_url = `/${this.globalImageId}`
                    this.curLoadBalance.image_tag = ''
                }
            },

            getVolumeNameList (type) {
                if (type === 'configmap') {
                    return this.configmapList
                } else if (type === 'secret') {
                    return this.secretList
                }
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

            removeVolumn (item, index) {
                const volumes = this.curLoadBalance.volumes
                volumes.splice(index, 1)
            },

            addVolumn () {
                const volumes = this.curLoadBalance.volumes
                volumes.push({
                    'volume': {
                        'hostPath': '',
                        'mountPath': '',
                        'subPath': '',
                        'user': '',
                        'readOnly': false
                    },
                    'type': '',
                    'name': ''
                })
            },

            toggleMore () {
                this.isShowMore = !this.isShowMore
            }
        }
    }
</script>

<style scoped>
    @import '../../loadbalance.css';
    @import './index.css';
</style>
