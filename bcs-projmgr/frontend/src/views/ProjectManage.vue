<template>
    <div v-bkloading="{isLoading: isDataLoading}" class="pm-box">
        <div class="biz-pm biz-pm-index biz-create-pm">
            <template v-if="projectList.length || isDataLoading">
                <div class="biz-pm-header">
                    <div class="title">项目管理</div>
                    <div class="action">
                        <!-- <label class="bk-form-checkbox bk-checkbox-small">
                            <input type="checkbox" value="1" name="isFilterByOffline" v-model="isFilterByOffline">
                            <i class="bk-checkbox-text">显示已停用项目</i>
                        </label> -->
                        <button class="bk-button bk-primary" @click="togglePMDialog(true)">
                            <i class="bk-icon icon-plus"></i>
                            <span style="margin-left: 0;">新建项目</span>
                        </button>
                        <div class="search-input-row">
                            <input type="text" name="searchInput" placeholder="输入关键字按Enter搜索" v-model="inputValue" @keyup.enter="filterProjectList(isFilterByOffline)">
                            <!-- <i v-if="inputValue" class="bk-icon icon-close-circle-shape"></i>
                            <i v-else class="bk-icon icon-search" @click="filterProjectList(isFilterByOffline)"></i> -->
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
                                <th style="width: 300px;border-bottom:none">项目名称</th>
                                <th style="width: 300px;border-bottom:none">项目英文名</th>
                                <th>项目说明</th>
                                <th style="width: 170px;">创建者</th>
                                <th style="width: 200px; text-align: center;">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="project in curPageData" :key="project.project_code">
                                <td>
                                    <!-- @click="modifyLogo(project)" -->
                                    <span class="avatar" v-if="project.logo_addr">
                                        <img class="avatar-addr" :src="project.logo_addr">
                                        <!-- <span class="bg-avatar">编辑</span> -->
                                    </span>
                                    <!-- @click="modifyLogo(project)" -->
                                    <span class="avatar" v-else :class="['project-avatar', 'match-color-blue']">
                                        {{ project.project_name.substr(0, 1) }}
                                        <!-- <span class="bg-avatar">编辑</span> -->
                                    </span>
                                    <div class="info">
                                        <p class="title">
                                            <template v-if="project.approval_status !== 2">
                                                <bk-tooltip :content="'没有操作权限'" placement="top">
                                                    <a href="javascript:void(0)" class="bk-text-button is-disabled" title="没有操作权限">{{project.project_name}}</a>
                                                </bk-tooltip>
                                            </template>
                                            <!-- <template v-else-if="project.permissions['modify:project:btn'] === 2">
                                                <bk-tooltip :content="'没有操作权限'" placement="top">
                                                    <a href="javascript:void(0)" class="bk-text-button is-disabled" title="没有操作权限">{{project.project_name}}</a>
                                                </bk-tooltip>
                                            </template> -->
                                            <template v-else>
                                                <a href="javascript:void(0)" @click.stop.prevent="goProject(project.project_code)" :class="['bk-text-button', {'is-disabled': project.is_offlined}]" v-if="!project.is_offlined">{{project.project_name}}</a>
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
                                    <!-- 状态为待审批 -->
                                    <template v-if="project.approval_status === 1">
                                        <bk-tooltip :content="'待审批，没有操作权限'" placement="top">
                                            <a href="javascript:void(0)" class="bk-text-button is-disabled" title="没有操作权限">编辑</a>
                                        </bk-tooltip>
                                        <!-- <bk-tooltip :content="'待审批，没有操作权限'" placement="top" style="margin: 0 15px;">
                                            <a href="javascript:void(0)" class="bk-text-button is-disabled" title="没有操作权限">启用</a>
                                        </bk-tooltip> -->
                                        <bk-tooltip :content="'待审批，没有操作权限'" placement="top">
                                            <a href="javascript:void(0)" class="bk-text-button is-disabled" title="没有操作权限">权限管理</a>
                                        </bk-tooltip>
                                    </template>
                                    <!-- 状态为已驳回 -->
                                    <template v-else-if="project.approval_status === 3">
                                        <a href="javascript:void(0)" :class="['bk-text-button']" @click.stop.prevent="togglePMDialog(true, project)">编辑</a>
                                        <!-- <bk-tooltip :content="'已驳回，没有操作权限'" placement="top" style="margin: 0 15px;">
                                            <a href="javascript:void(0)" class="bk-text-button is-disabled" title="没有操作权限">启用</a>
                                        </bk-tooltip> -->
                                        <bk-tooltip :content="'已驳回，没有操作权限'" placement="top">
                                            <a href="javascript:void(0)" class="bk-text-button is-disabled" title="没有操作权限">权限管理</a>
                                        </bk-tooltip>
                                    </template>
                                    <!-- 没操作权限 置灰 -->
                                    <!-- <template v-else-if="project.permissions['modify:project:btn'] === 2">
                                        <bk-tooltip :content="'没有操作权限'" placement="top">
                                            <a href="javascript:void(0)" class="bk-text-button is-disabled" title="没有操作权限">编辑</a>
                                        </bk-tooltip>
                                        <bk-tooltip :content="project.is_offlined?'没有操作权限':'此功能暂未开放'" placement="top">
                                            <a href="javascript:void(0)" style="margin-left: 15px;" class="bk-text-button is-disabled">{{project.is_offlined? '启用' : '停用'}}</a>
                                        </bk-tooltip>
                                        <bk-tooltip :content="'没有操作权限'" placement="top">
                                            <a href="javascript:void(0)" style="margin-left: 15px;" class="bk-text-button is-disabled" title="没有操作权限">权限管理</a>
                                        </bk-tooltip>
                                    </template> -->
                                    <!-- 否则正常显示 -->
                                    <template v-else>
                                        <a href="javascript:void(0)" :class="['bk-text-button', {'is-disabled': project.is_offlined}]" @click.stop.prevent="togglePMDialog(true, project)">编辑</a>
                                        <!-- <template v-if="project.is_offlined">
                                            <a href="javascript:void(0)" class="bk-text-button" @click.stop.prevent="offlineProject(project)">启用</a>
                                        </template>
                                        <template v-else>
                                            <bk-tooltip :content="'此功能暂未开放'" placement="top">
                                                <a href="javascript:void(0)" style="margin: 0 15px;" class="bk-text-button is-disabled">停用</a>
                                            </bk-tooltip>
                                        </template> -->
                                        <a href="javascript:void(0)" @click="goUserManager(project.project_code)" class="bk-text-button" v-if="!project.is_offlined">权限管理</a>
                                        <a href="javascript:void(0)" :class="['bk-text-button', {'is-disabled': project.is_offlined}]" v-else>权限管理</a>
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
                        <p class="title" v-if="!isFilterByOffline && offlineProjectNum">您有{{offlineProjectNum}}个项目已经停用，请点击右上角“显示已停用项目”或新建项目</p>
                        <p class="title" v-else>暂时没有数据！</p>
                    </div>
                </template>
            </template>
            <empty-tips v-else title='未找到您参与的项目' desc='您可以创建自己的项目，然后针对自己的项目进行相应用户和权限管理，也可以申请加入已有的项目'>
                <button class="bk-button bk-primary" @click="togglePMDialog(true)">
                    <i class="bk-icon icon-plus"></i>
                    <span style="margin-left: 0;">新建项目</span>
                </button>
                <a class="bk-button bk-success" :href="applyProjectUrl">
                    <span style="margin-left: 0;">申请加入项目</span>
                </a>
            </empty-tips>
        </div>
        <logo-dialog :showDialog='showlogoDialog' :toConfirmLogo="toConfirmLogo" :toCloseDialog="toCloseDialog" :fileChange="fileChange" :selectedUrl="selectedUrl" :isUploading="isUploading">
        </logo-dialog>
        <!-- <footer class="footer">
            <p class="logo-qt">
                <img class="img-logo" src="/static/home/images/qtlogo.png"><span>青藤云安全提供安全检测</span>
            </p>
            <p>
                <a id="contact_us" class="link">QQ咨询(800802001)</a>
                | <a href="http://bbs.bk.tencent.com/forum.php" target="_blank" hotrep="hp.footer.feedback" class="link">蓝鲸论坛</a>
                | <a href="http://bk.tencent.com/" target="_blank" hotrep="hp.footer.feedback" class="link">蓝鲸官网</a>
                | <a href="/" target="_blank" hotrep="hp.footer.feedback" class="link">蓝鲸智云工作台</a>
                |<a class="follow-us" href="###">关注我们<span class="qr-box"><span class="qr"><img src="/static/home/images/qr.png"></span><span class="qr-caret"></span></span></a>
            </p>
            <p>Copyright © 2012-2019 Tencent BlueKing. All Rights Reserved.</p>
            <p>蓝鲸智云 版权所有</p>
        </footer> -->
    </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Watch } from 'vue-property-decorator'
import { State, Action } from 'vuex-class'
import logoDialog from '../components/logoDialog/index.vue'

@Component({
    components: {
        logoDialog
    }
})
export default class ProjectManage extends Vue {
    @State projectList
    @State newProject
    @Action toggleProjectDialog
    @Action ajaxUpdatePM
    @Action getProjects
    @Action changeProjectLogo

    applyProjectUrl: string = `${APPLY_PROJECT_URL}`
    isFilterByOffline: boolean = false
    showlogoDialog: boolean = false
    isUploading: boolean = false
    curProjectData: object
    selectedFile: object
    isDataLoading: boolean = false
    selectedUrl: string = ''
    curSelectProject: string = ''
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
                    project.is_offlined === false &&
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

    togglePMDialog(show: boolean, project = null): void {
        this.toggleProjectDialog({
            showProjectDialog: show,
            project
        })
    }

    goProject(project_code: string): void {
        // window.open(`/console/perm/my-project?project_code=${project_code}`, '_blank')
        window.open(`/console/bcs/${project_code}/cluster?v`, '_blank')
    }

    goUserManager() {
        window.open(USER_MANAGER_URL)
    }

    formatDate(dateStr: string): string {
        try {
            const date = new Date(dateStr)
            if (date.toString() === 'Invalid Date') throw new Error(`error date format： ${dateStr}`)
            const month = date.getMonth() + 1
            const day = date.getDate()
            return `${date.getFullYear()}-${month > 9 ? month : `0${month}`}-${day > 9 ? day : `0${day}`}`
        } catch (e) {
            console.error(e)
            return '--'
        }
    }

    offlineProject(project: any): void {
        let _this = this
        const { is_offlined, project_id } = project
        this.curProjectData = JSON.parse(JSON.stringify(project))

        const message = is_offlined ? '确定要启用？' : '确定要停用？'

        this.$bkInfo({
            title: message,
            confirmFn() {
                const params = {
                    id: project_id,
                    data: {
                        is_offlined: !is_offlined
                    }
                }
                _this.updateProject(params)
                return true
            }
        })
    }

    matchForCode(project_code) {
        let event = project_code.substr(0, 1)
        let key = event.charCodeAt() % 4
        return this.matchColorList[key]
    }

    modifyLogo(project) {
        if (project.logo_addr) {
            this.selectedUrl = project.logo_addr
        } else {
            this.selectedUrl = ''
        }
        this.showlogoDialog = true
        this.isUploading = false
        this.curSelectProject = project.project_id
    }

    async toConfirmLogo() {
        if (this.selectedUrl && this.selectedFile) {
            this.isUploading = true

            let formData = new FormData()
            formData.append('logo', this.selectedFile[0])

            try {
                const res = await this.changeProjectLogo({
                    projectId: this.curSelectProject,
                    formData
                })

                if (res) {
                    this.$bkMessage({
                        theme: 'success',
                        message: 'LOGO修改成功！'
                    })

                    this.showlogoDialog = false
                    this.projectList.forEach(item => {
                        if (item.project_id === this.curSelectProject) {
                            item.logo_addr = res.logo_addr
                        }
                    })
                }
            } catch (e) {
                this.$bkMessage({
                    message: e.message,
                    theme: 'error'
                })

                this.isUploading = false
            } finally {
                this.selectedFile = undefined
            }
        } else if (!this.selectedUrl) {
            this.$bkMessage({
                message: '请选择要上传的图片',
                theme: 'error'
            })
        } else {
            this.showlogoDialog = false
        }
        this.resetUploadInput()
    }

    toCloseDialog() {
        this.showlogoDialog = false
        this.selectedFile = undefined
        this.resetUploadInput()
    }

    fileChange(e): void {
        let file = e.target.files[0]
        if (file) {
            if (!(file.type === 'image/jpeg' || file.type === 'image/png')) {
                this.$bkMessage({
                    theme: 'error',
                    message: '请上传png、jpg格式的图片'
                })
            } else if (file.size > 2 * 1024 * 1024) {
                this.$bkMessage({
                    theme: 'error',
                    message: '请上传大小不超过2M的图片'
                })
            } else {
                let reader = new FileReader()
                reader.readAsDataURL(file)
                reader.onload = evts => {
                    this.selectedUrl = evts.target.result
                }
                this.selectedFile = e.target.files
            }
        }
    }

    /**
     * 清空input file的值
     */
    resetUploadInput() {
        this.$nextTick(() => {
            let inputElement = <HTMLInputElement>document.getElementById('inputfile')
            inputElement.value = ''
        })
    }

    async updateProject(project: any) {
        try {
            const res = await this.ajaxUpdatePM(project)

            this.$bkMessage({
                theme: 'success',
                message: '项目修改成功！'
            })
            this.togglePMDialog(false)
            this.getProjects()
        } catch (e) {
            this.$bkMessage({
                message: e.message,
                theme: 'error'
            })
        }
    }

    created() {
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
        cursor: pointer;
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
