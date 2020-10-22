<template>
    <div class='devops-header'>
        <div class='header-left-bar'>
            <router-link class='header-logo' to='/console/'>
                <Logo :name="$t('serviceLogo')" :width="$t('serviceLogo') === 'service-logo-en' ? 200 : 150" height='40' />
            </router-link>
            <bk-dropdown ref='projectDropdown' v-if='showProjectList' class='devops-project-dropdown' :list='selectProjectList' :selected='projectId' :placeholder="$t('chooseProject')" displayKey='project_name' settingKey='project_code' searchKey='project_name' :searchable='true' @visible-toggle='handleDropdownVisible' @item-selected='handleProjectChange' :has-create-item='true'>
                <div class="bk-selector-create-item" @click.stop.prevent="popProjectDialog()">
                    <i class="bk-icon icon-plus-circle"></i>
                    <i class="text">{{ $t('addProject') }}</i>
                </div>
                <div class="bk-selector-create-item" @click.stop.prevent="goToPm">
                    <i class="bk-icon icon-apps"></i>
                    <i class="text">{{ $t('projectTitle') }}</i>
                </div>
            </bk-dropdown>

            <!-- <nav-menu v-if='showNav'></nav-menu> -->
            <!-- <nav-menu v-if='!title'></nav-menu> -->
            <!-- <h3 v-if='title' class='service-title' @click='goHome'>
                <logo :name='serviceLogo' size='20'  />
                {{ title }}
            </h3> -->

            <h3 v-for='service in serviceList' :class="{'activeClass': service.isActive, 'service-title': true }" @click='service.action(service.key)' :key='service.key'>
                <logo :name="service.key" size='20' />
                {{ service.name }}
            </h3>
        </div>
        <div class='header-right-bar'>
            <i class='bk-icon icon-helper' @click.stop="goToDocs" />
            <!-- <i class='bk-icon icon-notification' /> -->
            <User class='user-info' v-bind='user' />
        </div>

        <project-dialog :initShowDialog='showProjectDialog' :title='projectDialogTitle'>
        </project-dialog>
    </div>
</template>


<script lang="ts">
import Vue from 'vue'
import { Component, Watch, Prop } from 'vue-property-decorator'
import { State, Action, Getter } from 'vuex-class'
import User from '../User/index.vue'
import NavMenu from './NavMenu.vue'
import Logo from '../Logo/index.vue'
import ProjectDialog from '../ProjectDialog/index.vue'
import { mapState } from 'vuex'
import eventBus from '../../utils/eventBus'
@Component({
    components: {
        User,
        NavMenu,
        ProjectDialog,
        Logo
    }
})
export default class Header extends Vue {
    @State user
    @State projectList
    @State showProjectDialog
    @State projectDialogTitle
    @State headerConfig

    @Getter onlineProjectList

    @Action toggleProjectDialog
    @Action togglePopupShow
    @Action getUserPerms
    @Action getProjectPerms

    isDropdownMenuVisible: boolean = false
    isShowTooltip: boolean = true

    get showProjectList(): boolean {
        return this.headerConfig.showProjectList
    }
    get showNav(): boolean {
        return this.headerConfig.showNav
    }
    get projectId(): string {
        return this.$route.params.projectId
    }
    get title(): string {
        return this.$route.meta.header
    }
    get serviceLogo(): string {
        return this.$route.meta.logo
    }

    get serviceList(): object[] {
        return [
            {
                name: this.$t('bcsName'),
                key: 'bcs',
                isActive: this.title === this.$t('bcsName'),
                action: this.title === this.$t('bcsName') ? this.goHome : this.goConitor
            },
            {
                name: this.$t('monitorName'),
                key: 'monitor',
                isActive: this.title === this.$t('monitorName'),
                action: this.title === this.$t('monitorName') ? this.goHome : this.goConitor
            }
        ]
    }

    get selectProjectList(): Project[] {
        let list = this.projectList.filter(
            item => !item.is_offlined && item.permissions && item.permissions.project_view
        )
        // console.log('==========================' + list)
        return list.sort(function(a, b) {
            return a.created_at < b.created_at ? 1 : -1
        })
    }

    $refs: {
        projectDropdown: any
    }

    created() {
        eventBus.$on('show-project-menu', () => {
            const ele = this.$refs.projectDropdown.$el
            ele && ele.click()
        })

        eventBus.$on('hide-project-menu', () => {
            if (this.isDropdownMenuVisible) {
                const ele = this.$refs.projectDropdown.$el
                ele && ele.click()
            }
        })

        eventBus.$on('show-project-dialog', (project: Project) => {
            this.popProjectDialog(project)
        })
    }

    handleDropdownVisible(isShow: boolean): void {
        if (this.isDropdownMenuVisible !== isShow) {
            this.togglePopupShow(isShow)
        }
        this.isDropdownMenuVisible = isShow
    }

    goHome(): void {
        eventBus.$emit('goHome')
        const homeRouter = this.$route.meta.to
        if (homeRouter) {
            this.$router.push({
                name: homeRouter,
                params: this.$route.params
            })
        }
    }
    goConitor(type): void {
        let path = ''
        const projectId = window.localStorage.projectId
        const index = projectId ? this.selectProjectList.findIndex(item => item.project_code === projectId) : -1
        let id = index > -1 ? projectId : this.selectProjectList[0]['project_code']
        if (type === 'bcs') {
            path = `/console/bcs/${id}/cluster?v`
        } else if (type === 'monitor') {
            path = `/console/monitor/${id}/`
        }
        this.$router.push({
            path: path,
            params: this.$route.params
        })
    }

    handleProjectChange(id: string, project: object) {
        const { projectId } = this.$route.params
        if (projectId && this.selectProjectList.every(project => project.project_code !== projectId)) {
            //当前无权限时返回首页
            this.$router.replace({
                name: this.$route.name,
                params: {
                    projectId: id
                }
            })
        } else {
            this.$router.replace({
                params: {
                    projectId: id
                }
            })
        }
    }

    to(url: string): void {
        window.open(url, '_blank')
    }

    goToDocs(): void {
        window.open(BCS_DOCS_URL, '_blank')
    }

    goToPm(): void {
        // this.to('/console/pm')
        this.to('/console/')
    }

    async popProjectDialog(project: Project) {
        let showEdit = false
        let res
        try {
            if (!project) {
                res = await this.getUserPerms({})
                // @ts-ignore
                if (res.project_create && !res.project_create.is_allowed && res.project_create.apply_url) {
                    this.$showAskPermissionDialog({
                        noPermissionList: [{
                            resource: this.$t('project'), 
                            option: this.$t('create')
                        }],
                        // @ts-ignore
                        applyPermissionUrl: res.project_create.apply_url
                    })
                } else {
                    showEdit = true
                }
            } else {
                res = await this.getProjectPerms({
                    project_id: project.project_id,
                    action_ids: ['project_edit']
                })
                // @ts-ignore
                if (res.project_edit && !res.project_edit.is_allowed && res.project_edit.apply_url) {
                    this.$showAskPermissionDialog({
                        noPermissionList: [{
                            resource: this.$t('project'), 
                            option: this.$t('edit')
                        }],
                        // @ts-ignore
                        applyPermissionUrl: res.project_edit.apply_url
                    })
                } else {
                    showEdit = true
                }
            }
        } catch (err) {
            this.$bkMessage({
                theme: 'error',
                message: err.message || err
            })   
        }
        showEdit && this.toggleProjectDialog({
            showProjectDialog: true,
            project
        })
    }

    closeTooltip(): void {
        this.isShowTooltip = false
    }
}
</script>

<style lang="scss">
@import '../../assets/scss/conf';

.activeClass {
    background-color: black;
}
$headerBgColor: #191929;
.link {
    color: white;
    margin: 0 20px;
}
.devops-header {
    height: $headerHeight;
    display: flex;
    align-items: center;
    position: relative;
    z-index: 1234;
    min-width: 1280px;
    background-color: $headerBgColor;
    transition: all 0.3s ease;
    .header-left-bar {
        height: 100%;
        flex: 1;
        display: flex;
        align-items: center;
        .header-logo {
            margin-left: 15px;
            margin-right: 15px;
            width: 230px;
        }
        $dropdownBorder: #2a2a42;
        .devops-project-dropdown {
            width: 233px;
            color: $fontColor;
            .bk-selector-input {
                border-color: $dropdownBorder;
                background-color: $headerBgColor;
                color: $fontLigtherColor;
                height: 36px;
                line-height: 36px;
                &:hover,
                &.active {
                    border-color: $dropdownBorder !important;
                    background-color: black;
                    color: white !important;
                }
            }
            .bk-selector-icon {
                top: 15px;
                color: $fontLigtherColor !important;
            }
            .bk-selector-list {
                top: 45px !important;
            }
            .bk-selector-create-item:hover {
                &,
                .text {
                    color: $primaryColor;
                }
            }
        }

        .service-title {
            display: flex;
            align-items: center;
            height: 100%;
            padding: 0 18px;
            margin-left: 10px;
            color: $fontLigtherColor;
            font-size: 14px;
            cursor: pointer;

            &:hover {
                color: white;
                background-color: black;
            }
            > svg {
                margin-right: 5px;
            }
        }
    }

    .header-right-bar {
        justify-self: flex-end;
        height: $headerHeight;
        display: flex;
        display: flex;
        align-items: center;

        > .bk-icon:hover,
        > .feed-back-icon:hover,
        > .user-info:hover,
        > .feed-back-icon.active,
        > .user-info.active {
            color: white;
            background-color: black;
        }

        > .seperate-line {
            padding: 0 5px;
            font-size: 20px;
            // color: $fontLigtherColor;
            line-height: $headerHeight;
        }

        > .bk-icon {
            padding: 0 10px;
            font-size: 20px;
            color: $fontLigtherColor;
            line-height: $headerHeight;
            cursor: pointer;
        }

        > .user-info {
            margin: 0 10px;
        }
    }
}
</style>
