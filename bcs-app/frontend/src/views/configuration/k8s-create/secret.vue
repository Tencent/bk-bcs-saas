<template>
    <div class="biz-content">
        <biz-header ref="commonHeader"
            @exception="exceptionHandler"
            @saveSecretSuccess="saveSecretSuccess"
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
                    <biz-tabs @tabChange="tabResource" ref="commonTab"></biz-tabs>
                    <div class="biz-tab-content" v-bkloading="{ isLoading: isTabChanging }">
                        <template v-if="!secrets.length">
                            <div class="biz-guide-box mt0">
                                <button class="bk-button bk-primary" @click.stop.prevent="addLocalSecret">
                                    <i class="bk-icon icon-plus"></i>
                                    <span style="margin-left: 0;">添加Secret</span>
                                </button>
                            </div>
                        </template>
                        <template v-else>
                            <div class="biz-configuration-topbar">
                                <div class="biz-list-operation">
                                    <div class="item" v-for="(secret, index) in secrets" :key="secret.id">
                                        <button :class="['bk-button', { 'bk-primary': curSecret.id === secret.id }]" @click.stop="setCurSecret(secret, index)">
                                            {{(secret && secret.config.metadata.name) || '未命名'}}
                                            <span class="biz-update-dot" v-show="secret.isEdited"></span>
                                        </button>
                                        <span class="bk-icon icon-close" @click.stop="removeSecret(secret, index)"></span>
                                    </div>

                                    <bk-tooltip ref="secretTooltip" :content="'添加Secret'" placement="top">
                                        <button class="bk-button bk-default is-outline is-icon" @click.stop="addLocalSecret">
                                            <i class="bk-icon icon-plus"></i>
                                        </button>
                                    </bk-tooltip>
                                </div>
                            </div>

                            <div class="biz-configuration-content" style="position: relative; margin-bottom: 105px;">
                                <div class="bk-form biz-configuration-form">
                                    <a href="javascript:void(0);" class="bk-text-button from-json-btn" @click.stop.prevent="showJsonPanel">导入YAML</a>

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

                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 105px;">名称：</label>
                                        <div class="bk-form-content" style="margin-left: 105px;">
                                            <input type="text" :class="['bk-form-input',{ 'is-danger': errors.has('secretName') }]" placeholder="请输入30个以内的字符" style="width: 310px;" maxlength="30" v-model="curSecret.config.metadata.name" name="secretName" v-validate="{ required: true, regex: /^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$/ }">
                                            <div class="bk-form-tip" v-if="errors.has('secretName')">
                                                <p class="bk-tip-text">名称必填，以小写字母或数字开头和结尾，只能包含：小写字母、数字、连字符(-)、点(.)</p>
                                            </div>
                                        </div>
                                    </div>
                                    <template>
                                        <div class="bk-form-item is-required">
                                            <label class="bk-label" style="width: 105px;">键：</label>
                                            <div class="bk-form-content" style="margin-left: 105px;">
                                                <div class="biz-list-operation">
                                                    <div class="item" v-for="(data, index) in curSecret.secretKeyList" :key="index">
                                                        <button :class="['bk-button', { 'bk-primary': curKeyIndex === index }]" @click.stop.prevent="setCurKey(data, index)" v-if="!data.isEdit">
                                                            {{data.key || '未命名'}}
                                                        </button>
                                                        <bk-input
                                                            type="text"
                                                            placeholder=""
                                                            v-else
                                                            style="width: 150px;"
                                                            :auto-focus="true"
                                                            :value.sync="data.key"
                                                            :list="varList"
                                                            @blur="setKey(data, index)">
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
                                            <div class="bk-form-item">
                                                <label class="bk-label" style="width: 105px;">值：</label>
                                                <div class="bk-form-content" style="margin-left: 105px;">
                                                    <textarea class="bk-form-textarea" style="height: 200px;" v-model="curKeyParams.content" :placeholder="'请输入键' + curKeyParams.key + '的内容'"></textarea>
                                                    <p class="biz-tip mt10 f14">实例化时会将值的内容做base64编码</p>
                                                </div>
                                            </div>
                                        </template>
                                    </template>
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
    import secretParams from '@open/json/k8s-secret.json'
    import ace from '@open/components/ace-editor'
    import header from './header.vue'
    import yamljs from 'js-yaml'
    import _ from 'lodash'
    import tabs from './tabs.vue'
    import mixinBase from '@open/mixins/configuration/mixin-base'
    import k8sBase from '@open/mixins/configuration/k8s-base'

    export default {
        components: {
            'biz-header': header,
            'biz-tabs': tabs,
            'ace': ace
        },
        mixins: [mixinBase, k8sBase],
        data () {
            return {
                isTabChanging: false,
                winHeight: 0,
                exceptionCode: null,
                isDataLoading: true,
                isDataSaveing: false,
                curSecretCache: Object.assign({}, secretParams),
                curSecret: secretParams,
                secretKeyList: [],
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
                    lang: 'yaml',
                    readOnly: false,
                    fullScreen: false,
                    value: '',
                    editor: null
                },
                yamlEditorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'yaml',
                    readOnly: false,
                    fullScreen: false,
                    value: '',
                    editor: null
                }
            }
        },
        computed: {
            varList () {
                return this.$store.state.variable.varList
            },
            isTemplateSaving () {
                return this.$store.state.k8sTemplate.isTemplateSaving
            },
            curTemplate () {
                return this.$store.state.k8sTemplate.curTemplate
            },
            curVersion () {
                return this.$store.state.k8sTemplate.curVersion
            },
            deployments () {
                return this.$store.state.k8sTemplate.deployments
            },
            services () {
                return this.$store.state.k8sTemplate.services
            },
            configmaps () {
                return this.$store.state.k8sTemplate.configmaps
            },
            secrets () {
                return this.$store.state.k8sTemplate.secrets
            },
            daemonsets () {
                return this.$store.state.k8sTemplate.daemonsets
            },
            jobs () {
                return this.$store.state.k8sTemplate.jobs
            },
            statefulsets () {
                return this.$store.state.k8sTemplate.statefulsets
            },
            projectId () {
                return this.$route.params.projectId
            },
            templateId () {
                return this.$route.params.templateId
            }
        },
        async beforeRouteLeave (to, form, next) {
            // 修改模板集信息
            // await this.$refs.commonHeader.saveTemplate()
            this.updateSecretDatas()
            next(true)
        },
        mounted () {
            this.$refs.commonHeader.initTemplate((data) => {
                this.initResource(data)
                this.isDataLoading = false
            })
            this.winHeight = window.innerHeight
        },
        methods: {
            exceptionHandler (exceptionCode) {
                this.isDataLoading = false
                this.exceptionCode = exceptionCode
            },
            setCurKey (data, index) {
                this.curKeyParams = data
                this.curKeyIndex = index
            },
            editKey (data, index) {
                data.isEdit = true
            },
            removeKey (data, index) {
                if (this.curKeyIndex > index) {
                    this.curKeyIndex = this.curKeyIndex - 1
                } else if (this.curKeyIndex === index) {
                    this.curKeyIndex = 0
                }
                this.curSecret.secretKeyList.splice(index, 1)
                this.curKeyParams = this.curSecret.secretKeyList[this.curKeyIndex]
            },
            setKey (data, index) {
                if (data.key === '') {
                    data.key = 'key-' + this.curSecret.secretKeyList.length
                } else {
                    const nameReg = /^[a-zA-Z{]{1}[a-zA-Z0-9-_.{}]{0,254}$/
                    if (!nameReg.test(data.key)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: '键名错误，只能包含：字母、数字、连字符(-)、点(.)、下划线(_)，首字母必须是字母，长度小于30个字符',
                            delay: 5000
                        })
                        return false
                    }

                    const keyObj = {}
                    for (const item of this.curSecret.secretKeyList) {
                        if (!keyObj[item.key]) {
                            keyObj[item.key] = true
                        } else {
                            this.$bkMessage({
                                theme: 'error',
                                message: '键不可重复',
                                delay: 5000
                            })
                            return false
                        }
                    }
                }
                this.curKeyParams = this.curSecret.secretKeyList[index]
                this.curKeyIndex = index
                data.isEdit = false
            },
            addKey () {
                const index = this.curSecret.secretKeyList.length + 1
                this.curSecret.secretKeyList.push({
                    key: 'key-' + index,
                    isEdit: true,
                    content: ''
                })
                this.curKeyParams = this.curSecret.secretKeyList[index - 1]
                this.curKeyIndex = index - 1
                this.$refs.keyTooltip.visible = false
            },
            updateLocalData (data) {
                if (data.id) {
                    this.curSecret.id = data.id
                }
                if (data.version) {
                    this.$store.commit('k8sTemplate/updateCurVersion', data.version)
                }
                this.$store.commit('k8sTemplate/updateSecrets', this.secrets)
                setTimeout(() => {
                    this.secrets.forEach(item => {
                        if (item.id === data.id) {
                            this.setCurSecret(item)
                        }
                    })
                }, 500)
            },
            setCurSecret (secret) {
                // 同步上一个键值
                const params = {}
                const keys = this.curSecret.secretKeyList
                if (keys && keys.length) {
                    keys.forEach(item => {
                        params[item.key] = item.content
                    })
                    this.curSecret.config.data = params
                }

                // 切换到当前项
                secret.secretKeyList = []
                this.curSecret = secret
                this.initSecretKeyList(secret)

                clearInterval(this.compareTimer)
                clearTimeout(this.setTimer)
                this.setTimer = setTimeout(() => {
                    if (!this.curSecret.cache) {
                        this.curSecret.cache = JSON.parse(JSON.stringify(secret))
                    }
                    this.watchChange()
                }, 500)
            },
            initSecretKeyList (secret) {
                const list = []
                const keys = secret.config.data
                for (const [key, value] of Object.entries(keys)) {
                    list.push({
                        key: key,
                        isEdit: false,
                        content: value
                    })
                }
                this.curKeyIndex = 0
                if (list.length) {
                    this.curKeyParams = list[0]
                } else {
                    this.curKeyParams = null
                }

                secret.secretKeyList.splice(0, secret.secretKeyList.length, ...list)
            },
            watchChange () {
                this.compareTimer = setInterval(() => {
                    const appCopy = JSON.parse(JSON.stringify(this.curSecret))
                    const cacheCopy = JSON.parse(JSON.stringify(this.curSecret.cache))

                    // 删除无用属性
                    delete appCopy.isEdited
                    delete appCopy.cache
                    delete appCopy.id
                    if (appCopy.secretKeyList) {
                        appCopy.secretKeyList.forEach(item => {
                            delete item.isEdit
                        })
                    }

                    delete cacheCopy.isEdited
                    delete cacheCopy.cache
                    delete cacheCopy.id
                    if (cacheCopy.secretKeyList) {
                        cacheCopy.secretKeyList.forEach(item => {
                            delete item.isEdit
                        })
                    }

                    const appStr = JSON.stringify(appCopy)
                    const cacheStr = JSON.stringify(cacheCopy)
                    const keyObj = {}

                    const keys = this.curSecret.secretKeyList
                    keys.forEach(item => {
                        keyObj[item.key] = item.content
                    })

                    if (String(this.curSecret.id).indexOf('local_') > -1) {
                        this.curSecret.isEdited = true
                    } else if (appStr !== cacheStr) {
                        this.curSecret.isEdited = true
                    } else {
                        this.curSecret.isEdited = false
                    }
                }, 1000)
            },
            removeLocalSecret (secret, index) {
                // 是否删除当前项
                if (this.curSecret.id === secret.id) {
                    if (index === 0 && this.secrets[index + 1]) {
                        this.setCurSecret(this.secrets[index + 1])
                    } else if (this.secrets[0]) {
                        this.setCurSecret(this.secrets[0])
                    }
                }
                this.secrets.splice(index, 1)
            },
            removeSecret (secret, index) {
                const self = this
                const projectId = this.projectId
                const version = this.curVersion
                const secretId = secret.id

                this.$bkInfo({
                    title: '确认',
                    content: this.$createElement('p', { style: { 'text-align': 'center' } }, `删除Secret：${secret.config.metadata.name || '未命名'}`),
                    confirmFn () {
                        if (secretId.indexOf && secretId.indexOf('local_') > -1) {
                            self.removeLocalSecret(secret, index)
                        } else {
                            self.$store.dispatch('k8sTemplate/removeSecret', { secretId, version, projectId }).then(res => {
                                const data = res.data
                                self.removeLocalSecret(secret, index)

                                if (data.version) {
                                    self.$store.commit('k8sTemplate/updateCurVersion', data.version)
                                    self.$store.commit('k8sTemplate/updateBindVersion', true)
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
            addLocalSecret () {
                const secret = JSON.parse(JSON.stringify(secretParams))
                const index = this.secrets.length + 1
                const now = +new Date()

                secret.id = 'local_' + now
                secret.isEdited = true
                secret.config.metadata.name = 'secret-' + index
                this.secrets.push(secret)
                this.setCurSecret(secret)
                this.$refs.secretTooltip && (this.$refs.secretTooltip.visible = false)
                this.$store.commit('k8sTemplate/updateSecrets', this.secrets)
            },
            saveSecretSuccess (params) {
                this.secrets.forEach(item => {
                    if (params.responseData.id === item.id || params.preId === item.id) {
                        item.cache = JSON.parse(JSON.stringify(item))
                    }
                })
                if (params.responseData.id === this.curSecret.id || params.preId === this.curSecret.id) {
                    this.updateLocalData(params.resource)
                }
            },
            updateSecretDatas () {
                const keyObj = {}
                const keys = this.curSecret.secretKeyList
                if (keys) {
                    keys.forEach(item => {
                        keyObj[item.key] = item.content
                    })
                    this.curSecret.config.data = keyObj
                }
            },
            initResource (data) {
                if (data.secrets && data.secrets.length) {
                    this.setCurSecret(data.secrets[0], 0)
                } else if (data.secret && data.secret.length) {
                    this.setCurSecret(data.secret[0], 0)
                }
            },
            async tabResource (type, target) {
                this.isTabChanging = true
                await this.$refs.commonHeader.autoSaveResource(type)
                this.$refs.commonTab.goResource(target)
            },
            showJsonPanel () {
                this.toJsonDialogConf.title = this.curSecret.config.metadata.name + '.yaml'
                const keyObj = {}
                const keys = this.curSecret.secretKeyList
                const appConfig = JSON.parse(JSON.stringify(this.curSecret.config))

                if (keys && keys.length) {
                    keys.forEach(item => {
                        keyObj[item.key] = item.content
                    })
                    appConfig.data = keyObj
                }

                const yamlStr = yamljs.dump(appConfig)
                this.editorConfig.value = yamlStr
                this.toJsonDialogConf.isShow = true
            },
            hideApplicationJson () {
                this.toJsonDialogConf.isShow = false
            },
            closeToJson () {
                this.toJsonDialogConf.isShow = false
                this.toJsonDialogConf.title = ''
                this.editorConfig.value = ''
            },
            editorInitAfter (editor) {
                this.editorConfig.editor = editor
                this.editorConfig.editor.setStyle('biz-app-container-tojson-ace')
            },
            getAppParamsKeys (obj, result) {
                for (const key in obj) {
                    if (key === 'data') continue
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
                const appParams = secretParams.config
                const appParamKeys = [
                    'id',
                    'creationTimestamp'
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
                        const match = editor.find(`${key}`)
                        if (match) {
                            editor.moveCursorTo(match.end.row, match.end.column)
                        }
                        return false
                    }
                }
                return true
            },
            formatJson (jsonObj) {
                return jsonObj
            },
            saveApplicationJson () {
                const editor = this.editorConfig.editor
                const yaml = editor.getValue()
                let appObj = null
                if (!yaml) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入YAML!'
                    })
                    return false
                }

                try {
                    appObj = yamljs.load(yaml)
                } catch (err) {
                    this.$bkMessage({
                        theme: 'error',
                        message: '请输入合法的YAML!'
                    })
                    return false
                }

                const annot = editor.getSession().getAnnotations()
                if (annot && annot.length) {
                    editor.gotoLine(annot[0].row, annot[0].column, true)
                    return false
                }

                const newConfObj = _.merge({}, secretParams.config, appObj)
                const jsonFromat = this.formatJson(newConfObj)
                this.curSecret.config = jsonFromat
                this.initSecretKeyList(this.curSecret)
                this.toJsonDialogConf.isShow = false
            }
        }
    }
</script>

<style scoped>
    @import './secret.css';
</style>
