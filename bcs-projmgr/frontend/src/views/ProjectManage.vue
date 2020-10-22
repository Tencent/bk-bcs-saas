<template>
    <div v-bkloading="{isLoading: isDataLoading}" class="pm-box">
        <div class="biz-pm biz-pm-index biz-create-pm">
            <template v-if="projectList.length || isDataLoading">
                <div class="biz-pm-header">
                    <div class="title">{{ $t('projectTitle') }}</div>
                    <div class="action">
                        <button class="bk-button bk-primary" @click="togglePMDialog(true)">
                            <i class="bk-icon icon-plus"></i>
                            <span style="margin-left: 0;">{{ $t('addProject') }}</span>
                        </button>
                        <div class="search-input-row">
                            <input type="text" name="searchInput" :placeholder="$t('searchTips')" v-model="inputValue" @keyup.enter="filterProjectList(isFilterByOffline)">
                            <a href="javascript:void(0)" class="biz-search-btn">
                                <i v-if="inputValue" class="bk-icon icon-close-circle-shape" @click="clearFilter"></i>
                                <i v-else class="bk-icon icon-search" @click="filterProjectList(isFilterByOffline)"></i>
                            </a>
                        </div>
                    </div>
                </div>
                <template v-if="curProjectList.length">
                    <table class="bk-table has-table-hover biz-table biz-pm-table">
                        <thead>
                            <tr>
                                <th style="width: 300px;border-bottom:none">{{ $t('projectTable.name') }}</th>
                                <th style="width: 300px;border-bottom:none">{{ $t('projectTable.englishName') }}</th>
                                <th>{{ $t('projectTable.desc') }}</th>
                                <th style="width: 100px;">{{ $t('projectTable.creator') }}</th>
                                <th style="width: 200px; text-align: center;">{{ $t('projectTable.operation') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="project in curPageData" :key="project.project_code">
                                <td>
                                    <span class="avatar" v-if="project.logo_addr">
                                        <img class="avatar-addr" :src="project.logo_addr">
                                    </span>
                                    <span class="avatar" v-else :class="['project-avatar', 'match-color-blue']">
                                        {{ project.project_name.substr(0, 1) }}
                                    </span>
                                    <div class="info">
                                        <p class="title">
                                            <template>
                                                <a href="javascript:void(0)" @click.stop.prevent="goProject(project)" :class="['bk-text-button', {'is-disabled': project.is_offlined}]" v-if="!project.is_offlined">{{project.project_name}}</a>
                                                <a href="javascript:void(0)" :class="['bk-text-button', {'is-disabled': project.is_offlined}]" v-else>{{project.project_name}}</a>
                                            </template>
                                        </p>
                                        <time class="time">{{ formatDate(project.created_at) }}</time>
                                    </div>
                                </td>
                                <td>
                                    <p class="desc">{{project.english_name}}</p>
                                </td>
                                <td>
                                    <p class="desc">{{project.description}}</p>
                                </td>
                                <td>
                                    <p class="desc">{{project.creator}}</p>
                                </td>
                                <td class="action">
                                    <template>
                                        <a v-if="project.permissions && !project.permissions.project_edit && !project.permissions.project_view" href="javascript:void(0)" @click="goProject(project)" class="bk-text-button">{{ $t('pageTips.joinProject') }}</a>
                                        <a v-else href="javascript:void(0)" :class="['bk-text-button', {'is-disabled': project.is_offlined}, {'en-underline': isEn}]" @click.stop.prevent="togglePMDialog(true, project)">{{ $t('projectTable.edit') }}</a>
                                        <!--<a href="javascript:void(0)" @click="goUserManager(project.project_code)" class="bk-text-button">{{ $t('projectTable.auth') }}</a>-->
                                    </template>
                                </td>
                            </tr>
                        </tbody>
                    </table>

                    <div class="biz-pm-page" v-if="pageConf && pageConf.show">
                        <bk-paging :cur-page.sync='pageConf.curPage' :total-page="pageConf.totalPage" @page-change='pageChange'></bk-paging>
                    </div>
                </template>
                <template v-else>
                    <div class="biz-guide-box" v-show="!isDataLoading">
                        <p class="title">{{ $t('pageTips.noFoundProject') }}</p>
                    </div>
                </template>
            </template>
            <empty-tips v-else :title="$t('pageTips.noProjectTitle')" :desc="$t('pageTips.noProjectDesc')">
                <button class="bk-button bk-primary" @click="togglePMDialog(true)">
                    <i class="bk-icon icon-plus"></i>
                    <span style="margin-left: 0;">{{ $t('addProject') }}</span>
                </button>
                <!--<a class="bk-button bk-success" :href="applyProjectUrl">
                    <span style="margin-left: 0;">{{ $t('pageTips.joinProject') }}</span>
                </a>-->
            </empty-tips>
        </div>
    </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Watch } from 'vue-property-decorator'
import { State, Action } from 'vuex-class'
import { getAuthUrl } from '../utils/util'
import Cookies from 'js-cookie'

@Component({})
export default class ProjectManage extends Vue {
    @State projectList
    @State newProject
    @Action toggleProjectDialog
    @Action ajaxUpdatePM
    @Action getProjects
    @Action getPermissionUrl
    @Action getUserPerms
    @Action getProjectPerms

    isFilterByOffline: boolean = false
    isDataLoading: boolean = false
    inputValue: string = ''
    offlineProjectNum: number
    curProjectList: object[] = []
    curPageData: object[] = []
    pageConf: any = {
        totalPage: 1,
        pageSize: 10,
        curPage: 1,
        show: false
    }
    matchColorList: any = ['green', 'yellow', 'red', 'blue']

    get isEn (): Boolean {
        const enArr: any = ['en', 'EN', 'ENGLISH', 'english', 'en-US']
        return Cookies.get('blueking_language') && enArr.includes(Cookies.get('blueking_language')) ? true : false
    }

    @Watch('isFilterByOffline')
    watchFilterOffline(isFilterByOffline: boolean): void {
        this.filterProjectList(isFilterByOffline)
    }

    @Watch('projectList', { deep: true })
    watchProjects(val): void {
        this.initList()
        this.reloadCurPage()
    }

    initList() {
        this.isDataLoading = true
        this.filterProjectList(this.isFilterByOffline)
        this.isDataLoading = false
    }

    filterProjectList(showOfflined) {
        let offlineList = this.projectList.filter(project => {
            return project.is_offlined === true
        })
        this.offlineProjectNum = offlineList.length

        if (showOfflined) {
            this.curProjectList = this.projectList.filter(project => {
                return project.project_name.indexOf(this.inputValue) !== -1 && project.approval_status !== 3
            })
        } else {
            this.curProjectList = this.projectList.filter(project => {
                return (
                    // project.is_offlined === false &&
                    project.project_name.indexOf(this.inputValue) !== -1 &&
                    project.approval_status !== 3
                )
            })
        }
        this.initPageConf()
        this.pageConf.curPage = 1
        this.curPageData = this.getDataByPage(this.pageConf.curPage)
    }

    clearFilter() {
        this.inputValue = ''
        this.filterProjectList(this.isFilterByOffline)
    }

    initPageConf() {
        let total = this.curProjectList.length
        if (total <= this.pageConf.pageSize) {
            this.pageConf.show = false
        } else {
            this.pageConf.show = true
        }
        this.pageConf.totalPage = Math.ceil(total / this.pageConf.pageSize)
    }

    reloadCurPage() {
        this.initPageConf()
        if (this.pageConf.curPage > this.pageConf.totalPage) {
            this.pageConf.curPage = this.pageConf.totalPage
        }
        this.curPageData = this.getDataByPage(this.pageConf.curPage)
    }

    getDataByPage(page) {
        let startIndex = (page - 1) * this.pageConf.pageSize
        let endIndex = page * this.pageConf.pageSize
        if (startIndex < 0) {
            startIndex = 0
        }
        if (endIndex > this.curProjectList.length) {
            endIndex = this.curProjectList.length
        }
        let data = this.curProjectList.slice(startIndex, endIndex)
        return data
    }

    pageChange(page) {
        this.pageConf.curPage = page
        let data = this.getDataByPage(page)
        this.curPageData = JSON.parse(JSON.stringify(data))
    }

    // 点击新增或编辑项目
    async togglePMDialog(show: boolean, project = null) {
        let showEdit = false
        let res = {}
        if (show) {
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
        } else {
            showEdit = true
        }
        showEdit && this.toggleProjectDialog({
            showProjectDialog: show,
            project
        })
    }

    async goProject(project: Project) {
        // @ts-ignore
        if (project && project.permissions && project.permissions.project_view) {
            window.open(`/console/bcs/${project.project_code}/cluster?v`, '_self')
        } else {
            const res = await this.getProjectPerms({
                project_id: project.project_id,
                action_ids: ['project_view']
            })
            if (res.project_view && res.project_view.apply_url) {
                this.$showAskPermissionDialog({
                    noPermissionList: [{
                        resource: this.$t('project'), 
                        option: this.$t('view')
                    }],
                    applyPermissionUrl: res.project_view.apply_url
                })
            }
        }
        
    }

    async applyJoin(projectCode: string) {
        const params = getAuthUrl(projectCode)
        try {
            const res = await this.getPermissionUrl(params)
            if (res && res.url) {
                window.open(res.url, '_blank')
            }
        } catch (err) {
            this.$bkMessage({
                theme: 'error',
                message: err.message || err
            })
        }
    }

    formatDate(dateStr: string): string {
        try {
            const date = new Date(dateStr)
            if (date.toString() === 'Invalid Date') throw new Error(`error date format： ${dateStr}`)
            const month = date.getMonth() + 1
            const day = date.getDate()
            return `${date.getFullYear()}-${month > 9 ? month : `0${month}`}-${day > 9 ? day : `0${day}`}`
        } catch (e) {
            return '--'
        }
    }

    async created() {
        this.initList()
        this.initPageConf()
    }
}
</script>

<style lang="scss" scoped>
.footer {
    display: block;
    height: 70px;
    background: #313b4c;
    color: #bfcbd7;
    font-size: 12px;
    position: absolute;
    width: 100%;
    line-height: 20px;
    padding: 20px 0 30px;
    bottom: 0px;
}
.pm-box {
    display: flex;
    flex: 1;
    justify-content: center;
    // width: 1280px;
    // padding: 30px 0 100px 0;
    overflow: auto;
}
.biz-pm-index {
    width: 1180px;
    margin: 0 auto 0 auto;
}
.biz-order {
    padding: 0;
    min-width: 20px;
    text-align: center;
}
.biz-pm-page {
    text-align: center;
    margin-top: 30px;
}
.biz-pm-index {
    padding-bottom: 75px;
}
.biz-pm-header {
    margin: 30px 0 25px 0;
    height: 36px;
    line-height: 36px;
    .title {
        float: left;
        font-size: 18px;
        color: #333948;
        a {
            color: #333948;
        }
    }
    .action {
        float: right;
    }
    .search-input-row {
        float: right;
        margin-left: 45px;
        padding: 0 10px;
        height: 36px;
        margin-top: 1px;
        width: 220px;
        border: 1px solid #dde4eb;
        background-color: #fff;
        input {
            padding: 0;
            border: 0;
            -webkit-box-shadow: border-box;
            box-shadow: border-box;
            outline: none;
            height: 32px;
            margin-top: -2px;
            margin: -3px 3px;
            margin-left: 0;
        }
        .bk-icon {
            float: right;
            margin-top: 12px;
            color: #c3cdd7;
            cursor: pointer;
        }
    }
}
.biz-table {
    font-weight: normal;
    td:first-child {
        display: flex;
        align-items: center;
    }
    .title {
        color: #7b7d8a;
        font-weight: bold;
        white-space: nowrap;
        padding: 0;
        margin: 0 0 5px 0;
        a {
            color: #333948;
            &:hover {
                color: #3c96ff;
            }
        }
    }
    .action {
        text-align: center;
        .en-underline:hover {
            border-bottom: 1px solid #3c96ff;
            padding-bottom: 3px;
        }
    }
    .time {
        color: #a3a4ac;
    }
    .disabled {
        color: #c3cdd7;
        .title,
        .time,
        .desc {
            color: #c3cdd7 !important;
        }
    }
    .avatar,
    .bg-avatar {
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
        &:hover {
            .bg-avatar {
                display: block;
            }
        }
    }
    .avatar-addr {
        width: 100%;
        height: 100%;
        border-radius: 16px;
        object-fit: cover;
    }
    .bg-avatar {
        position: absolute;
        top: 0;
        left: 0;
        background: rgba(0, 0, 0, 0.4);
        font-size: 12px;
        display: none;
    }
    .match-color-green {
        background-color: #30d878;
    }
    .match-color-yellow {
        background-color: #ffb400;
    }
    .match-color-red {
        background-color: #ff5656;
    }
    .match-color-blue {
        background-color: #3c96ff;
    }
}
.biz-pm-form {
    margin: 0 auto 15px auto;
}
.bk-form-checkbox {
    margin-right: 35px;
}
.desc {
    word-break: break-all;
}
.biz-text-bum {
    position: absolute;
    bottom: 8px;
    right: 10px;
    font-size: 12px;
}

.create-project-dialog {
    button.disabled {
        background-color: #fafafa;
        border-color: #e6e6e6;
        color: #cccccc;
        cursor: not-allowed;
        &:hover {
            background-color: #fafafa;
            border-color: #e6e6e6;
        }
    }
}

.bk-table > tbody > tr > td,
.bk-table > tbody > tr > th,
.bk-table > thead > tr > td,
.bk-table > thead > tr > th {
    height: 60px;
    vertical-align: middle;
    border-color: #e9edee;
    color: #7b7d8a;
    font-size: 14px;
    padding: 7px 10px;
    line-height: 20px;
}
.bk-table > thead > tr > th {
    background: none;
    height: 50px;
}
.biz-pm-table > tbody > tr:hover {
    background-color: #fff;
    box-shadow: 0 1px 10px 0 rgba(0, 0, 0, 0.1);
}
.biz-guide-box {
    background-color: #fff;
    padding: 75px 30px;
    border-radius: 4px;
    box-shadow: 0 0 3px rgba(0, 0, 0, 0.1);
    text-align: center;
    margin-top: 30px;
    .title {
        font-size: 22px;
        color: #333;
    }
}
</style>

<style lang="scss">
@import '../assets/scss/conf.scss';
@import '../assets/scss/mixins/scroller.scss';

@media screen and (max-width: $mediaWidth) {
    .biz-create-pm .bk-dialog-body {
        max-height: 440px;
        overflow: auto;
        @include scroller(#9e9e9e);
    }
}
</style>
