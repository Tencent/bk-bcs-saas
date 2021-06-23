import { SetupContext, ref } from '@vue/composition-api'
import { ISubscribeData } from './use-subscribe'

/**
 * 加载表格数据
 * @param ctx
 * @returns
 */
export default function useTableData (ctx: SetupContext) {
    const isLoading = ref(false)
    const data = ref<ISubscribeData>({
        manifest_ext: {},
        manifest: {}
    })

    const { $store } = ctx.root

    const fetchList = async (type: string, category: string): Promise<ISubscribeData> => {
        isLoading.value = true
        const tableData = await $store.dispatch('dashboard/getTableData', {
            $type: type,
            $category: category
        })
        data.value = tableData
        isLoading.value = false
        return tableData
    }

    return {
        isLoading,
        data,
        fetchList
    }
}
