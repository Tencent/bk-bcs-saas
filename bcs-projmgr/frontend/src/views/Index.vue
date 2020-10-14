<template>
    <div v-bkloading='loadingOption' class='devops-index'>
        <template v-if='projectList'>
            <Header />
            <main>
                <template v-if='hasProjectList'>
                    <empty-tips v-if='!hasProject' :title="`${$t('pageTips.noPermissionTitlePrefix')}${$t('pageTips.noPermissionTitleSuffix')}`" :desc="$t('pageTips.noPermissionDesc')">

                        <bk-button type='primary' @click='switchProject'>{{ $t('pageTips.switchProject') }}</bk-button>
                        <bk-button type='success' @click='joinProject'>{{ $t('pageTips.joinProject') }}</bk-button>
                    </empty-tips>
                </template>
                <router-view v-if='!hasProjectList || isOnlineProject || isApprovalingProject'></router-view>
            </main>
        </template>

        <login-dialog v-if='showLoginDialog'></login-dialog>
    </div>
</template>

<script lang="ts">
import Vue from 'vue'
import Header from '../components/Header'
import LoginDialog from '../components/LoginDialog'
import { Component, Watch } from 'vue-property-decorator'
import { State, Getter, Action } from 'vuex-class'
import eventBus from '../utils/eventBus'
import { urlJoin, getAuthUrl } from '../utils/util'
import compilePath from '../utils/pathExp'

@Component({
    components: {
        Header,
        LoginDialog
    }
})
export default class Index extends Vue {
    @State projectList
    @State headerConfig
    @State isShowPreviewTips
    @Getter onlineProjectList
    @Getter approvalingProjectList
    @Action getPermissionUrl

    showLoginDialog: boolean = false
    showExplorerTips: string = localStorage.getItem('showExplorerTips')

    get loadingOption(): object {
        return {
            isLoading: this.projectList === null
        }
    }

    get hasProject(): boolean {
        return this.projectList.some(project => project.project_code === this.$route.params.projectId && project.permission !== false)
    }

    get isOfflineProject(): boolean {
        const project = this.projectList.find(project => project.project_code === this.$route.params.projectId)
        return project ? project.is_offlined : false
    }

    get isApprovalingProject(): boolean {
        return !!this.approvalingProjectList.find(project => project.project_code === this.$route.params.projectId)
    }

    get isOnlineProject(): boolean {
        return !!this.onlineProjectList.find(project => project.project_code === this.$route.params.projectId)
    }

    get hasProjectList(): boolean {
        return this.headerConfig.showProjectList
    }

    get chromeExplorer(): boolean {
        let explorer = window.navigator.userAgent
        return explorer.indexOf('Chrome') >= 0 && explorer.indexOf('QQ') === -1
    }

    @Watch('$route.path')
    routeChange(name: string): void {
        this.hasProjectList && this.saveProjectId()
    }
    
    switchProject() {
        this.iframeUtil.toggleProjectMenu(true)
    }

    async joinProject() {
        location.href = '/console'
    }

    saveProjectId(): void {
        const { $route, projectList } = this
        if (
            projectList.find(
                project =>
                    project.project_code === $route.params.projectId &&
                    !project.is_offlined &&
                    (project.approval_status === 2 || project.approval_status === 1)
            )
        ) {
            localStorage.setItem('projectId', $route.params.projectId)
        }
    }

    created() {
        this.hasProjectList && this.saveProjectId()
        eventBus.$on('toggle-login-dialog', isShow => {
            this.showLoginDialog = isShow
        })
        if (this.showExplorerTips === null) {
            localStorage.setItem('showExplorerTips', 'true')
            this.showExplorerTips = localStorage.getItem('showExplorerTips')
        }
        eventBus.$on('update-project-id', projectId => {
            this.$router.replace({
                params: {
                    projectId
                }
            })
        })
    }
}
</script>

<style lang="scss">
@import '../assets/scss/conf';
.devops-index {
    height: 100%;
    display: flex;
    flex: 1;
    flex-direction: column;
    background-color: $bgHoverColor;
    > main {
        display: flex;
        flex: 1;
        overflow: auto;
    }
    .user-prompt {
        display: flex;
        justify-content: space-between;
        padding: 0 24px;
        min-width: 1280px;
        line-height: 32px;
        background-color: #ff9600;
        color: #fff;
        .icon-info-circle-shape {
            position: relative;
            top: 2px;
            margin-right: 7px;
            font-size: 16px;
        }
        .close-remind {
            margin-right: 20px;
            cursor: pointer;
        }
        .icon-close {
            top: 8px;
            right: 24px;
            font-size: 14px;
            cursor: pointer;
        }
    }
}
</style>
