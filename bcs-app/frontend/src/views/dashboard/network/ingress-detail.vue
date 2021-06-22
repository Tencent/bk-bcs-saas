<template>
    <div class="detail p30">
        <!-- 基础信息 -->
        <div class="detail-title">
            {{ $t('基础信息') }}
        </div>
        <div class="detail-content basic-info">
            <div class="basic-info-item">
                <label>{{ $t('命名空间') }}</label>
                <span>{{ data.metadata.namespace }}</span>
            </div>
            <div class="basic-info-item">
                <label>UID</label>
                <span class="bcs-ellipsis">{{ data.metadata.uid }}</span>
            </div>
            <div class="basic-info-item">
                <label>Class</label>
                <span>{{ data.spec.ingressClassName || '--' }}</span>
            </div>
            <div class="basic-info-item">
                <label>Hosts</label>
                <span>{{ extData.hosts.join('/') || '--' }}</span>
            </div>
            <div class="basic-info-item">
                <label>Address</label>
                <span>{{ extData.addresses.join('/') || '--' }}</span>
            </div>
            <div class="basic-info-item">
                <label>Port(s)</label>
                <span>{{ extData.default_ports || '--' }}</span>
            </div>
            <div class="basic-info-item">
                <label>{{ $t('创建时间') }}</label>
                <span>{{ extData.createTime }}</span>
            </div>
            <div class="basic-info-item">
                <label>{{ $t('存在时间') }}</label>
                <span>{{ extData.updateTime }}</span>
            </div>
        </div>
        <!-- 配置、标签、注解 -->
        <bcs-tab class="mt20" type="card" :label-height="40">
            <bcs-tab-panel name="config" :label="$t('配置')">
                <p class="detail-title">{{ $t('主机列表') }}（spec.tls）</p>
                <bk-table :data="data.spec.tls" class="mb20">
                    <bk-table-column label="Hosts" prop="hosts"></bk-table-column>
                    <bk-table-column label="SecretName" prop="secretName"></bk-table-column>
                </bk-table>
                <p class="detail-title">{{ $t('规则') }}（spec.rules）</p>
                <bk-table :data="data.spec.rules">
                    <bk-table-column label="Host" prop="hosts"></bk-table-column>
                    <bk-table-column label="Path"></bk-table-column>
                    <bk-table-column label="ServiceName"></bk-table-column>
                    <bk-table-column label="Port"></bk-table-column>
                </bk-table>
            </bcs-tab-panel>
            <bcs-tab-panel name="label" :label="$t('标签')">
                <bk-table :data="handleTransformObjToArr(data.metadata.labels)">
                    <bk-table-column label="Key" prop="key"></bk-table-column>
                    <bk-table-column label="Value" prop="value"></bk-table-column>
                </bk-table>
            </bcs-tab-panel>
            <bcs-tab-panel name="annotations" :label="$t('注解')">
                <bk-table :data="handleTransformObjToArr(data.metadata.annotations)">
                    <bk-table-column label="Key" prop="key"></bk-table-column>
                    <bk-table-column label="Value" prop="value"></bk-table-column>
                </bk-table>
            </bcs-tab-panel>
        </bcs-tab>
    </div>
</template>
<script lang="ts">
    import { defineComponent } from '@vue/composition-api'

    export default defineComponent({
        name: 'IngressDetail',
        props: {
            // 当前行数据
            data: {
                type: Object,
                default: () => ({})
            },
            // 当前行对应的manifest_ext数据
            extData: {
                type: Object,
                default: () => ({})
            }
        },
        setup (props, ctx) {
            const handleTransformObjToArr = (obj) => {
                if (!obj) return []

                return Object.keys(obj).reduce<any[]>((data, key) => {
                    data.push({
                        key,
                        value: obj[key]
                    })
                    return data
                }, [])
            }

            return {
                handleTransformObjToArr
            }
        }
    })
</script>
<style lang="postcss" scoped>
@import './detail.css';
</style>
