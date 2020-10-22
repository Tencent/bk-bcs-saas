<template>
    <bk-dialog class='devops-project-dialog' :is-show.sync='showDialog' :width='width' :quick-close='false' :close-icon='false'>
        <h3 slot="header" class="project-dialog-header">{{title}}</h3>
        <main slot='content' class='bk-form biz-pm-form'>

            <div class='bk-form-item is-required'>
                <label class='bk-label'>{{ $t('projectTable.name') }}：</label>
                <div class='bk-form-content'>
                    <input type='text' maxlength='12' class='bk-form-input' :class="{'is-danger': errors.has('project_name')}" :value='newProject.project_name' name='project_name' v-validate='{required: true, min: 4, max: 12}' @input='handleProjectChange' :placeholder="$t('projectDialog.namePlaceholder')" />
                    <div class='error-tips' v-if='errors.has("project_name")'>
                        {{ errors.first("project_name") }}
                    </div>
                </div>
            </div>
            <div class='bk-form-item is-required'>
                <label class='bk-label'>{{ $t('projectTable.englishName') }}：</label>
                <div class='bk-form-content'>
                    <input type='text' maxlength='32' class='bk-form-input' :class="{'is-danger': errors.has('english_name')}" :disabled="!isNew" :value='newProject.english_name' name='english_name' v-validate='{required: true, min: 2, max: 32, projectEnglishNameReg: true, projectEnglishNameUnique: true}' @input='handleProjectChange' :placeholder="$t('projectDialog.englishNamePlaceholder')" />
                    <div class='error-tips' v-if='errors.has("english_name")'>
                        {{ errors.first("english_name") }}
                    </div>
                </div>
            </div>
            <div class='bk-form-item is-required'>
                <label class='bk-label'>{{ $t('projectTable.desc') }}：</label>
                <div class='bk-form-content'>
                    <span class='biz-text-bum'>{{ $t('projectDialog.descTipsPrefix') }}<strong>{{ descriptionLength - newProject.description.length }}</strong>{{ $t('projectDialog.descTipsSuffix') }}</span>
                    <textarea maxlength='100' :class="{'bk-form-textarea': true, 'is-danger': errors.has('description')}" :placeholder="$t('projectDialog.descPlaceholder')" v-validate='{ required: true }' :value='newProject.description' name='description' @input='handleProjectChange'></textarea>
                </div>
            </div>
        </main>
        <template slot="footer">
            <div class="bk-dialog-outer">
                <template v-if="isCreating">
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                        {{ isNew ? $t('projectDialog.creatingBtn') : $t('projectDialog.updatingBtn') }}
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                       {{ $t('projectDialog.cancelBtn') }}
                    </button>
                </template>
                <template v-else>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="saveProject">
                        {{ $t('projectDialog.confirmBtn') }}
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="cancelProject">
                        {{ $t('projectDialog.cancelBtn') }}
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
    title: any = '新增项目'
    isNew: boolean = true
    isCreating: boolean = false
    
    @State newProject
    @State showProjectDialog
    @Getter isEmptyProject
    @Action updateNewProject
    @Action toggleProjectDialog
    @Action ajaxUpdatePM
    @Action ajaxAddPM
    @Action getProjects

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
            this.title = this.isEmptyProject(this.newProject) ? this.$t('addProject') : this.$t('editProject')
        }
    }

    closeDialog() {
        this.showDialog = false
    }

    async addProject(data) {
        try {
            let res = await this.ajaxAddPM(data)

            if (res) {
                this.$bkMessage({
                    theme: 'success',
                    message: this.$t('projectDialog.addSuccessTips')
                })
                this.closeDialog()
                await this.getProjects()
                eventBus.$emit('addNewProject', data)
            } else {
                this.$bkMessage({
                    theme: 'error',
                    message: this.$t('projectDialog.apiErrorTips')
                })
            }
            setTimeout(() => {
                this.isCreating = false
            }, 100)
        } catch (err) {
            if (err.code === 4003) {
                // 弹窗显示无权限
                this.closeDialog()
                this.$showAskPermissionDialog({
                    noPermissionList: [{
                        resource: this.$t('project'),
                        option: this.$t('create')
                    }],
                    applyPermissionUrl: (err.data && err.data.apply_url) || ''
                })
            } else {
                this.$bkMessage({
                    theme: 'error',
                    message: err.message || this.$t('projectDialog.apiErrorTips')
                })
            }
            
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
                    message: this.$t('projectDialog.saveSuccessTips')
                })
                await this.getProjects()
            } else {
                this.$bkMessage({
                    theme: 'error',
                    message: this.$t('projectDialog.apiErrorTips')
                })
            }
            setTimeout(() => {
                this.isCreating = false
            }, 100)
        } catch (err) {
            if (err.code === 4003) {
                // 弹窗显示无权限
                this.closeDialog()
                this.$showAskPermissionDialog({
                    noPermissionList: [{
                        resource: this.$t('project'),
                        option: this.$t('edit')
                    }],
                    applyPermissionUrl: (err.data && err.data.apply_url) || ''
                })
            } else {
                let message = err.message || this.$t('projectDialog.apiErrorTips')
                this.$bkMessage({
                    theme: 'error',
                    message
                })
            }
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
                message: this.$t('projectDialog.projectNameRequiredTips')
            })
            return false
        } else if (data.project_name.length <= 3 || data.project_name.length > 20) {
            this.$bkMessage({
                theme: 'error',
                message: this.$t('projectDialog.projectNameLengthTips')
            })
            return false
        }

        if (!engReg.test(data.english_name)) {
            this.$bkMessage({
                theme: 'error',
                message: this.$t('projectDialog.englishNameRegTips')
            })
            return false
        }
        if (data.description === '') {
            this.$bkMessage({
                theme: 'error',
                message: this.$t('projectDialog.descRequiredTips')
            })
            return false
        }
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
        this.title = this.isEmptyProject(this.newProject) ? this.$t('addProject') : this.$t('editProject')
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
