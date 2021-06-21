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
        <div class="scerets-title">
            Scerets
        </div>
        <div class="scerets-content">
            <bk-table :data="data.secrets">
                <bk-table-column label="name">
                    <template slot-scope="{ row }">
                        {{ row.name }}
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
    </div>
</template>
<script lang="ts">
    import { defineComponent } from '@vue/composition-api'

    export default defineComponent({
        name: 'ConfigMapsDetail',
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
        border-radius: 3px;
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
    .scerets-title {
        margin-bottom: 10px;
        font-size: 16px;
        color: #333948;
    }
}
</style>
