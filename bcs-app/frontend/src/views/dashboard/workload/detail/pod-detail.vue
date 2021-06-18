<template>
    <div class="workload-detail" v-bkloading="{ isLoading }">
        <div class="workload-detail-info">
            <!-- todo -->
        </div>
        <div class="workload-detail-body">
            <div class="workload-metric">
                <Metric :title="$t('CPU使用率')" metric="cpu_usage" :params="params" category="pods" colors="#30d878"></Metric>
                <Metric :title="$t('内存使用率')" metric="memory_usage" :params="params" category="pods" colors="#3a84ff"></Metric>
                <Metric :title="$t('网络')"
                    :metric="['network_receive', 'network_transmit']"
                    :params="params"
                    category="pods"
                    :colors="['#853cff', '#30d878']">
                </Metric>
            </div>
            <bcs-tab class="workload-tab" :active.sync="activePanel" type="card" :label-height="40">
                <bcs-tab-panel name="container" :label="$t('容器')">
                    <bk-table :data="container">
                        <bk-table-column :label="$t('容器名称')" prop="name">
                            <template #default="{ row }">
                                <bk-button class="bcs-button-ellipsis" text @click="gotoContainerDetail(row)">{{ row.name }}</bk-button>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('状态')" prop="status">
                            <template #default="{ row }">
                                <StatusIcon :status="row.status"></StatusIcon>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('镜像')" prop="image"></bk-table-column>
                    </bk-table>
                </bcs-tab-panel>
                <bcs-tab-panel name="conditions" :label="$t('状态（Conditions）')">
                    <bk-table :data="conditions">
                        <bk-table-column :label="$t('类别')" prop="type"></bk-table-column>
                        <bk-table-column :label="$t('状态')" prop="status">
                            <template #default="{ row }">
                                <StatusIcon :status="row.status"></StatusIcon>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('最后迁移时间')" prop="lastTransitionTime"></bk-table-column>
                        <bk-table-column :label="$t('原因')" prop=""></bk-table-column>
                    </bk-table>
                </bcs-tab-panel>
                <bcs-tab-panel name="storage" :label="$t('存储')">
                    <div class="storage storage-pvcs">
                        <div class="title">PersistentVolumeClaims</div>
                        <bk-table :data="storageTableData.pvcs"></bk-table>
                    </div>
                    <div class="storage storage-config">
                        <div class="title">ConfigMaps</div>
                        <bk-table :data="storageTableData.configmaps"></bk-table>
                    </div>
                    <div class="storage storage-secrets">
                        <div class="title">Secrets</div>
                        <bk-table :data="storageTableData.secrets"></bk-table>
                    </div>
                </bcs-tab-panel>
                <bcs-tab-panel name="label" :label="$t('标签')">
                    <bk-table :data="labels">
                        <bk-table-column label="Key" prop="key"></bk-table-column>
                        <bk-table-column label="Value" prop="value"></bk-table-column>
                    </bk-table>
                </bcs-tab-panel>
                <bcs-tab-panel name="annotations" :label="$t('注解')">
                    <bk-table :data="annotations">
                        <bk-table-column label="Key" prop="key"></bk-table-column>
                        <bk-table-column label="Value" prop="value"></bk-table-column>
                    </bk-table>
                </bcs-tab-panel>
            </bcs-tab>
        </div>
    </div>
</template>
<script lang="ts">
    /* eslint-disable camelcase */
    import { computed, defineComponent, onMounted, ref, toRefs } from '@vue/composition-api'
    import StatusIcon from '../../common/status-icon'
    import Metric from '../../common/metric.vue'
    import useDetail from './use-detail'

    export interface IDetail {
        manifest: any;
        manifest_ext: any;
    }

    export interface IStorage {
        pvcs: IDetail | null;
        configmaps: IDetail | null;
        secrets: IDetail | null;
    }

    export default defineComponent({
        name: 'PodDetail',
        components: {
            StatusIcon,
            Metric
        },
        props: {
            namespace: {
                type: String,
                default: '',
                required: true
            },
            // pod 名称
            name: {
                type: String,
                default: '',
                required: true
            }
        },
        setup (props, ctx) {
            const {
                isLoading,
                detail,
                activePanel,
                labels,
                annotations,
                handleGetDetail
            } = useDetail(ctx, {
                ...props,
                category: 'pods',
                defaultActivePanel: 'container'
            })
            const { $store } = ctx.root
            const { name, namespace } = toRefs(props)
            const params = computed(() => {
                return {
                    pod_name_list: [name.value]
                }
            })

            // 容器
            const container = ref([])
            const handleGetContainer = async () => {
                container.value = await $store.dispatch('dashboard/listContainers', {
                    $podId: name.value,
                    $namespaceId: namespace.value
                })
            }
            // 状态
            const conditions = computed(() => {
                return detail.value?.manifest.status?.conditions || []
            })
            // 存储
            const storage = ref<IStorage>({
                pvcs: null,
                configmaps: null,
                secrets: null
            })
            const storageTableData = computed(() => {
                return {
                    pvcs: storage.value.pvcs?.manifest.items || [],
                    configmaps: storage.value.configmaps?.manifest.items || [],
                    secrets: storage.value.secrets?.manifest.items || []
                }
            })
            const handleGetStorage = async () => {
                const types = ['pvcs', 'configmaps', 'secrets']
                const promises = types.map(type => {
                    return $store.dispatch('dashboard/listStoragePods', {
                        $podId: name.value,
                        $type: type,
                        $namespaceId: namespace.value
                    })
                })
                const [pvcs = {}, configmaps = {}, secrets = {}] = await Promise.all(promises)
                storage.value = {
                    pvcs,
                    configmaps,
                    secrets
                }
            }

            // 跳转容器详情
            const gotoContainerDetail = (row) => {
                ctx.emit('container-detail', row)
            }

            onMounted(async () => {
                isLoading.value = true
                await Promise.all([
                    await handleGetDetail(),
                    await handleGetStorage(),
                    await handleGetContainer()
                ])
                isLoading.value = false
            })

            return {
                params,
                container,
                conditions,
                storage,
                storageTableData,
                isLoading,
                detail,
                activePanel,
                labels,
                annotations,
                handleGetStorage,
                handleGetContainer,
                gotoContainerDetail
            }
        }
    })
</script>
<style lang="postcss" scoped>
.workload-detail {
    width: 100%;
    &-info {

    }
    &-body {
        background: #FAFBFD;
        padding: 0 24px;
        .workload-metric {
            display: flex;
            background: #fff;
            margin-top: 16px;
            height: 230px;
        }
        .workload-tab {
            margin-top: 16px;
        }
        .storage {
            margin-top: 24px;
            .title {
                font-size: 14px;
                color: #313238;
                margin-bottom: 8px;
            }
        }
    }
}
</style>
