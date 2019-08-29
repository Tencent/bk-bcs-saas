<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-topbar-title">
                Secrets
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
                        <button class="bk-button bk-default" @click.stop.prevent="removeSecrets" v-if="curPageData.length">
                            <span>批量删除</span>
                        </button>
                    </div>
                    <div class="right">
                        <bk-data-searcher
                            :placeholder="'输入名称或命名空间，按Enter搜索'"
                            :scope-list="searchScopeList"
                            :search-key.sync="searchKeyword"
                            :search-scope.sync="searchScope"
                            @search="searchSecret"
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
                                            <input type="checkbox" name="check-all-user" :checked="isCheckCurPageAll" @click="toggleCheckCurPage" :disabled="!secretList.length">
                                        </label>
                                    </th>
                                    <th style="width: 300px;">名称</th>
                                    <th style="width: 300px;">所属集群</th>
                                    <th style="width: 300px;">命名空间</th>
                                    <th style="width: 150px">来源</th>
                                    <th style="width: 300px;">创建时间</th>
                                    <th style="width: 300px;">更新时间</th>
                                    <th style="width: 300px;">更新人</th>
                                    <th style="width: 100px">操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template v-if="secretList.length">
                                    <tr v-for="(secret, index) in curPageData" :key="index">
                                        <td style="position: relative;">
                                            <label class="bk-form-checkbox">
                                                <input
                                                    type="checkbox"
                                                    name="check-variable"
                                                    :disabled="!secret.can_delete || !secret.permissions.use"
                                                    v-model="secret.isChecked"
                                                    @click="rowClick" />
                                            </label>
                                            <div class="bk-spin-loading bk-spin-loading-mini bk-spin-loading-warning" v-if="secret.status === 'updating'">
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
                                            <a href="javascript: void(0)" class="bk-text-button biz-table-title biz-text-wrapper biz-resource-title" @click.stop.prevent="showSecretDetail(secret, index)">{{secret.resourceName}}</a>
                                        </td>
                                        <td>
                                            <bk-tooltip :content="secret.cluster_id || '--'" placement="top">
                                                <p class="biz-text-wrapper">{{secret.cluster_name ? secret.cluster_name : '--'}}</p>
                                            </bk-tooltip>
                                        </td>
                                        <td>
                                            {{secret.namespace}}
                                        </td>
                                        <td>
                                            {{secret.source_type}}
                                        </td>
                                        <td>
                                            {{formatDate(secret.createTime)}}
                                        </td>
                                        <td>
                                            {{formatDate(secret.update_time) || '--'}}
                                        </td>
                                        <td>
                                            {{secret.updator || '--'}}
                                        </td>
                                        <td>
                                            <li style="width: 100px;">
                                                <span v-if="secret.can_update" @click.stop="updateSecret(secret)" class="biz-operate">更新</span>
                                                <bk-tooltip :content="secret.can_update_msg" v-else placement="left">
                                                    <span class="biz-not-operate">更新</span>
                                                </bk-tooltip>
                                                <span v-if="secret.can_delete" @click.stop="removeSecret(secret)" class="biz-operate">删除</span>
                                                <bk-tooltip :content="secret.can_delete_msg || '不可删除'" v-else placement="left">
                                                    <span class="biz-not-operate">删除</span>
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
                v-if="curSecret"
                :quick-close="true"
                :is-show.sync="secretSlider.isShow"
                :title="secretSlider.title"
                :width="'640'">
                <div class="p30" slot="content">
                    <table class="bk-table biz-data-table has-table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 270px;">键</th>
                                <th>值<a href="javascript:void(0)" v-if="curSecretKeyList.length" class="bk-text-button display-text-btn" @click.stop.prevent="showKeyValue">{{isShowKeyValue ? '隐藏' : '明文显示'}}</a></th>
                            </tr>
                        </thead>
                        <tbody>
                            <template v-if="curSecretKeyList.length">
                                <tr v-for="(item, index) in curSecretKeyList" :key="index">
                                    <td>{{item.key}}</td>
                                    <td>
                                        <textarea v-if="isShowKeyValue" readonly :title="item.value" class="bk-form-textarea  key-box" v-model="item.value"></textarea>
                                        <span v-else>******</span>
                                    </td>
                                </tr>
                            </template>
                            <template v-else>
                                <tr>
                                    <td colspan="2"><p class="biz-no-data">无数据</p></td>
                                </tr>
                            </template>
                        </tbody>
                    </table>

                    <div class="actions">
                        <button class="show-labels-btn bk-button bk-button-small bk-primary">显示标签</button>
                    </div>

                    <div class="point-box">
                        <template v-if="curSecret.labels.length">
                            <ul class="key-list">
                                <li v-for="(label, index) in curSecret.labels" :key="index">
                                    <span class="key">{{label[0]}}</span>
                                    <span class="value">{{label[1]}}</span>
                                </li>
                            </ul>
                        </template>
                        <template v-else>
                            <p class="biz-no-data">无数据</p>
                        </template>
                    </div>
                </div>
            </bk-sideslider>

            <bk-sideslider
                :quick-close="false"
                :is-show.sync="addSlider.isShow"
                :title="addSlider.title"
                :width="'800'">
                <div class="p30 bk-resource-secret" slot="content">
                    <div v-bkloading="{ isLoading: isUpdateLoading }">
                        <div class="bk-form-item">
                            <div class="bk-form-item" style="margin-bottom: 20px;">
                                <label class="bk-label">名称：</label>
                                <div class="bk-form-content" style="margin-left: 105px;">
                                    <input
                                        type="text"
                                        class="bk-form-input"
                                        name="curSecretName"
                                        disabled="disabled"
                                        style="min-width: 310px; cursor: not-allowed;"
                                        v-model="curSecretName" />
                                </div>
                            </div>
                            <label class="bk-label">键：</label>
                            <div class="bk-form-content" style="margin-left: 105px;">
                                <div class="biz-list-operation">
                                    <div class="item" v-for="(data, index) in secretKeyList" :key="index">
                                        <button :class="['bk-button', { 'bk-primary': curKeyIndex === index }]" @click.stop.prevent="setCurKey(data, index)" v-if="!data.isEdit">
                                            {{data.key || '未命名'}}
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
                                    <bk-tooltip ref="keyTooltip" :content="'添加Key'" placement="top">
                                        <button class="bk-button bk-default is-outline is-icon" @click.stop.prevent="addKey">
                                            <i class="bk-icon icon-plus"></i>
                                        </button>
                                    </bk-tooltip>
                                </div>
                            </div>
                        </div>
                        <template v-if="curKeyParams">
                            <div class="bk-form-item" style="margin-top: 13px;">
                                <label class="bk-label">值：</label>
                                <div class="bk-form-content" style="margin-left: 105px;">
                                    <textarea class="bk-form-textarea" style="height: 200px;" v-model="curKeyParams.content" :placeholder="'请输入键' + curKeyParams.key + '的内容'"></textarea>
                                </div>
                                <label style="margin-left: 105px; font-size: 14px; color: #c3cdd7;">实例化时会将值的内容做base64编码</label>
                            </div>
                        </template>
                        <div class="action-inner" style="margin-top: 20px; margin-left: 105px;">
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="submitUpdateSecret">
                                保存
                            </button>
                            <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="cancleUpdateSecret">
                                取消
                            </button>
                        </div>
                    </div>
                </div>
            </bk-sideslider>

            <bk-dialog
                :is-show="batchDialogConfig.isShow"
                :width="400"
                :has-header="false"
                :quick-close="false"
                @confirm="deleteSecrets(batchDialogConfig.data)"
                @cancel="batchDialogConfig.isShow = false">
                <div slot="content">
                    <div class="biz-batch-wrapper">
                        <p class="batch-title">确定要删除以下Secret？</p>
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
    import { catchErrrorHandler, formatDate } from '@open/common/util'
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
                curSecret: null,
                curPageData: [],
                isShowKeyValue: false,
                pageConf: {
                    total: 1,
                    totalPage: 1,
                    pageSize: 10,
                    curPage: 1,
                    show: true
                },
                secretSlider: {
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
                secretKeyList: [],
                curKeyIndex: 0,
                curKeyParams: null,
                curSecretName: '',
                namespaceId: 0,
                instanceId: 0,
                clusterId: '',
                namespace: '',
                isUpdateLoading: false,
                secretTimer: null,
                curProject: {},
                currentView: 'k8sService',
                isBatchRemoving: false,
                curSelectedData: [],
                alreadySelectedNums: 0
            }
        },
        computed: {
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
            secretList () {
                const list = this.$store.state.resource.secretList
                list.forEach(item => {
                    item.isChecked = false
                })
                return JSON.parse(JSON.stringify(list))
            },
            curSecretKeyList () {
                if (this.curSecret) {
                    const results = []
                    let data = {}

                    if (this.currentView === 'k8sService') {
                        data = this.curSecret.data.data

                        const keys = Object.keys(data)
                        keys.forEach(key => {
                            results.push({
                                key: key,
                                value: data[key]
                            })
                        })
                    } else {
                        data = this.curSecret.data.datas

                        const keys = Object.keys(data)
                        keys.forEach(key => {
                            results.push({
                                key: key,
                                value: data[key].content
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
                    name: '全部集群'
                })

                return results
            },
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            }
        },
        created () {
            this.getSecretList()
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
                this.getSecretList()
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
                    this.alreadySelectedNums = this.secretList.filter(item => item.isChecked).length
                })
            },

            /**
             * 清空选择
             */
            clearselectSecrets () {
                this.curPageData.forEach((item) => {
                    item.isChecked = false
                })
            },

            /**
             * 确认批量删除Secrets
             */
            async removeSecrets () {
                const data = []
                const names = []

                this.secretList.forEach(item => {
                    if (item.isChecked) {
                        data.push({
                            cluster_id: item.cluster_id,
                            namespace: item.namespace,
                            name: item.name
                        })
                        names.push(item.resourceName)
                    }
                })
                if (!data.length) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请选择要删除的Secret！'
                    })
                    return false
                }

                this.batchDialogConfig.list = names
                this.batchDialogConfig.data = data
                this.batchDialogConfig.isShow = true
            },

            /**
             * 删除secret
             * @param  {Object} data secret
             */
            async deleteSecrets (data) {
                const me = this
                const projectId = this.projectId

                this.batchDialogConfig.isShow = false
                this.isPageLoading = true
                try {
                    await this.$store.dispatch('resource/deleteSecrets', {
                        projectId,
                        data
                    })
                    this.$bkMessage({
                        theme: 'success',
                        message: '删除成功！'
                    })
                    setTimeout(() => {
                        me.getSecretList()
                    }, 500)
                } catch (e) {
                    // 4004，已经被删除过，但接口不能立即清除，再重新拉数据，防止重复删
                    if (e.code === 4004) {
                        setTimeout(() => {
                            me.getSecretList()
                        }, 500)
                    }
                    catchErrrorHandler(e, this)
                    this.isPageLoading = false
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
             * 更新secret
             * @param  {Object} secret secret
             */
            async updateSecret (secret) {
                if (!secret.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: secret.namespace_id,
                        resource_name: secret.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.addSlider.isShow = true
                this.isUpdateLoading = true
                this.addSlider.title = `更新${secret.name}`
                this.curSecretName = secret.name
                this.namespaceId = secret.namespace_id
                this.instanceId = secret.instance_id
                this.namespace = secret.namespace
                this.clusterId = secret.cluster_id

                try {
                    const res = await this.$store.dispatch('resource/updateSelectSecret', {
                        projectId: this.projectId,
                        namespace: this.namespace,
                        name: this.curSecretName
                    })
                    const SecretObj = res.data.data[0] || {}
                    this.initKeyList(SecretObj)
                } catch (e) {
                    catchErrrorHandler(e, this)
                } finally {
                    this.isUpdateLoading = false
                }
            },

            /**
             * 删除secret前的确认
             * @param  {Object} secret secret
             * @return {[type]}
             */
            async removeSecret (secret) {
                if (!secret.permissions.use) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: secret.namespace_id,
                        resource_name: secret.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                const me = this
                me.$bkInfo({
                    title: ``,
                    clsName: 'biz-remove-dialog',
                    content: me.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `确定要删除Secret【${secret.name}】？`),
                    confirmFn () {
                        me.deleteSecret(secret)
                    }
                })
            },

            /**
             * 删除secret
             * @param {Object} secret secret
             */
            async deleteSecret (Secret) {
                const me = this
                const projectId = me.projectId
                const clusterId = Secret.cluster_id
                const namespace = Secret.namespace
                const name = Secret.name

                this.isPageLoading = true
                try {
                    await me.$store.dispatch('resource/deleteSecret', {
                        projectId,
                        clusterId,
                        namespace,
                        name
                    })

                    me.$bkMessage({
                        theme: 'success',
                        message: '删除成功！'
                    })
                    setTimeout(() => {
                        me.getSecretList()
                    }, 500)
                } catch (e) {
                    catchErrrorHandler(e, this)
                    this.isPageLoading = false
                }
            },

            /**
             * 向服务器提交secret更新数据
             */
            async submitUpdateSecret () {
                const enity = {}
                enity.namespace_id = this.namespaceId
                enity.instance_id = this.instanceId
                enity.config = {}
                const oName = {
                    name: this.curSecretName
                }
                enity.config['metadata'] = oName
                const keyList = []
                const oKey = {}
                if (this.currentView === 'k8sService') {
                    const k8sList = this.secretKeyList
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
                                message: `键${aKey[i]}重复`
                            })
                            return
                        }
                    }
                    enity.config['data'] = oKey
                    enity.config['type'] = 'Opaque'
                } else {
                    const mesosList = this.secretKeyList
                    const mesosLength = mesosList.length
                    for (let i = 0; i < mesosLength; i++) {
                        const item = mesosList[i]
                        keyList.push(item.key)
                        oKey[item.key] = {
                            content: item.content
                        }
                    }
                    const aKey = keyList.sort()
                    for (let i = 0; i < aKey.length; i++) {
                        if (aKey[i] === aKey[i + 1]) {
                            this.bkMessageInstance = this.$bkMessage({
                                theme: 'error',
                                message: `键${aKey[i]}重复`
                            })
                            return
                        }
                    }
                    enity.config['datas'] = oKey
                }
                try {
                    this.isPageLoading = true
                    await this.$store.dispatch('resource/updateSingleSecret', {
                        projectId: this.projectId,
                        clusterId: this.clusterId,
                        namespace: this.namespace,
                        name: this.curSecretName,
                        data: enity
                    })
                    this.$bkMessage({
                        theme: 'success',
                        message: '更新成功！'
                    })
                    this.getSecretList()
                } catch (e) {
                    this.isPageLoading = false
                    catchErrrorHandler(e, this)
                } finally {
                    this.cancleUpdateSecret()
                }
            },

            /**
             * 取消更新secret
             */
            cancleUpdateSecret () {
                // 数据清空或恢复默认值
                this.addSlider.isShow = false
                this.isUpdateLoading = false
                this.secretKeyList.splice(0, this.secretKeyList.length, ...[])
                this.curKeyIndex = 0
                this.namespaceId = 0
                this.instanceId = 0
                this.curKeyParams = null
                this.curSecretName = ''
                this.namespace = ''
                this.clusterId = ''
            },

            /**
             * 添加key
             */
            addKey () {
                const index = this.secretKeyList.length + 1
                if (this.currentView === 'k8sService') {
                    this.secretKeyList.push({
                        key: 'key-' + index,
                        isEdit: false,
                        content: ''
                    })
                } else {
                    this.secretKeyList.push({
                        key: 'key-' + index,
                        isEdit: false,
                        type: 'file',
                        content: ''
                    })
                }
                this.curKeyParams = this.secretKeyList[index - 1]
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
                    data.key = 'key-' + this.secretKeyList.length
                } else {
                    const nameReg = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,254}$/
                    const varReg = /\{\{([^\{\}]+)?\}\}/g

                    if (!nameReg.test(data.key.replace(varReg, 'key'))) {
                        this.$bkMessage({
                            theme: 'error',
                            message: '键名错误，只能包含：字母、数字、连字符(-)、点(.)、下划线(_)，首字母必须是字母，长度小于30个字符',
                            delay: 5000
                        })
                        return false
                    }

                    const keyObj = {}
                    for (const item of this.secretKeyList) {
                        if (!keyObj[item.key]) {
                            keyObj[item.key] = true
                        } else {
                            this.$bkMessage({
                                theme: 'error',
                                message: '键不可重复',
                                delay: 5000
                            })
                            data.isEdit = false
                            return false
                        }
                    }
                }
                this.curKeyParams = this.secretKeyList[index]
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
                this.secretKeyList.splice(index, 1)
                this.curKeyParams = this.secretKeyList[this.curKeyIndex]
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
            initKeyList (secret) {
                const list = []
                if (this.currentView === 'k8sService') {
                    const k8sSecretData = secret.data.data
                    for (const [key, value] of Object.entries(k8sSecretData)) {
                        list.push({
                            key: key,
                            isEdit: false,
                            content: value
                        })
                    }
                } else {
                    const mesosSecretData = secret.data.datas
                    for (const [key, value] of Object.entries(mesosSecretData)) {
                        list.push({
                            key: key,
                            isEdit: false,
                            content: value.content
                        })
                    }
                }
                this.curKeyIndex = 0
                if (list.length) {
                    this.curKeyParams = list[0]
                } else {
                    this.curKeyParams = null
                }
                this.secretKeyList.splice(0, this.secretKeyList.length, ...list)
            },

            /**
             * 展示secret详情
             * @param  {Object} secret secret
             * @param  {Number} index 索引
             */
            async showSecretDetail (secret, index) {
                if (!secret.permissions.view) {
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: secret.namespace_id,
                        resource_name: secret.namespace,
                        resource_type: 'namespace'
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }

                this.secretSlider.title = secret.resourceName
                this.curSecret = secret
                this.secretSlider.isShow = true
            },

            showKeyValue () {
                this.isShowKeyValue = !this.isShowKeyValue
            },

            /**
             * 加载secret列表数据
             */
            async getSecretList () {
                const projectId = this.projectId

                try {
                    await this.$store.dispatch('resource/getSecretList', projectId)

                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.curPage)
                    // 如果有搜索关键字，继续显示过滤后的结果
                    if (this.searchScope || this.searchKeyword) {
                        this.searchSecret()
                    }
                } catch (e) {
                    catchErrrorHandler(e, this)
                    clearTimeout(this.secretTimer)
                    this.secretTimer = null
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
                this.searchSecret()
            },

            /**
             * 搜索secret
             */
            searchSecret () {
                const keyword = this.searchKeyword.trim()
                const keyList = ['resourceName', 'namespace', 'cluster_id']
                let list = JSON.parse(JSON.stringify(this.$store.state.resource.secretList))

                if (this.searchScope) {
                    list = list.filter(item => {
                        return item.cluster_id === this.searchScope
                    })
                }

                const results = list.filter(item => {
                    for (const key of keyList) {
                        if (item[key].indexOf(keyword) > -1) {
                            return true
                        }
                    }
                    return false
                })
                this.secretList.splice(0, this.secretList.length, ...results)
                this.pageConf.curPage = 1
                this.initPageConf()
                this.curPageData = this.getDataByPage(this.pageConf.curPage)
            },

            /**
             * 初始化分页配置
             */
            initPageConf () {
                const total = this.secretList.length
                this.pageConf.total = total
                this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
                if (this.pageConf.curPage > this.pageConf.totalPage) {
                    this.pageConf.curPage = this.pageConf.totalPage
                }
            },

            /**
             * 重新加载当面页数据
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
                if (endIndex > this.secretList.length) {
                    endIndex = this.secretList.length
                }
                setTimeout(() => {
                    this.isPageLoading = false
                }, 200)
                return this.secretList.slice(startIndex, endIndex)
            },

            /**
             * 页数改变回调
             * @param  {number} page 第几页
             */
            pageChangeHandler (page = 1) {
                this.pageConf.curPage = page
                if (this.secretTimer) {
                    this.getSecretList()
                } else {
                    const data = this.getDataByPage(page)
                    // this.curPageData = JSON.parse(JSON.stringify(data))
                    this.curPageData = data
                }
            },

            /**
             * 每行的多选框点击事件
             */
            rowClick () {
                this.$nextTick(() => {
                    this.alreadySelectedNums = this.secretList.filter(item => item.isChecked).length
                })
            }
        }
    }
</script>

<style scoped>
    @import './secret.css';
    .bk-spin-loading  {
        position: absolute;
        top: 28px;
        left: 48px;
    }
</style>
