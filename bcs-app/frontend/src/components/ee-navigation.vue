<template>
    <bcs-navigation navigation-type="top-bottom" :need-menu="false" :side-title="$t('蓝鲸容器管理平台')">
        <template slot="side-icon">
            <img src="@/images/bcs2.svg" class="all-icon">
        </template>
        <template #header>
            <div class="bcs-navigation-header">
                <div class="nav-left">
                    <bcs-select class="header-select" :clearable="false" searchable :value="curProjectCode" @selected="handleProjectSelected">
                        <bk-option v-for="option in onlineProjectList"
                            :key="option.project_code"
                            :id="option.project_code"
                            :name="option.project_name">
                        </bk-option>
                        <div slot="extension">
                            <div class="extension-item" @click="showCreateProject = true"><i class="bk-icon icon-plus-circle mr5"></i>{{$t('新建项目')}}</div>
                            <div class="extension-item" @click="handleGotoProjectManage"><i class="bcs-icon bcs-icon-apps mr5"></i>{{$t('项目管理')}}</div>
                        </div>
                    </bcs-select>
                </div>
                <div class="nav-right">
                    <div class="header-help">
                        <i class="bcs-icon bcs-icon-help-2"></i>
                    </div>
                    <bcs-popover theme="light navigation-message" :arrow="false" offset="0, 10" placement="bottom-start" :tippy-options="{ 'hideOnClick': false }">
                        <div class="header-user">
                            {{user.username}}
                            <i class="bk-icon icon-down-shape"></i>
                        </div>
                        <template slot="content">
                            <ul class="bcs-navigation-admin">
                                <li class="nav-item" v-for="userItem in userItems" :key="userItem.id" @click="handleUserItemClick(userItem)">
                                    {{userItem.name}}
                                </li>
                            </ul>
                        </template>
                    </bcs-popover>
                </div>
            </div>
        </template>
        <template #default>
            <App />
            <bcs-dialog v-model="showCreateProject"
                theme="primary"
                :mask-close="false"
                :title="$t('新建项目')"
                width="860"
                @confirm="handleCreateProject">
                <bk-form v-model="formData">
                    <bk-form-item :label="$t('项目名称')" property="project_name" required>
                        <bk-input class="create-input" :placeholder="$t('请输入4-12字符的项目名称')" v-model="formData.project_name"></bk-input>
                    </bk-form-item>
                    <bk-form-item :label="$t('项目英文名')" property="english_name" required>
                        <bk-input class="create-input" :placeholder="$t('请输入2-32字符的小写字母+数字，以小写字母开头')" v-model="formData.english_name"></bk-input>
                    </bk-form-item>
                    <bk-form-item :label="$t('项目说明')" property="description" required>
                        <bk-input
                            class="create-input"
                            :placeholder="$t('请输入项目描述')"
                            type="textarea"
                            :rows="3"
                            :maxlength="100"
                            v-model="formData.description">
                        </bk-input>
                    </bk-form-item>
                </bk-form>
            </bcs-dialog>
        </template>
    </bcs-navigation>
</template>
<script lang="ts">
    import { computed, defineComponent, onMounted, ref } from '@vue/composition-api'
    import App from '@/App.vue'
    import { createProject } from '@/api/base'
    import bkLogout from '@/common/bklogout'
    export default defineComponent({
        name: "Navigation",
        components: {
            App
        },
        setup: (props, { root }) => {
            const { $i18n, $store, $router, $route, $bkMessage } = root
            const userItems = [
                {
                    id: 'project',
                    name: $i18n.t('项目管理')
                },
                {
                    id: 'auth',
                    name: $i18n.t('权限中心')
                },
                {
                    id: 'exit',
                    name: $i18n.t('退出')
                }
            ]
            const showCreateProject = ref(false)
            const user = computed(() => {
                return $store.state.user
            })
            const formData = ref({
                project_name: '',
                english_name: '',
                description: ''
            })
            const curProjectCode = computed(() => {
                return $store.state.curProjectCode
            })
            const onlineProjectList = computed(() => {
                return $store.state.sideMenu.onlineProjectList
            })
            const handleProjectSelected = (code) => {
                const item = onlineProjectList.value.find(item => item.project_code === code)
                $router.replace({
                    name: $route.name,
                    params: {
                        projectCode: code,
                        // eslint-disable-next-line camelcase
                        projectId: item?.project_id
                    }
                })
                const event = new CustomEvent('change::$currentProjectId', { detail: { currentProjectId: code } })
                window.dispatchEvent(event)
            }
            const handleGotoProjectManage = () => {
                $router.replace({
                    name: 'projectManage'
                })
            }
            const handleUserItemClick = (item) => {
                switch (item.id) {
                    case 'project':
                        handleGotoProjectManage()
                        break
                    case 'auth':
                        window.open(`${window.BK_IAM_APP_URL}/my-perm`)
                        break
                    case 'exit':
                        bkLogout.logout()
                        break
                }
            }
            const handleCreateProject = async () => {
                const result = await createProject({
                    bg_id: "",
                    bg_name: "",
                    center_id: "",
                    center_name: "",
                    deploy_type: [],
                    dept_id: "",
                    dept_name: "",
                    description: formData.value.description,
                    english_name: formData.value.english_name,
                    is_secrecy: false,
                    kind: "0",
                    project_name: formData.value.project_name,
                    project_type: ""
                }).catch(() => false)
                result && $bkMessage({
                    message: $i18n.t('创建成功'),
                    theme: 'success'
                })
            }
            onMounted(async () => {
                if (!window.$userInfo?.username && !Object.keys($store.state.user).length) {
                    await $store.dispatch('userInfo').catch(e => console.log(e))
                }
            })
            return {
                formData,
                userItems,
                user,
                curProjectCode,
                onlineProjectList,
                showCreateProject,
                handleProjectSelected,
                handleUserItemClick,
                handleCreateProject,
                handleGotoProjectManage
            }
        }
    })
</script>
<style lang="postcss" scoped>
/deep/ .bk-navigation-wrapper .container-content {
    padding: 0;
}
.bcs-navigation-admin {
    display:flex;
    flex-direction:column;
    background:#FFFFFF;
    border:1px solid #E2E2E2;
    margin:0;
    color:#63656E;
    padding: 6px 0;
}
.nav-item {
    flex:0 0 32px;
    display:flex;
    align-items:center;
    padding:0 20px;
    list-style:none;
    &:hover {
        color:#3A84FF;
        cursor:pointer;
        background-color:#F0F1F5;
    }
}
.extension-item {
    &:hover {
        cursor: pointer;
    }
}
/deep/ .create-input {
    width: 90%;
}
.bcs-navigation-header {
    flex:1;
    height:100%;
    display:flex;
    align-items:center;
    justify-content: space-between;
    font-size:14px;
    .nav-left {
        flex: 1;
        display:flex;
        padding:0;
        margin:0;
        .header-select {
            width:240px;
            margin-right:34px;
            border:none;
            background:#252F43;
            color:#D3D9E4;
            box-shadow:none;
        }
        .header-nav-item {
            list-style:none;
            height:50px;
            display:flex;
            align-items:center;
            margin-right:40px;
            color:#96A2B9;
            min-width:56px;
            &:hover {
                cursor:pointer;
                color:#D3D9E4;
            }
            &.active {
                color: #fff;
            }
        }
    }
    .nav-right {
        display: flex;
        align-items: center;
        .header-help {
            color:#768197;
            font-size:16px;
            position:relative;
            height:32px;
            width:32px;
            display:flex;
            align-items:center;
            justify-content:center;
            margin-right:8px;
            &:hover {
                background:linear-gradient(270deg,rgba(37,48,71,1) 0%,rgba(38,50,71,1) 100%);
                border-radius:100%;
                cursor:pointer;
                color:#D3D9E4;
            }
        }
        /deep/ .header-user {
            height:100%;
            display:flex;
            align-items:center;
            justify-content:center;
            color:#96A2B9;
            margin-left:8px;
            .bk-icon {
                margin-left:5px;
                font-size:12px;
            }
            &:hover {
                cursor:pointer;
                color:#D3D9E4;
            }
        }
    }
}
</style>
