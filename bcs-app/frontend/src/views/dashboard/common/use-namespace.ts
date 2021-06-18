import { ref, computed, SetupContext, Ref } from "@vue/composition-api"
import { ISubscribeData } from './use-subscribe'

export interface IUseNamespace {
    namespaceLoading: Ref<boolean>;
    namespaceData: Ref<ISubscribeData>;
    getNamespaceData: () => Promise<ISubscribeData>;
}

/**
 * 获取命名空间
 * @param ctx
 * @returns
 */
export default function useNamespace (ctx: SetupContext): IUseNamespace {
    const { $route, $store } = ctx.root

    const projectId = computed(() => $route.params.projectId)
    const curClusterId = computed(() => $store.state.curClusterId).value

    const namespaceLoading = ref(false)
    const namespaceData = ref<ISubscribeData>({
        manifest: {},
        manifest_ext: {}
    })

    const getNamespaceData = async (): Promise<ISubscribeData> => {
        namespaceLoading.value = true
        const res = await $store.dispatch('dashboard/getNamespaceList', {
            projectId: projectId.value,
            clusterId: curClusterId
        }).catch(_ => ({ data: {
            manifest: {},
            manifest_ext: {}
        } }))
        namespaceData.value = res.data
        namespaceLoading.value = false
        return res.data
    }

    // onMounted(getNamespaceData)

    return {
        namespaceLoading,
        namespaceData,
        getNamespaceData
    }
}
