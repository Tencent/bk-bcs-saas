<template>
    <section class="cluster">
        <div class="title">{{ $t('创建或导入KuBernetes集群') }}</div>
        <div class="mode-wrapper mt15">
            <div class="mode-panel" v-for="item in modes" :key="item.id" @click="handleCreateCluster(item)">
                <span class="mode-panel-icon"><i :class="item.icon"></i></span>
                <span class="mode-panel-title">{{ item.title }}</span>
                <span class="mode-panel-desc">{{ item.desc }}</span>
            </div>
        </div>
        <div class="cluster-template-title">
            <span class="title">{{ $t('管理集群模板') }}</span>
            <bcs-button size="small" @click="handleCreateTemplate">{{ $t('新建集群模板') }}</bcs-button>
        </div>
        <bcs-table class="mt15" :data="tableData" :pagination="pagination" v-bcsloading="{ isLoading }">
            <bcs-table-column type="selection" width="60"></bcs-table-column>
            <bcs-table-column :label="$t('模板名称')">
                <template #default="{ row }">
                    <bcs-button text>{{ row.name }}</bcs-button>
                </template>
            </bcs-table-column>
            <bcs-table-column :label="$t('描述')" prop=""></bcs-table-column>
            <bcs-table-column :label="$t('创建者')" prop=""></bcs-table-column>
            <bcs-table-column :label="$t('更新者')" prop=""></bcs-table-column>
            <bcs-table-column :label="$t('更新时间')" prop=""></bcs-table-column>
            <bcs-table-column :label="$t('操作')">
                <template #default="{ row }">
                    <bcs-button text @click="handleEditTemplate(row)">{{ $t('编辑') }}</bcs-button>
                    <bcs-button text @click="handleDeleteTemplate(row)">{{ $t('删除') }}</bcs-button>
                </template>
            </bcs-table-column>
        </bcs-table>
    </section>
</template>
<script lang="ts">
    import { defineComponent, ref } from '@vue/composition-api'

    export default defineComponent({
        name: 'CreateCluster',
        setup (props, ctx) {
            const { $i18n, $router } = ctx.root
            const modes = ref([
                {
                    id: 'form',
                    title: $i18n.t('自建集群'),
                    desc: $i18n.t('可自定义集群基本信息和集群版本'),
                    icon: ''
                },
                {
                    id: 'import',
                    title: $i18n.t('导入集群'),
                    desc: $i18n.t('支持快速导入已存在的集群'),
                    icon: 'bcs-icon bcs-icon-upload'
                }
            ])

            // 创建集群
            const handleCreateCluster = (item) => {
                item.id === 'form' ? $router.push({ name: 'createFormCluster' }) : $router.push({ name: 'createImportCluster' })
            }

            const pagination = ref({
                current: 1,
                count: 0,
                limit: 20
            })
            const isLoading = ref(false)
            const tableData = ref([])
            // 获取表格数据
            const handleGetTableData = async () => {
                isLoading.value = true
                // todo
                isLoading.value = false
            }
            // 创建集群模板
            const handleCreateTemplate = () => {
                $router.push({ name: 'createClusterTemplate' })
            }
            // 编辑集群模板
            const handleEditTemplate = (row) => {}
            // 删除集群模板
            const handleDeleteTemplate = (row) => {}
            return {
                modes,
                isLoading,
                tableData,
                pagination,
                handleCreateCluster,
                handleGetTableData,
                handleCreateTemplate,
                handleEditTemplate,
                handleDeleteTemplate
            }
        }
    })
</script>
<style lang="postcss" scoped>
.cluster {
    padding: 30px 20px;
    .title {
        font-size: 14px;
        font-weight: 700;
        text-align: left;
        color: #63656e;
        line-height: 22px;
    }
    .mode-wrapper {
        display: flex;
        align-items: center;
    }
    .mode-panel {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-right: 24px;
        flex: 1;
        background: #fff;
        border-radius: 1px;
        box-shadow: 0px 2px 4px 0px rgba(25,25,41,0.05);
        height: 238px;
        cursor: pointer;
        &:hover {
            border: 1px solid #1768ef;
            .mode-panel-icon {
                background: #e1ecff;
            }
            .mode-panel-title {
                color: #3a84ff;
            }
        }
        &:last-child {
            margin-right: 0;
        }
        &-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            color: #979ba5;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #f5f7fa;
        }
        &-title {
            margin-top: 20px;
            font-size: 20px;
            font-weight: 400;
            color: #63656e;
            line-height: 28px;
        }
        &-desc {
            margin-top: 8px;
            font-size: 14px;
            font-weight: 400;
            text-align: center;
            color: #979ba5;
            line-height: 22px;
        }
    }
    .cluster-template-title {
        display: flex;
        justify-content: space-between;
        margin-top: 40px;
    }
}
</style>
