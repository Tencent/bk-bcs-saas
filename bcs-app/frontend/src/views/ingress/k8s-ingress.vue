<template>
    <div class="bk-form biz-configuration-form">
        <div class="bk-form-item">
            <div class="bk-form-item">
                <div class="bk-form-content" style="margin-left: 0;">
                    <div class="bk-form-item is-required">
                        <label class="bk-label" style="width: 130px;">{{$t('名称')}}：</label>
                        <div class="bk-form-content" style="margin-left: 130px;">
                            <input type="text" :class="['bk-form-input',{ 'is-danger': errors.has('applicationName') }]" :placeholder="$t('请输入64个字符以内')" style="width: 310px;" v-model="curIngress.config.metadata.name" maxlength="64" name="applicationName" v-validate="{ required: true, regex: /^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$/ }">
                        </div>
                        <div class="bk-form-tip is-danger" style="margin-left: 130px;" v-if="errors.has('applicationName')">
                            <p class="bk-tip-text">{{$t('名称必填，以小写字母或数字开头和结尾，只能包含：小写字母、数字、连字符(-)、点(.)')}}</p>
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
                                        <tr v-for="(computer, index) in curIngress.config.spec.tls" :key="index">
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
                                                    :allow-clear="true"
                                                    :has-create-item="true"
                                                    :setting-key="'certId'"
                                                    :display-key="'certName'"
                                                    :is-loading="isCertListLoading"
                                                    :selected.sync="computer.certId"
                                                    :list="certList"
                                                    :tools="certTools"
                                                    @item-selected="handlerSelectCert(computer, ...arguments)"
                                                    @edit="editBcsTls"
                                                    @del="deleteBcsTls(computer, ...arguments)"
                                                >
                                                    <div class="bk-selector-create-item" slot="newItem" @click="goCertList" v-if="certListUrl">
                                                        <i class="bk-icon icon-apps"></i>
                                                        <i class="text">{{$t('证书列表')}}</i>
                                                    </div>
                                                    <div class="bk-selector-create-item" slot="newItem" @click="showBcsTlsEditor">
                                                        <i class="bk-icon icon-plus-circle"></i>
                                                        <i class="text">{{$t('新建证书')}}</i>
                                                    </div>
                                                </bk-selector>
                                            </td>
                                            <td>
                                                <button class="action-btn ml5" @click.stop.prevent="addTls">
                                                    <i class="bk-icon icon-plus"></i>
                                                </button>
                                                <button class="action-btn" v-if="curIngress.config.spec.tls.length > 1" @click.stop.prevent="removeTls(index, computer)">
                                                    <i class="bk-icon icon-minus">{{$t('新建证书')}}</i>
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
                    <div class="item" v-for="(rule, index) in curIngress.config.spec.rules" :key="index">
                        <button :class="['bk-button bk-default is-outline', { 'is-selected': curRuleIndex === index }]" @click.stop="setCurRule(rule, index)">
                            {{rule.host || $t('未命名')}}
                        </button>
                        <span class="bk-icon icon-close-circle" @click.stop="removeRule(index)" v-if="curIngress.config.spec.rules.length > 1"></span>
                    </div>
                    <bk-tooltip ref="containerTooltip" :content="curIngress.config.spec.rules.length >= 5 ? $t('最多添加5个') : $t('添加Rule')" placement="top">
                        <button type="button" class="bk-button bk-default is-outline is-icon" :disabled="curIngress.config.spec.rules.length >= 5 " @click.stop.prevent="addLocalRule">
                            <i class="bk-icon icon-plus"></i>
                        </button>
                    </bk-tooltip>
                </div>
            </div>

            <bk-dialog
                :title="tlsParams.id ? $t('编辑证书') : $t('新建证书')"
                :is-show.sync="certKeyConf.isShow"
                :width="800"
                :quick-close="false"
                :content="certKeyConf.content"
                @confirm="saveBcsTls"
                @cancel="certKeyConf.isShow = false">
                <template slot="content">
                    <form class="bk-form">
                        <div class="bk-form-item is-required">
                            <label class="bk-label" style="width: 80px;">Name：</label>
                            <div class="bk-form-content" style="margin-left: 80px;">
                                <input class="bk-form-input" v-model="tlsParams.name" :placeholder="$t('请输入名称，英文大小写、数字、下划线和英文句号，最大长度为64个字符')" maxlength="64" />
                            </div>
                        </div>
                        <div class="bk-form-item is-required">
                            <label class="bk-label" style="width: 80px;">Cert：</label>
                            <div class="bk-form-content" style="margin-left: 80px;">
                                <textarea class="bk-form-textarea" v-model="tlsParams.cert" style="height: 130px;" :placeholder="$t('请输入证书')"></textarea>
                            </div>
                        </div>
                        <div class="bk-form-item is-required">
                            <label class="bk-label" style="width: 80px;">Key：</label>
                            <div class="bk-form-content" style="margin-left: 80px;">
                                <textarea class="bk-form-textarea" v-model="tlsParams.key" style="height: 130px;" :placeholder="$t('请输入私钥')"></textarea>
                            </div>
                        </div>
                    </form>
                </template>
            </bk-dialog>

            <div class="bk-form biz-configuration-form pb15">
                <div class="biz-span">
                    <span class="title">{{$t('基础信息')}}</span>
                </div>
                <div class="bk-form-item is-required">
                    <label class="bk-label" style="width: 130px;">{{$t('虚拟主机名')}}：</label>
                    <div class="bk-form-content" style="margin-left: 130px;">
                        <input type="text" :class="['bk-form-input']" :placeholder="$t('请输入30个字符以内')" style="width: 310px;" v-model="curRule.host" maxlength="30" name="ruleName">
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
        </div>
    </div>
</template>
<script>
    import bkKeyer from '@open/components/keyer'
    import ingressParams from '@open/json/k8s-ingress.json'
    import ruleParams from '@open/json/k8s-ingress-rule.json'
    import { catchErrorHandler } from '@open/common/util'

    export default {
        components: {
            bkKeyer
        },
        props: {
            ingressData: {
                type: Object,
                default () {
                    return JSON.parse(JSON.stringify(ingressParams))
                }
            }
        },
        data () {
            return {
                certKey: '',
                curRuleIndex: 0,
                isPanelShow: false,
                isTlsPanelShow: false,
                isCertListLoading: false,
                curIngress: this.ingressData,
                curRule: this.ingressData.config.spec.rules[0],
                computerList: [{
                    name: '',
                    cert: ''
                }],
                tlsParams: {
                    name: '',
                    cert: '',
                    key: ''
                },
                curComputer: {
                    certKey: ''
                },
                certKeyConf: {
                    isShow: false
                },
                certTools: {
                    edit: true,
                    del: true
                }
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            linkServices () {
                const list = this.$store.state.k8sTemplate.linkServices.map(item => {
                    item._id = item.service_tag
                    item._name = item.service_name
                    return item
                })
                list.forEach(item => {
                    list[item.service_name] = []
                    item.service_ports.forEach(port => {
                        list[item.service_name].push({
                            _id: port,
                            _name: port
                        })
                    })
                })
                return list
            },
            serviceNames () {
                return this.$store.state.k8sTemplate.linkServices.map(item => {
                    return item.service_name
                })
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
                // 如果有缓存直接使用
                if (this.curIngress.config.webCache && this.curIngress.config.webCache.labelListCache) {
                    return this.curIngress.config.webCache.labelListCache
                }
                const labels = this.curIngress.config.metadata.labels
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
                // 如果有缓存直接使用
                if (this.curIngress.config.webCache && this.curIngress.config.webCache.remarkListCache) {
                    return this.curIngress.config.webCache.remarkListCache
                }
                const annotations = this.curIngress.config.metadata.annotations
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
        mounted () {
            this.$nextTick(() => {
                this.checkService()
            })
        },
        methods: {
            /**
             *  选择证书回调
             * @param  {object} computer 证书
             * @param  {number} index 证书索引
             * @param  {object} data  证书对象
             */
            handlerSelectCert (computer, index, data) {
                computer.certType = data.certType
            },
            /**
             * 编辑证书
             * @param  {number} index 索引
             */
            async editBcsTls (index) {
                const projectId = this.projectId
                const tls = this.certList[index]
                const certId = tls.certId

                try {
                    const res = await this.$store.dispatch('k8sTemplate/getBcsTlsDetail', { projectId, certId })
                    this.tlsParams = res.data
                    this.certKeyConf.isShow = true
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },
            /**
             * 删除当前的密钥
             * @param {object} computer 当前主机
             * @param {number} index 证书索引
             */
            async deleteBcsTls (computer, index) {
                const projectId = this.projectId
                const tls = this.certList[index]
                const certId = tls.certId
                const me = this

                me.$bkInfo({
                    title: ``,
                    clsName: 'biz-remove-dialog',
                    content: this.$createElement('p', {
                        class: 'biz-confirm-desc'
                    }, `${this.$t('确认要删除证书')}【${certId}？】`),
                    async confirmFn () {
                        try {
                            await me.$store.dispatch('k8sTemplate/deleteBcsTls', { projectId, certId })
                            me.$bkMessage({
                                theme: 'success',
                                message: this.$t('删除成功')
                            })
                            me.isCertListLoading = true
                            me.resetSelectedTls(certId)
                            await me.$store.dispatch('k8sTemplate/getCertList', projectId)
                            me.isCertListLoading = false
                        } catch (e) {
                            catchErrorHandler(e, me)
                        }
                    }
                })
            },

            /**
             * 当删除证书回调，将已经选择此证书的给清空
             * @param  {number} certId certId
             */
            resetSelectedTls (certId) {
                const tlsList = this.curIngress.config.spec.tls
                tlsList.forEach(tls => {
                    if (tls.certId === certId) {
                        tls.certId = ''
                    }
                })
            },

            /**
             * 保存当前的密钥
             */
            async saveBcsTls () {
                const nameReg = /^[A-Za-z0-9_.]{1,64}$/

                if (!this.tlsParams.name) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入Name')
                    })
                    return false
                }

                if (!nameReg.test(this.tlsParams.name)) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('Name错误，只能包含英文大小写、数字、下划线和英文句号')
                    })
                    return false
                }

                if (!this.tlsParams.cert) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入Cert')
                    })
                    return false
                }

                if (!this.tlsParams.key) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('请输入Key')
                    })
                    return false
                }

                const projectId = this.projectId
                const data = this.tlsParams
                try {
                    if (this.tlsParams.id) {
                        const certId = this.tlsParams.id
                        await this.$store.dispatch('k8sTemplate/updateBcsTls', { projectId, certId, data })
                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('更新证书成功')
                        })
                    } else {
                        await this.$store.dispatch('k8sTemplate/createBcsTls', { projectId, data })
                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('创建证书成功')
                        })
                    }

                    this.hideCertKeyEditor()
                    this.isCertListLoading = true
                    await this.$store.dispatch('k8sTemplate/getCertList', projectId)
                    this.isCertListLoading = false
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 显示证书密钥编辑
             * @return {object} computer 证书
             */
            showBcsTlsEditor (computer) {
                this.tlsParams = {
                    name: '',
                    cert: '',
                    key: ''
                }
                this.certKeyConf.isShow = true
            },

            /**
             * 隐藏证书密钥编辑
             */
            hideCertKeyEditor () {
                this.certKeyConf.isShow = false
            },

            goCertList () {
                if (this.certListUrl) {
                    window.open(this.certListUrl)
                }
            },
            addTls () {
                this.curIngress.config.spec.tls.push({
                    hosts: '',
                    certId: ''
                })
            },
            removeTls (index, curTls) {
                this.curIngress.config.spec.tls.splice(index, 1)
            },
            togglePanel () {
                this.isTlsPanelShow = false
                this.isPanelShow = !this.isPanelShow
            },
            toggleTlsPanel () {
                this.isPanelShow = false
                this.isTlsPanelShow = !this.isTlsPanelShow
            },
            setCurRule (rule, index) {
                this.curRule = rule
                this.curRuleIndex = index
            },
            removeRule (index) {
                const rules = this.curIngress.config.spec.rules
                rules.splice(index, 1)
                if (this.curRuleIndex === index) {
                    this.curRuleIndex = 0
                } else {
                    this.curRuleIndex = this.curRuleIndex - 1
                }

                this.curRule = rules[this.curRuleIndex]
            },
            addLocalRule () {
                const rule = JSON.parse(JSON.stringify(ruleParams))
                const rules = this.curIngress.config.spec.rules
                const index = rules.length
                rule.host = 'rule-' + (index + 1)
                rules.push(rule)
                this.setCurRule(rule, index)
                this.$refs.containerTooltip.visible = false
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
            checkService (pathRule) {
                const rules = this.curIngress.config.spec.rules
                for (const rule of rules) {
                    const paths = rule.http.paths
                    for (const path of paths) {
                        if (path.backend.serviceName && !this.serviceNames.includes(path.backend.serviceName)) {
                            this.$bkMessage({
                                theme: 'error',
                                message: this.$t('{name}中路径组：关联的Service【{serviceName}】不存在，请重新绑定', {
                                    name: this.curIngress.config.metadata.name,
                                    serviceName: path.backend.serviceName
                                }),
                                delay: 5000
                            })
                            return false
                        }
                    }
                }
                return true
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '@open/css/variable.css';
    @import '@open/css/mixins/clearfix.css';

    .biz-simple-table {
        width: auto;
    }
    .action-btn {
        height: 36px;
        text-align: center;
        display: inline-block;
        border: none;
        background: transparent;
        outline: none;
        float: left;
        .bk-icon {
            width: 24px;
            height: 24px;
            line-height: 24px;
            border-radius: 50%;
            vertical-align: middle;
            border: 1px solid #dde4eb;
            color: #737987;
            font-size: 14px;
            display: inline-block;
            &.icon-minus {
                font-size: 15px;
            }
        }
    }
    .biz-part-header {
        margin-top: 40px;
        text-align: center;
    }
    .bk-text-button {
        .bk-icon {
            transition: all ease 0.3s;
        }
        &.rotate {
            .bk-icon {
                transform: rotate(180deg);
            }
        }
    }
    .bk-button-group {
        @mixin clearfix;
        .item {
            position: relative;
            display: inline-block;
            float: left;

            &:hover {
                z-index: 10;
                >.bk-icon {
                    display: inline-block;
                }
            }

            &:first-child {
                .bk-button {
                    border-radius: 2px 0 0 2px;
                }
            }

            >.bk-button {
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
                border-radius: 0;
                &.is-selected {
                    background-color: #c3cdd7 !important;
                    border-color: #c3cdd7 !important;
                }
            }

            >.bk-icon {
                cursor: pointer;
                background: #fff;
                position: absolute;
                border-radius: 50%;
                right: -5px;
                top: -5px;
                display: none;
                font-size: 16px;
                z-index: 1;
                color: $primaryColor;
                &:hover {
                    color: $primaryColor;
                }
            }
        }
    }
    .bk-form .bk-form-content .bk-form-tip {
        overflow: hidden;
        padding: 0;
        margin: 10px 0 0 0;
        position: relative;
        height: auto;
        line-height: 1;
        left: 0;
    }
</style>
