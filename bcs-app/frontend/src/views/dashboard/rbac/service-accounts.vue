<template>
    <BaseLayout title="ServiceAccounts" kind="ServiceAccount" category="service_accounts" type="rbac">
        <template #default="{ curPageData, pageConf, handlePageChange, handlePageSizeChange, handleGetExtData }">
            <bk-table
                :data="curPageData"
                :pagination="pageConf"
                @page-change="handlePageChange"
                @page-limit-change="handlePageSizeChange">
                <bk-table-column :label="$t('名称')" prop="metadata.name" sortable :resizable="false"></bk-table-column>
                <bk-table-column :label="$t('命名空间')" prop="metadata.namespace" sortable :resizable="false"></bk-table-column>
                <bk-table-column label="Secrets">
                    <template #default="{ row }">
                        <span>{{ handleGetExtData(row.metadata.uid, 'secrets') || '--' }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column label="Age" :resizable="false">
                    <template #default="{ row }">
                        <span v-bk-tooltips="{ content: handleGetExtData(row.metadata.uid, 'createTime') }">{{ handleGetExtData(row.metadata.uid, 'age') }}</span>
                    </template>
                </bk-table-column>
            </bk-table>
        </template>
    </BaseLayout>
</template>
<script>
    import { defineComponent } from '@vue/composition-api'
    import BaseLayout from '@open/views/dashboard/common/base-layout'

    export default defineComponent({
        components: { BaseLayout }
    })
</script>
