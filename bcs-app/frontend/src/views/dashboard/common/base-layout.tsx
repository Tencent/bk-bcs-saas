import { defineComponent, computed, ref, watch, onMounted, toRefs } from '@vue/composition-api'
import DashboardTopActions from './dashboard-top-actions'
import useCluster from './use-cluster'
import useInterval from './use-interval'
import useNamespace from './use-namespace'
import usePage from './use-page'
import useSearch from './use-search'
import useSubscribe from './use-subscribe'
import useTableData from './use-table-data'
import { sort } from '@/common/util'
import yamljs from 'js-yaml'
import * as ace from '@/components/ace-editor'
import './base-layout.css'

export default defineComponent({
    name: 'BaseLayout',
    components: {
        ace
    },
    props: {
        title: {
            type: String,
            default: '',
            required: true
        },
        // 父分类，eg: workloads、networks（注意复数）
        type: {
            type: String,
            default: '',
            required: true
        },
        // 子分类，eg: deployments、ingresses
        category: {
            type: String,
            default: '',
            required: true
        },
        // 轮询时类型，eg: Deployment、Ingress（注意首字母大写）
        kind: {
            type: String,
            default: '',
            required: true
        },
        // 是否显示命名空间（不展示的话不会发送获取命名空间列表的请求）
        showNameSpace: {
            type: Boolean,
            default: true
        }
    },
    setup (props, ctx) {
        const { $router, $i18n } = ctx.root
        const { type, category, kind, showNameSpace } = toRefs(props)
        // 模糊搜索字段
        const keys = ref(['metadata.name'])
        // 命名空间
        const namespaceValue = ref('')
        // 详情侧栏
        const showDetailPanel = ref(false)
        // 当前详情行数据
        const curDetailRow = ref<any>({
            data: {},
            extData: {}
        })
        // 侧栏展示类型
        const detailType = ref({
            active: 'overview',
            list: [
                {
                    id: 'overview',
                    name: $i18n.t('总览')
                },
                {
                    id: 'yaml',
                    name: 'YAML'
                }
            ]
        })

        // 初始化集群列表信息
        useCluster(ctx)

        // 获取命名空间
        const { namespaceLoading, namespaceData, getNamespaceData } = useNamespace(ctx)
        // 命名空间数据
        const namespaceList = computed(() => {
            return namespaceData.value.manifest.items || []
        })

        // 排序
        const sortData = ref({
            prop: '',
            order: ''
        })
        const handleSortChange = (data) => {
            sortData.value = {
                prop: data.prop,
                order: data.order
            }
        }
        // 表格数据
        const { isLoading, data, fetchList } = useTableData(ctx)
        const tableData = computed(() => {
            const items = JSON.parse(JSON.stringify(data.value.manifest.items || []))
            const { prop, order } = sortData.value
            return prop ? sort(items, prop, order) : items
        })
        const resourceVersion = computed(() => {
            return data.value.manifest?.metadata?.resourceVersion || ''
        })

        // 模糊搜索功能
        const { tableDataMatchSearch, searchValue } = useSearch(tableData, keys)

        // 命名空间精确搜索
        const searchData = computed(() => {
            if (!namespaceValue.value) return tableDataMatchSearch.value

            return tableDataMatchSearch.value.filter(item => item.metadata.namespace === namespaceValue.value)
        })

        // 分页
        const { pagination, curPageData, pageConf, pageChange, pageSizeChange } = usePage(searchData)
        // 搜索时重置分页
        watch([searchValue, namespaceValue], () => {
            pageConf.current = 1
        })

        // 订阅事件
        const { initParams, handleSubscribe } = useSubscribe(data, ctx)
        const { start, stop } = useInterval(handleSubscribe, 5000)

        watch(resourceVersion, (newVersion, oldVersion) => {
            if (newVersion && newVersion !== oldVersion) {
                stop()
                initParams(kind.value, resourceVersion.value)
                resourceVersion.value && start()
            }
        })

        // 获取额外字段方法
        const handleGetExtData = (uid: string, ext?: string) => {
            const extData = data.value.manifest_ext[uid] || {}
            return ext ? extData[ext] : extData
        }

        // 跳转详情界面
        const gotoDetail = (row) => {
            $router.push({
                name: 'dashboardWorkloadDetail',
                params: {
                    category: category.value,
                    name: row.metadata.name,
                    namespace: row.metadata.namespace,
                    kind: kind.value
                }
            })
        }

        // 显示侧栏详情
        const handleShowDetail = (row) => {
            curDetailRow.value.data = row
            curDetailRow.value.extData = handleGetExtData(row.metadata.uid)
            showDetailPanel.value = true
        }
        // 切换详情类型
        const handleChangeDetailType = (type) => {
            detailType.value.active = type
        }
        // 重置详情类型
        watch(showDetailPanel, () => {
            handleChangeDetailType('overview')
        })
        // yaml内容
        const yaml = computed(() => {
            return yamljs.dump(curDetailRow.value.data || {})
        })

        onMounted(() => {
            showNameSpace.value && getNamespaceData()
            fetchList(type.value, category.value)
        })
        return {
            namespaceValue,
            namespaceLoading,
            showDetailPanel,
            curDetailRow,
            yaml,
            detailType,
            isLoading,
            pageConf: pagination,
            nameValue: searchValue,
            data,
            curPageData,
            namespaceList,
            stop,
            handlePageChange: pageChange,
            handlePageSizeChange: pageSizeChange,
            handleGetExtData,
            handleSortChange,
            gotoDetail,
            handleShowDetail,
            handleChangeDetailType
        }
    },
    render () {
        return (
            <div class="biz-content base-layout">
                <div class="biz-top-bar">
                    <div class="dashboard-top-title">
                        {this.title}
                    </div>
                    <DashboardTopActions />
                </div>
                <div class="biz-content-wrapper" v-bkloading={{ isLoading: this.isLoading }}>
                    <div class="search-wapper mb20">
                        {
                            this.showNameSpace
                                ? (
                                    <bcs-select
                                        loading={this.namespaceLoading}
                                        class="namespace-select"
                                        v-model={this.namespaceValue}
                                        searchable
                                        placeholder={this.$t('请选择命名空间')}>
                                        {
                                            this.namespaceList.map(option => (
                                                <bcs-option
                                                    key={option.metadata.name}
                                                    id={option.metadata.name}
                                                    name={option.metadata.name}>
                                                </bcs-option>
                                            ))
                                        }
                                    </bcs-select>
                                )
                                : null
                        }
                        <bk-input
                            class="search-input"
                            clearable
                            v-model={this.nameValue}
                            placeholder={this.$t('输入名称搜索')}>
                        </bk-input>
                    </div>
                    {
                        this.$scopedSlots.default && this.$scopedSlots.default({
                            isLoading: this.isLoading,
                            pageConf: this.pageConf,
                            data: this.data,
                            curPageData: this.curPageData,
                            handlePageChange: this.handlePageChange,
                            handlePageSizeChange: this.handlePageSizeChange,
                            handleGetExtData: this.handleGetExtData,
                            handleSortChange: this.handleSortChange,
                            gotoDetail: this.gotoDetail,
                            handleShowDetail: this.handleShowDetail
                        })
                    }
                </div>
                <bcs-sideslider
                    quick-close
                    isShow={this.showDetailPanel}
                    width={800}
                    {
                    ...{
                        on: {
                            'update:isShow': (show: boolean) => {
                                this.showDetailPanel = show
                            }
                        },
                        scopedSlots: {
                            header: () => (
                                <div class="detail-header">
                                    <span>{this.curDetailRow.data?.metadata?.name}</span>
                                    <div class="bk-button-group">
                                        {
                                            this.detailType.list.map(item => (
                                                <bk-button class={{ 'is-selected': this.detailType.active === item.id }}
                                                    onClick={() => {
                                                        this.handleChangeDetailType(item.id)
                                                    }}>
                                                    {item.name}
                                                </bk-button>
                                            ))
                                        }
                                    </div>
                                </div>
                            ),
                            content: () =>
                                this.detailType.active === 'overview'
                                    ? (this.$scopedSlots.detail && this.$scopedSlots.detail({
                                        ...this.curDetailRow
                                    }))
                                    : <ace width="100%" height="100%" lang="yaml" readOnly={true} value={this.yaml}></ace>
                        }
                    }
                    }></bcs-sideslider>
            </div>
        )
    }
})
