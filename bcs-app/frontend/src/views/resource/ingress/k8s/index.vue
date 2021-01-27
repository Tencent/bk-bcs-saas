<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-topbar-title">
                Ingress
                <span class="biz-tip f12 ml10">{{$t('请通过模板集或Helm创建Ingress')}}</span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper p0" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <template v-if="!isInitLoading">
                <div class="biz-panel-header">
                    <div class="left">
                        <button
                            class="bk-button bk-default"
                            v-if="curPageData.length"
                            @click.stop.prevent="removeIngresses">
                            <span>{{$t('批量删除')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="getIngressList"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>

                <div class="biz-resource">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isInitLoading }">
                        <table class="bk-table has-table-hover biz-table biz-resource-table">
                            <thead>
                                <tr>
                                    <th style="width: 80px;">
                                        <label class="bk-form-checkbox">
                                            <input
                                                type="checkbox"
                                                name="check-all-user"
                                                :checked="isCheckCurPageAll"
                                                :disabled="!ingressList.length"
                                                @click="toogleCheckCurPage" />
                                        </label>
                                    </th>
                                    <th style="width: 300px;">{{$t('名称')}}</th>
                                    <th style="width: 300px;">{{$t('所属集群')}}</th>
                                    <th style="width: 300px;">{{$t('命名空间')}}</th>
                                    <th style="min-width: 70px;">{{$t('来源')}}</th>
                                    <th style="width: 300px;">{{$t('创建时间')}}</th>
                                    <th style="width: 300px;">{{$t('更新时间')}}</th>
                                    <th style="width: 300px;">{{$t('更新人')}}</th>
                                    <th style="width: 100px">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="ingressList.length">
                                    <tr v-for="(ingress, index) in curPageData" :key="index">
                                        <td>
                                            <label class="bk-form-checkbox">
                                                <input
                                                    type="checkbox"
                                                    name="check-variable"
                                                    :disabled="!ingress.can_delete || !ingress.permissions.use"
                                                    v-model="ingress.isChecked"
                                                    @click="rowClick" />
                                            </label>
                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="ingress.status === 'updating'">
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
                                            <a href="javascript: void(0)" class="bk-text-button biz-resource-title" @click.stop.prevent="showIngressDetail(ingress, index)">{{ingress.resourceName}}</a>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="ingress.cluster_id || '--'" placement="top">
                                                <p class="biz-text-wrapper">{{ingress.cluster_name ? ingress.cluster_name : '--'}}</p>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            {{ingress.namespace}}
                                        </td>
                                        <td>
                                            {{ingress.source_type ? ingress.source_type : '--'}}
                                        </td>
                                        <td>
                                            {{ingress.createTime ? formatDate(ingress.createTime) : '--'}}
                                        </td>
                                        <td>
                                            {{ingress.updateTime ? formatDate(ingress.updateTime) : '--'}}
                                        </td>
                                        <td>
                                            {{ingress.updator || '--'}}
                                        </td>
                                        <td>
                                            <li style="width: 100px;">
                                                <a v-if="ingress.can_update" href="javascript:void(0);" class="bk-text-button" @click="showIngressEditDialog(ingress)">{{$t('更新')}}</a>
                                                <bk-tooltip :content="ingress.can_update_msg" v-else placement="left">
                                                    <a href="javascript:void(0);" class="bk-text-button is-disabled">{{$t('更新')}}</a>
                                                </bk-tooltip>
                                                <a v-if="ingress.can_delete" @click.stop="removeIngress(ingress)" class="bk-text-button ml10">{{$t('删除')}}</a>
                                                <bk-tooltip :content="ingress.can_delete_msg || $t('不可删除')" v-else placement="left">
                                                    <span class="bk-text-button is-disabled ml10">{{$t('删除')}}</span>
                                                </bk-tooltip>
                                            </li>
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
                v-if="curIngress"
                :quick-close="true"
                :is-show.sync="ingressSlider.isShow"
                :title="ingressSlider.title"
                :width="'800'">
                <div class="pt20 pr30 pb20 pl30" slot="content">
                    <label class="biz-title">{{$t('主机列表')}}（spec.tls）</label>
                    <table class="bk-table biz-data-table has-table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 270px;">{{$t('主机名')}}</th>
                                <th>SecretName</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curIngress.tls.length">
                                <tr v-for="(rule, index) in curIngress.tls" :key="index">
                                    <td>{{rule.host || '--'}}</td>
                                    <td>{{rule.secretName || '--'}}</td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="2"><p style="padding: 10px; text-align: center;">{{$t('无数据')}}</p></td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <label class="biz-title">{{$t('规则')}}（spec.rules）</label>
                    <table class="bk-table biz-data-table has-table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 200px;">{{$t('主机名')}}</th>
                                <th style="width: 150px;">{{$t('路径')}}</th>
                                <th>{{$t('服务名称')}}</th>
                                <th style="width: 100px;">{{$t('服务端口')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curIngress.rules.length">
                                <tr v-for="(rule, index) in curIngress.rules" :key="index">
                                    <td>{{rule.host || '--'}}</td>
                                    <td>{{rule.path || '--'}}</td>
                                    <td>{{rule.serviceName || '--'}}</td>
                                    <td>{{rule.servicePort || '--'}}</td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="4"><p style="padding: 10px; text-align: center;">{{$t('无数据')}}</p></td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <div class="actions">
                        <button class="show-labels-btn bk-button bk-button-small bk-primary">{{$t('显示标签')}}</button>
                    </div>

                    <div class="point-box">
                        <template v-if="curIngress.labels.length">
                            <ul class="key-list">
                                <li v-for="(label, index) in curIngress.labels" :key="index">
                                    <span class="key">{{label[0]}}</span>
                                    <span class="value">{{label[1] || '--'}}</span>
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
                :width="'1020'"
                @hidden="handleCancelUpdate">
                <div slot="content">
                    <div class="bk-form biz-configuration-form pt20 pb20 pl10 pr20">
                        <div class="bk-form-item">
                            <div class="bk-form-item">
                                <div class="bk-form-content" style="margin-left: 0;">
                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 130px;">{{$t('名称')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <input
                                                type="text"
                                                class="bk-form-input"
                                                :disabled="true"
                                                style="width: 310px;"
                                                v-model="curEditedIngress.config.metadata.name"
                                                maxlength="64"
                                                name="applicationName">
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="bk-form-item">
                                <div class="bk-form-content" style="margin-left: 130px;">
                                    <button :class="['bk-text-button f12 mb10 pl0', { 'rotate': isTlsPanelShow }]" @click.stop.prevent="toggleTlsPanel">
                                        {{$t('TLS设置')}}<i class="bk-icon icon-angle-double-down ml5"></i>
                                    </button>
                                    <button :class="['bk-text-button f12 mb10 pl0', { 'rotate': isPanelShow }]" @click.stop.prevent="togglePanel">
                                        {{$t('更多设置')}}<i class="bk-icon icon-angle-double-down ml5"></i>
                                    </button>
                                </div>
                            </div>

                            <div class="bk-form-item mt0" v-show="isTlsPanelShow">
                                <div class="bk-form-content" style="margin-left: 130px;">
                                    <bk-tab :type="'fill'" :active-name="'tls'" :size="'small'">
                                        <bk-tabpanel name="tls" title="TLS">
                                            <div class="p20">
                                                <table class="biz-simple-table">
                                                    <tbody>
                                                        <tr v-for="(computer, index) in curEditedIngress.config.spec.tls" :key="index">
                                                            <td>
                                                                <bk-input
                                                                    type="text"
                                                                    :placeholder="$t('主机名，多个用英文逗号分隔')"
                                                                    style="width: 310px;"
                                                                    :value.sync="computer.hosts"
                                                                    :list="varList"
                                                                >
                                                                </bk-input>
                                                            </td>
                                                            <td>
                                                                <bk-selector
                                                                    :placeholder="$t('选择一个证书')"
                                                                    style="width: 350px;"
                                                                    :setting-key="'certId'"
                                                                    :display-key="'certName'"
                                                                    :selected.sync="computer.certId"
                                                                    :list="certList"
                                                                    @item-selected="handlerSelectCert(computer, ...arguments)"
                                                                >
                                                                    <div class="bk-selector-create-item" slot="newItem" @click="goCertList" v-if="certListUrl">
                                                                        <i class="bk-icon icon-apps"></i>
                                                                        <i class="text">{{$t('证书列表')}}</i>
                                                                    </div>
                                                                </bk-selector>
                                                            </td>
                                                            <td>
                                                                <button class="action-btn ml5" @click.stop.prevent="addTls">
                                                                    <i class="bk-icon icon-plus"></i>
                                                                </button>
                                                                <button class="action-btn" v-if="curEditedIngress.config.spec.tls.length > 1" @click.stop.prevent="removeTls(index, computer)">
                                                                    <i class="bk-icon icon-minus"></i>
                                                                </button>
                                                            </td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            </div>
                                        </bk-tabpanel>
                                    </bk-tab>
                                </div>
                            </div>

                            <div class="bk-form-item mt0" v-show="isPanelShow">
                                <div class="bk-form-content" style="margin-left: 130px;">
                                    <bk-tab :type="'fill'" :active-name="'remark'" :size="'small'">
                                        <bk-tabpanel name="remark" :title="$t('注解')">
                                            <div class="biz-tab-wrapper m20">
                                                <bk-keyer :key-list.sync="curRemarkList" :var-list="varList" ref="remarkKeyer"></bk-keyer>
                                            </div>
                                        </bk-tabpanel>
                                        <bk-tabpanel name="label" :title="$t('标签')">
                                            <div class="biz-tab-wrapper m20">
                                                <bk-keyer :key-list.sync="curLabelList" :var-list="varList" ref="labelKeyer"></bk-keyer>
                                            </div>
                                        </bk-tabpanel>
                                    </bk-tab>
                                </div>
                            </div>

                            <!-- part2 start -->
                            <div class="biz-part-header">
                                <div class="bk-button-group">
                                    <div class="item" v-for="(rule, index) in curEditedIngress.config.spec.rules" :key="index">
                                        <button :class="['bk-button bk-default is-outline', { 'is-selected': curRuleIndex === index }]" @click.stop="setCurRule(rule, index)">
                                            {{rule.host || $t('未命名')}}
                                        </button>
                                        <span class="bk-icon icon-close-circle" @click.stop="removeRule(index)" v-if="curEditedIngress.config.spec.rules.length > 1"></span>
                                    </div>
                                    <bk-tooltip ref="containerTooltip" :content="curEditedIngress.config.spec.rules.length >= 5 ? $t('最多添加5个') : $t('添加Rule')" placement="top">
                                        <button type="button" class="bk-button bk-default is-outline is-icon" :disabled="curEditedIngress.config.spec.rules.length >= 5 " @click.stop.prevent="addLocalRule">
                                            <i class="bk-icon icon-plus"></i>
                                        </button>
                                    </bk-tooltip>
                                </div>
                            </div>

                            <div class="bk-form biz-configuration-form pb15">
                                <div class="biz-span">
                                    <span class="title">{{$t('基础信息')}}</span>
                                </div>
                                <div class="bk-form-item is-required">
                                    <label class="bk-label" style="width: 130px;">{{$t('虚拟主机名')}}：</label>
                                    <div class="bk-form-content" style="margin-left: 130px;">
                                        <input type="text" :class="['bk-form-input']" :placeholder="$t('请输入')" style="width: 310px;" v-model="curRule.host" name="ruleName">
                                    </div>
                                </div>
                                <div class="bk-form-item">
                                    <label class="bk-label" style="width: 130px;">{{$t('路径组')}}：</label>
                                    <div class="bk-form-content" style="margin-left: 130px;">
                                        <table class="biz-simple-table">
                                            <tbody>
                                                <tr v-for="(pathRule, index) of curRule.http.paths" :key="index">
                                                    <td>
                                                        <bk-input
                                                            type="text"
                                                            :placeholder="$t('路径')"
                                                            style="width: 310px;"
                                                            :value.sync="pathRule.path"
                                                            :list="varList"
                                                        >
                                                        </bk-input>
                                                    </td>
                                                    <td style="text-align: center;">
                                                        <i class="bk-icon icon-arrows-right"></i>
                                                    </td>
                                                    <td>
                                                        <bk-selector
                                                            style="width: 180px;"
                                                            :placeholder="$t('Service名称')"
                                                            :disabled="isLoadBalanceEdited"
                                                            :setting-key="'_name'"
                                                            :display-key="'_name'"
                                                            :selected.sync="pathRule.backend.serviceName"
                                                            :list="linkServices || []"
                                                            @item-selected="handlerSelectService(pathRule)">
                                                        </bk-selector>
                                                    </td>
                                                    <td>
                                                        <bk-selector
                                                            style="width: 180px;"
                                                            :placeholder="$t('端口')"
                                                            :disabled="isLoadBalanceEdited"
                                                            :setting-key="'_id'"
                                                            :display-key="'_name'"
                                                            :selected.sync="pathRule.backend.servicePort"
                                                            :list="linkServices[pathRule.backend.serviceName] || []">
                                                        </bk-selector>
                                                    </td>
                                                    <td>
                                                        <button class="action-btn ml5" @click.stop.prevent="addRulePath">
                                                            <i class="bk-icon icon-plus"></i>
                                                        </button>
                                                        <button class="action-btn" v-if="curRule.http.paths.length > 1" @click.stop.prevent="removeRulePath(pathRule, index)">
                                                            <i class="bk-icon icon-minus"></i>
                                                        </button>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                        <p class="biz-tip">{{$t('提示：同一个虚拟主机名可以有多个路径')}}</p>
                                    </div>
                                </div>
                            </div>

                            <div class="bk-form-item mt25" style="margin-left: 130px;">
                                <button :class="['bk-button bk-primary', { 'is-loading': isDetailSaving }]" @click.stop.prevent="saveIngressDetail">{{$t('保存并更新')}}</button>
                                <button class="bk-button bk-default" @click.stop.prevent="handleCancelUpdate">{{$t('取消')}}</button>
                            </div>
            
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
    import ingressParams from '@open/json/k8s-ingress.json'
    import ruleParams from '@open/json/k8s-ingress-rule.json'
    import bkKeyer from '@open/components/keyer'

    export default {
        components: {
            bkKeyer
        },
        data () {
            return {
                formatDate: formatDate,
                isInitLoading: true,
                isPageLoading: false,
                searchKeyword: '',
                searchScope: '',
                curPageData: [],
                curIngress: null,
                curEditedIngress: ingressParams,
                isPanelShow: false,
                isTlsPanelShow: false,
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
                batchDialogConfig: {
                    isShow: false,
                    list: [],
                    data: []
                },
                curRuleIndex: 0,
                curRule: ingressParams.config.spec.rules[0],
                curIngressName: '',
                alreadySelectedNums: 0,
                ingressEditSlider: {
                    title: '',
                    isShow: false
                },
                linkServices: []
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
            isCheckCurPageAll () {
                if (this.curPageData.length) {
                    const list = this.curPageData
                    const selectList = list.filter((item) => {
                        return item.isChecked === true
                    })
                    const canSelectList = list.filter((item) => {
                        return item.can_delete && item.permissions.use
                    })
                    if (selectList.length && (selectList.length === canSelectList.length)) {
                        return true
                    } else {
                        return false
                    }
                } else {
                    return false
                }
            },
            projectId () {
                return this.$route.params.projectId
            },
            ingressList () {
                const list = this.$store.state.resource.ingressList
                list.forEach(item => {
                    item.isChecked = false
                })
                return JSON.parse(JSON.stringify(list))
            },
            isClusterDataReady () {
                return this.$store.state.cluster.isClusterDataReady
            },
            varList () {
                const list = this.$store.state.variable.varList.map(item => {
                    item._id = item.key
                    item._name = item.key
                    return item
                })
                return list
            },
            certListUrl () {
                return this.$store.state.k8sTemplate.certListUrl
            },
            certList () {
                return this.$store.state.k8sTemplate.certList
            },
            curLabelList () {
                const list = []
                const labels = this.curEditedIngress.config.metadata.labels
                for (const [key, value] of Object.entries(labels)) {
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
            curRemarkList () {
                const list = []
                const annotations = this.curEditedIngress.config.metadata.annotations
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
                            
                            this.getIngressList()
                        }, 1000)
                    }
                }
            }
        },
        created () {
            this.initPageConf()
            this.getCertList()
            // this.initServices()
            // this.getIngressList()
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
             * 全选/取消全选当前页数据
             */
            toogleCheckCurPage () {
                const isChecked = this.isCheckCurPageAll
                this.curPageData.forEach((item) => {
                    if (item.can_delete && item.permissions.use) {
                        item.isChecked = !isChecked
                    }
                })
                this.$nextTick(() => {
                    this.alreadySelectedNums = this.ingressList.filter(item => item.isChecked).length
                })
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
                    await this.$store.dispatch('resource/deleteIngresses', { projectId, data })
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
                    await this.$store.dispatch('resource/deleteIngress', {
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
            showIngressDetail (ingress, index) {
                this.ingressSlider.title = ingress.resourceName
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
                const params = {
                    cluster_id: this.searchScope
                }
                try {
                    this.isPageLoading = true
                    await this.$store.dispatch('resource/getIngressList', {
                        projectId,
                        params
                    })

                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)

                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchKeyword) {
                        this.searchIngress()
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
                const keyList = ['resourceName', 'namespace', 'cluster_name']
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
                        if (item[key].indexOf(keyword) > -1) {
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

                if (!ingress.data.spec.hasOwnProperty('tls')) {
                    ingress.data.spec.tls = [
                        {
                            hosts: '',
                            certId: ''
                        }
                    ]
                } else if (JSON.stringify(ingress.data.spec.tls) === '[{}]') {
                    ingress.data.spec.tls = [
                        {
                            hosts: '',
                            certId: ''
                        }
                    ]
                }
                const ingressClone = JSON.parse(JSON.stringify(ingress))
                ingressClone.data.spec.tls.forEach(item => {
                    if (item.hosts && item.hosts.join) {
                        item.hosts = item.hosts.join(',')
                    }
                })
                this.curEditedIngress = ingressClone
                this.curEditedIngress.config = ingressClone.data
                this.ingressEditSlider.title = ingress.name
                delete this.curEditedIngress.data
                
                if (this.curEditedIngress.config.spec.rules.length) {
                    this.setCurRule(this.curEditedIngress.config.spec.rules[0], 0)
                } else {
                    this.addLocalRule()
                }
                this.getServiceList(ingress.cluster_id, ingress.namespace_id)
                this.ingressEditSlider.isShow = true
            },

            togglePanel () {
                this.isTlsPanelShow = false
                this.isPanelShow = !this.isPanelShow
            },
            toggleTlsPanel () {
                this.isPanelShow = false
                this.isTlsPanelShow = !this.isTlsPanelShow
            },
            goCertList () {
                if (this.certListUrl) {
                    window.open(this.certListUrl)
                }
            },
            addTls () {
                this.curEditedIngress.config.spec.tls.push({
                    hosts: '',
                    certId: ''
                })
            },
            removeTls (index, curTls) {
                this.curEditedIngress.config.spec.tls.splice(index, 1)
            },
            setCurRule (rule, index) {
                this.curRule = rule
                this.curRuleIndex = index
            },
            removeRule (index) {
                const rules = this.curEditedIngress.config.spec.rules
                rules.splice(index, 1)
                if (this.curRuleIndex === index) {
                    this.curRuleIndex = 0
                } else if (this.curRuleIndex !== 0) {
                    this.curRuleIndex = this.curRuleIndex - 1
                }

                this.curRule = rules[this.curRuleIndex]
            },
            addLocalRule () {
                const rule = JSON.parse(JSON.stringify(ruleParams))
                const rules = this.curEditedIngress.config.spec.rules
                const index = rules.length
                rule.host = 'rule-' + (index + 1)
                rules.push(rule)
                this.setCurRule(rule, index)
            },
            addRulePath () {
                const params = {
                    backend: {
                        serviceName: '',
                        servicePort: ''
                    },
                    path: ''
                }

                this.curRule.http.paths.push(params)
            },
            removeRulePath (pathRule, index) {
                this.curRule.http.paths.splice(index, 1)
            },
            handlerSelectService (pathRule) {
                pathRule.backend.servicePort = ''
            },
            async initServices (version) {
                const projectId = this.projectId
                await this.$store.dispatch('k8sTemplate/getServicesByVersion', { projectId, version })
            },
            /**
             * 获取service列表
             */
            async getServiceList (clusterId, namespaceId) {
                const projectId = this.projectId
                const params = {
                    cluster_id: clusterId
                }

                try {
                    const res = await this.$store.dispatch('network/getServiceList', {
                        projectId,
                        params
                    })

                    const serviceList = res.data.data.filter(service => {
                        return service.namespace_id === namespaceId
                    }).map(service => {
                        const ports = service.data.spec.ports || []
                        return {
                            _name: service.resourceName,
                            service_name: service.resourceName,
                            service_ports: ports
                        }
                    })
                    serviceList.forEach(service => {
                        serviceList[service.service_name] = []
                        service.service_ports.forEach(item => {
                            serviceList[service.service_name].push({
                                _id: item.port,
                                _name: item.port
                            })
                        })
                    })
                    this.linkServices = serviceList
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            checkData () {
                const ingress = this.curEditedIngress
                const nameReg = /^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$/
                const pathReg = /\/((?!\.)[\w\d\-./~]+)*/
                let megPrefix = ''

                for (const rule of ingress.config.spec.rules) {
                    // 检查rule
                    if (!rule.host) {
                        megPrefix += this.$t('规则：')
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('主机名不能为空')
                        })
                        return false
                    }

                    if (!nameReg.test(rule.host)) {
                        megPrefix += this.$t('规则主机名：')
                        this.$bkMessage({
                            theme: 'error',
                            message: megPrefix + this.$t('名称错误，只能包含：小写字母、数字、连字符(-)，首字母必须是字母'),
                            delay: 8000
                        })
                        return false
                    }

                    const paths = rule.http.paths

                    for (const path of paths) {
                        if (!path.path) {
                            megPrefix += `${rule.host}中${this.$t('路径组')}：`
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('请填写路径！'),
                                delay: 8000
                            })
                            return false
                        }

                        if (path.path && !pathReg.test(path.path)) {
                            megPrefix += `${rule.host}中${this.$t('路径组')}：`
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('路径不正确'),
                                delay: 8000
                            })
                            return false
                        }

                        if (!path.backend.serviceName) {
                            megPrefix += `${rule.host}中${this.$t('路径组')}：`
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('请关联服务！'),
                                delay: 8000
                            })
                            return false
                        }

                        if (!path.backend.servicePort) {
                            megPrefix += `${rule.host}中${this.$t('路径组')}：`
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + this.$t('请关联服务端口！'),
                                delay: 8000
                            })
                            return false
                        }

                        if (path.backend.serviceName && !this.linkServices.hasOwnProperty(path.backend.serviceName)) {
                            megPrefix += `${rule.host}中${this.$t('路径组')}：`
                            this.$bkMessage({
                                theme: 'error',
                                message: megPrefix + `关联的Service【${path.backend.serviceName}】不存在，请重新绑定！`,
                                delay: 8000
                            })
                            return false
                        }
                    }
                }
                return true
            },

            formatData () {
                const params = JSON.parse(JSON.stringify(this.curEditedIngress))
                delete params.config.metadata.resourceVersion
                delete params.config.metadata.selfLink
                delete params.config.metadata.uid
                
                params.config.metadata.annotations = this.$refs.remarkKeyer.getKeyObject()
                params.config.metadata.labels = this.$refs.labelKeyer.getKeyObject()

                // 如果不是变量，转为数组形式
                const varReg = /\{\{([^\{\}]+)?\}\}/g
                params.config.spec.tls.forEach(item => {
                    if (!varReg.test(item.hosts)) {
                        item.hosts = item.hosts.split(',')
                    }
                })
                return params
            },

            /**
             * 保存service
             */
            async saveIngressDetail () {
                if (this.checkData()) {
                    const data = this.formatData()
                    const projectId = this.projectId
                    const clusterId = this.curEditedIngress.cluster_id
                    const namespace = this.curEditedIngress.namespace
                    const ingressId = this.curEditedIngress.config.metadata.name

                    if (this.isDetailSaving) {
                        return false
                    }

                    this.isDetailSaving = true

                    try {
                        await this.$store.dispatch('resource/saveIngressDetail', {
                            projectId,
                            clusterId,
                            namespace,
                            ingressId,
                            data
                        })

                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('保存成功'),
                            hasCloseIcon: true,
                            delay: 3000
                        })
                        this.getIngressList()
                        this.handleCancelUpdate()
                    } catch (e) {
                        catchErrorHandler(e, this)
                    } finally {
                        this.isDetailSaving = false
                    }
                }
            },

            handleCancelUpdate () {
                this.ingressEditSlider.isShow = false
            },

            async getCertList () {
                const projectId = this.projectId
                try {
                    await this.$store.dispatch('k8sTemplate/getCertList', projectId)
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            handlerSelectCert (computer, index, data) {
                computer.certType = data.certType
            }
        }
    }
</script>

<style scoped>
    @import '../../ingress.css';
</style>
