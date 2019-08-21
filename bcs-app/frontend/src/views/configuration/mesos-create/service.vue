<template>
    <div class="biz-content">
        <biz-header ref="commonHeader"
            @exception="exceptionHandler"
            @saveServiceSuccess="saveServiceSuccess"
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
                    <biz-tabs @tab-change="tabResource"></biz-tabs>
                    <div class="biz-tab-content" v-bkloading="{ isLoading: isTabChanging }">
                        <template v-if="!services.length">
                            <div class="biz-guide-box mt0" style="padding: 140px 30px;">
                                <button class="bk-button bk-primary" @click.stop.prevent="addLocalService">
                                    <i class="bk-icon icon-plus"></i>
                                    <span style="margin-left: 0;">添加Service</span>
                                </button>
                            </div>
                        </template>

                        <template v-else>
                            <div class="biz-configuration-topbar">
                                <div class="biz-list-operation">
                                    <div class="item" v-for="(service, index) in services" :key="service.id">
                                        <button :class="['bk-button', { 'bk-primary': curService.id === service.id }]" @click.stop="setCurService(service, index)">
                                            {{(service && service.config.metadata.name) || '未命名'}}
                                            <span class="biz-update-dot" v-show="service.isEdited"></span>
                                        </button>
                                        <span class="bk-icon icon-close" @click.stop="removeService(service, index)"></span>
                                    </div>

                                    <bk-tooltip ref="serviceTooltip" :content="'添加Service'" placement="top">
                                        <button class="bk-button bk-default is-outline is-icon" @click.stop="addLocalService">
                                            <i class="bk-icon icon-plus"></i>
                                        </button>
                                    </bk-tooltip>
                                </div>
                            </div>

                            <div class="biz-configuration-content">
                                <div class="bk-form biz-configuration-form">
                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 130px;">名称：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-input
                                                type="text"
                                                placeholder="请输入30个以内的字符"
                                                style="width: 310px;"
                                                maxlength="30"
                                                :value.sync="curService.config.metadata.name"
                                                :list="varList"
                                            >
                                            </bk-input>
                                            <div class="bk-form-tip" v-if="errors.has('serviceName')">
                                                <p class="bk-tip-text">名称必填，以字母开头，只能含小写字母、数字、连字符(-)</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 130px;">关联应用：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div class="bk-dropdown-box" style="width: 310px;" @click="reloadApplications">
                                                <bk-selector
                                                    placeholder="请选择要关联的Application"
                                                    :setting-key="'app_id'"
                                                    :multi-select="true"
                                                    :display-key="'app_name'"
                                                    :selected.sync="curService.config.webCache.link_app"
                                                    :list="applicationList"
                                                    :prevent-init-trigger="'true'"
                                                    :is-loading="isLoadingApps"
                                                    @item-selected="selectApps">
                                                </bk-selector>
                                            </div>
                                            <span class="biz-guard-tip ml10" v-if="!isDataLoading && !applicationList.length">请先配置Application，再进行关联</span>
                                        </div>
                                    </div>
                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 130px;">权重设置(%)：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <template v-if="curService.config.webCache.link_app_weight.length">
                                                <div class="bk-form-input-group is-addon-left mr10" v-for="(app, index) in curService.config.webCache.link_app_weight" :key="index">
                                                    <span class="input-group-addon">
                                                        {{getAppNameById(app.id)}}
                                                    </span>
                                                    <bk-number-input
                                                        :value.sync="app.weight"
                                                        :min="0"
                                                        :max="100"
                                                        :hide-operation="true"
                                                        :ex-style="{ 'width': '25px' }"
                                                        :placeholder="'输入'"
                                                        @change="checkTotalPercent">
                                                    </bk-number-input>
                                                </div>
                                                <p :class="['biz-tip', { 'bk-danger': isWeightError }]">权重的值为大于等于0的整数，且所有权重相加为100</p>
                                            </template>
                                            <template v-else>
                                                <p class="mt5 biz-tip">请关联相应的Application</p>
                                            </template>
                                        </div>
                                    </div>
                                    <div class="bk-form-item">
                                        <label class="bk-label" style="width: 130px;">Service类型：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div class="bk-dropdown-box" style="width: 310px;">
                                                <bk-selector
                                                    placeholder="请选择"
                                                    :setting-key="'id'"
                                                    :display-key="'name'"
                                                    :selected.sync="curService.config.spec.type"
                                                    :list="serviceTypeList">
                                                </bk-selector>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="bk-form-item" v-show="curService.config.spec.type !== 'None'">
                                        <label class="bk-label" style="width: 130px;">IP：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <input type="text" class="bk-form-input" placeholder="多个IP以逗号分隔" style="width: 310px;" v-model="curService.serviceIPs">
                                        </div>
                                    </div>
                                    <div class="bk-form-item">
                                        <label class="bk-label" style="width: 130px;">端口映射：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div class="biz-keys-list mb10">
                                                <template v-if="curService.config.webCache.link_app.length">
                                                    <template v-if="appPortList.length && curService.config.spec.ports.length">
                                                        <table class="biz-simple-table">
                                                            <thead>
                                                                <tr>
                                                                    <th style="width: 130px;">端口名称</th>
                                                                    <th style="width: 120px;">协议</th>
                                                                    <th style="width: 100px;">目标端口</th>
                                                                    <th style="width: 100px;">服务端口</th>
                                                                    <th style="width: 125px;">域名</th>
                                                                    <th style="width: 125px;">路径</th>
                                                                    <th></th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                <tr v-for="(port, index) in curService.config.spec.ports" :key="index">
                                                                    <td>
                                                                        <bk-selector
                                                                            placeholder="端口名称"
                                                                            :setting-key="'id'"
                                                                            :display-key="'name'"
                                                                            :selected.sync="port.id"
                                                                            :allow-clear="true"
                                                                            :filter-list="curServicePortList"
                                                                            :is-link="true"
                                                                            :init-prevent-trigger="true"
                                                                            :list="appPortList"
                                                                            @clear="clearPort(port)"
                                                                            @item-selected="selectPort(port)">
                                                                        </bk-selector>
                                                                    </td>
                                                                    <td>

                                                                        <input type="text" class="bk-form-input" disabled :value="getProtocalById(port.id)" style="width: 120px;">
                                                                    </td>
                                                                    <td>
                                                                        <input type="text" class="bk-form-input" disabled :value="getTargetPortById(port.id)" style="width: 100px;">
                                                                    </td>
                                                                    <td>
                                                                        <bk-input
                                                                            type="number"
                                                                            placeholder="服务端口"
                                                                            :value.sync="port.servicePort"
                                                                            :min="1"
                                                                            :max="65535"
                                                                            :list="varList">
                                                                        </bk-input>
                                                                    </td>
                                                                    <td>
                                                                        <bk-input
                                                                            type="text"
                                                                            placeholder="域名"
                                                                            style="width: 125px;"
                                                                            :disabled="port.protocol !== 'HTTP'"
                                                                            :value.sync="port.domainName"
                                                                            :list="varList">
                                                                        </bk-input>
                                                                    </td>
                                                                    <td>
                                                                        <bk-input
                                                                            type="text"
                                                                            placeholder="路径"
                                                                            style="width: 125px;"
                                                                            :disabled="port.protocol !== 'HTTP'"
                                                                            :value.sync="port.path"
                                                                            :list="varList">
                                                                        </bk-input>
                                                                    </td>
                                                                    <td>
                                                                        <button class="action-btn ml5" @click.stop.prevent="addPort" v-show="curService.config.spec.ports.length < appPortList.length">
                                                                            <i class="bk-icon icon-plus"></i>
                                                                        </button>
                                                                        <button class="action-btn" @click.stop.prevent="removePort(port, index)" v-show="curService.config.spec.ports.length > 1">
                                                                            <i class="bk-icon icon-minus"></i>
                                                                        </button>
                                                                    </td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    </template>
                                                    <template v-else>
                                                        <p class="mt5">请先配置关联应用的容器端口映射信息</p>
                                                    </template>
                                                </template>
                                                <template v-else>
                                                    <p class="mt5 biz-tip">请关联相应的Application</p>
                                                </template>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="bk-form-item">
                                        <label class="bk-label" style="width: 130px;">标签管理：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-keyer :key-list.sync="curLabelList" :var-list="varList" ref="labelKeyer" @change="updateLabelList"></bk-keyer>
                                        </div>
                                    </div>

                                    <div class="bk-form-item">
                                        <div class="bk-form-content" style="margin-left: 130px">
                                            <label class="bk-form-checkbox">
                                                <input type="checkbox" v-model="curService.config.isLinkLoadBalance">
                                                <i class="bk-checkbox-text">关联LoadBalance</i>
                                            </label>
                                        </div>
                                    </div>

                                    <div class="bk-form-item" v-if="curService.config.isLinkLoadBalance">
                                        <label class="bk-label" style="width: 130px;">负载均衡算法：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div class="bk-dropdown-box" style="width: 310px;">
                                                <bk-selector
                                                    placeholder="请选择"
                                                    :setting-key="'id'"
                                                    :display-key="'name'"
                                                    :selected.sync="algorithmIndex"
                                                    :list="algorithmList"
                                                    @item-selected="selectAlgorithm">
                                                </bk-selector>
                                            </div>
                                        </div>
                                    </div>
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
    import serviceParams from '@open/json/service.json'
    import bkKeyer from '@open/components/keyer'
    import header from './header.vue'
    import tabs from './tabs.vue'

    export default {
        async beforeRouteLeave (to, from, next) {
            // 修改模板集信息
            // await this.$refs.commonHeader.saveTemplate()
            clearInterval(this.compareTimer)
            next(true)
        },
        components: {
            'bk-keyer': bkKeyer,
            'biz-header': header,
            'biz-tabs': tabs
        },
        data () {
            return {
                isTabChanging: false,
                exceptionCode: null,
                isDataLoading: true,
                isDataSaveing: false,
                isWeightError: false,
                isLoadingApps: false,
                algorithmList: [
                    {
                        id: 'roundrobin',
                        name: 'roundrobin'
                    },
                    {
                        id: 'source',
                        name: 'source'
                    },
                    {
                        id: 'leastconn',
                        name: 'leastconn'
                    }
                ],
                serviceTypeList: [
                    {
                        id: 'ClusterIP',
                        name: 'ClusterIP'
                    },
                    {
                        id: 'None',
                        name: 'None'
                    }
                ],
                weight: 10,
                curServiceIPs: '',
                linkAppVersion: 0,
                protocolIndex: -1,
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
                appPortList: [],
                curServiceCache: Object.assign({}, serviceParams),
                compareTimer: 0, // 定时器，查看用户是否有修改
                setTimer: 0,
                curService: serviceParams,
                algorithmIndex: 'roundrobin'
            }
        },
        computed: {
            curTemplate () {
                return this.$store.state.mesosTemplate.curTemplate
            },
            varList () {
                return this.$store.state.variable.varList
            },
            applicationList () {
                return this.$store.state.mesosTemplate.linkApps
            },
            isTemplateSaving () {
                return this.$store.state.mesosTemplate.isTemplateSaving
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
            },
            curServicePortList () {
                const results = []
                // let ports = this.curServicePortMap
                const ports = this.curService.config.spec.ports
                ports.forEach(item => {
                    if (item.id) {
                        results.push(item.id)
                    }
                })
                return results
            },
            curLabelList () {
                const list = []
                const labels = this.curService.config.metadata.labels
                // 如果有缓存直接使用
                if (this.curService.config.webCache && this.curService.config.webCache.labelListCache) {
                    return this.curService.config.webCache.labelListCache
                }
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
            }
        },
        watch: {
            'applications' () {
                if (this.curVersion) {
                    this.initApplications(this.curVersion)
                }
            },
            'curService.config.isLinkLoadBalance' (val) {
                if (val) {
                    if (this.curService.config.metadata.lb_labels) {
                        this.algorithmIndex = this.curService.config.metadata.lb_labels['BCSBALANCE']
                    } else {
                        this.algorithmIndex = 'roundrobin'
                        this.curService.config.metadata.lb_labels = {
                            'BCSBALANCE': 'roundrobin'
                        }
                    }
                } else {
                    delete this.curService.config.metadata.lb_labels
                }
            }
        },
        mounted () {
            this.$refs.commonHeader.initTemplate((data) => {
                this.initResource(data)
                this.isDataLoading = false
            })
        },
        methods: {
            initResource (data) {
                const version = data.latest_version_id || data.version
                if (version) {
                    this.initApplications(version, () => {
                        if (data.services && data.services.length) {
                            this.setCurService(data.services[0], 0)
                        } else if (data.service && data.service.length) {
                            this.setCurService(data.service[0], 0)
                        }
                    })
                } else {
                    this.$store.commit('mesosTemplate/updateLinkApps', [])
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
            reloadApplications () {
                if (this.curVersion) {
                    this.isLoadingApps = true
                    this.initApplications(this.curVersion)
                }
            },
            selectApps (index, data) {
                const appIds = []
                this.curService.app_id = {}
                this.curService.config.webCache.link_app_weight = []
                data.forEach(item => {
                    appIds.push(item.app_id)
                    this.curService.config.webCache.link_app_weight.push({
                        id: item.app_id,
                        name: item.app_name,
                        weight: 0
                    })
                })
                this.getPorts(appIds)
            },
            getAppNameById (id) {
                for (const item of this.applicationList) {
                    if (item.app_id === id) {
                        return item.app_name
                    }
                }
                return '--'
            },
            selectAlgorithm (index, data) {
                this.curService.config.metadata.lb_labels.BCSBALANCE = index
            },
            selectPort (port) {
                const id = port.id
                this.appPortList.forEach(item => {
                    if (item.id === id) {
                        port.name = item.name
                        port.protocol = item.protocol
                        port.targetPort = item.target_port

                        // 清空
                        port.domainName = ''
                        port.path = ''
                        port.servicePort = ''
                    }
                })
            },
            clearPort (port) {
                port.id = ''
                port.name = ''
                port.protocol = ''
                port.targetPort = ''
                port.domainName = ''
                port.path = ''
                port.servicePort = ''
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
            addPort () {
                const ports = this.curService.config.spec.ports
                ports.push({
                    'id': '',
                    'name': '',
                    'protocol': 'http',
                    'domainName': '',
                    'path': '',
                    'servicePort': ''
                })
            },
            removePort (port, index) {
                const ports = this.curService.config.spec.ports
                ports.splice(index, 1)
            },
            initApplications (version, callback) {
                const projectId = this.projectId
                this.linkAppVersion = version
                this.$store.dispatch('mesosTemplate/getApplicationsByVersion', { projectId, version }).then(res => {
                    callback && callback()
                    this.isLoadingApps = false
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
            filterAppWeight () {
                const appIds = []
                const appKeys = []

                // 过滤已经删除的app
                const filterResults = []
                this.applicationList.forEach(item => {
                    appKeys.push(item.app_id)
                })
                this.curService.config.webCache.link_app_weight.forEach(item => {
                    if (appKeys.includes(item.id)) {
                        appIds.push(item.id)
                        filterResults.push(item)
                    }
                })
                this.curService.config.webCache.link_app_weight.splice(0, this.curService.config.webCache.link_app_weight.length, ...filterResults)
                this.getPorts(appIds)
            },
            updateLocalData (data) {
                if (data.id) {
                    this.curService.id = data.id
                }
                if (data.version) {
                    this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                }
                this.$store.commit('mesosTemplate/updateServices', this.services)
                setTimeout(() => {
                    this.services.forEach(item => {
                        if (item.id === data.id) {
                            this.setCurService(item)
                        }
                    })
                }, 500)
            },
            setCurService (service, index) {
                this.curService = service
                this.curServiceIPs = this.curService.config.spec.clusterIP.join(',')
                if (!this.curService.config.spec.ports.length) {
                    this.addPort()
                }
                clearInterval(this.compareTimer)
                clearTimeout(this.setTimer)
                this.setTimer = setTimeout(() => {
                    if (!this.curService.cache) {
                        this.curService.cache = JSON.parse(JSON.stringify(service))
                    }
                    this.filterAppWeight()
                    this.watchChange()
                }, 1500)
            },
            watchChange () {
                this.compareTimer = setInterval(() => {
                    const appCopy = JSON.parse(JSON.stringify(this.curService))
                    const cacheCopy = JSON.parse(JSON.stringify(this.curService.cache))

                    // 删除无用属性
                    delete appCopy.isEdited
                    delete appCopy.cache
                    delete appCopy.id

                    delete cacheCopy.isEdited
                    delete cacheCopy.cache
                    delete cacheCopy.id

                    const appStr = JSON.stringify(appCopy)
                    const cacheStr = JSON.stringify(cacheCopy)
                    if (String(this.curService.id).indexOf('local_') > -1) {
                        this.curService.isEdited = true
                    } else if (appStr !== cacheStr) {
                        this.curService.isEdited = true
                    } else {
                        this.curService.isEdited = false
                    }
                }, 1500)
            },
            getProtocalById (id) {
                let result = null
                this.appPortList.forEach(item => {
                    if (item.id === id) {
                        result = item
                    }
                })
                if (result) {
                    return result.protocol
                } else {
                    return ''
                }
            },
            getTargetPortById (id) {
                let result = null
                this.appPortList.forEach(item => {
                    if (item.id === id) {
                        result = item
                    }
                })
                if (result) {
                    return result.target_port
                } else {
                    return ''
                }
            },
            getPorts (apps) {
                const projectId = this.projectId
                const version = this.curVersion
                this.$store.dispatch('mesosTemplate/getPortsByApps', { projectId, version, apps }).then(res => {
                    const ports = res.data.filter(item => {
                        return item.name && item.protocol && item.target_port
                    })
                    const keys = []
                    let results = []
                    ports.forEach(port => {
                        keys.push(port.id)
                        port.domainName = ''
                        port.path = ''
                        port.servicePort = ''
                    })
                    this.appPortList.splice(0, this.appPortList.length, ...ports)
                    results = this.curService.config.spec.ports.filter(item => {
                        if (!item.id) {
                            return true
                        } else if (keys.includes(item.id)) {
                            return true
                        } else {
                            return false
                        }
                    })
                    this.curService.config.spec.ports.splice(0, this.curService.config.spec.ports.length, ...results)
                    if (!this.curService.config.spec.ports.length) {
                        this.addPort()
                    }
                }, res => {
                    this.appPortList.splice(0, this.appPortList.length)
                })
            },
            removeLocalService (service, index) {
                // 是否删除当前项
                if (this.curService.id === service.id) {
                    if (index === 0 && this.services[index + 1]) {
                        this.setCurService(this.services[index + 1])
                    } else if (this.services[0]) {
                        this.setCurService(this.services[0])
                    }
                }
                this.services.splice(index, 1)
            },
            removeService (service, index) {
                const self = this
                const projectId = this.projectId
                const version = this.curVersion
                const serviceId = service.id

                this.$bkInfo({
                    title: '确认',
                    content: this.$createElement('p', { style: { 'text-align': 'center' } }, `删除Service：${service.config.metadata.name || '未命名'}`),
                    confirmFn () {
                        if (serviceId.indexOf && serviceId.indexOf('local_') > -1) {
                            self.removeLocalService(service, index)
                        } else {
                            self.$store.dispatch('mesosTemplate/removeService', { serviceId, version, projectId }).then(res => {
                                const data = res.data
                                self.removeLocalService(service, index)

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
            saveServiceSuccess (params) {
                this.services.forEach(item => {
                    if (params.responseData.id === item.id || params.preId === item.id) {
                        item.cache = JSON.parse(JSON.stringify(item))
                    }
                })
                if (params.responseData.id === this.curService.id || params.preId === this.curService.id) {
                    this.updateLocalData(params.resource)
                }
            },
            createService () {
                const version = this.curVersion
                const projectId = this.projectId
                const data = this.curService
                this.$store.dispatch('mesosTemplate/addService', { projectId, version, data }).then(res => {
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
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
            },
            createFirstService () {
                const templateId = this.templateId
                const projectId = this.projectId
                const data = this.curService
                this.$store.dispatch('mesosTemplate/addFirstService', { projectId, templateId, data }).then(res => {
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
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
            },
            updateService () {
                const version = this.curVersion
                const projectId = this.projectId
                const data = this.curService
                const serviceId = this.curService.id
                this.$store.dispatch('mesosTemplate/updateService', { projectId, version, data, serviceId }).then(res => {
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
                        message: message,
                        hasCloseIcon: true,
                        delay: '10000'
                    })
                    this.isDataSaveing = false
                })
            },
            initServiceList () {
                const templateId = this.templateId
                const projectId = this.projectId
                const version = this.curTemplate.latest_version_id
                this.$store.dispatch('mesosTemplate/getTemplateResource', { projectId, templateId, version }).then(res => {
                    const data = res.data
                    if (data.version) {
                        this.$store.commit('mesosTemplate/updateCurVersion', data.version)
                    }
                    if (data.service) {
                        this.services.splice(0, this.services.length, ...data.service)
                        if (this.services.length === 0) {
                            // this.addLocalService()
                        } else {
                            this.curService = this.services[0]
                            if (this.curService.config.spec.clusterIP.length) {
                                this.curServiceIPs = this.curService.config.spec.clusterIP.join(',')
                            } else {
                                this.curServiceIPs = ''
                            }
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
            addLocalService () {
                const service = JSON.parse(JSON.stringify(serviceParams))
                const index = this.services.length
                const now = +new Date()

                service.id = 'local_' + now
                service.isEdited = true
                service.config.metadata.name = 'service-' + (index + 1)
                this.services.push(service)

                this.setCurService(service, index)
                this.$refs.serviceTooltip && (this.$refs.serviceTooltip.visible = false)
                this.$store.commit('mesosTemplate/updateServices', this.services)
            },
            checkTotalPercent () {
                let total = 0
                this.curService.config.webCache.link_app_weight.forEach(item => {
                    total += item.weight
                })
                if (total !== 100) {
                    this.isWeightError = true
                    return false
                }
                this.isWeightError = false
                return true
            },
            updateLabelList (list, data) {
                if (!this.curService.config.webCache) {
                    this.curService.config.webCache = {}
                }
                this.curService.config.webCache.labelListCache = list
            },
            saveService () {
                if (!this.checkData()) {
                    return false
                }
                if (this.isDataSaveing) {
                    return false
                } else {
                    this.isDataSaveing = true
                }

                this.formatData()

                if (this.curVersion) {
                    if (this.curService.id.indexOf && (this.curService.id.indexOf('local') > -1)) {
                        this.createService()
                    } else {
                        this.updateService()
                    }
                } else {
                    this.createFirstService()
                }
            }
        }
    }
</script>

<style scoped>
    @import './service.css';
</style>
