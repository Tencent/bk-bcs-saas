<template>
    <BaseLayout title="Pods" kind="Pod" category="pods" type="workloads">
        <template #default="{ curPageData, pageConf, handlePageChange, handlePageSizeChange, handleGetExtData, gotoDetail, handleSortChange }">
            <bk-table
                :data="curPageData"
                :pagination="pageConf"
                @page-change="handlePageChange"
                @page-limit-change="handlePageSizeChange"
                @sort-change="handleSortChange">
                <bk-table-column :label="$t('名称')" prop="metadata.name" sortable :resizable="false">
                    <template #default="{ row }">
                        <bk-button class="bcs-button-ellipsis" text @click="gotoDetail(row)">{{ row.metadata.name }}</bk-button>
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
                <bk-table-column label="Host IP" width="140" :resizable="false">
                    <template slot-scope="{ row }">{{row.status.hostIP || '--'}}</template>
                </bk-table-column>
                <bk-table-column label="Pod IP" width="140" :resizable="false">
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
        </template>
    </BaseLayout>
</template>
<script>
    import { defineComponent } from '@vue/composition-api'
    import BaseLayout from '@open/views/dashboard/common/base-layout'
    import StatusIcon from '@open/views/dashboard/common/status-icon'

    export default defineComponent({
        components: { BaseLayout, StatusIcon }
    })
</script>
