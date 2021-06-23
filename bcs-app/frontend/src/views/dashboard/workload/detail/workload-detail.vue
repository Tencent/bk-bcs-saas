<template>
    <div class="workload-detail" v-bkloading="{ isLoading }">
        <div class="workload-detail-info">
            <div class="workload-info-basic">
                <span class="name mr20">{{ metadata.name }}</span>
                <div class="basic-wrapper">
                    <div v-for="item in basicInfoList"
                        :key="item.label"
                        class="basic-item">
                        <span class="label">{{ item.label }}</span>
                        <span class="value">{{ item.value }}</span>
                    </div>
                </div>
            </div>
            <div class="workload-main-info">
                <div class="info-item">
                    <span class="label">{{ $t('命名空间') }}</span>
                    <span class="value">{{ metadata.namespace }}</span>
                </div>
                <div class="info-item">
                    <span class="label">{{ $t('镜像') }}</span>
                    <span class="value" v-bk-overflow-tips="getImagesTips(manifestExt.images)">{{ manifestExt.images && manifestExt.images.join(', ') }}</span>
                </div>
                <div class="info-item">
                    <span class="label">UID</span>
                    <span class="value">{{ metadata.uid }}</span>
                </div>
                <div class="info-item">
                    <span class="label">{{ $t('创建时间') }}</span>
                    <span class="value">{{ manifestExt.createTime }}</span>
                </div>
                <div class="info-item">
                    <span class="label">{{ $t('存在时间') }}</span>
                    <span class="value">{{ manifestExt.age }}</span>
                </div>
            </div>
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
                <bcs-tab-panel name="pod" label="Pod">
                    <bk-table :data="pods">
                        <bk-table-column :label="$t('名称')" prop="metadata.name" sortable :resizable="false">
                            <template #default="{ row }">
                                <bk-button class="bcs-button-ellipsis" text @click="gotoPodDetail(row)">{{ row.metadata.name }}</bk-button>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('命名空间')" prop="metadata.namespace" sortable :resizable="false"></bk-table-column>
                        <bk-table-column :label="$t('镜像')" width="450" :resizable="false">

                        </bk-table-column>
                        <bk-table-column label="Status" :resizable="false">
                            <template slot-scope="{ row }">
                                <StatusIcon :status="row.status"></StatusIcon>
                            </template>
                        </bk-table-column>
                        <bk-table-column label="Ready" width="110" :resizable="false">
                            <!--todo-->
                        </bk-table-column>
                        <bk-table-column label="Restarts" width="110" :resizable="false" prop="restartCnt"></bk-table-column>
                        <bk-table-column label="IP" :resizable="false">
                            <template slot-scope="{ row }">{{row.status.podIP || '--'}}</template>
                        </bk-table-column>
                        <bk-table-column label="Node" :resizable="false">
                            <template slot-scope="{ row }">{{row.spec.nodeName || '--'}}</template>
                        </bk-table-column>
                        <bk-table-column label="Age" :resizable="false" prop="age"></bk-table-column>
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
    import { bkOverflowTips } from 'bk-magic-vue'
    import StatusIcon from '../../common/status-icon'
    import Metric from '../../common/metric.vue'
    import useDetail from './use-detail'
    import detailBasicList from './detail-basic'

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
        directives: {
            bkOverflowTips
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
            const workloadPods = ref<IDetail|null>(null)
            const basicInfoList = detailBasicList(ctx, {
                category: props.category,
                detail
            })
            // pods数据
            const pods = computed(() => {
                const data = workloadPods.value?.manifest?.items || []
                return data.map(item => ({
                    ...item,
                    ...workloadPods.value?.manifest_ext[item.metadata.uid]
                }))
            })
            // 指标参数
            const params = computed<IParams | null>(() => {
                const list = pods.value.map(item => item.metadata.name)
                return list.length
                    ? { pod_name_list: list }
                    : null
            })
            // metadata 数据
            const metadata = computed(() => detail.value?.manifest?.metadata || {})
            // manifestExt 数据
            const manifestExt = computed(() => detail.value?.manifest_ext || {})

            // 跳转pod详情
            const gotoPodDetail = (row) => {
                ctx.emit('pod-detail', row)
            }

            // 获取镜像tips
            const getImagesTips = (images) => {
                if (!images) {
                    return {
                        content: ''
                    }
                }
                return {
                    allowHTML: true,
                    maxWidth: 480,
                    content: images.join('<br />')
                }
            }

            const { $store } = ctx.root

            onMounted(async () => {
                isLoading.value = true
                await handleGetDetail()
                const matchLabels = detail.value?.manifest?.spec?.selector?.matchLabels || {}
                const labelSelector = Object.keys(matchLabels).reduce((pre, key, index) => {
                    pre += `${index > 0 ? ',' : ''}${key}=${matchLabels[key]}`
                    return pre
                }, '')
                workloadPods.value = await $store.dispatch('dashboard/listWorkloadPods', {
                    $namespaceId: props.namespace,
                    label_selector: labelSelector
                })
                isLoading.value = false
            })

            return {
                isLoading,
                detail,
                metadata,
                manifestExt,
                basicInfoList,
                activePanel,
                params,
                pods,
                labels,
                annotations,
                gotoPodDetail,
                getImagesTips
            }
        }
    })
</script>
<style lang="postcss" scoped>
@import './detail-info.css';
.workload-detail {
    width: 100%;
    &-info {
        @mixin detail-info 3;
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
