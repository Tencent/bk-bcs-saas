<template>
    <div class="workload-detail" v-bkloading="{ isLoading }">
        <div class="workload-detail-info">
            <!-- todo -->
        </div>
        <div class="workload-detail-body">
            <div class="workload-metric">
                <Metric :title="$t('CPU使用率')" metric="cpu_usage" :params="params" category="pods" colors="#30d878"></Metric>
                <Metric :title="$t('内存使用率')" metric="memory_usage" :params="params" unit="byte" category="pods" colors="#3a84ff"></Metric>
                <Metric :title="$t('网络')"
                    :metric="['network_receive', 'network_transmit']"
                    :params="params"
                    category="pods"
                    unit="byte"
                    :colors="['#853cff', '#30d878']">
                </Metric>
            </div>
            <bcs-tab class="workload-tab" :active.sync="activePanel" type="card" :label-height="40">
                <bcs-tab-panel name="pod" label="Pod" v-bkloading="{ isLoading: podLoading }">
                    <bk-table :data="pods">
                        <bk-table-column :label="$t('名称')" prop="metadata.name" sortable :resizable="false">
                            <template #default="{ row }">
                                <bk-button class="bcs-button-ellipsis" text @click="gotoPodDetail(row)">{{ row.metadata.name }}</bk-button>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('命名空间')" prop="metadata.namespace" sortable :resizable="false"></bk-table-column>
                        <bk-table-column :label="$t('镜像')" width="450" :resizable="false">
                            <template slot-scope="{ row }">
                                <div class="images-wrapper">
                                    <div class="image-item"
                                        :title="image"
                                        v-for="(image, imageIndex) in handleGetExtData(row.metadata.uid, 'images')"
                                        :key="imageIndex">
                                        {{image}}
                                    </div>
                                </div>
                            </template>
                        </bk-table-column>
                        <bk-table-column label="Status" :resizable="false">
                            <template slot-scope="{ row }">
                                <StatusIcon :status="handleGetExtData(row.metadata.uid, 'status')"></StatusIcon>
                            </template>
                        </bk-table-column>
                        <bk-table-column label="Ready" width="110" :resizable="false">
                            <template slot-scope="{ row }">
                                {{handleGetExtData(row.metadata.uid, 'readyCnt')}}/{{handleGetExtData(row.metadata.uid, 'totalCnt')}}
                            </template>
                        </bk-table-column>
                        <bk-table-column label="Restarts" width="110" :resizable="false">
                            <template slot-scope="{ row }">{{handleGetExtData(row.metadata.uid, 'restartCnt')}}</template>
                        </bk-table-column>
                        <bk-table-column label="IP" :resizable="false">
                            <template slot-scope="{ row }">{{row.status.podIP || '--'}}</template>
                        </bk-table-column>
                        <bk-table-column label="Node" :resizable="false">
                            <template slot-scope="{ row }">{{row.spec.nodeName || '--'}}</template>
                        </bk-table-column>
                        <bk-table-column label="Age" :resizable="false">
                            <template #default="{ row }">
                                <span>{{handleGetExtData(row.metadata.uid, 'age')}}</span>
                            </template>
                        </bk-table-column>
                    </bk-table>
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
    import { defineComponent, computed, ref, onMounted } from '@vue/composition-api'
    import StatusIcon from '../../common/status-icon'
    import Metric from '../../common/metric.vue'
    import useDetail from './use-detail'

    export interface IDetail {
        manifest: any;
        manifest_ext: any;
    }

    export interface IParams {
        pod_name_list: string[];
    }

    export default defineComponent({
        name: 'WorkloadDetail',
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
            // workload类型
            category: {
                type: String,
                default: '',
                required: true
            },
            // 名称
            name: {
                type: String,
                default: '',
                required: true
            }
        },
        setup (props, ctx) {
            const { $store } = ctx.root
            const {
                isLoading,
                detail,
                activePanel,
                labels,
                annotations,
                handleGetDetail
            } = useDetail(ctx, {
                ...props,
                defaultActivePanel: 'pod'
            })
            const podLoading = ref(false)
            const workloadPods = ref<IDetail|null>(null)

            // pods数据
            const pods = computed(() => {
                return workloadPods.value?.manifest?.items || []
            })
            // 获取pod manifest_ext数据
            const handleGetExtData = (uid, prop) => {
                return workloadPods.value?.manifest_ext?.[uid]?.[prop]
            }
            // 指标参数
            const params = computed<IParams | null>(() => {
                const list = pods.value.map(item => item.metadata.name)
                return list.length
                    ? { pod_name_list: list }
                    : null
            })

            // 跳转pod详情
            const gotoPodDetail = (row) => {
                ctx.emit('pod-detail', row)
            }

            onMounted(async () => {
                // 详情接口前置
                await handleGetDetail()

                // 获取工作负载下对应的pod数据
                podLoading.value = true
                const matchLabels = detail.value?.manifest?.spec.selector.matchLabels || {}
                const labelSelector = Object.keys(matchLabels).reduce((pre, key, index) => {
                    pre += `${index > 0 ? ',' : ''}${key}=${matchLabels[key]}`
                    return pre
                }, '')
                workloadPods.value = await $store.dispatch('dashboard/listWorkloadPods', {
                    $namespaceId: props.namespace,
                    label_selector: labelSelector
                })
                podLoading.value = false
            })

            return {
                isLoading,
                detail,
                activePanel,
                params,
                pods,
                labels,
                annotations,
                podLoading,
                gotoPodDetail,
                handleGetExtData
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
    }
}
</style>
