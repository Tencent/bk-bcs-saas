<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="biz-helm-title">
                <a class="bk-icon icon-arrows-left back" @click="goTplList"></a>
                <span>Chart详情</span>
            </div>
            <div class="biz-actions" style="top: 11px;">
                <router-link :to="{ name: 'helmTplInstance', params: { tplId: curTpl.id } }" :class="['bk-button bk-primary']">
                    部署
                </router-link>
            </div>
        </div>

        <div class="biz-content-wrapper" v-bkloading="{ isLoading: createInstanceLoading }">
            <div>
                <div class="biz-helm-header">
                    <div class="left">
                        <svg style="display: none;">
                            <title>模板集默认图标</title>
                            <symbol id="biz-set-icon" viewBox="0 0 32 32">
                                <path d="M6 3v3h-3v23h23v-3h3v-23h-23zM24 24v3h-19v-19h19v16zM27 24h-1v-18h-18v-1h19v19z"></path>
                                <path d="M13.688 18.313h-6v6h6v-6z"></path>
                                <path d="M21.313 10.688h-6v13.625h6v-13.625z"></path>
                                <path d="M13.688 10.688h-6v6h6v-6z"></path>
                            </symbol>
                        </svg>
                        <div class="info">
                            <div class="logo-wrapper" v-if="curTpl.icon && isImage(curTpl.icon)">
                                <img :src="curTpl.icon" style="width: 100px;">
                            </div>
                            <svg class="logo" v-else>
                                <use xlink:href="#biz-set-icon"></use>
                            </svg>
                            <div class="title">{{curTpl.name}}</div>
                            <div class="desc" :title="curTpl.description">
                                <span>简介：</span>
                                {{curTpl.description || '--'}}
                            </div>
                        </div>
                    </div>

                    <div class="right">
                        <div class="bk-collapse biz-collapse">
                            <div class="bk-collapse-item bk-collapse-item-active">
                                <div class="bk-collapse-item-header" style="cursor: default;">
                                    版本
                                </div>
                                <div class="bk-collapse-item-content f13" style="padding: 15px;">
                                    <div class="config-box">
                                        <div class="inner">
                                            <label class="title">Chart版本</label>
                                            <bk-selector :placeholder="'请选择'"
                                                style="width: 560px;"
                                                :selected.sync="tplsetVerIndex"
                                                :list="curTplVersions"
                                                :setting-key="'id'"
                                                :display-key="'version'"
                                                @item-selected="getTplDetail">
                                            </bk-selector>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="tplsetVerIndex" v-bkloading="{ isLoading: isVersionLoading }">
                    <bk-tab :active-name="'files'" class="mt20">
                        <bk-tabpanel name="files" title="资源文件">
                            <template v-if="previewList.length">
                                <div class="biz-resource-wrapper">
                                    <div class="tree-box" style="max-height: 500px;">
                                        <bk-tree
                                            ref="tree1"
                                            :data="treeData"
                                            :node-key="'id'"
                                            :has-border="true"
                                            @on-click="getFileDetail">
                                        </bk-tree>
                                    </div>
                                    <div class="resource-box">
                                        <div class="biz-code-wrapper">
                                            <ace
                                                :value="curReourceFile.value"
                                                :width="editorConfig.width"
                                                :height="editorConfig.height"
                                                :lang="editorConfig.lang"
                                                :read-only="editorConfig.readOnly"
                                                :full-screen="editorConfig.fullScreen">
                                            </ace>
                                        </div>
                                    </div>
                                </div>
                            </template>
                            <template v-else>
                                <div class="bk-message-box">
                                    <p class="message empty-message">无数据</p>
                                </div>
                            </template>
                        </bk-tabpanel>
                        <bk-tabpanel name="readme" title="详细说明">
                            <template v-if="curTplReadme">
                                <div class="p20">
                                    <div class="biz-scroller-container">
                                        <pre style="white-space: pre-line;">{{curTplReadme}}</pre>
                                    </div>
                                </div>
                            </template>
                            <template v-else>
                                <div class="bk-message-box">
                                    <p class="message empty-message">无数据</p>
                                </div>
                            </template>
                        </bk-tabpanel>
                    </bk-tab>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import path2tree from '@open/common/path2tree'
    import baseMixin from '@open/mixins/helm/mixin-base'
    import { catchErrorHandler } from '@open/common/util'

    export default {
        mixins: [baseMixin],
        data () {
            return {
                curTplReadme: '',
                yamlEditor: null,
                yamlFile: '',
                curTplYaml: '',
                activeName: ['config'],
                collapseName: ['var'],
                tplsetVerList: [],
                formData: {},
                createInstanceLoading: false,
                previewList: [],
                curReourceFile: {
                    name: '',
                    value: ''
                },
                isVersionLoading: true,
                tplPreviewList: [],
                difference: '',
                previewInstanceLoading: true,
                editor: null,
                curTpl: {
                    data: {
                        name: ''
                    }
                },
                editorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'yaml',
                    readOnly: true,
                    fullScreen: false,
                    values: [],
                    editors: []
                },
                curTplVersions: [],
                tplsetVerIndex: '',
                namespaceId: '',
                answers: {},
                namespaceList: [],
                curLabelList: [
                    {
                        key: '',
                        value: ''
                    }
                ],
                treeData: []
            }
        },
        computed: {
            curProject () {
                return this.$store.state.curProject
            },
            projectId () {
                return this.$route.params.projectId
            },
            tplList () {
                return this.$store.state.helm.tplList
            }
        },
        async mounted () {
            const tplId = this.$route.params.tplId
            this.curTpl = await this.getTplById(tplId)
            this.getTplVersions(tplId)
            this.getNamespaceList()
        },
        methods: {
            /**
             * 返回chart 模版列表
             */
            goTplList () {
                const projectCode = this.$route.params.projectCode
                this.$router.push({
                    name: 'helmTplList',
                    params: {
                        projectCode: projectCode
                    }
                })
            },

            /**
             * 获取文件详情
             * @param  {object} file 文件
             */
            getFileDetail (file) {
                if (file.hasOwnProperty('value')) {
                    this.curReourceFile = file
                }
            },

            /**
             * 获取模板
             * @param  {number} id 模板ID
             * @return {object} result 模板
             */
            async getTplById (id) {
                let result = {}
                let list = this.tplList
                // 如果没有缓存，获取远程数据
                if (!list.length) {
                    try {
                        const projectId = this.projectId
                        const res = await this.$store.dispatch('helm/asyncGetTplList', projectId)
                        list = res.data
                    } catch (e) {
                        catchErrorHandler(e, this)
                    }
                }

                list.forEach(item => {
                    // 跟由获取的id为string，转number
                    if (item.id === Number(id)) {
                        result = item
                    }
                })
                return result
            },

            /**
             * 根据版本号获取模板详情
             * @param  {number} index 索引
             * @param  {object} data 数据
             */
            async getTplDetail (index, data) {
                const list = []
                const projectId = this.projectId
                const version = index
                const chartId = this.$route.params.tplId

                this.isVersionLoading = true
                this.treeData = []

                try {
                    const res = await this.$store.dispatch('helm/getChartByVersion', {
                        projectId,
                        chartId,
                        version
                    })

                    const tplData = res.data
                    const files = tplData.data.files
                    const tplName = tplData.name
                    this.formData = tplData.data.questions

                    for (const key in files) {
                        list.push({
                            name: key,
                            value: files[key]
                        })
                    }

                    this.previewList.splice(0, this.previewList.length, ...list)
                    const tree = path2tree(this.previewList, { expandIndex: 0 })
                    this.treeData.push(tree)
                    this.curTplReadme = files[`${tplName}/README.md`]
                    this.curTplYaml = files[`${tplName}/values.yaml`]

                    // default: 显示第一个
                    if (this.previewList.length) {
                        this.curReourceFile = this.previewList[0]
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                } finally {
                    this.isVersionLoading = false
                }
            },

            /**
             * 获取模板版本列表
             * @param  {number} tplId 模板ID
             */
            async getTplVersions (tplId) {
                const projectId = this.projectId

                try {
                    const res = await this.$store.dispatch('helm/getTplVersions', { projectId, tplId })

                    this.curTplVersions = res.data.results
                    if (this.curTplVersions.length) {
                        const firstVersion = this.curTplVersions[0]
                        const versionId = firstVersion.id

                        this.tplsetVerIndex = versionId
                        this.getTplDetail(versionId, firstVersion)
                    }
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            },

            /**
             * 获取命名空间列表
             */
            async getNamespaceList () {
                const projectId = this.projectId

                try {
                    const res = await this.$store.dispatch('helm/getNamespaceList', projectId)
                    this.namespaceList = res.data
                } catch (e) {
                    catchErrorHandler(e, this)
                }
            }
        }
    }
</script>

<style scoped>
    @import './common.css';
    @import './tpl-detail.css';
</style>
