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
                    <biz-tabs @tab-change="tabResource" ref="commonTab"></biz-tabs>
                    <div class="biz-tab-content" v-bkloading="{ isLoading: isTabChanging }">
                        <template v-if="!services.length">
                            <div class="biz-guide-box mt0">
                                <button class="bk-button bk-primary" @click.stop.prevent="addLocalService">
                                    <i class="bk-icon icon-plus"></i>
                                    <span style="margin-left: 0;">添加Service</span>
                                </button>
                            </div>
                        </template>

                        <template v-else>
                            <div class="biz-configuration-topbar">
                                <div class="biz-list-operation">
                                    <div class="item" v-for="(service, index) in services" :key="index">
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

                            <div class="biz-configuration-content" style="position: relative; margin-bottom: 105px;">
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
                                                <p class="bk-tip-text">名称必填，以小写字母或数字开头和结尾，只能包含：小写字母、数字、连字符(-)、点(.)</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 130px;">关联应用：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div class="bk-dropdown-box" style="width: 310px;" @click="reloadApplications">
                                                <bk-selector
                                                    placeholder="请选择要关联的应用"
                                                    :setting-key="'deploy_tag'"
                                                    :multi-select="true"
                                                    :display-key="'deploy_name'"
                                                    :selected.sync="curService.deploy_tag_list"
                                                    :list="applicationList"
                                                    :prevent-init-trigger="'true'"
                                                    :is-loading="isLoadingApps"
                                                    @item-selected="selectApps">
                                                </bk-selector>
                                            </div>
                                            <span class="biz-tip ml10" v-if="!isDataLoading && !applicationList.length">请先配置Deployment/DaemonSet/StatefulSet，再进行关联</span>
                                        </div>
                                    </div>
                                    <div class="bk-form-item is-required">
                                        <label class="bk-label" style="width: 130px;">关联标签：</label>
                                        <div class="bk-form-content key-tip-wrapper" style="margin-left: 130px;">
                                            <template v-if="appLabels.length && !isLabelsLoading">
                                                <ul class="key-list">
                                                    <li v-for="(label,index) in appLabels" @click="selectLabel(label)" :key="index">
                                                        <span class="key">
                                                            <label class="bk-form-checkbox bk-checkbox-small pt0 pb0">
                                                                <input type="checkbox" name="linkapp" :checked="label.isSelected">
                                                            </label>
                                                        </span>
                                                        <span class="value">{{label.key}}:{{label.value}}</span>
                                                    </li>
                                                </ul>
                                                <p class="biz-tip mt10 mb15">Service使用标签来查找所有正在运行的容器。请注意：同一个命名空间下，使用了选中标签的应用都会被导流</p>
                                            </template>
                                            <div v-else-if="!isLabelsLoading" class="biz-tip mt10 biz-danger">
                                                {{curService.deploy_tag_list.length ? '关联的应用没有公共的标签（注：Key、Value都相同的标签为公共标签）' : '请先关联应用'}}
                                            </div>
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
                                                    :list="serviceTypeList"
                                                    @item-selected="selectServiceType">
                                                </bk-selector>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="bk-form-item" v-show="curService.config.spec.type !== 'NodePort'">
                                        <label class="bk-label" style="width: 130px;">ClusterIP：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <input type="text" class="bk-form-input" placeholder="请输入ClusterIP" style="width: 310px;" v-model="curService.config.spec.clusterIP">
                                            <p class="biz-tip mt10">不填或None</p>
                                        </div>
                                    </div>
                                    <div class="bk-form-item">
                                        <label class="bk-label" style="width: 130px;">端口映射：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <div class="biz-keys-list mb10">
                                                <template v-if="curService.deploy_tag_list.length">
                                                    <template v-if="appPortList.length && curService.config.spec.ports.length">
                                                        <table class="biz-simple-table">
                                                            <thead>
                                                                <tr>
                                                                    <th style="width: 100px;">端口名称</th>
                                                                    <th style="width: 100px;">端口</th>
                                                                    <th style="width: 120px;">协议</th>
                                                                    <th style="width: 120px;">目标端口</th>
                                                                    <th style="width: 100px;" v-if="curService.config.spec.type === 'NodePort'">NodePort</th>
                                                                    <th></th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                <tr v-for="(port, index) in curService.config.spec.ports" :key="index">
                                                                    <td>
                                                                        <bk-input
                                                                            type="text"
                                                                            placeholder="请输入"
                                                                            style="width: 100px;"
                                                                            :value.sync="port.name"
                                                                            :list="varList"
                                                                        >
                                                                        </bk-input>
                                                                    </td>
                                                                    <td>
                                                                        <bk-input
                                                                            type="number"
                                                                            placeholder="请输入"
                                                                            style="width: 100px;"
                                                                            :min="1"
                                                                            :max="65535"
                                                                            :value.sync="port.port"
                                                                            :list="varList"
                                                                        >
                                                                        </bk-input>
                                                                    </td>
                                                                    <td>
                                                                        <bk-selector
                                                                            placeholder="协议"
                                                                            :setting-key="'id'"
                                                                            :allow-clear="true"
                                                                            :selected.sync="port.protocol"
                                                                            :list="protocolList">
                                                                        </bk-selector>
                                                                    </td>
                                                                    <td>
                                                                        <bk-selector
                                                                            placeholder="请选择"
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
                                                                    <td v-if="curService.config.spec.type === 'NodePort'">
                                                                        <bk-input
                                                                            type="number"
                                                                            placeholder="请输入"
                                                                            style="width: 76px;"
                                                                            :min="0"
                                                                            :max="32767"
                                                                            :disabled="curService.config.spec.type !== 'NodePort'"
                                                                            :value.sync="port.nodePort"
                                                                            :list="varList"
                                                                        >
                                                                        </bk-input>
                                                                        <bk-tooltip placement="top">
                                                                            <i class="bk-icon icon-question-circle" style="vertical-align: middle; cursor: pointer;"></i>
                                                                            <div slot="content">
                                                                                输入node port值，值的范围为[30000-32767]；或者不填写，k8s会生成一个可用的随机端口，此时，可在 网络->Service 查看node port值

                                                                            </div>
                                                                        </bk-tooltip>
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
                                                        <p class="mt5 biz-tip biz-danger">请先填写已关联应用的容器端口映射信息</p>
                                                    </template>
                                                </template>
                                                <template v-else>
                                                    <p class="mt5 biz-tip biz-danger">请先关联应用</p>
                                                </template>
                                                <p class="biz-tip">
                                                    ClusterIP为None时，端口映射可以不填；否则请先关联应用后，再填写端口映射
                                                    <a href="javascript:void(0);" class="bk-text-button" @click="showPortExampleDialg">查看示例</a>
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="bk-form-item">
                                        <label class="bk-label" style="width: 130px;">标签管理：</label>
                                        <div class="bk-form-content" style="margin-left: 130px;">
                                            <bk-keyer :key-list.sync="curLabelList" ref="labelKeyer" @change="updateLabelList" :var-list="varList"></bk-keyer>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
            <bk-dialog
                :is-show.sync="exampleDialogConf.isShow"
                :width="exampleDialogConf.width"
                :title="exampleDialogConf.title"
                :close-icon="exampleDialogConf.closeIcon"
                :has-footer="false"
                :ext-cls="'biz-example-dialog'"
                @cancel="exampleDialogConf.isShow = false">
                <template slot="content">
                    <img src="@open/images/service-example.png">
                </template>
            </bk-dialog>
        </template>
    </div>
</template>

<script>
    import serviceParams from '@open/json/k8s-service.json'
    import bkKeyer from '@open/components/keyer'
    import header from './header.vue'
    import tabs from './tabs.vue'
    import mixinBase from '@open/mixins/configuration/mixin-base'
    import k8sBase from '@open/mixins/configuration/k8s-base'

    export default {
        components: {
            'bk-keyer': bkKeyer,
            'biz-header': header,
            'biz-tabs': tabs
        },
        mixins: [mixinBase, k8sBase],
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
                exampleDialogConf: {
                    isShow: false,
                    title: '端口映射示例',
                    width: 800,
                    closeIcon: true
                },
                isLabelsLoading: true,
                serviceTypeList: [
                    {
                        id: 'ClusterIP',
                        name: 'ClusterIP'
                    },
                    {
                        id: 'NodePort',
                        name: 'NodePort'
                    }
                ],
                weight: 10,
                curServiceIPs: '',
                linkAppVersion: 0,
                protocolIndex: -1,
                protocolList: [
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
                appLabels: [],
                curServiceCache: Object.assign({}, serviceParams),
                curService: serviceParams
            }
        },
        computed: {
            varList () {
                return this.$store.state.variable.varList
            },
            curTemplate () {
                return this.$store.state.k8sTemplate.curTemplate
            },
            applicationList () {
                const data = this.$store.state.k8sTemplate.linkApplications
                return data
            },
            isTemplateSaving () {
                return this.$store.state.k8sTemplate.isTemplateSaving
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
            },
            curServicePortList () {
                const results = []
                const ports = this.curService.config.spec.ports
                ports.forEach(item => {
                    results.push(item.targetPort)
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
            'deployments' () {
                if (this.curVersion) {
                    this.initApplications(this.curVersion)
                }
            },
            'daemonsets' () {
                if (this.curVersion) {
                    this.initApplications(this.curVersion)
                }
            },
            'jobs' () {
                if (this.curVersion) {
                    this.initApplications(this.curVersion)
                }
            },
            'statefulsets' () {
                if (this.curVersion) {
                    this.initApplications(this.curVersion)
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
            showPortExampleDialg () {
                this.exampleDialogConf.isShow = true
            },
            selectLabel (labels) {
                labels.isSelected = !labels.isSelected
                this.curService.config.webCache.link_labels = []
                this.curService.config.spec.selector = {}
                this.appLabels.forEach(label => {
                    if (label.isSelected) {
                        this.curService.config.webCache.link_labels.push(label.id)
                        this.curService.config.spec.selector[label.key] = label.value
                    }
                })
            },
            selectServiceType (index, item) {
                if (index !== 'NodePort') {
                    this.curService.config.spec.ports.forEach(port => {
                        port.nodePort = ''
                    })
                }
            },
            async initResource (data) {
                const version = data.latest_version_id || data.version
                if (version) {
                    await this.initApplications(version)
                }

                if (data.services && data.services.length) {
                    this.setCurService(data.services[0], 0)
                }
            },
            async tabResource (type, target) {
                this.isTabChanging = true
                await this.$refs.commonHeader.autoSaveResource(type)
                this.$refs.commonTab.goResource(target)
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
            selectPort (port) {
                const id = port.id
                this.appPortList.forEach(item => {
                    if (item.id === id) {
                        port.targetPort = item.name
                    }
                })
            },
            clearPort (port) {
                port.targetPort = ''
            },
            toggleRouter (target) {
                this.$router.push({
                    name: target,
                    params: {
                        projectId: this.projectId,
                        templateId: this.templateId
                    }
                })
            },
            addPort () {
                const ports = this.curService.config.spec.ports
                const port = {
                    'id': '',
                    'name': '',
                    'port': '',
                    'protocol': 'TCP',
                    'targetPort': '',
                    'nodePort': ''
                }
                ports.push(port)
            },
            removePort (port, index) {
                const ports = this.curService.config.spec.ports
                ports.splice(index, 1)
            },
            initApplications (version) {
                const projectId = this.projectId
                this.linkAppVersion = version
                this.$store.dispatch('k8sTemplate/getAppsByVersion', { projectId, version }).then(res => {
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
            updateLocalData (data) {
                if (data.id) {
                    this.curService.id = data.id
                }
                if (data.version) {
                    this.$store.commit('k8sTemplate/updateCurVersion', data.version)
                }
                this.$store.commit('k8sTemplate/updateServices', this.services)
                setTimeout(() => {
                    this.services.forEach(item => {
                        if (item.id === data.id) {
                            this.setCurService(item)
                        }
                    })
                }, 500)
            },
            setCurService (service, index) {
                this.isLabelsLoading = true
                this.curService = service
                this.curServiceIPs = this.curService.config.spec.clusterIP
                if (!this.curService.config.spec.ports.length) {
                    this.addPort()
                }
                clearInterval(this.compareTimer)
                clearTimeout(this.setTimer)
                this.setTimer = setTimeout(() => {
                    if (!this.curService.cache) {
                        this.curService.cache = JSON.parse(JSON.stringify(service))
                    }
                    this.appPortList = []
                    this.initLinkResource()
                    this.watchChange()
                }, 500)
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
                }, 1000)
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
            selectApps (appIds, data) {
                this.curService.config.webCache.link_labels = []
                this.curService.config.spec.selector = {}
                this.getPorts(appIds)
                this.getLabels(appIds)
                // 如果关联应用, 且clusterIp为None
                if (appIds && appIds.length) {
                    if (this.curService.config.spec.clusterIP === 'None') {
                        this.curService.config.spec.clusterIP = ''
                    }
                } else {
                    if (!this.curService.config.spec.clusterIP) {
                        this.curService.config.spec.clusterIP = 'None'
                    }
                }
            },
            initLinkResource () {
                const appIds = []
                const appKeys = []

                // 过滤已经删除的app
                this.applicationList.forEach(item => {
                    item.children.forEach(child => {
                        appKeys.push(child.deploy_tag)
                    })
                })
                this.curService.deploy_tag_list.forEach(item => {
                    if (appKeys.includes(item)) {
                        appIds.push(item)
                    }
                })
                this.getPorts(appIds)
                this.getLabels(appIds)
            },
            getLabels (apps) {
                this.isLabelsLoading = true
                const projectId = this.projectId
                const version = this.curVersion

                this.$store.dispatch('k8sTemplate/getLabelsByDeployments', { projectId, version, apps }).then(res => {
                    if (!res.data) {
                        return false
                    }
                    const labels = []
                    for (const key in res.data) {
                        const params = {
                            id: key + ':' + res.data[key],
                            key: key,
                            value: res.data[key],
                            isSelected: false
                        }
                        if (this.curService.config.webCache.link_labels && this.curService.config.webCache.link_labels.indexOf(params.id) > -1) {
                            params.isSelected = true
                        }
                        labels.push(params)
                    }
                    this.appLabels.splice(0, this.appLabels.length, ...labels)
                }, res => {
                    this.appLabels.splice(0, this.appLabels.length)
                }).finally(() => {
                    this.isLabelsLoading = false
                })
            },
            getPorts (apps) {
                const projectId = this.projectId
                const version = this.curVersion
                setTimeout(() => {
                    this.$store.dispatch('k8sTemplate/getPortsByDeployments', { projectId, version, apps }).then(res => {
                        if (!res.data) {
                            return false
                        }
                        const ports = res.data.filter(item => {
                            return item.name
                        })
                        const keys = []
                        let results = []
                        ports.forEach(port => {
                            keys.push(port.id)
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
                        this.curService.config.spec.ports.splice(0, this.appPortList.length)
                    })
                }, 300)
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
                const serviceId = service.id

                this.$bkInfo({
                    title: '确认',
                    content: this.$createElement('p', { style: { 'text-align': 'center' } }, `删除Service：${service.config.metadata.name || '未命名'}`),
                    confirmFn () {
                        if (serviceId.indexOf && serviceId.indexOf('local_') > -1) {
                            self.removeLocalService(service, index)
                        } else {
                            self.deleteService(service, index)
                        }
                    }
                })
            },
            async deleteService (service, index) {
                const projectId = this.projectId
                const version = this.curVersion
                const serviceId = service.id

                try {
                    const res = await this.$store.dispatch('k8sTemplate/removeService', { serviceId, version, projectId })
                    const data = res.data
                    this.removeLocalService(service, index)

                    if (data.version) {
                        this.$store.commit('k8sTemplate/updateCurVersion', data.version)
                        this.$store.commit('k8sTemplate/updateBindVersion', true)
                    }
                    this.unBindStatefulset(service, data.version)
                } catch (res) {
                    const message = res.message
                    this.$bkMessage({
                        theme: 'error',
                        message: message
                    })
                }
            },
            async unBindStatefulset (service, version) {
                const statefulsetItem = service.deploy_tag_list.find(item => {
                    return item.indexOf('K8sStatefulSet') > -1
                })

                if (statefulsetItem) {
                    const statefulsetId = statefulsetItem.split('|')[0]
                    try {
                        // 绑定
                        this.statefulsets.forEach(statefulset => {
                            // 把其它已经绑定的statefulset进行解绑
                            if (statefulset.deploy_tag === statefulsetId) {
                                statefulset.service_tag = ''
                                this.$store.dispatch('k8sTemplate/bindServiceForStatefulset', {
                                    projectId: this.projectId,
                                    versionId: version,
                                    statefulsetId: statefulset.deploy_tag,
                                    data: {
                                        service_tag: ''
                                    }
                                })
                            }
                        })
                    } catch (res) {
                        this.$bkMessage({
                            theme: 'error',
                            message: res.message,
                            hasCloseIcon: true
                        })
                    }
                }
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
                this.$store.commit('k8sTemplate/updateServices', this.services)
            },
            updateLabelList (list, data) {
                if (!this.curService.config.webCache) {
                    this.curService.config.webCache = {}
                }
                this.curService.config.webCache.labelListCache = list
            }
        }
    }
</script>

<style scoped>
    @import './service.css';
</style>
