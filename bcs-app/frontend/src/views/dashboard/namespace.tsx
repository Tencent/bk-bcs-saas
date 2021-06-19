import { defineComponent, computed, ref, watch, onMounted } from '@vue/composition-api'
import DashboardTopActions from './dashboard-top-actions'
import useCluster from './common/use-cluster'
import useInterval from './common/use-interval'
import useNamespace from './common/use-namespace'
import usePage from './common/use-page'
import useSearch from './common/use-search'
import useSubscribe from './common/use-subscribe'
import './index.css'

export default defineComponent({
    name: 'Namespace',
    components: {
        DashboardTopActions
    },
    setup (props, ctx) {
        const keys = ref(['metadata.name'])

        // 初始化集群列表信息
        useCluster(ctx)
        // 获取命名空间
        const { namespaceLoading, namespaceData, getNamespaceData } = useNamespace(ctx)

        // 表格数据
        const tableData = computed(() => {
            return namespaceData.value.manifest?.items || []
        })
        // resourceVersion
        const resourceVersion = computed(() => {
            return namespaceData.value.manifest?.metadata?.resourceVersion || ''
        })
        // 搜索功能
        const { tableDataMatchSearch, searchValue } = useSearch(tableData, keys)

        // 分页
        const { pagination, curPageData, pageConf, pageChange, pageSizeChange } = usePage(tableDataMatchSearch)
        // 搜索时重置分页
        watch(searchValue, () => {
            pageConf.current = 1
        })

        // 处理额外字段
        const handleExtCol = (row: any, key: string) => {
            const ext = namespaceData.value.manifest_ext[row.metadata?.uid] || {}
            return ext[key] || '--'
        }

        // 订阅事件
        const { initParams, handleSubscribe } = useSubscribe(namespaceData, ctx)
        const { start } = useInterval(handleSubscribe, 5000)

        watch(resourceVersion, (newVersion, oldVersion) => {
            if (newVersion && newVersion !== oldVersion) {
                stop()
                initParams('Namespace', resourceVersion.value)
                resourceVersion.value && start()
            }
        })

        onMounted(() => {
            getNamespaceData()
        })

        return {
            namespaceLoading,
            pagination,
            searchValue,
            curPageData,
            pageChange,
            pageSizeChange,
            handleExtCol
        }
    },
    render () {
        return (
            <div class="biz-content" v-bkloading={{ isLoading: this.namespaceLoading }}>
                <div class="biz-top-bar">
                    <div class="dashboard-top-title">
                        {this.$t('命名空间')}
                    </div>
                    <DashboardTopActions />
                </div>
                <div class="biz-content-wrapper">
                    <bcs-input class="mb20 search-input"
                        right-icon="bk-icon icon-search"
                        placeholder={this.$t('搜索名称')}
                        v-model={this.searchValue}>
                    </bcs-input>
                    <bcs-table data={this.curPageData}
                        pagination={this.pagination}
                        on-page-change={this.pageChange}
                        on-page-limit-change={this.pageSizeChange}>
                        <bcs-table-column label={this.$t('名称')}
                            scopedSlots={{
                                default: ({ row }: { row: any }) => row.metadata?.name || '--'
                            }}>
                        </bcs-table-column>
                        <bcs-table-column label={this.$t('状态')}
                            scopedSlots={{
                                default: ({ row }: { row: any }) => row.status?.phase || '--'
                            }}>
                        </bcs-table-column>
                        <bcs-table-column label={this.$t('Age')}
                            scopedSlots={{
                                default: ({ row }: { row: any }) => this.handleExtCol(row, 'age')
                            }}>
                        </bcs-table-column>
                    </bcs-table>
                </div>
            </div>
        )
    }
})
