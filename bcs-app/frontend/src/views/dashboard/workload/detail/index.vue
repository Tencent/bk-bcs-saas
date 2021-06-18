<template>
    <div class="detail">
        <DetailTopNav :titles="titles" @change="handleNavChange"></DetailTopNav>
        <!-- <keep-alive>
        </keep-alive> -->
        <component
            :is="componentId"
            v-bind="componentProps"
            @pod-detail="handleGotoPodDetail"
            @container-detail="handleGotoContainerDetail">
        </component>
    </div>
</template>
<script lang="ts">
    import { defineComponent, ref, computed } from '@vue/composition-api'
    import DetailTopNav from './detail-top-nav.vue'
    import WorkloadDetail from './workload-detail.vue'
    import PodDetail from './pod-detail.vue'
    import ContainerDetail from './container-detail.vue'

    export type ComponentIdType = 'WorkloadDetail' | 'PodDetail' | 'ContainerDetail'
    export interface ITitle {
        name: string;
        id: string;
    }

    export default defineComponent({
        components: {
            DetailTopNav,
            WorkloadDetail,
            PodDetail,
            ContainerDetail
        },
        props: {
            // 命名空间
            namespace: {
                type: String,
                default: ''
            },
            // workload类型
            category: {
                type: String,
                default: ''
            },
            // 名称
            name: {
                type: String,
                default: ''
            }
        },
        setup (props, ctx) {
            const { $router } = ctx.root
            const defaultComId = props.category === 'pods' ? 'PodDetail' : 'WorkloadDetail'
            // 顶部导航内容
            const titles = ref<ITitle[]>([
                {
                    name: props.category,
                    id: ''
                },
                {
                    name: props.name,
                    id: defaultComId
                }
            ])
            const componentId = ref(defaultComId)
            const parentName = ref(props.name)
            const currentName = ref(props.name)

            const componentProps = computed(() => {
                return {
                    namespace: props.namespace,
                    category: props.category,
                    name: currentName.value,
                    parent: parentName.value
                }
            })

            const handleNavChange = (item: ITitle) => {
                const { id } = item
                const index = titles.value.findIndex(item => item.id === id)
                if (id === '') {
                    $router.back()
                } else {
                    // 保存上一次的值
                    parentName.value = currentName.value
                    currentName.value = item.name
                    componentId.value = id
                    if (index > -1) {
                        titles.value = titles.value.slice(0, index + 1)
                    } else {
                        titles.value.push(item)
                    }
                }
            }

            const handleGotoPodDetail = (row) => {
                handleNavChange({
                    name: row.metadata.name,
                    id: 'PodDetail'
                })
            }

            const handleGotoContainerDetail = (row) => {
                handleNavChange({
                    name: row.name,
                    id: 'ContainerDetail'
                })
            }

            return {
                currentName,
                componentId,
                componentProps,
                titles,
                handleNavChange,
                handleGotoPodDetail,
                handleGotoContainerDetail
            }
        }
    })
</script>
<style scoped>
.detail {
    width: 100%;
}
</style>
