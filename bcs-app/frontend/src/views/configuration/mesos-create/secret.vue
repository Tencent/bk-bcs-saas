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
                    <biz-tabs @tab-change="tabResource" ref="commonTab"></biz-tabs>

                    <div class="biz-tab-content" v-bkloading="{ isLoading: isTabChanging }">
                        <template v-if="!secrets.length">
                            <p class="biz-template-tip f12 mb10">
                                {{$t('Secret是一种包含少量敏感信息例如密码、token 或 key 的对象，与ConfigMap相比更加安全')}}，<a class="bk-text-button" :href="PROJECT_CONFIG.doc.mesosSecret" target="_blank">{{$t('详情查看文档')}}</a>
                            </p>
                            <div class="biz-guide-box mt0" style="padding: 140px 30px;">
                                <bk-button type="primary" @click.stop.prevent="addLocalSecret">
                                    <i class="bcs-icon bcs-icon-plus"></i>
                                    <span style="margin-left: 0;">{{$t('添加')}}Secret</span>
                                </bk-button>
                            </div>
                        </template>

                        <template v-else>
                            <div class="biz-configuration-topbar">
                                <p class="biz-template-tip f12 mb10">
                                    {{$t('Secret是一种包含少量敏感信息例如密码、token 或 key 的对象，与ConfigMap相比更加安全')}}，<a class="bk-text-button" :href="PROJECT_CONFIG.doc.mesosSecret" target="_blank">{{$t('详情查看文档')}}</a>
                                </p>
                                <div class="biz-list-operation">
                                    <div class="item" v-for="(secret, index) in secrets" :key="secret.id">
                                        <bk-button :class="['bk-button', { 'bk-primary': curSecret.id === secret.id }]" @click.stop="setCurSecret(secret, index)">
                                            {{(secret && secret.config.metadata.name) || $t('未命名')}}
                                            <span class="biz-update-dot" v-show="secret.isEdited"></span>
                                        </bk-button>
                                        <span class="bcs-icon bcs-icon-close" @click.stop="removeSecret(secret, index)"></span>
                                    </div>

                                    <bcs-popover ref="secretTooltip" :content="$t('添加Secret')" placement="top">
                                        <bk-button class="bk-button bk-default is-outline is-icon" @click.stop="addLocalSecret">
                                            <i class="bcs-icon bcs-icon-plus"></i>
                                        </bk-button>
                                    </bcs-popover>
                                </div>
                            </div>

                            <div class="biz-configuration-content" style="position: relative;">
                                <div class="bk-form biz-configuration-form">
                                    <a href="javascript:void(0);" class="bk-text-button from-json-btn" @click.stop.prevent="showJsonPanel"></a>

                                    <bk-sideslider
                                        :is-show.sync="toJsonDialogConf.isShow"
                                        :title="toJsonDialogConf.title"
                                        :width="toJsonDialogConf.width"
                                        :quick-close="false"
                                        class="biz-app-container-tojson-sideslider"
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
                                    </bk-sideslider>

                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 105px;">{{$t('名称')}}：</label>
                                        <div class="bk-form-content" style="margin-left: 105px;">
                                            <input type="text" :class="['bk-form-input',{ 'is-danger': errors.has('secretName') }]" :placeholder="$t('请输入64个以内的字符')" style="width: 310px;" maxlength="64" v-model="curSecret.config.metadata.name" name="secretName" v-validate="{ required: true, regex: /^[a-z]{1}[a-z0-9-]{0,63}$/ }">
                                            <div class="bk-form-tip" v-if="errors.has('secretName')">
                                                <p class="bk-tip-text">{{$t('名称必填，以字母开头，只能含小写字母、数字、连字符(-)')}}</p>
                                            </div>
                                        </div>
                                    </div>
                                    <template>
                                        <div class="bk-form-item">
                                            <label class="bk-label" style="width: 105px;">{{$t('键')}}：</label>
                                            <div class="bk-form-content" style="margin-left: 105px;">
                                                <div class="biz-list-operation">
                                                    <div class="item" v-for="(data, index) in curSecret.secretKeyList" :key="index">
                                                        <bk-button :class="['bk-button', { 'bk-primary': curKeyIndex === index }]" @click.stop.prevent="setCurKey(data, index)" v-if="!data.isEdit">
                                                            {{data.key || $t('未命名')}}
                                                        </bk-button>
                                                        <bkbcs-input
                                                            type="text"
                                                            :placeholder="$t('请输入')"
                                                            style="width: 150px;"
                                                            :auto-focus="true"
                                                            v-else
                                                            :value.sync="data.key"
                                                            :list="varList"
                                                            @blur="setKey(data, index)"
                                                        >
                                                        </bkbcs-input>
                                                        <span class="bcs-icon bcs-icon-edit" v-show="!data.isEdit" @click.stop.prevent="editKey(data, index)"></span>
                                                        <span class="bcs-icon bcs-icon-close" v-show="!data.isEdit" @click.stop.prevent="removeKey(data, index)"></span>
                                                    </div>

                                                    <bcs-popover ref="keyTooltip" :content="$t('添加Key')" placement="top">
                                                        <bk-button class="bk-button bk-default is-outline is-icon" @click.stop.prevent="addKey">
                                                            <i class="bcs-icon bcs-icon-plus"></i>
                                                        </bk-button>
                                                    </bcs-popover>
                                                </div>
                                            </div>
                                        </div>
                                        <template v-if="curKeyParams">
                                            <div class="bk-form-item is-required">
                                                <label class="bk-label" style="width: 105px;">{{$t('值来源')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 105px;">
                                                    <bk-radio-group v-model="curKeyParams.type">
                                                        <bk-radio value="file">{{$t('在线编辑')}}</bk-radio>
                                                        <bk-radio value="env" disabled>{{$t('仓库获取')}}</bk-radio>
                                                    </bk-radio-group>
                                                </div>
                                            </div>
                                            <div class="bk-form-item is-required">
                                                <label class="bk-label" style="width: 105px;">{{$t('值')}}：</label>
                                                <div class="bk-form-content" style="margin-left: 105px;">
                                                    <textarea class="bk-form-textarea" style="height: 300px;" :placeholder="$t('请输入键') + curKeyParams.key + $t('的内容')" v-model="curKeyParams.content"></textarea>
                                                    <p class="biz-tip mt5">{{$t('实例化时会将值的内容做base64编码')}}</p>
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
    import secretParams from '@open/json/secret.json'
    import ace from '@open/components/ace-editor'
    import header from './header.vue'
    import tabs from './tabs.vue'
    import _ from 'lodash'

    export default {
        async beforeRouteLeave (to, from, next) {
            // 修改模板集信息
            // await this.$refs.commonHeader.saveTemplate()
            clearInterval(this.compareTimer)
            this.updateSecretDatas()
            next(true)
        },
        components: {
            'biz-header': header,
            'biz-tabs': tabs,
            'ace': ace
        },
        data () {
            return {
                isTabChanging: false,
                winHeight: 0,
                exceptionCode: null,
                isDataLoading: true,
                isDataSaveing: false,
                curSecretCache: Object.assign({}, secretParams),
                compareTimer: 0, // 定时器，查看用户是否有修改
                curSecret: secretParams,
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
                }
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
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            templateId () {
                return this.$route.params.templateId
            }
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
            editorInit () {
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
                    const nameReg = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,29}$/
                    const varReg = /\{\{([^\{\}]+)?\}\}/

                    const key = data.key.replace(varReg, 'key')
                    if (!nameReg.test(key)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: this.$t('键名错误，只能包含：字母、数字、连字符(-)、点(.)、下划线(_)，必须是字母开头，长度小于30个字符'),
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
                                message: this.$t('键不可重复'),
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
                    content: '',
                    type: 'file'
                })
                this.curKeyParams = this.curSecret.secretKeyList[index - 1]
                this.curKeyIndex = index - 1
                this.$refs.keyTooltip.visible = false
            },
            setCurSecret (secret) {
                // 同步上一个键值
                const params = {}
                const keys = this.curSecret.secretKeyList
                if (keys && keys.length) {
                    keys.forEach(item => {
                        params[item.key] = {
                            content: item.content
                        }
                    })
                    this.curSecret.config.datas = params
                }

                // 切换到当前项
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
                const keys = secret.config.datas
                if (!secret.secretKeyList) {
                    secret.secretKeyList = []
                }
                for (const [key, value] of Object.entries(keys)) {
                    list.push({
                        key: key,
                        isEdit: false,
                        content: value.content
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
                    for (const item of keys) {
                        keyObj[item.key] = {
                            content: item.content
                        }
                    }

                    if (String(this.curSecret.id).indexOf('local_') > -1) {
                        this.curSecret.isEdited = true
                    } else if (appStr !== cacheStr) {
                        this.curSecret.isEdited = true
                    } else {
                        this.curSecret.isEdited = false
                    }
                }, 1000)
            },
            removeLocalSecret (service, index) {
                // 是否删除当前项
                if (this.curSecret.id === service.id) {
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
                    title: this.$t('确认删除'),
                    content: this.$createElement('p', { style: { 'text-align': 'left' } }, `${this.$t('删除Secret')}：${secret.config.metadata.name || this.$t('未命名')}`),
                    confirmFn () {
                        if (secretId.indexOf && secretId.indexOf('local_') > -1) {
                            self.removeLocalSecret(secret, index)
                        } else {
                            self.$store.dispatch('mesosTemplate/removeSecret', { secretId, version, projectId }).then(res => {
                                const data = res.data

                                self.removeLocalSecret(secret, index)

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
            initTemplate () {
                const templateId = this.templateId
                const projectId = this.projectId
                this.$store.dispatch('mesosTemplate/getTemplateById', { projectId, templateId }).then(res => {
                    const data = res.data
                    this.curTemplate = data

                    this.initSecretList()
                    this.$store.commit('mesosTemplate/updateCurTemplate', data)
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
            initSecretList () {
                const templateId = this.templateId
                const projectId = this.projectId
                const version = this.curTemplate.latest_version_id
                this.$store.dispatch('mesosTemplate/getTemplateResource', { projectId, templateId, version }).then(res => {
                    const data = res.data
                    if (data.version) {
                        this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                    }
                    if (data.secret) {
                        this.secrets.splice(0, this.secrets.length, ...data.secret)
                        if (this.secrets.length === 0) {
                            // this.addLocalSecret()
                        } else {
                            this.curSecret = this.secrets[0]
                        }
                    } else {
                        // this.addLocalSecret()
                    }

                    this.$store.commit('mesosTemplate/updateResources', data)
                    this.isDataLoading = false
                }, res => {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataLoading = false
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
                // this.curSecret = secret
                this.$refs.secretTooltip && (this.$refs.secretTooltip.visible = false)
                this.$store.commit('mesosTemplate/updateSecrets', this.secrets)
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
            updateLocalData (data) {
                if (data.id) {
                    this.curSecret.id = data.id
                }
                if (data.version) {
                    this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                }

                this.$store.commit('mesosTemplate/updateSecrets', this.secrets)

                setTimeout(() => {
                    this.secrets.forEach(item => {
                        if (item.id === data.id) {
                            this.setCurSecret(item)
                        }
                    })
                }, 500)
            },
            updateSecretDatas () {
                const keyObj = {}
                const keys = this.curSecret.secretKeyList
                if (keys) {
                    for (const item of keys) {
                        keyObj[item.key] = {
                            content: item.content
                        }
                    }
                    this.curSecret.config.datas = keyObj
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
                await this.$refs.commonHeader.saveTemplate()
                await this.$refs.commonHeader.autoSaveResource(type)
                this.$refs.commonTab.goResource(target)
            },
            showJsonPanel () {
                this.toJsonDialogConf.title = this.curSecret.config.metadata.name + '.json'
                const appConfig = JSON.parse(JSON.stringify(this.curSecret.config))
                delete appConfig.webCache

                const jsonStr = JSON.stringify(appConfig, null, 4)
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
            checkJson (jsonObj) {
                const editor = this.editorConfig.editor
                const appParams = secretParams.config
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

                const newConfObj = _.merge({}, secretParams.config, appObj)
                const jsonFromat = this.formatJson(newConfObj)
                this.curSecret.config = jsonFromat
                this.initSecretKeyList(this.curSecret)
                this.toJsonDialogConf.isShow = false
            },
            formatJson (jsonObj) {
                return jsonObj
            }
        }
    }
</script>

<style scoped>
    @import './secret.css';
</style>
