<template>
    <BaseLayout title="ConfigMaps" kind="ConfigMap" category="configmaps" type="configs">
        <template #default="{ curPageData, pageConf, handlePageChange, handlePageSizeChange, handleGetExtData, handleShowDetail }">
            <bk-table
                :data="curPageData"
                :pagination="pageConf"
                @page-change="handlePageChange"
                @page-limit-change="handlePageSizeChange">
                <bk-table-column :label="$t('名称')" prop="metadata.name" sortable :resizable="false">
                    <template #default="{ row }">
                        <bk-button class="bcs-button-ellipsis" text @click="handleShowDetail(row)">{{ row.metadata.name }}</bk-button>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('命名空间')" prop="metadata.namespace" sortable :resizable="false"></bk-table-column>
                <bk-table-column label="Data">
                    <template #default="{ row }">
                        <span>{{ handleGetExtData(row.metadata.uid, 'data').join(', ') || '--' }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="Age" :resizable="false">
                    <template #default="{ row }">
                        <span v-bk-tooltips="{ content: handleGetExtData(row.metadata.uid, 'createTime') }">{{ handleGetExtData(row.metadata.uid, 'age') }}</span>
                    </template>
                </bk-table-column>
            </bk-table>
        </template>
        <template #detail="{ data }">
            <ConfigMapsDetail :data="data"></ConfigMapsDetail>
        </template>
    </BaseLayout>
</template>
<script>
    import { defineComponent } from '@vue/composition-api'
    import ConfigMapsDetail from './config-maps-detail.vue'
    import BaseLayout from '@open/views/dashboard/common/base-layout'

    export default defineComponent({
        components: { BaseLayout, ConfigMapsDetail }
    })
</script>
