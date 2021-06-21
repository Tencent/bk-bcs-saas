<template>
    <div class="detail p30">
        <div class="detail-title">
            {{ $t('基础信息') }}
        </div>
        <div class="detail-content basic-info">
            <table class="detail-table" border="1">
                <tbody>
                    <tr>
                        <td>{{ $t('命名空间') }}</td>
                        <td>{{ data.metadata.namespace || '--' }}</td>
                    </tr>
                    <tr>
                        <td>UID</td>
                        <td>{{ data.metadata.uid || '--' }}</td>
                    </tr>
                    <tr>
                        <td>{{ $t('创建时间') }}</td>
                        <td>{{ extData.createTime || '--' }}</td>
                    </tr>
                    <tr>
                        <td>{{ $t('存在时间') }}</td>
                        <td>{{ extData.age || '--' }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <bcs-tab class="mt20" :label-height="40">
            <bcs-tab-panel name="data" label="Data">
                <bk-table :data="data.data">
                    <bk-table-column label="Key">
                        <template slot-scope="props">
                            {{ props.$index }}
                        </template>
                    </bk-table-column>
                    <bk-table-column label="Value">
                        <template slot-scope="{ row }">
                            {{ row }}
                        </template>
                    </bk-table-column>
                </bk-table>
            </bcs-tab-panel>
            <bcs-tab-panel name="lebel" :label="$t('标签')">
                <bk-table :data="data.metadata.labels">
                    <bk-table-column label="Key">
                        <template slot-scope="props">
                            {{ props.$index }}
                        </template>
                    </bk-table-column>
                    <bk-table-column label="Value">
                        <template slot-scope="{ row }">
                            {{ row }}
                        </template>
                    </bk-table-column>
                </bk-table>
            </bcs-tab-panel>
            <bcs-tab-panel name="annotation" :label="$t('注释')">
                <bk-table :data="data.metadata.annotations">
                    <bk-table-column label="Key">
                        <template slot-scope="props">
                            {{ props.$index }}
                        </template>
                    </bk-table-column>
                    <bk-table-column label="Value">
                        <template slot-scope="{ row }">
                            {{ row }}
                        </template>
                    </bk-table-column>
                </bk-table>
            </bcs-tab-panel>
        </bcs-tab>
    </div>
</template>
<script lang="ts">
    import { defineComponent } from '@vue/composition-api'

    export default defineComponent({
        name: 'SecretsDetail',
        props: {
            // 当前行数据
            data: {
                type: Object,
                default: () => ({})
            },
            extData: {
                type: Object,
                default: () => ({})
            }
        }
    })
</script>
<style lang="postcss" scoped>
.detail {
    &-title {
        margin-bottom: 10px;
        font-size: 16px;
        color: #333948;
    }
    &-content {
        font-size: 14px;
        margin-bottom: 20px;
    }
    &-table {
        width: 100%;
        border: 1px solid #dfe0e5;
        color: #737987;
        th {
            text-align: left;
            padding-left: 15px;
            height: 32px;
        }
        tr {
            height: 32px;
            td {
                padding-left: 15px;
                &:hover {
                    background-color: #F7F8FA;
                }
            }
            td:nth-child(1) {
                width: 215px;
            }
        }
    }
}
</style>
