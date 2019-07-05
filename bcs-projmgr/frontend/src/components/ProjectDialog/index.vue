<template>
    <bk-dialog class='devops-project-dialog' :is-show.sync='showDialog' :width='width' :quick-close='false' :close-icon='false'>
        <h3 slot="header" class="project-dialog-header">{{title}}</h3>
        <main slot='content' class='bk-form biz-pm-form'>

            <div class='bk-form-item is-required'>
                <label class='bk-label'>项目名称：</label>
                <div class='bk-form-content'>
                    <!-- projectNameUnique: [ newProject.project_id ] -->
                    <input type='text' maxlength='12' class='bk-form-input' :class="{'is-danger': errors.has('project_name')}" :value='newProject.project_name' name='project_name' data-vv-validate-on='blur' v-validate='{required: true, min: 4, max: 12}' @input='handleProjectChange' placeholder="请输入4-12字符的项目名称" />
                    <div class='error-tips' v-if='errors.has("project_name")'>
                        {{ errors.first("project_name") }}
                        <span v-if='errors.first("project_name") === "项目名称已存在"'>如有疑问请联系<a class="text-link" href="wxwork://message/?username=DevOps">蓝盾助手</a></span>
                    </div>
                </div>
            </div>
            <div class='bk-form-item is-required'>
                <label class='bk-label'>英文缩写：</label>
                <div class='bk-form-content'>
                    <input type='text' maxlength='32' class='bk-form-input' :class="{'is-danger': errors.has('english_name')}" :disabled="!isNew" :value='newProject.english_name' name='english_name' data-vv-validate-on='blur' v-validate='{required: true, min: 2, max: 32, projectEnglishNameReg: true, projectEnglishNameUnique: true}' @input='handleProjectChange' placeholder='请输入2-32字符的小写字母+数字，以小写字母开头' />
                    <div class='error-tips' v-if='errors.has("english_name")'>
                        {{ errors.first("english_name") }}
                    </div>
                </div>
            </div>
            <div class='bk-form-item is-required'>
                <label class='bk-label'>项目描述：</label>
                <div class='bk-form-content'>
                    <span class='biz-text-bum'>还可以输入<strong>{{ descriptionLength - newProject.description.length }}</strong>个字符</span>
                    <textarea maxlength='100' :class="{'bk-form-textarea': true, 'is-danger': errors.has('description')}" placeholder='请输入项目描述' v-validate='"required"' :value='newProject.description' name='description' @input='handleProjectChange'></textarea>
                </div>
            </div>
            <!-- <div class="bk-form-item is-required">
                <label class="bk-label">所属中心：</label>
                <div class="bk-form-content">
                    <div class="bk-dropdown-box">
                        <bk-dropdown
                            :list="curDepartmentInfo.bg"
                            :setting-key="'id'"
                            :display-key="'name'"
                            :searchKey="'name'"
                            :placeholder="'BG'"
                            :is-loading='deptLoading.bg'
                            :searchable="true"
                            :selected.sync="newProject.bg_id"
                            name='bg'
                            data-vv-value-path='selected'
                            v-validate='"required"'
                            @item-selected="setBgName">
                        </bk-dropdown>
                    </div>
                    <div class="bk-dropdown-box">
                        <bk-dropdown
                            :list="curDepartmentInfo.dept"
                            :setting-key="'id'"
                            :display-key="'name'"
                            :searchKey="'name'"
                            :placeholder="'部门'"
                            :is-loading='deptLoading.dept'
                            :searchable="true"
                            v-validate='"required"'
                            name='dept'
                            data-vv-value-path='selected'
                            :selected.sync="newProject.dept_id"
                            @item-selected="setDeptName">
                        </bk-dropdown>
                    </div>
                    <div class="bk-dropdown-box">
                        <bk-dropdown
                            :list="curDepartmentInfo.center"
                            :setting-key="'id'"
                            :display-key="'name'"
                            :searchKey="'name'"
                            :placeholder="'中心'"
                            :is-loading='deptLoading.center'
                            :searchable="true"
                            v-validate='"required"'
                            name='center'
                            data-vv-value-path='selected'
                            :selected.sync="newProject.center_id"
                            @item-selected="setCenterName">
                        </bk-dropdown>
                    </div>
                </div>
            </div>
            <div class="bk-form-item is-required">
                <label class="bk-label">项目类型：</label>
                <div class="bk-form-content">
                    <bk-dropdown
                        :list="projectTypeList"
                        :setting-key="'id'"
                        :display-key="'name'"
                        :placeholder="'选择项目类型'"
                        v-validate='"required"'
                        name='project_type'
                        data-vv-value-path='selected'
                        :selected.sync="newProject.project_type">
                    </bk-dropdown>
                </div>
            </div> -->
        </main>
        <template slot="footer">
            <div class="bk-dialog-outer">
                <template v-if="isCreating">
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                        {{isNew ? '新建中...' : '修改中...'}}
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                        取消
                    </button>
                </template>
                <template v-else>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="saveProject">
                        确定
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="cancelProject">
                        取消
                    </button>
                </template>
            </div>
        </template>
    </bk-dialog>
</template>

<script lang='ts'>
import Vue from 'vue'
import { Component, Prop, Watch } from 'vue-property-decorator'
import { State, Action, Getter } from 'vuex-class'
import eventBus from '../../utils/eventBus'

@Component
export default class ProjectDialog extends Vue {
    @Prop({ default: false })
    initShowDialog: boolean

    @Prop({ default: 860 })
    width: number | string

    descriptionLength: number = 100
    validate: object = {}
    title: string = '新建项目'
    curDepartmentInfo: any = {
        bg: [],
        dept: [],
        center: []
    }
    isNew: boolean = true
    isCreating: boolean = false
    deptLoading: any = {
        bg: false,
        dept: false,
        center: false
    }
    projectTypeList: object = [
        {
            id: 1,
            name: '手游'
        },
        {
            id: 2,
            name: '端游'
        },
        {
            id: 3,
            name: '页游'
        },
        {
            id: 4,
            name: '平台产品'
        },
        {
            id: 5,
            name: '支撑产品'
        }
    ]

    @State newProject
    @State showProjectDialog
    @Getter isEmptyProject
    @Action updateNewProject
    @Action checkProjectField
    @Action toggleProjectDialog
    @Action getDepartmentInfo
    @Action ajaxUpdatePM
    @Action ajaxAddPM
    @Action getProjects
    @Action getMyDepartmentInfo

    handleProjectChange(e): void {
        const { name, value, type, checked } = e.target
        const isCheckbox = type === 'checkbox'

        this.updateNewProject({
            [name]: isCheckbox ? checked : value
        })
    }

    get showDialog(): boolean {
        return this.showProjectDialog
    }

    set showDialog(showProjectDialog: boolean) {
        this.toggleProjectDialog({
            showProjectDialog
        })
    }

    @Watch('showDialog')
    async watchDialog(show: boolean) {
        if (show) {
            this.$validator.reset()
            if (this.newProject.project_name) {
                this.isNew = false
            } else {
                this.isNew = true
            }
            // this.getDepartment('bg', 0)
            this.title = this.isEmptyProject(this.newProject) ? '新建项目' : '编辑项目'
            if (this.isEmptyProject(this.newProject)) {
                this.deptLoading['bg'] = true
                this.deptLoading['dept'] = true
                this.deptLoading['center'] = true
                let res = await this.getMyDepartmentInfo()
                console.log('res', res)
                if (res) {
                    this.newProject.bg_id = res.bg_id
                    this.newProject.bg_name = res.bg_name
                    this.newProject.dept_id = res.dept_id
                    this.newProject.dept_name = res.dept_name
                    this.newProject.center_id = res.center_id
                    this.newProject.center_name = res.center_name
                }
            }
        }
    }

    @Watch('newProject.bg_id')
    watchBg(bgId: number): void {
        this.curDepartmentInfo['dept'] = []
        this.curDepartmentInfo['center'] = []
        bgId && this.getDepartment('dept', this.newProject.bg_id)
    }

    @Watch('newProject.dept_id')
    watchDept(deptId: number): void {
        this.curDepartmentInfo['center'] = []
        deptId && this.getDepartment('center', this.newProject.dept_id)
    }

    async getDepartment(type: string, id: number) {
        this.deptLoading[type] = true
        try {
            const res = await this.getDepartmentInfo({
                type,
                id
            })
            this.curDepartmentInfo[type] = res
            this.curDepartmentInfo[type].splice(0, this.curDepartmentInfo[type].length, ...res)
        } catch (e) {
            this.curDepartmentInfo[type] = []
        }
        this.deptLoading[type] = false
    }

    setBgName(index, data) {
        this.newProject.bg_name = data.name
    }

    setDeptName(index, data) {
        this.newProject.dept_name = data.name
    }

    setCenterName(index, data) {
        this.newProject.center_name = data.name
    }

    closeDialog() {
        this.showDialog = false
    }

    async addProject(data) {
        // let data = this.newProject
        try {
            let res = await this.ajaxAddPM(data)

            if (typeof res === 'boolean' && res) {
                this.$bkMessage({
                    theme: 'success',
                    message: '项目创建成功！'
                })
                this.closeDialog()
                await this.getProjects()
                eventBus.$emit('addNewProject', data)
            } else {
                this.$bkMessage({
                    theme: 'error',
                    message: '接口报错！'
                })
            }
            setTimeout(() => {
                this.isCreating = false
            }, 100)
        } catch (err) {
            this.$bkMessage({
                theme: 'error',
                message: err.message || '接口异常！'
            })
            setTimeout(() => {
                this.isCreating = false
            }, 100)
        }
    }

    async updateProject(data) {
        try {
            let res = await this.ajaxUpdatePM(data)
            if (res) {
                this.closeDialog()
                this.$bkMessage({
                    theme: 'success',
                    message: '项目修改成功！'
                })
                await this.getProjects()
            } else {
                this.$bkMessage({
                    theme: 'error',
                    message: '接口报错！'
                })
            }
            setTimeout(() => {
                this.isCreating = false
            }, 100)
        } catch (err) {
            let message = err.message || '接口异常！'
            this.$bkMessage({
                theme: 'error',
                message
            })
            setTimeout(() => {
                this.isCreating = false
            }, 100)
        }
    }

    async saveProject() {
        let data = this.newProject
        let engReg = /^[a-z][a-z0-9]{1,32}$/
        data.project_name = data.project_name.split(' ').join('')
        if (data.project_name === '') {
            this.$bkMessage({
                theme: 'error',
                message: '项目名称不能为空！'
            })
            return false
        } else if (data.project_name.length <= 3 || data.project_name.length > 20) {
            this.$bkMessage({
                theme: 'error',
                message: '项目名称长度必须大于3字符小于21字符！'
            })
            return false
        }

        if (!engReg.test(data.english_name)) {
            this.$bkMessage({
                theme: 'error',
                message: '英文缩写必须由小写字母+数字组成，以小写字母开头，长度限制32字符！'
            })
            return false
        }
        if (data.description === '') {
            this.$bkMessage({
                theme: 'error',
                message: '请输入项目描述！'
            })
            return false
        }
        // if (data.bg_id === '') {
        //     this.$bkMessage({
        //         theme: 'error',
        //         message: '请选择BG！'
        //     })
        //     return false
        // }
        // if (data.dept_id === '') {
        //     this.$bkMessage({
        //         theme: 'error',
        //         message: '请选择部门！'
        //     })
        //     return false
        // }
        // if (data.center_id === '') {
        //     this.$bkMessage({
        //         theme: 'error',
        //         message: '请选择中心！'
        //     })
        //     return false
        // }
        // if (data.project_type === '') {
        //     this.$bkMessage({
        //         theme: 'error',
        //         message: '请选择项目类型！'
        //     })
        //     return false
        // }
        this.isCreating = true
        if (this.isNew) {
            this.addProject(data)
        } else {
            let id = this.newProject.project_id
            let params = {
                id: id,
                data: data
            }
            this.updateProject(params)
        }
        return true
    }

    cancelProject() {
        this.isCreating = false
        this.showDialog = false
    }

    async created() {
        this.title = this.isEmptyProject(this.newProject) ? '新建项目' : '编辑项目'
    }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/conf';
.project-dialog-header {
    text-align: center;
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
}
.biz-table {
    font-weight: normal;
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
}
.biz-pm-form {
    margin: 0 50px 15px auto;
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

.devops-project-dialog {
    overflow: auto;
    button.disabled {
        background-color: #fafafa;
        border-color: #e6e6e6;
        color: #ccc;
        cursor: not-allowed;
        &:hover {
            background-color: #fafafa;
            border-color: #e6e6e6;
        }
    }
    .bk-form .bk-label {
        font-weight: 700;
        color: #737987;
        padding-right: 20px;
    }
    .error-tips {
        .text-link {
            color: $primaryColor;
            padding: 0 5px;
        }
        &:before {
            display: none;
        }
    }
    .bk-dropdown-box {
        width: 203px;
        display: inline-block;
        vertical-align: middle;
    }
    .bk-form-input[disabled],
    .bk-form-select[disabled] {
        color: inherit;
    }
}
</style>
