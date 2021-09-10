<template>
    <bcs-navigation navigation-type="top-bottom" :need-menu="false" :side-title="$t('蓝鲸容器管理平台')">
        <template slot="side-icon">
            <img src="@/images/bcs.svg" class="all-icon">
        </template>
        <template #header>
            <div class="bcs-navigation-header">
                <div class="nav-left">
                    <bcs-select ref="projectSelectRef" class="header-select" :clearable="false" searchable :value="curProjectCode"
                        v-show="$route.name !== 'projectManage'"
                        @selected="handleProjectSelected">
                        <bk-option v-for="option in onlineProjectList"
                            :key="option.project_code"
                            :id="option.project_code"
                            :name="option.project_name">
                        </bk-option>
                        <template #extension>
                            <div class="extension-item" @click="handleCreateProject"><i class="bk-icon icon-plus-circle mr5"></i>{{$t('新建项目')}}</div>
                            <div class="extension-item" @click="handleGotoProjectManage"><i class="bcs-icon bcs-icon-apps mr5"></i>{{$t('项目管理')}}</div>
                        </template>
                    </bcs-select>
                </div>
                <div class="nav-right">
                    <div class="header-help" @click="handleGotoHelp">
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
            <ProjectCreate v-model="showCreateProject"></ProjectCreate>
        </template>
    </bcs-navigation>
</template>
<script>
    import App from '@/App.vue'
    import ProjectCreate from '@/views/project/project-create.vue'
    export default {
        name: "Navigation",
        components: {
            App,
            ProjectCreate
        },
        data () {
            return {
                userItems: [
                    {
                        id: 'project',
                        name: this.$t('项目管理')
                    },
                    {
                        id: 'auth',
                        name: this.$t('权限中心')
                    },
                    {
                        id: 'exit',
                        name: this.$t('退出')
                    }
                ],
                showCreateProject: false
            }
        },
        computed: {
            user () {
                return this.$store.state.user
            },
            curProjectCode () {
                return this.$route.params.projectCode
            },
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            }
        },
        watch: {
            curProjectCode (code) {
                if (code) {
                    window.$currentProjectId = code
                    this.init(code)
                }
            }
        },
        async created () {
            if (!window.$syncUrl) {
                window.$syncUrl = (path, flag = false) => {
                    const resolve = this.$router.resolve({ path: `${SITE_URL}${path}` })
                    if (this.$route.name === resolve?.route?.name || !flag) return

                    window.location.href = `${SITE_URL}${path}`
                    // console.log(curPath, path)
                    // this.$router.push({
                    //     path: `${SITE_URL}${path}`
                    // })
                }
            }
            const list = []
            list.push(this.$store.dispatch('getProjectList').catch(() => ([])))
            list.push(this.$store.dispatch('userInfo').catch(e => console.log(e)))
            const [projectList, userInfo] = await Promise.all(list)
            window.$projectList = projectList
            window.$userInfo = userInfo
        },
        methods: {
            init (code) {
                const event = new CustomEvent('change::$currentProjectId', { detail: { currentProjectId: code } })
                window.dispatchEvent(event)
            },
            async handleProjectSelected (code) {
                window.$currentProjectId = code
                const item = this.onlineProjectList.find(item => item.project_code === code)
                this.$router.push({
                    name: this.$route.name,
                    params: {
                        projectCode: code,
                        // eslint-disable-next-line camelcase
                        projectId: item?.project_id
                    }
                })
                this.init(code)
            },
            handleGotoProjectManage () {
                this.$refs.projectSelectRef && this.$refs.projectSelectRef.close()
                if (this.$route.name === 'projectManage') return
                this.$router.replace({
                    name: 'projectManage'
                })
            },
            handleUserItemClick (item) {
                switch (item.id) {
                    case 'project':
                        this.handleGotoProjectManage()
                        break
                    case 'auth':
                        window.open(`${window.BK_IAM_APP_URL}/my-perm`)
                        break
                    case 'exit':
                        break
                }
            },
            handleCreateProject () {
                this.$refs.projectSelectRef && this.$refs.projectSelectRef.close()
                this.showCreateProject = true
            },
            handleGotoHelp () {
                window.open(window.BCS_CONFIG?.doc?.help)
            }
        }
    }
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
    margin: 0 -16px;
    padding: 0 16px;
    &:hover {
        cursor: pointer;
        background-color: #f0f1f5;
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
