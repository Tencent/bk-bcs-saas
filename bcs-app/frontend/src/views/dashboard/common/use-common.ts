import { SetupContext, computed, ref, watch, onMounted } from '@vue/composition-api'
import useCluster from './use-cluster'
import useInterval from './use-interval'
import useNamespace from './use-namespace'
import usePage from './use-page'
import useSearch from './use-search'
import useSubscribe from './use-subscribe'
import useTableData from './use-table-data'
import { sort } from '@/common/util'

interface IOptions {
    kind: string; // 轮询kind
    category: string; // 子类型
    type: string; // 父类型
    showNameSpace: boolean; // 是否显示命名空间
}

export default function useCommon (ctx: SetupContext, options: IOptions) {
    const keys = ref(['metadata.name'])
    const namespaceValue = ref('')
    const showDetailPanel = ref(false)
    const curDetailRow = ref<any>({})

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
    watch([searchValue, namespaceList], () => {
        pageConf.current = 1
    })

    // 订阅事件
    const { initParams, handleSubscribe } = useSubscribe(data, ctx)
    const { start, stop } = useInterval(handleSubscribe, 5000)

    watch(resourceVersion, (newVersion, oldVersion) => {
        if (newVersion && newVersion !== oldVersion) {
            stop()
            initParams(options.kind, resourceVersion.value)
            resourceVersion.value && start()
        }
    })

    // 获取额外字段方法
    const handleGetExtData = (uid: string, ext: string) => {
        const extData = data.value.manifest_ext[uid] || {}
        return extData[ext]
    }

    // 跳转详情界面
    const gotoDetail = (row) => {
        ctx.root.$router.push({
            name: 'dashboardWorkloadDetail',
            params: {
                category: options.category,
                name: row.metadata.name,
                namespace: row.metadata.namespace
            }
        })
    }

    // 显示侧栏详情
    const handleShowDetail = (row) => {
        curDetailRow.value = row
        showDetailPanel.value = true
    }

    onMounted(() => {
        options.showNameSpace && getNamespaceData()
        fetchList(options.type, options.category)
    })

    return {
        namespaceValue,
        namespaceLoading,
        showDetailPanel,
        curDetailRow,
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
        handleShowDetail
    }
}
