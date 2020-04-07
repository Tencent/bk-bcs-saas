<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-topbar-title">
                ConfigMaps
                <span class="biz-tip f12 ml10">{{currentView === 'mesosService' ? $t('请通过模板集创建ConfigMap') : $t('请通过模板集或Helm创建ConfigMap')}}</span>
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper p0" v-bkloading="{ isLoading: isInitLoading, opacity: 0.1 }">
            <app-exception
                v-if="exceptionCode && !isInitLoading"
                :type="exceptionCode.code"
                :text="exceptionCode.msg">
            </app-exception>

            <template v-if="!exceptionCode && !isInitLoading">
                <div class="biz-panel-header">
                    <div class="left">
                        <button class="bk-button bk-default" @click.stop.prevent="removeConfigmaps" v-if="curPageData.length">
                            <span>{{$t('批量删除')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="$t('输入名称或命名空间，按Enter搜索')"
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="searchConfigmap"
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
                                                :disabled="!configmapList.length"
                                                @click="toggleCheckCurPage" />
                                        </label>
                                    </th>
                                    <th style="min-width: 200px;">{{$t('名称')}}</th>
                                    <th style="min-width: 130px;">{{$t('所属集群')}}</th>
                                    <th style="min-width: 130px;">{{$t('命名空间')}}</th>
                                    <th style="min-width: 130px">{{$t('来源')}}</th>
                                    <th style="min-width: 130px;">{{$t('创建时间')}}</th>
                                    <th style="min-width: 130px;">{{$t('更新时间')}}</th>
                                    <th style="min-width: 130px;">{{$t('更新人')}}</th>
                                    <th style="min-width: 130px">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="configmapList.length">
                                    <tr v-for="(configmap, index) in curPageData" :key="index">
                                        <td style="position: relative;">
                                            <label class="bk-form-checkbox">
                                                <input
                                                    type="checkbox"
                                                    name="check-variable"
                                                    :disabled="!configmap.can_delete || !configmap.permissions.use"
                                                    v-model="configmap.isChecked"
                                                    @click="rowClick" />
                                            </label>
                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="configmap.status === 'updating'">
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
                                            <a href="javascript: void(0)" class="bk-text-button biz-table-title biz-resource-title biz-text-wrapper" @click.stop.prevent="showConfigmapDetail(configmap, index)">{{configmap.resourceName}}</a>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="configmap.cluster_id || '--'" placement="top">
                                                <p class="biz-text-wrapper">{{configmap.cluster_name ? configmap.cluster_name : '--'}}</p>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            {{configmap.namespace}}
                                        </td>
                                        <td>
                                            {{configmap.source_type}}
                                        </td>
                                        <td>
                                            {{configmap.createTime ? formatDate(configmap.createTime) : '--'}}
                                        </td>
                                        <td>
                                            {{configmap.update_time ? formatDate(configmap.update_time) : '--'}}
                                        </td>
                                        <td>
                                            {{configmap.updator || '--'}}
                                        </td>
                                        <td>
                                            <li>
                                                <span v-if="configmap.can_update" @click.stop="updateConfigmap(configmap)" class="biz-operate">{{$t('更新')}}</span>
                                                <bk-tooltip :content="configmap.can_update_msg" v-else placement="left">
                                                    <span class="biz-not-operate">{{$t('更新')}}</span>
                                                </bk-tooltip>
                                                <span v-if="configmap.can_delete" @click.stop="removeConfigmap(configmap)" class="biz-operate">{{$t('删除')}}</span>
                                                <bk-tooltip :content="configmap.can_delete_msg || $t('不可删除')" v-else placement="left">
                                                    <span class="biz-not-operate">{{$t('删除')}}</span>
                                                </bk-tooltip>
                                            </li>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="8">
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
                v-if="curConfigmap"
                :quick-close="true"
                :is-show.sync="configmapSlider.isShow"
                :title="configmapSlider.title"
                :width="'640'">
                <div class="p30" slot="content">
                    <table class="bk-table biz-data-table has-table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 270px;">{{$t('键')}}</th>
                                <th>{{$t('值')}}<a href="javascript:void(0)" v-if="curConfigmapKeyList.length" class="bk-text-button display-text-btn" @click.stop.prevent="showKeyValue">{{isShowKeyValue ? $t('隐藏') : $t('明文显示')}}</a></th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curConfigmapKeyList.length">
                                <tr v-for="item in curConfigmapKeyList" :key="item.key">
                                    <td>{{item.key}}</td>
                                    <td>
                                        <textarea v-if="isShowKeyValue" readonly :title="item.value" class="bk-form-textarea  key-box" v-model="item.value"></textarea>
                                        <span v-else>******</span>
                                    </td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="2"><p style="padding: 10px; text-align: center;">{{$t('无数据')}}</p></td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <div class="actions">
                        <button class="show-labels-btn bk-button bk-button-small bk-primary">{{$t('显示标签')}}</button>
                    </div>

                    <div class="point-box">
                        <template v-if="curConfigmap.labels.length">
                            <ul class="key-list">
                                <li v-for="(label, index) in curConfigmap.labels" :key="index">
                                    <span class="key">{{label[0]}}</span>
                                    <span class="value">{{label[1]}}</span>
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
                :is-show.sync="addSlider.isShow"
                :title="addSlider.title"
                :width="'800'"
                :quick-close="false">
                <div class="p30 bk-resource-configmap" slot="content">
                    <div v-bkloading="{ isLoading: isUpdateLoading }">
                        <div class="bk-form-item">
                            <div class="bk-form-item" style="margin-bottom: 20px;">
                                <label class="bk-label">{{$t('名称')}}：</label>
                                <div class="bk-form-content" style="margin-left: 105px;">
                                    <input
                                        type="text"
                                        class="bk-form-input"
                                        name="configmapName"
                                        disabled="disabled"
                                        style="min-width: 310px; cursor: not-allowed;"
                                        v-model="curConfigmapName" />
                                </div>
                            </div>
                            <label class="bk-label">{{$t('键')}}：</label>
                            <div class="bk-form-content" style="margin-left: 105px;">
                                <div class="biz-list-operation">
                                    <div class="item" v-for="(data, index) in configmapKeyList" :key="index">
                                        <button
                                            :class="['bk-button', { 'bk-primary': curKeyIndex === index }]"
                                            v-if="!data.isEdit"
                                            @click.stop.prevent="setCurKey(data, index)">
                                            {{data.key || $t('未命名')}}
                                        </button>
                                        <bk-input
                                            type="text"
                                            placeholder=""
                                            v-else
                                            style="width: 78px;"
                                            :value.sync="data.key"
                                            :list="varList"
                                            @blur="setKey(data, index)"
                                        >
                                        </bk-input>
                                        <span class="bk-icon icon-edit" v-show="!data.isEdit" @click.stop.prevent="editKey(data, index)"></span>
                                        <span class="bk-icon icon-close" v-show="!data.isEdit" @click.stop.prevent="removeKey(data, index)"></span>
                                    </div>
                                    <bk-tooltip ref="keyTooltip" :content="$t('添加Key')" placement="top">
                                        <button class="bk-button bk-default is-outline is-icon" @click.stop.prevent="addKey">
                                            <i class="bk-icon icon-plus"></i>
                                        </button>
                                    </bk-tooltip>
                                </div>
                            </div>
                        </div>
                        <template v-if="curKeyParams">
                            <div class="bk-form-item" style="margin-top: 0;" v-if="currentView === 'mesosService'">
                                <label class="bk-label">{{$t('值来源')}}：</label>
                                <div class="bk-form-content" style="margin-left: 105px;">
                                    <label class="bk-form-radio">
                                        <input type="radio" name="key-type" value="file" v-model="curKeyParams.type">
                                        <i class="bk-radio-text">{{$t('在线编辑')}}</i>
                                    </label>
                                    <label class="bk-form-radio">
                                        <input type="radio" name="key-type" value="http" v-model="curKeyParams.type">
                                        <i class="bk-radio-text">{{$t('仓库获取')}}</i>
                                    </label>
                                </div>
                            </div>
                            <div class="bk-form-item" style="margin-top: 13px;">
                                <label class="bk-label">{{$t('值')}}：</label>
                                <div class="bk-form-content" style="margin-left: 105px;" v-if="currentView === 'k8sService'">
                                    <textarea class="bk-form-textarea" style="height: 200px;" v-model="curKeyParams.content" :placeholder="$t('请输入键') + curKeyParams.key + $t('的内容')"></textarea>
                                </div>
                                <div class="bk-form-content" style="margin-left: 105px;" v-else>
                                    <textarea class="bk-form-textarea" style="height: 200px;" v-model="curKeyParams.content" :placeholder="$t('请输入键') + curKeyParams.key + $t('的内容')" v-if="curKeyParams.type === 'file'"></textarea>
                                    <textarea class="bk-form-textarea" style="height: 200px;" v-model="curKeyParams.content" :placeholder="$t('请输入仓库中配置文件的相对路径')" v-else></textarea>
                                </div>
                                <label style="margin-left: 105px; font-size: 14px; color: #c3cdd7;" v-if="currentView === 'mesosService' && curKeyParams.type === 'file'">{{$t('实例化时会将值的内容做base64编码')}}</label>
                            </div>
                        </template>
                        <div class="action-inner" style="margin-top: 20px; margin-left: 105px;">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="submitUpdateConfigmap">
                                {{$t('保存')}}
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="cancleUpdateConfigmap">
                                {{$t('取消')}}
                            </button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>

            <bk-dialog
                :is-show="batchDialogConfig.isShow"
                :width="550"
                :has-header="false"
                :quick-close="false"
                @confirm="deleteConfigmaps(batchDialogConfig.data)"
                @cancel="batchDialogConfig.isShow = false">
                <div slot="content">
                    <div class="biz-batch-wrapper">
                        <p class="batch-title">{{$t('确定要删除以下ConfigMap？')}}</p>
                        <ul class="batch-list">
                            <li v-for="(item, index) of batchDialogConfig.list" :key="index" :title="item">{{item}}</li>
                        </ul>
                    </div>
                </div>
            </bk-dialog>
        </div>
    </div>
</template>

<script>
    import { catchErrorHandler, formatDate } from '@open/common/util'
    import globalMixin from '@open/mixins/global'

    export default {
        mixins: [globalMixin],
        data () {
            return {
                formatDate: formatDate,
                isInitLoading: true,
                isPageLoading: false,
                exceptionCode: null,
                searchKeyword: '',
                searchScope: '',
                curPageData: [],
                curConfigmap: null,
                isShowKeyValue: false,
                pageConf: {
                    total: 1,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                batchDialogConfig: {
                    isShow: false,
                    list: [],
                    data: []
                },
                configmapSlider: {
                    title: '',
                    isShow: false
                },
                addSlider: {
                    title: '',
                    isShow: false
                },
                configmapKeyList: [],
                curKeyIndex: 0,
                curKeyParams: null,
                curConfigmapName: '',
                namespaceId: 0,
                instanceId: 0,
                clusterId: '',
                namespace: '',
                isUpdateLoading: false,
                configmapTimer: null,
                curProject: {},
                currentView: 'k8sService',
                isBatchRemoving: false,
                curSelectedData: [],
                alreadySelectedNums: 0
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
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
            configmapList () {
                const list = this.$store.state.resource.configmapList
                list.forEach(item => {
                    item.isChecked = false
                })
                return JSON.parse(JSON.stringify(list))
            },
            curConfigmapKeyList () {
                if (this.curConfigmap) {
                    const results = []
                    let data = {}

                    if (this.currentView === 'k8sService') {
                        data = this.curConfigmap.data.data || {}

                        const keys = Object.keys(data)
                        keys.forEach(item => {
                            results.push({
                                key: item,
                                value: data[item]
                            })
                        })
                    } else {
                        data = this.curConfigmap.data.datas || {}

                        const keys = Object.keys(data)
                        keys.forEach(item => {
                            results.push({
                                key: item,
                                value: data[item].content
                            })
                        })
                    }

                    return results
                } else {
                    return []
                }
            },
            varList () {
                return this.$store.state.variable.varList
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
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            }
        },
        created () {
            this.initPageConf()
            this.getConfigmapList()
        },
        mounted () {
            this.curProject = this.initCurProject()
            this.setComponent()
        },
        methods: {
            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.getConfigmapList()
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
             * 全选/反选当前页
             */
            toggleCheckCurPage () {
                const isChecked = this.isCheckCurPageAll
                this.curPageData.forEach((item) => {
                    if (item.can_delete && item.permissions.use) {
                        item.isChecked = !isChecked
                    }
                })

                this.$nextTick(() => {
                    this.alreadySelectedNums = this.configmapList.filter(item => item.isChecked).length
                })
            },

            /**
             * 清空选择
             */
            clearSelectConfigmaps () {
                this.curPageData.forEach((item) => {
                    item.isChecked = false
                })
            },

            /**
             * 确认删除configmap
             */
            async removeConfigmaps () {
                const data = []
                const names = []

                this.configmapList.forEach(item => {
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
                        message: this.$t('请选择要删除的ConfigMap')
                    })
                    return false
                }

                this.batchDialogConfig.list = names
                this.batchDialogConfig.data = data
                this.batchDialogConfig.isShow = true
            },

            /**
             * 删除configmap
             * @param  {Object} data configmap
             */
            async deleteConfigmaps (data) {
                const me = this
                const projectId = this.projectId

                this.batchDialogConfig.isShow = false
                this.isPageLoading = true
                try {
                    await this.$store.dispatch('resource/deleteConfigmaps', {
                        projectId,
                        data
                    })

                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除成功')
                    })
                    // 稍晚一点加载数据，接口不一定立即清除
                    setTimeout(() => {
                        me.getConfigmapList()
                    }, 500)
                } catch (e) {
                    // 4004，已经被删除过，但接口不能立即清除，再重新拉数据，防止重复删除
                    if (e.code === 4004) {
                        setTimeout(() => {
                            me.getConfigmapList()
                        }, 500)
                    } else {
                        me.isPageLoading = false
                    }
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 根据当前项目调用k8s/mesos
             */
            setComponent () {
                if (this.curProject.kind === PROJECT_MESOS) {
                    this.currentView = 'mesosService'
                } else if (this.curProject.kind === PROJECT_K8S) {
                    this.currentView = 'k8sService'
                }
            },

            /**
             * 更新configmap
             * @param  {Object} configmap configmap
             */
            async updateConfigmap (configmap) {
                if (!configmap.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: configmap.namespace_id,
                        resource_name: configmap.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.addSlider.isShow = true
                this.isUpdateLoading = true
                this.addSlider.title = `${this.$t('更新')}${configmap.name}`
                this.curConfigmapName = configmap.name
                this.namespaceId = configmap.namespace_id
                this.instanceId = configmap.instance_id
                this.namespace = configmap.namespace
                this.clusterId = configmap.cluster_id

                try {
                    const res = await this.$store.dispatch('resource/updateSelectConfigmap', {
                        projectId: this.projectId,
                        namespace: this.namespace,
                        name: this.curConfigmapName,
                        clusterId: this.clusterId
                    })
                    const configmapObj = res.data.data[0] || {}
                    this.initKeyList(configmapObj)
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isUpdateLoading = false
                }
            },

            /**
             * 删除configmap前的确认
             * @param  {Object} configmap configmap
             * @return {[type]}
             */
            async removeConfigmap (configmap) {
                if (!configmap.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: configmap.namespace_id,
                        resource_name: configmap.namespace,
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
                    }, `${this.$t('确定要删除ConfigMap')}【${configmap.cluster_name} / ${configmap.namespace} / ${configmap.name}】？`),
                    confirmFn () {
                        me.deleteConfigmap(configmap)
                    }
                })
            },

            /**
             * 删除configmap
             * @param {Object} configmap configmap
             */
            async deleteConfigmap (configmap) {
                const me = this
                const projectId = me.projectId
                const clusterId = configmap.cluster_id
                const namespace = configmap.namespace
                const name = configmap.name

                this.isPageLoading = true
                try {
                    await this.$store.dispatch('resource/deleteConfigmap', { projectId, clusterId, namespace, name })
                    me.$bkMessage({
                        theme: 'success',
                        message: this.$t('删除成功')
                    })
                    // 稍晚一点加载数据，接口不一定立即清除
                    setTimeout(() => {
                        me.getConfigmapList()
                    }, 500)
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.isPageLoading = false
                }
            },

            /**
             * 向服务器提交configmap更新数据
             */
            async submitUpdateConfigmap () {
                const enity = {}
                enity.namespace_id = this.namespaceId
                enity.instance_id = this.instanceId
                enity.config = {}
                const oName = {
                    name: this.curConfigmapName
                }
                enity.config['metadata'] = oName
                const keyList = []
                const oKey = {}

                if (this.currentView === 'k8sService') {
                    const k8sList = this.configmapKeyList
                    const k8sLength = k8sList.length
                    for (let i = 0; i < k8sLength; i++) {
                        const item = k8sList[i]
                        keyList.push(item.key)
                        oKey[item.key] = item.content
                    }
                    const aKey = keyList.sort()
                    for (let i = 0; i < aKey.length; i++) {
                        if (aKey[i] === aKey[i + 1]) {
                            this.bkMessageInstance = this.$bkMessage({
                                theme: 'error',
                                message: `${this.$t('键')}【${aKey[i]}】${this.$t('重复')}`
                            })
                            return
                        }
                    }
                    enity.config['data'] = oKey
                } else {
                    const mesosList = this.configmapKeyList
                    const mesosLength = mesosList.length
                    for (let i = 0; i < mesosLength; i++) {
                        const item = mesosList[i]
                        keyList.push(item.key)
                        oKey[item.key] = {
                            type: item.type,
                            content: item.content
                        }
                    }
                    const aKey = keyList.sort()
                    for (let i = 0; i < aKey.length; i++) {
                        if (aKey[i] === aKey[i + 1]) {
                            this.bkMessageInstance = this.$bkMessage({
                                theme: 'error',
                                message: `${this.$t('键')}【${aKey[i]}】${this.$t('重复')}`
                            })
                            return
                        }
                    }
                    enity.config['datas'] = oKey
                }

                try {
                    await this.$store.dispatch('resource/updateSingleConfigmap', {
                        projectId: this.projectId,
                        clusterId: this.clusterId,
                        namespace: this.namespace,
                        name: this.curConfigmapName,
                        data: enity
                    })
                    this.isPageLoading = true
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('更新成功')
                    })
                    this.getConfigmapList()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.cancleUpdateConfigmap()
                }
            },

            /**
             * 取消更新configmap
             */
            cancleUpdateConfigmap () {
                // 数据清空或恢复默认值
                this.addSlider.isShow = false
                this.isUpdateLoading = false
                this.configmapKeyList.splice(0, this.configmapKeyList.length, ...[])
                this.curKeyIndex = 0
                this.namespaceId = 0
                this.instanceId = 0
                this.curKeyParams = null
                this.curConfigmapName = ''
                this.namespace = ''
                this.clusterId = ''
            },

            /**
             * 添加key
             */
            addKey () {
                const index = this.configmapKeyList.length + 1
                if (this.currentView === 'k8sService') {
                    this.configmapKeyList.push({
                        key: 'key-' + index,
                        isEdit: false,
                        content: ''
                    })
                } else {
                    this.configmapKeyList.push({
                        key: 'key-' + index,
                        isEdit: false,
                        type: 'file',
                        content: ''
                    })
                }
                this.curKeyParams = this.configmapKeyList[index - 1]
                this.curKeyIndex = index - 1
                this.$refs.keyTooltip.visible = false
            },

            /**
             * 设置当前key
             * @param {Object} data 当前key数据
             * @param {number} index 索引
             */
            setKey (data, index) {
                if (data.key === '') {
                    data.key = 'key-' + this.configmapKeyList.length
                } else {
                    const nameReg = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,254}$/
                    const varReg = /\{\{([^\{\}]+)?\}\}/g

                    if (!nameReg.test(data.key.replace(varReg, 'key'))) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('键名错误，只能包含：字母、数字、连字符(-)、点(.)、下划线(_)，首字母必须是字母，长度小于30个字符'),
                            delay: 5000
                        })
                        return false
                    }

                    const keyObj = {}
                    for (const item of this.configmapKeyList) {
                        if (!keyObj[item.key]) {
                            keyObj[item.key] = true
                        } else {
                            this.$bkMessage({
                                theme: 'error',
                                message: this.$t('键不可重复'),
                                delay: 5000
                            })
                            data.isEdit = false
                            return false
                        }
                    }
                }
                this.curKeyParams = this.configmapKeyList[index]
                this.curKeyIndex = index
                data.isEdit = false
            },

            /**
             * 删除key
             * @param  {Object} data data
             * @param  {Number} index 索引
             */
            removeKey (data, index) {
                if (this.curKeyIndex > index) {
                    this.curKeyIndex = this.curKeyIndex - 1
                } else if (this.curKeyIndex === index) {
                    this.curKeyIndex = 0
                }
                this.configmapKeyList.splice(index, 1)
                this.curKeyParams = this.configmapKeyList[this.curKeyIndex]
            },

            /**
             * 编辑key
             * @param  {Object} data data
             * @param  {Number} index 索引
             */
            editKey (data, index) {
                data.isEdit = true
            },

            /**
             * 选择当前key
             * @param  {Object} data data
             * @param  {Number} index 索引
             */
            setCurKey (data, index) {
                this.curKeyParams = data
                this.curKeyIndex = index
            },

            /**
             * 编辑key
             * @param  {Object} data data
             * @param  {Number} index 索引
             */
            initKeyList (configmap) {
                const list = []
                if (this.currentView === 'k8sService') {
                    const k8sConfigmapData = configmap.data.data
                    for (const [key, value] of Object.entries(k8sConfigmapData)) {
                        list.push({
                            key: key,
                            isEdit: false,
                            content: value
                        })
                    }
                } else {
                    const mesosConfigmapData = configmap.data.datas
                    for (const [key, value] of Object.entries(mesosConfigmapData)) {
                        list.push({
                            key: key,
                            isEdit: false,
                            content: value.content,
                            type: value.type
                        })
                    }
                }
                this.curKeyIndex = 0
                if (list.length) {
                    this.curKeyParams = list[0]
                } else {
                    this.curKeyParams = null
                }
                this.configmapKeyList.splice(0, this.configmapKeyList.length, ...list)
            },

            /**
             * 展示configmap详情
             * @param  {Object} configmap configmap
             * @param  {Number} index 索引
             */
            async showConfigmapDetail (configmap, index) {
                if (!configmap.permissions.view) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: configmap.namespace_id,
                        resource_name: configmap.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.configmapSlider.title = configmap.resourceName
                this.curConfigmap = configmap
                this.configmapSlider.isShow = true
            },

            showKeyValue () {
                this.isShowKeyValue = !this.isShowKeyValue
            },

            /**
             * 加载configmap列表数据
             */
            async getConfigmapList () {
                const projectId = this.projectId
                try {
                    await this.$store.dispatch('resource/getConfigmapList', projectId)
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)
                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchScope || this.searchKeyword) {
                        this.searchConfigmap()
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                    clearTimeout(this.configmapTimer)
                    this.configmapTimer = null
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
                this.searchConfigmap()
            },

            /**
             * 搜索configmap
             */
            searchConfigmap () {
                const keyword = this.searchKeyword.trim()
                const keyList = ['resourceName', 'namespace', 'cluster_id']
                let list = JSON.parse(JSON.stringify(this.$store.state.resource.configmapList))
                let results = []
                this.pageConf.curPage = 1
                this.isPageLoading = true

                if (this.searchScope) {
                    list = list.filter(item => {
                        return item.cluster_id === this.searchScope
                    })
                }

                if (keyword) {
                    clearTimeout(this.configmapTimer)

                    list.forEach(item => {
                        item.isChecked = false
                        for (const key of keyList) {
                            if (item[key].indexOf(keyword) > -1) {
                                results.push(item)
                                return true
                            }
                        }
                    })
                } else {
                    results = list
                }
                this.configmapList.splice(0, this.configmapList.length, ...results)
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.configmapList.length
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
                if (endIndex > this.configmapList.length) {
                    endIndex = this.configmapList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.configmapList.slice(startIndex, endIndex)
            },

            /**
             * 页数改变回调
             * @param  {number} page 第几页
             */
            pageChangeHandler (page = 1) {
                this.pageConf.curPage = page
                if (this.configmapTimer) {
                    this.getConfigmapList()
                } else {
                    const data = this.getDataByPage(page)
                    this.curPageData = data
                }
            },

            /**
             * 每行的多选框点击事件
             */
            rowClick () {
                this.$nextTick(() => {
                    this.alreadySelectedNums = this.configmapList.filter(item => item.isChecked).length
                })
            }
        }
    }
</script>

<style scoped>
    @import './configmap.css';
    .bk-spin-loading  {
        position: absolute;
        top: 28px;
        left: 48px;
    }
</style>
