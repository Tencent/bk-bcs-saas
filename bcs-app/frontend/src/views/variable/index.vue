<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-var-title">
                {{$t('变量管理')}}
            </div>
            <bk-guide></bk-guide>
        </div>
        <div class="biz-content-wrapper" style="margin: 0; padding: 0;" v-bkloading="{ isLoading: isLoading, opacity: 0.1 }">
            <template v-if="!isLoading">
                <div class="biz-panel-header">
                    <div class="left">
                        <button class="bk-button bk-primary" @click.stop.prevent="addVar">
                            <i class="bk-icon icon-plus"></i>
                            <span>{{$t('新增变量')}}</span>
                        </button>
                        <button class="bk-button bk-default" @click.stop.prevent="removeVars">
                            <span>{{$t('批量删除')}}</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            :search-placeholder="$t('请选择作用范围')"
                            @search="searchVar"
                            @refresh="refresh">
                        </bk-data-searcher>
                    </div>
                </div>
                <div class="biz-variable">
                    <div class="biz-table-wrapper" v-bkloading="{ isLoading: isPageLoading && !isLoading }">
                        <table class="bk-table biz-variable-table has-table-hover">
                            <thead>
                                <tr>
                                    <th style="width: 50px;">
                                        <label class="bk-form-checkbox">
                                            <input type="checkbox" name="check-all-user" v-model="isCheckCurPageAll" @click="toogleCheckCurPage" v-if="curPageData.filter(item => item.category !== 'sys').length">
                                            <input type="checkbox" v-else name="check-all-user" disabled="disabled" />
                                        </label>
                                    </th>
                                    <th style="width: 200px;">
                                        {{$t('变量名称')}}
                                    </th>
                                    <th>KEY</th>
                                    <th>{{$t('默认值')}}</th>
                                    <th style="width: 110px;">{{$t('类型')}}</th>
                                    <th style="width: 130px;">{{$t('作用范围')}}</th>
                                    <th style="width: 250px; "><span>{{$t('操作')}}</span></th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curPageData.length">
                                    <tr v-for="variable in curPageData" :key="variable.key">
                                        <td>
                                            <label class="bk-form-checkbox">
                                                <input type="checkbox" name="check-variable" v-model="variable.isChecked" @click="rowClick(variable)" :disabled="variable.category === 'sys'">
                                            </label>
                                        </td>
                                        <td class="biz-table-title">
                                            {{variable.name}}
                                        </td>
                                        <td>
                                            <bk-tooltip :content="variable.key" placement="top">
                                                <span class="biz-text-wrapper">
                                                    {{variable.key}}
                                                </span>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="variable.default.value" placement="top">
                                                <span class="var-value">{{variable.default.value}}</span>
                                            </bk-tooltip>
                                        </td>
                                        <td>{{variable.category_name}}</td>
                                        <td>{{variable.scope_name}}</td>
                                        <td>
                                            <a href="javascript:void(0);" class="bk-text-button" @click="getQuoteDetail(variable)">{{$t('查看引用')}}</a>
                                            <a href="javascript:void(0);" class="ml10 bk-text-button" @click="batchUpdate(variable)" v-show="variable.category !== 'sys' && (variable.scope === 'namespace' || variable.scope === 'cluster')">{{$t('批量更新')}}</a>

                                            <template v-if="variable.category === 'sys'">
                                                <bk-tooltip :content="$t('系统内置变量，不能编辑')" placement="left">
                                                    <a href="javascript:void(0);" class="bk-text-button is-disabled ml10">{{$t('编辑')}}</a>
                                                </bk-tooltip>
                                            </template>
                                            <template v-else>
                                                <a href="javascript:void(0);" class=" ml10 bk-text-button" @click="editVar(variable)">{{$t('编辑')}}</a>
                                            </template>

                                            <template v-if="variable.category === 'sys'">
                                                <bk-tooltip :content="variable.category === 'sys' ? $t('系统内置变量') : $t('已经被引用，不能删除')" placement="left">
                                                    <a href="javascript:void(0);" class="ml10 bk-text-button is-disabled">{{$t('删除')}}</a>
                                                </bk-tooltip>
                                            </template>
                                            <template v-else>
                                                <a href="javascript:void(0);" class="ml10 bk-text-button" @click="removeVar(variable)">{{$t('删除')}}</a>
                                            </template>
                                        </td>
                                    </tr>
                                </template>
                                <template v-else>
                                    <tr style="background: none;">
                                        <td colspan="8">
                                            <div class="bk-message-box">
                                                <p class="message empty-message" v-if="!isLoading">{{$t('无数据')}}</p>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                    <div class="biz-page-wrapper" v-show="pageConf.total">
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
                        <div class="already-selected-nums" v-if="alreadySelectedNums">{{$t('已选')}} {{alreadySelectedNums}} {{$t('条')}}</div>
                    </div>
                </div>
            </template>
        </div>

        <bk-sideslider
            :is-show.sync="batchUpdateConf.isShow"
            :title="batchUpdateConf.title"
            :width="batchUpdateConf.width">
            <div style="padding: 20px 20px 10px 20px;" slot="content" v-bkloading="{ isLoading: isBatchVarLoading }">
                <table class="bk-table biz-data-table has-table-bordered">
                    <thead>
                        <tr>
                            <th v-if="curBatchVar && curBatchVar.scope === 'namespace'" style="width: 250px;">{{$t('所属')}}{{$t('集群')}}</th>
                            <th style="min-width: 200px;">{{$t('所属')}}{{curBatchVar && curBatchVar.scope === 'namespace' ? $t('命名空间') : $t('集群')}}</th>
                            <th>值</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-if="batchVarList.length">
                            <tr v-for="(variable, index) in batchVarList" :key="index">
                                <td v-if="curBatchVar && curBatchVar.scope === 'namespace'">{{variable.cluster_name}}</td>
                                <td>{{variable.name}}</td>
                                <td><input type="text" class="bk-form-input" v-model="variable.variable_value"></td>
                            </tr>
                        </template>
                        <template v-else>
                            <tr>
                                <td colspan="2"><p style="padding: 10px; text-align: center;">{{$t('无数据')}}</p></td>
                            </tr>
                        </template>
                    </tbody>
                </table>
                <div v-if="batchVarList.length">
                    <button class="bk-button bk-primary" @click="saveBatchVar">{{$t('保存')}}</button>
                    <button class="bk-button bk-default" @click="cancelBatchVar">{{$t('取消')}}</button>
                </div>
            </div>
        </bk-sideslider>

        <bk-dialog
            :is-show="batchDialogConfig.isShow"
            :width="400"
            :has-header="false"
            :quick-close="false"
            @confirm="deleteVar(batchDialogConfig.removeIds)"
            @cancel="batchDialogConfig.isShow = false">
            <div slot="content">
                <div class="biz-batch-wrapper">
                    <p class="batch-title">{{$t('确定要删除以下变量？')}}</p>
                    <ul class="batch-list">
                        <li v-for="(item, index) of batchDialogConfig.list" :key="index">{{item}}</li>
                    </ul>
                </div>
            </div>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="varDialogConfig.isShow"
            :width="varDialogConfig.width"
            :title="varDialogConfig.title"
            :quick-close="false"
            @cancel="varDialogConfig.isShow = false">
            <div slot="content" v-bkloading="{ isLoading: isSaving }">
                <div class="content-inner">
                    <div class="bk-form" style="margin-bottom: 20px; margin-right: 10px;">
                        <div class="bk-form-item">
                            <label class="bk-label" style="width: 95px;">{{$t('作用范围')}}：</label>
                            <div class="bk-form-content" style="margin-left: 95px;">
                                <label class="bk-form-radio">
                                    <input type="radio" value="global" name="scope" v-model="curVar.scope" :disabled="curVar.quote_num !== undefined && curVar.quote_num > 0">
                                    <i class="bk-radio-text">{{$t('全局变量')}}</i>
                                </label>
                                <label class="bk-form-radio">
                                    <input type="radio" value="cluster" name="scope" v-model="curVar.scope" :disabled="curVar.quote_num !== undefined && curVar.quote_num > 0">
                                    <i class="bk-radio-text">{{$t('集群变量')}}</i>
                                </label>
                                <label class="bk-form-radio" style="margin-right: 0;">
                                    <input type="radio" value="namespace" name="scope" v-model="curVar.scope" :disabled="curVar.quote_num !== undefined && curVar.quote_num > 0">
                                    <i class="bk-radio-text">{{$t('命名空间变量')}}</i>
                                </label>
                            </div>
                        </div>
                        <div class="bk-form-item is-required">
                            <label class="bk-label" style="width: 95px;">{{$t('名称')}}：</label>
                            <div class="bk-form-content" style="margin-left: 95px;">
                                <input type="text"
                                    maxlength="32"
                                    :class="['bk-form-input']"
                                    :placeholder="$t('请输入32个字符以内的名称')"
                                    v-model="curVar.name">
                            </div>
                        </div>
                        <div class="bk-form-item is-required">
                            <label class="bk-label" style="width: 95px;">KEY：</label>
                            <div class="bk-form-content" style="margin-left: 95px;">
                                <input type="text"
                                    :disabled="curVar.quote_num !== undefined && curVar.quote_num > 0"
                                    :class="['bk-form-input']"
                                    maxlength="64"
                                    :placeholder="$t('请输入')"
                                    v-model="curVar.key">
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label" style="width: 95px;">{{$t('默认值')}}：</label>
                            <div class="bk-form-content" style="margin-left: 95px;">
                                <input type="text"
                                    :class="['bk-form-input']"
                                    :placeholder="$t('请输入')"
                                    v-model="curVar.default.value">
                            </div>
                        </div>
                        <div class="bk-form-item">
                            <label class="bk-label" style="width: 95px;">{{$t('说明')}}：</label>
                            <div class="bk-form-content" style="margin-left: 95px;">
                                <textarea maxlength="100" :class="['bk-form-textarea']" :placeholder="$t('请输入')" v-model="curVar.desc" style="height: 60px;"></textarea>
                                <p class="biz-tip" style="text-align: left; margin-top: 10px;">{{$t('您可以在模板集中使用')}} {{curVarKeyText}} {{$t('来引用该变量')}}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <template slot="footer">
                <div class="bk-dialog-outer">
                    <template v-if="isSaving">
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                            {{$t('提交')}}...
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                            {{$t('取消')}}
                        </button>
                    </template>
                    <template v-else>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                            @click="saveVar">
                            {{$t('提交')}}
                        </button>
                        <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="cancelVar">
                            {{$t('取消')}}
                        </button>
                    </template>
                </div>
            </template>
        </bk-dialog>

        <bk-dialog
            :is-show.sync="quoteDialogConf.isShow"
            :width="quoteDialogConf.width"
            :content="quoteDialogConf.content"
            :has-header="quoteDialogConf.hasHeader"
            :has-footer="false"
            :close-icon="quoteDialogConf.closeIcon"
            :ext-cls="'biz-var-quote-dialog'">
            <div slot="content">
                <div style="margin: -20px;">
                    <div class="bk-dialog-tool">
                        <i class="bk-dialog-close bk-icon icon-close" @click="hideQuoteDialog"></i>
                    </div>
                    <div class="quote-title">
                        {{curVar.name}}
                    </div>
                    <div style="min-height: 150px;" v-bkloading="{ isLoading: isQuoteLoading }">
                        <table class="bk-table has-table-hover biz-table biz-var-quote-table" :style="{ borderBottomWidth: curQuotePageData.length ? '1px' : 0 }" v-show="!isQuoteLoading">
                            <thead>
                                <tr>
                                    <th style="padding-left: 30px;">{{$t('被引用位置')}}</th>
                                    <th style="width: 150px;">{{$t('上下文')}}</th>
                                    <th style="width: 120px;">{{$t('操作')}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="curQuotePageData.length">
                                    <tr v-for="(quote, index) in curQuotePageData" :key="index">
                                        <td style="padding-left: 30px;">
                                            {{quote.quote_location}}
                                        </td>
                                        <td>
                                            {{quote.context}}
                                        </td>
                                        <td>
                                            <a href="javascript:void(0)" class="bk-text-button" @click="checkVarQuote(quote)">{{$t('查看详情')}}</a>
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
                    <div class="biz-page-box" v-if="!isQuoteLoading && quotePageConf.show && curQuotePageData.length">
                        <bk-paging
                            :size="'small'"
                            :cur-page.sync="quotePageConf.curPage"
                            :total-page="quotePageConf.totalPage"
                            @page-change="quotePageChange">
                        </bk-paging>
                    </div>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>

<script>
    import { catchErrorHandler } from '@open/common/util'

    export default {
        data () {
            return {
                varScoped: {
                    global: this.$t('全局变量'),
                    namespace: this.$t('命名空间变量'),
                    cluster: this.$t('集群变量')
                },
                curProjectData: null,
                isQuoteLoading: true,
                curAllSelectedData: [],
                curQuotePageData: [],
                quoteList: [],
                batchVarList: [],
                pageConf: {
                    total: 0,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1
                },
                batchDialogConfig: {
                    isShow: false,
                    list: [],
                    removeIds: []
                },
                quotePageConf: {
                    totalPage: 1,
                    pageSize: 5,
                    curPage: 1,
                    show: true
                },
                curPageData: [],
                searchKeyword: '',
                searchScope: '',
                varDialogConfig: {
                    isShow: false,
                    width: 640,
                    title: this.$t('新增变量')
                },
                isBatchVarLoading: false,
                batchUpdateConf: {
                    isShow: false,
                    title: '',
                    width: 690
                },
                quoteDialogConf: {
                    isShow: false,
                    width: 690,
                    hasHeader: false,
                    closeIcon: false
                },
                curBatchVar: null,
                curVar: {
                    name: '',
                    key: '',
                    default: {
                        value: ''
                    },
                    desc: '',
                    scope: 'global'
                },
                isLoading: true,
                isPageLoading: false,
                isSaving: false,
                searchScopeList: [
                    {
                        id: '',
                        name: this.$t('全部作用范围')
                    },
                    {
                        id: 'global',
                        name: this.$t('全局变量')
                    },
                    {
                        id: 'cluster',
                        name: this.$t('集群变量')
                    },
                    {
                        id: 'namespace',
                        name: this.$t('命名空间变量')
                    }
                ],
                alreadySelectedNums: 0
            }
        },
        computed: {
            isEn () {
                return this.$store.state.isEn
            },
            projectId () {
                return this.$route.params.projectId
            },
            varList () {
                return JSON.parse(JSON.stringify(this.$store.state.variable.varList))
            },
            curVarKeyText () {
                return `{{${this.curVar.key || this.$t('变量KEY')}}}`
            }
        },
        mounted () {
            this.getDataByPage()
        },
        methods: {
            /**
             * 刷新列表
             */
            refresh () {
                this.pageConf.curPage = 1
                this.isPageLoading = true
                this.getDataByPage()
            },

            /**
             * 分页大小更改
             *
             * @param {number} pageSize pageSize
             */
            changePageSize (pageSize) {
                this.pageConf.pageSize = pageSize
                this.pageConf.curPage = 1
                this.getDataByPage()
            },

            /**
             * 显示新增变量窗口
             */
            addVar () {
                this.isSaving = false
                this.clearInput()
                this.varDialogConfig.title = this.$t('新增变量')
                this.varDialogConfig.isShow = true
            },

            /**
             * 取消批量删除
             */
            cancelBatchVar () {
                this.batchUpdateConf.isShow = false
            },

            /**
             * 获取对应变量所有命名空间变量列表
             *
             * @param  {Object} data 变量
             */
            async batchUpdate (data) {
                this.curBatchVar = data
                const projectId = this.projectId
                const variableId = data.id
                this.batchUpdateConf.isShow = true
                this.batchUpdateConf.title = data.name
                this.isBatchVarLoading = true

                const url = data.scope === 'namespace' ? 'variable/getNamespaceBatchVarList' : 'variable/getClusterBatchVarList'
                try {
                    const res = await this.$store.dispatch(url, { projectId, variableId })
                    this.batchVarList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isBatchVarLoading = false
                }
            },

            /**
             * 保存所有命名空间下变量
             */
            async saveBatchVar () {
                const projectId = this.projectId
                const varId = this.curBatchVar.id
                let url = 'variable/updateNamespaceBatchVar'
                let data = {}
                if (this.curBatchVar.scope === 'namespace') {
                    data = {
                        ns_vars: {}
                    }
                    this.batchVarList.forEach(item => {
                        data.ns_vars[item.namespace_id] = item.variable_value
                    })
                } else {
                    data = {
                        cluster_vars: {}
                    }
                    this.batchVarList.forEach(item => {
                        data.cluster_vars[item.cluster_id] = item.variable_value
                    })
                    url = 'variable/updateClusterBatchVar'
                }

                try {
                    await this.$store.dispatch(url, { projectId, varId, data })
                    this.$bkMessage({
                        theme: 'success',
                        message: this.$t('变量更新成功')
                    })
                    this.batchUpdateConf.isShow = false
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 编辑变量
             * @param  {Object} data 变量
             */
            editVar (data) {
                this.isSaving = false
                this.curVar = JSON.parse(JSON.stringify(data))
                this.varDialogConfig.title = this.$t('编辑变量')
                this.varDialogConfig.isShow = true
            },

            /**
             * 批量删除变量
             */
            removeVars () {
                const names = []
                const ids = []

                if (this.curAllSelectedData.length) {
                    this.curAllSelectedData.forEach(item => {
                        names.push(item.name)
                        ids.push(item.id)
                    })
                } else {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请选择要删除的变量')
                    })
                    return false
                }

                this.batchDialogConfig.list = names
                this.batchDialogConfig.removeIds = ids
                this.batchDialogConfig.isShow = true
            },

            /**
             * 删除变量
             *
             * @param {Object} data 变量
             */
            removeVar (data) {
                const self = this
                this.$bkInfo({
                    title: ``,
                    clsName: 'biz-remove-dialog',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确定要删除变量')}【${data.name}】?`),
                    confirmFn () {
                        self.deleteVar([data.id])
                    }
                })
            },

            /**
             * 取消提交
             */
            cancelVar () {
                this.clearInput()
                this.varDialogConfig.isShow = false
            },

            /**
             * 重置当前变量数据
             */
            clearInput () {
                this.curVar = {
                    'name': '',
                    'key': '',
                    'default': {
                        'value': ''
                    },
                    'desc': '',
                    'scope': 'global'
                }
            },

            /**
             * 是否全选
             */
            toogleCheckCurPage (e) {
                this.$nextTick(() => {
                    const isChecked = this.isCheckCurPageAll
                    this.curPageData.forEach(item => {
                        item.isChecked = item.category === 'sys' ? false : isChecked
                    })

                    const curAllSelectedData = []
                    curAllSelectedData.splice(0, 0, ...this.curAllSelectedData)
                    // 用于区分是否已经选择过
                    const hasCheckedList = curAllSelectedData.map(item => item.id)
                    if (isChecked) {
                        const checkedList = this.curPageData.filter(
                            item => item.category !== 'sys' && !hasCheckedList.includes(item.id)
                        )
                        curAllSelectedData.push(...checkedList)
                        this.curAllSelectedData.splice(0, this.curAllSelectedData.length, ...curAllSelectedData)
                    } else {
                        // 当前页所有合法的 variable id 集合
                        const validIdList = this.curPageData.filter(
                            item => item.category !== 'sys'
                        ).map(item => item.id)

                        const newCurAllSelectedData = []
                        this.curAllSelectedData.forEach(checkedVariable => {
                            if (validIdList.indexOf(checkedVariable.id) < 0) {
                                newCurAllSelectedData.push(JSON.parse(JSON.stringify(checkedVariable)))
                            }
                        })
                        this.curAllSelectedData.splice(0, this.curAllSelectedData.length, ...newCurAllSelectedData)
                    }

                    this.alreadySelectedNums = this.curAllSelectedData.length
                })
            },

            /**
             * 每行的多选框点击事件
             *
             * @param {Object} variable 当前变量对象即当前行
             */
            rowClick (variable) {
                this.$nextTick(() => {
                    // 当前页选中的
                    const checkedCurPageList = this.curPageData.filter(item => item.isChecked)
                    // 当前页合法的
                    const validList = this.curPageData.filter(item => item.category !== 'sys')
                    this.isCheckCurPageAll = checkedCurPageList.length === validList.length

                    const curAllSelectedData = []
                    if (variable.isChecked) {
                        curAllSelectedData.splice(0, curAllSelectedData.length, ...this.curAllSelectedData)
                        if (!this.curAllSelectedData.filter(checkedVariable => checkedVariable.id === variable.id).length) {
                            curAllSelectedData.push(variable)
                        }
                    } else {
                        this.curAllSelectedData.forEach(checkedVariable => {
                            if (checkedVariable.id !== variable.id) {
                                curAllSelectedData.push(JSON.parse(JSON.stringify(checkedVariable)))
                            }
                        })
                    }
                    this.curAllSelectedData.splice(0, this.curAllSelectedData.length, ...curAllSelectedData)
                    this.alreadySelectedNums = this.curAllSelectedData.length
                })
            },

            /**
             * 取消选择
             */
            clearSelectedVarList () {
                this.curPageData.forEach((item) => {
                    item.isChecked = false
                })
            },

            /**
             * 初始化变量列表
             */
            async getVarList (offset, limit) {
                const projectId = this.projectId
                const keyword = this.searchKeyword
                const scope = this.searchScope
                try {
                    const res = await this.$store.dispatch('variable/getVarListByPage', { projectId, offset, limit, keyword, scope })

                    this.searchKeyWord = ''
                    this.pageConf.total = res.count
                    this.curPageData = res.results

                    const checkVariableIdList = this.curAllSelectedData.map(variable => variable.id)
                    this.curPageData.forEach(item => {
                        if (item.category !== 'sys') {
                            item.isChecked = checkVariableIdList.indexOf(item.id) > -1
                        }
                    })

                    // 当前页选中的
                    const checkedCurPageList = this.curPageData.filter(item => item.isChecked === true)
                    // 当前页合法的
                    const validList = this.curPageData.filter(item => item.category !== 'sys')
                    this.isCheckCurPageAll = validList.length === 0
                        ? false
                        : checkedCurPageList.length === validList.length

                    this.initPageConf()
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    // 晚消失是为了防止整个页面loading和表格数据loading效果叠加产生闪动
                    setTimeout(() => {
                        this.isLoading = false
                        this.isPageLoading = false
                    }, 200)
                }
            },

            /**
             * 搜索变量
             */
            searchVar () {
                this.getDataByPage()
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                this.pageConf.totalPage = Math.ceil(this.pageConf.total / this.pageConf.pageSize)
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
                if (this.pageConf.curPage === 0) {
                    this.pageConf.curPage = 1
                }
            },

            /**
             * 加载当前前页数据
             */
            reloadCurPage () {
                this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 获取相应页变量数据
             *
             * @param {Number} page 页
             */
            getDataByPage (page = 1) {
                const offset = (page - 1) * this.pageConf.pageSize
                const limit = this.pageConf.pageSize
                this.isPageLoading = true
                this.getVarList(offset, limit)
            },

            /**
             * 页改变
             */
            pageChange (page = 1) {
                this.pageConf.curPage = page
                this.getDataByPage(page)
            },

            /**
             * 初始化变量引用分页配置
             */
            initQuotePageConf () {
                const total = this.quoteList.length
                this.quotePageConf.totalPage = Math.ceil(total / this.quotePageConf.pageSize)
            },

            /**
             * 加载变量引用当前页数据
             */
            reloadQuoteCurPage () {
                this.initQuotePageConf()
                if (this.quotePageConf.curPage > this.quotePageConf.totalPage) {
                    this.quotePageConf.curPage = this.quotePageConf.totalPage
                }
                this.curQuotePageData = this.getDataByPage(this.quotePageConf.curPage)
            },

            /**
             * 获取相应页的变量引用数据
             *
             * @param {Number} page 页
             */
            getQuoteDataByPage (page) {
                let startIndex = (page - 1) * this.quotePageConf.pageSize
                let endIndex = page * this.quotePageConf.pageSize
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.quoteList.length) {
                    endIndex = this.quoteList.length
                }
                const data = this.quoteList.slice(startIndex, endIndex)
                return data
            },

            quotePageChange (page) {
                this.quotePageConf.curPage = page
                const data = this.getQuoteDataByPage(page)
                this.curQuotePageData = JSON.parse(JSON.stringify(data))
            },

            /**
             * 检查提交的变量数据
             */
            checkData () {
                if (!this.curVar.name) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入变量名称')
                    })
                    return false
                }

                if (this.curVar.name.length > 32) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入32个字符以内的变量名称')
                    })
                    return false
                }

                if (!this.curVar.key) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入变量KEY')
                    })
                    return false
                }

                const keyReg = /^[A-Za-z][A-Za-z0-9_]{0,63}$/
                if (!keyReg.test(this.curVar.key)) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('KEY 只能包含字母、数字和下划线，且以字母开头，最大长度为64个字符')
                    })
                    return false
                }
                return true
            },

            /**
             * 提交变量数据
             */
            saveVar () {
                if (!this.checkData()) {
                    return false
                }
                if (this.curVar.id) {
                    this.updateVar()
                } else {
                    this.newVar()
                }
            },

            /**
             * 提交新增的变量
             */
            async newVar () {
                this.isSaving = true
                const projectId = this.projectId
                const data = JSON.parse(JSON.stringify(this.curVar))

                try {
                    const res = await this.$store.dispatch('variable/addVar', { projectId, data })
                    if (res.code === 0) {
                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('变量创建成功')
                        })
                        this.clearInput()
                        this.varDialogConfig.isShow = false
                        this.getDataByPage()

                        this.pageConf.curPage = 1
                        this.isCheckCurPageAll = false
                        this.curAllSelectedData.splice(0, this.curAllSelectedData.length, ...[])
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.isSaving = false
                }
            },

            /**
             * 提交更新的变量
             */
            async updateVar () {
                this.isSaving = true
                const projectId = this.projectId
                const data = JSON.parse(JSON.stringify(this.curVar))
                const varId = data.id

                try {
                    const res = await this.$store.dispatch('variable/updateVar', { projectId, varId, data })
                    if (res.code === 0) {
                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('变量更新成功')
                        })
                        this.clearInput()
                        this.varDialogConfig.isShow = false
                        this.getDataByPage()

                        this.pageConf.curPage = 1
                        this.isCheckCurPageAll = false
                        this.curAllSelectedData.splice(0, this.curAllSelectedData.length, ...[])
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.isSaving = false
                }
            },

            /**
             * 删除变量
             * @param {Array} ids 变量id列表
             */
            async deleteVar (ids) {
                this.isSaving = true
                this.batchDialogConfig.isShow = false
                const projectId = this.projectId
                const data = {
                    id_list: JSON.stringify(ids)
                }
                this.isPageLoading = true

                try {
                    const res = await this.$store.dispatch('variable/deleteVar', { projectId, data })
                    if (res.code === 0) {
                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('变量删除成功')
                        })
                        this.getDataByPage()

                        this.pageConf.curPage = 1
                        this.isCheckCurPageAll = false
                        this.curAllSelectedData.splice(0, this.curAllSelectedData.length, ...[])
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.isPageLoading = false
                }
            },

            /**
             * 获取相应变量的引用列表
             * @param  {Object} variable 变量
             */
            async getQuoteDetail (variable) {
                const projectId = this.projectId
                const varId = variable.id
                this.curVar = variable
                this.isQuoteLoading = true
                this.quoteDialogConf.isShow = true
                this.quoteList = []
                this.curQuotePageData = []

                try {
                    const res = await this.$store.dispatch('variable/getQuoteDetail', { projectId, varId })
                    this.quoteList = res.data.quote_list
                    this.curProjectData = {
                        projectId: res.data.project_id,
                        projectCode: res.data.project_code,
                        projectKind: res.data.project_kind
                    }
                    this.quotePageConf.curPage = 1
                    this.initQuotePageConf()
                    this.curQuotePageData = this.getQuoteDataByPage(this.quotePageConf.curPage)
                    this.isQuoteLoading = false
                } catch (e) {
                    catchErrorHandler(e, this)
                    this.isQuoteLoading = false
                }
            },

            /**
             * 查看变量引用详情
             *
             * @param {Object} quote 引用
             */
            async checkVarQuote (quote) {
                if (this.curProjectData) {
                    if (!quote.permissions.view) {
                        await this.$store.dispatch('getResourcePermissions', {
                            project_id: this.projectId,
                            policy_code: 'view',
                            resource_code: quote.template_id,
                            resource_name: quote.template_name,
                            resource_type: 'templates'
                        })
                    }

                    let routeName = ''
                    const type = quote.category
                    if (this.curProjectData.projectKind === 1) {
                        const k8sRoutes = {
                            'K8sDeployment': 'k8sTemplatesetDeployment',
                            'K8sService': 'k8sTemplatesetService',
                            'K8sConfigMap': 'k8sTemplatesetConfigmap',
                            'K8sSecret': 'k8sTemplatesetSecret',
                            'K8sDaemonSet': 'k8sTemplatesetDaemonset',
                            'K8sStatefulSet': 'k8sTemplatesetStatefulset',
                            'K8sJob': 'k8sTemplatesetJob',
                            'K8sIngress': 'k8sTemplatesetIngress'
                        }

                        routeName = k8sRoutes[type]
                    } else if (this.curProjectData.projectKind === 2) {
                        const mesosRoutes = {
                            'application': 'mesosTemplatesetApplication',
                            'deployment': 'mesosTemplatesetDeployment',
                            'service': 'mesosTemplatesetService',
                            'configmap': 'mesosTemplatesetConfigmap',
                            'secret': 'mesosTemplatesetSecret'
                        }
                        routeName = mesosRoutes[type]
                    }
                    if (routeName) {
                        this.$router.push({
                            name: routeName,
                            params: {
                                projectId: this.curProjectData.projectId,
                                projectCode: this.curProjectData.projectCode,
                                templateId: quote.template_id
                            }
                        })
                    }
                }
            },

            hideQuoteDialog () {
                this.quoteDialogConf.isShow = false
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
