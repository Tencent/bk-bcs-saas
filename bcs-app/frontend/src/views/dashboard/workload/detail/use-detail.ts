/* eslint-disable camelcase */
import { ref, computed, SetupContext } from '@vue/composition-api'

export interface IWorkloadDetail {
    manifest: any;
    manifest_ext: any;
}

export interface IDetailOptions {
    category: string;
    name: string;
    namespace: string;
    defaultActivePanel: string;
}

export default function useDetail (ctx: SetupContext, options: IDetailOptions) {
    const { $store } = ctx.root
    const isLoading = ref(false)
    const detail = ref<IWorkloadDetail|null>(null)
    const activePanel = ref(options.defaultActivePanel)

    // 标签数据
    const labels = computed(() => {
        const obj = detail.value?.manifest?.metadata?.labels || {}
        return Object.keys(obj).map(key => ({
            key,
            value: obj[key]
        }))
    })
    // 注解数据
    const annotations = computed(() => {
        const obj = detail.value?.manifest?.metadata?.annotations || {}
        return Object.keys(obj).map(key => ({
            key,
            value: obj[key]
        }))
    })

    const handleTabChange = (item) => {
        activePanel.value = item.name
    }
    // 获取workload详情
    const handleGetDetail = async () => {
        const { namespace, category, name } = options
        // workload详情
        isLoading.value = true
        detail.value = await $store.dispatch('dashboard/getWorkloadDetail', {
            $namespaceId: namespace,
            $category: category,
            $name: name
        })
        isLoading.value = false
        return detail.value
    }

    return {
        isLoading,
        detail,
        activePanel,
        labels,
        annotations,
        handleTabChange,
        handleGetDetail
    }
}
