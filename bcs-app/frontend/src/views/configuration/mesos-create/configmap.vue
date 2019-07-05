<template>
    <div class="biz-content">
        <biz-header ref="commonHeader"
            @exception="exceptionHandler"
            @saveConfigmapSuccess="saveConfigmapSuccess"
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
                        <template v-if="!configmaps.length">
                            <div class="biz-guide-box mt0" style="padding: 140px 30px;">
                                <button class="bk-button bk-primary" @click.stop.prevent="addLocalConfigmap">
                                    <i class="bk-icon icon-plus"></i>
                                    <span style="margin-left: 0;">添加Configmap</span>
                                </button>
                            </div>
                        </template>
                        <template v-else>
                            <div class="biz-configuration-topbar">
                                <div class="biz-list-operation">
                                    <div class="item" v-for="(configmap, index) in configmaps" :key="configmap.id">
                                        <button :class="['bk-button', { 'bk-primary': curConfigmap.id === configmap.id }]" @click.stop="setCurConfigmap(configmap, index)">
                                            {{(configmap && configmap.config.metadata.name) || '未命名'}}
                                            <span class="biz-update-dot" v-show="configmap.isEdited"></span>
                                        </button>
                                        <span class="bk-icon icon-close" @click.stop="removeConfigmap(configmap, index)"></span>
                                    </div>

                                    <bk-tooltip ref="configmapTooltip" :content="'添加Configmap'" placement="top">
                                        <button class="bk-button bk-default is-outline is-icon" @click.stop="addLocalConfigmap">
                                            <i class="bk-icon icon-plus"></i>
                                        </button>
                                    </bk-tooltip>
                                </div>
                            </div>

                            <div class="biz-configuration-content" style="position: relative;">
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

                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 105px;">名称：</label>
                                        <div class="bk-form-content" style="margin-left: 105px;">
                                            <input type="text" :class="['bk-form-input',{ 'is-danger': errors.has('configmapName') }]" placeholder="请输入30个以内的字符" style="width: 310px;" maxlength="30" v-model="curConfigmap.config.metadata.name" name="configmapName" v-validate="{ required: true, regex: /^[a-z]{1}[a-z0-9-]{0,29}$/ }">
                                            <div class="bk-form-tip" v-if="errors.has('configmapName')">
                                                <p class="bk-tip-text">名称必填，以字母开头，只能含小写字母、数字、连字符(-)</p>
                                            </div>
                                        </div>
                                    </div>
                                    <template>
                                        <div class="bk-form-item">
                                            <label class="bk-label" style="width: 105px;">键：</label>
                                            <div class="bk-form-content" style="margin-left: 105px;">
                                                <div class="biz-list-operation">
                                                    <div class="item" v-for="(data, index) in curConfigmap.configmapKeyList" :key="index">
                                                        <button :class="['bk-button', { 'bk-primary': curKeyIndex === index }]" @click.stop.prevent="setCurKey(data, index)" v-if="!data.isEdit">
                                                            {{data.key || '未命名'}}
                                                        </button>

                                                        <bk-input
                                                            type="text"
                                                            placeholder="请输入"
                                                            style="width: 150px;"
                                                            :auto-focus="true"
                                                            v-else
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
                                            <div class="bk-form-item is-required">
                                                <label class="bk-label" style="width: 105px;">值来源：</label>
                                                <div class="bk-form-content" style="margin-left: 105px;">
                                                    <label class="bk-form-radio">
                                                        <input type="radio" name="key-type" value="file" v-model="curKeyParams.type">
                                                        <i class="bk-radio-text">在线编辑</i>
                                                    </label>
                                                    <label class="bk-form-radio">
                                                        <input type="radio" name="key-type" value="http" v-model="curKeyParams.type">
                                                        <i class="bk-radio-text">仓库获取</i>
                                                    </label>
                                                </div>
                                            </div>
                                            <div class="bk-form-item is-required">
                                                <label class="bk-label" style="width: 105px;">值：</label>
                                                <div class="bk-form-content" style="margin-left: 105px;">
                                                    <textarea class="bk-form-textarea" style="height: 200px;" v-model="curKeyParams.content" :placeholder="'请输入键' + curKeyParams.key + '的内容'" v-if="curKeyParams.type === 'file'"></textarea>
                                                    <textarea class="bk-form-textarea" style="height: 200px;" v-model="curKeyParams.content" :placeholder="'请输入仓库中配置文件的相对路径'" v-else></textarea>
                                                    <p class="biz-tip mt10 f14" v-show="curKeyParams.type === 'file'">实例化时会将值的内容做base64编码</p>
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
    import configmapParams from '@open/json/configmap.json'
    import ace from '@open/components/ace-editor'
    import header from './header.vue'
    import tabs from './tabs.vue'
    import _ from 'lodash'

    export default {
        async beforeRouteLeave (to, from, next) {
            // 修改模板集信息
            // await this.$refs.commonHeader.saveTemplate()
            clearInterval(this.compareTimer)
            this.updateConfigmapDatas()
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
                curConfigmapCache: Object.assign({}, configmapParams),
                compareTimer: 0, // 定时器，查看用户是否有修改
                curConfigmap: configmapParams,
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
                this.curConfigmap.configmapKeyList.splice(index, 1)
                this.curKeyParams = this.curConfigmap.configmapKeyList[this.curKeyIndex]
            },
            setKey (data, index) {
                if (data.key === '') {
                    data.key = 'key-' + this.curConfigmap.configmapKeyList.length
                } else {
                    const nameReg = /^[a-zA-Z]{1}[a-zA-Z0-9-_.]{0,29}$/
                    const varReg = /\{\{([^\{\}]+)?\}\}/

                    const key = data.key.replace(varReg, 'key')
                    if (!nameReg.test(key)) {
                        this.$bkMessage({
                            theme: 'error',
                            message: '键名错误，只能包含：字母、数字、连字符(-)、点(.)、下划线(_)，必须是字母开头，长度小于30个字符',
                            delay: 5000
                        })
                        return false
                    }
                    const keyObj = {}
                    for (const item of this.curConfigmap.configmapKeyList) {
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
                this.curKeyParams = this.curConfigmap.configmapKeyList[index]
                this.curKeyIndex = index
                data.isEdit = false
            },
            addKey () {
                const index = this.curConfigmap.configmapKeyList.length + 1
                this.curConfigmap.configmapKeyList.push({
                    key: 'key-' + index,
                    isEdit: true,
                    type: 'file',
                    content: ''
                })
                this.curKeyParams = this.curConfigmap.configmapKeyList[index - 1]
                this.curKeyIndex = index - 1
                this.$refs.keyTooltip.visible = false
            },
            updateLocalData (data) {
                if (data.id) {
                    this.curConfigmap.id = data.id
                }
                if (data.version) {
                    this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                }
                this.$store.commit('mesosTemplate/updateConfigmaps', this.configmaps)
                setTimeout(() => {
                    this.configmaps.forEach(item => {
                        if (item.id === data.id) {
                            this.setCurConfigmap(item)
                        }
                    })
                }, 500)
            },
            setCurConfigmap (configmap) {
                // 同步上一个键值
                const params = {}
                const keys = this.curConfigmap.configmapKeyList
                if (keys && keys.length) {
                    keys.forEach(item => {
                        params[item.key] = {
                            type: item.type,
                            content: item.content
                        }
                    })
                    this.curConfigmap.config.datas = params
                }

                // 切换到当前项
                this.curConfigmap = configmap
                this.initConfigmapKeyList(configmap)

                clearInterval(this.compareTimer)
                clearTimeout(this.setTimer)
                this.setTimer = setTimeout(() => {
                    if (!this.curConfigmap.cache) {
                        this.curConfigmap.cache = JSON.parse(JSON.stringify(configmap))
                    }
                    this.watchChange()
                }, 500)
            },
            initConfigmapKeyList (configmap) {
                const list = []
                const keys = configmap.config.datas
                if (!configmap.configmapKeyList) {
                    configmap.configmapKeyList = []
                }
                for (const [key, value] of Object.entries(keys)) {
                    list.push({
                        key: key,
                        type: value.type,
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

                configmap.configmapKeyList.splice(0, configmap.configmapKeyList.length, ...list)
            },
            watchChange () {
                this.compareTimer = setInterval(() => {
                    const appCopy = JSON.parse(JSON.stringify(this.curConfigmap))
                    const cacheCopy = JSON.parse(JSON.stringify(this.curConfigmap.cache))

                    // 删除无用属性
                    delete appCopy.isEdited
                    delete appCopy.cache
                    delete appCopy.id
                    if (appCopy.configmapKeyList) {
                        appCopy.configmapKeyList.forEach(item => {
                            delete item.isEdit
                        })
                    }

                    delete cacheCopy.isEdited
                    delete cacheCopy.cache
                    delete cacheCopy.id
                    if (cacheCopy.configmapKeyList) {
                        cacheCopy.configmapKeyList.forEach(item => {
                            delete item.isEdit
                        })
                    }

                    const appStr = JSON.stringify(appCopy)
                    const cacheStr = JSON.stringify(cacheCopy)
                    const keyObj = {}

                    const keys = this.curConfigmap.configmapKeyList
                    keys.forEach(item => {
                        keyObj[item.key] = {
                            type: item.type,
                            content: item.content
                        }
                    })

                    if (String(this.curConfigmap.id).indexOf('local_') > -1) {
                        this.curConfigmap.isEdited = true
                    } else if (appStr !== cacheStr) {
                        this.curConfigmap.isEdited = true
                    } else {
                        this.curConfigmap.isEdited = false
                    }
                }, 1000)
            },
            removeLocalConfigmap (configmap, index) {
                // 是否删除当前项
                if (this.curConfigmap.id === configmap.id) {
                    if (index === 0 && this.configmaps[index + 1]) {
                        this.setCurConfigmap(this.configmaps[index + 1])
                    } else if (this.configmaps[0]) {
                        this.setCurConfigmap(this.configmaps[0])
                    }
                }
                this.configmaps.splice(index, 1)
            },
            removeConfigmap (configmap, index) {
                const self = this
                const projectId = this.projectId
                const version = this.curVersion
                const configmapId = configmap.id

                this.$bkInfo({
                    title: '确认',
                    content: this.$createElement('p', { style: { 'text-align': 'center' } }, `删除Configmap：${configmap.config.metadata.name || '未命名'}`),
                    confirmFn () {
                        if (configmapId.indexOf && configmapId.indexOf('local_') > -1) {
                            self.removeLocalConfigmap(configmap, index)
                        } else {
                            self.$store.dispatch('mesosTemplate/removeConfigmap', { configmapId, version, projectId }).then(res => {
                                const data = res.data
                                self.removeLocalConfigmap(configmap, index)

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

                    this.initConfigmapList()
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
            initConfigmapList () {
                const templateId = this.templateId
                const projectId = this.projectId
                const version = this.curTemplate.latest_version_id
                if (this.configmaps.length) {
                    this.curConfigmap = this.configmaps[0]
                    return false
                }
                this.$store.dispatch('mesosTemplate/getTemplateResource', { projectId, templateId, version }).then(res => {
                    const data = res.data
                    if (data.version) {
                        this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                    }
                    if (data.configmap) {
                        this.configmaps.splice(0, this.configmaps.length, ...data.configmap)
                        if (this.configmaps.length === 0) {
                            // this.addLocalConfigmap()
                        } else {
                            this.curConfigmap = this.configmaps[0]
                        }
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
            addLocalConfigmap () {
                const configmap = JSON.parse(JSON.stringify(configmapParams))
                const index = this.configmaps.length + 1
                const now = +new Date()

                configmap.id = 'local_' + now
                configmap.isEdited = true
                configmap.config.metadata.name = 'configmap-' + index
                this.configmaps.push(configmap)
                this.setCurConfigmap(configmap)
                this.$refs.configmapTooltip && (this.$refs.configmapTooltip.visible = false)
                this.$store.commit('mesosTemplate/updateConfigmaps', this.configmaps)
            },
            saveConfigmapSuccess (params) {
                this.configmaps.forEach(item => {
                    if (params.responseData.id === item.id || params.preId === item.id) {
                        item.cache = JSON.parse(JSON.stringify(item))
                    }
                })
                if (params.responseData.id === this.curConfigmap.id || params.preId === this.curConfigmap.id) {
                    this.updateLocalData(params.resource)
                }
            },
            updateConfigmapDatas () {
                const keyObj = {}
                const keys = this.curConfigmap.configmapKeyList
                if (keys) {
                    keys.forEach(item => {
                        keyObj[item.key] = {
                            type: item.type,
                            content: item.content
                        }
                    })
                    this.curConfigmap.config.datas = keyObj
                }
            },
            initResource (data) {
                if (data.configmaps && data.configmaps.length) {
                    this.setCurConfigmap(data.configmaps[0], 0)
                } else if (data.configmap && data.configmap.length) {
                    this.setCurConfigmap(data.configmap[0], 0)
                }
            },
            tabResource (type) {
                this.isTabChanging = true
                this.$refs.commonHeader.saveTemplate()
                this.$refs.commonHeader.autoSaveResource(type)
            },
            showJsonPanel () {
                this.toJsonDialogConf.title = this.curConfigmap.config.metadata.name + '.json'
                const appConfig = JSON.parse(JSON.stringify(this.curConfigmap.config))
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
                const appParams = configmapParams.config
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

                const newConfObj = _.merge({}, configmapParams.config, appObj)
                const jsonFromat = this.formatJson(newConfObj)
                this.curConfigmap.config = jsonFromat
                this.initConfigmapKeyList(this.curConfigmap)
                this.toJsonDialogConf.isShow = false
            },
            formatJson (jsonObj) {
                return jsonObj
            }
        }
    }
</script>

<style scoped>
    @import './configmap.css';
</style>
