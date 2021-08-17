<template>
    <div class="project-manage" v-bkloading="{ isLoading: basicLoading, zIndex: 10 }">
        <div class="title mb20">
            {{$t('项目管理')}}
        </div>
        <!-- <bk-alert class="mb20" type="info" :title="$t('项目管理')"></bk-alert> -->
        <div class="operate mb15">
            <bk-button class="create-btn" theme="primary" icon="plus"
                @click="handleCreateProject">{{$t('创建项目')}}</bk-button>
            <bk-input
                class="search-input"
                clearable
                :placeholder="$t('输入关键字搜索')"
                :right-icon="'bk-icon icon-search'"
                v-model="keyword">
            </bk-input>
        </div>
        <bk-table :data="filterList" size="medium">
            <bk-table-column :label="$t('项目名称')" prop="project_name">
                <template #default="{ row }">
                    <div class="row-name">
                        <span class="row-name-left">{{row.project_name[0]}}</span>
                        <div class="row-name-right">
                            <bk-button theme="primary" text @click="handleGotoProject(row)">
                                {{row.project_name}}
                            </bk-button>
                            <span class="time">{{ row.updated_at }}</span>
                        </div>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t('项目英文名')" prop="english_name"></bk-table-column>
            <bk-table-column :label="$t('项目说明')" prop="description"></bk-table-column>
            <bk-table-column :label="$t('创建者')" prop="creator"></bk-table-column>
            <bk-table-column label="操作" width="120">
                <template #default="{ row }">
                    <bk-button class="mr10" theme="primary" text @click="handleEditProject(row)">{{$t('编辑项目')}}</bk-button>
                    <!-- <bk-button theme="primary" text>{{$t('申请监控中心')}}</bk-button> -->
                </template>
            </bk-table-column>
        </bk-table>
        <ProjectCreate v-model="showCreateDialog" :project-data="curProjectData"></ProjectCreate>
    </div>
</template>
<script lang="ts">
    import { defineComponent, ref, onMounted, computed } from '@vue/composition-api'
    import ProjectCreate from './project-create.vue'
    export default defineComponent({
        name: "ProjectManagement",
        components: {
            ProjectCreate
        },
        setup: (props, ctx) => {
            const { $store, $router } = ctx.root
            const projectList = ref<any[]>([])
            const filterList = computed(() => {
                return projectList.value.filter(item => item.project_name.indexOf(keyword.value) > -1)
            })
            const keyword = ref('')
            const basicLoading = ref(false)
            const showCreateDialog = ref(false)
            const curProjectData = ref(null)
            const handleGotoProject = (row) => {
                window.$currentProjectId = row.project_code
                $router.push({
                    name: 'clusterMain',
                    params: {
                        projectCode: row.project_code,
                        projectId: row.project_id
                    }
                })
                const event = new CustomEvent('change::$currentProjectId', { detail: { currentProjectId: row.project_code } })
                window.dispatchEvent(event)
            }
            const handleEditProject = (row) => {
                curProjectData.value = row
                showCreateDialog.value = true
            }
            const handleCreateProject = () => {
                curProjectData.value = null
                showCreateDialog.value = true
            }

            onMounted(async () => {
                basicLoading.value = true
                const data = await $store.dispatch('getProjectList').catch(() => ([]))
                projectList.value = data
                basicLoading.value = false
            })

            return {
                basicLoading,
                keyword,
                projectList,
                filterList,
                showCreateDialog,
                curProjectData,
                handleGotoProject,
                handleEditProject,
                handleCreateProject
            }
        }
    })
</script>
<style lang="postcss" scoped>
.project-manage {
    padding: 20px 60px 20px 60px;
    background: #f5f7fa;
    width: 100%;
    .title {
        font-size: 16px;
        color: #313238;
    }
    .operate {
        display: flex;
        align-content: center;
        justify-content: space-between;
        .create-btn {
            width: 120px;
        }
        .search-input {
            width: 500px;
        }
    }
    .row-name {
        display: flex;
        align-items: center;
        &-left {
            display: inline-block;
            position: relative;
            margin-right: 10px;
            width: 32px;
            height: 32px;
            line-height: 30px;
            border-radius: 16px;
            text-align: center;
            color: #fff;
            font-size: 16px;
            background-color: rgb(227, 213, 194);
        }
        &-right {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            flex: 1;
        }
    }
}
</style>
