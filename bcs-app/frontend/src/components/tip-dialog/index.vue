<template>
    <bk-dialog
        :class="'biz-warning-tip'"
        :is-show.sync="tipDialogConf.isShow"
        :has-header="false"
        :has-footer="false"
        :quick-close="false"
        :width="tipDialogConf.width"
        :title="tipDialogConf.title">
        <template slot="content">
            <div :class="`dialog-wrapper ${type}`">
                <div class="dialog-header">
                    <div class="logo">
                        <i :class="icon"></i>
                    </div>
                    <h2 class="dialog-title">{{title}}</h2>
                    <span v-if="showClose" class="close-btn" title="关闭" @click="cancel">╳</span>
                </div>
                <div class="dialog-content">
                    <strong>{{subTitle}}</strong>
                    <ul class="update-list">
                        <li v-for="(item, index) of noticeList" :key="index">
                            <label :class="['bk-form-checkbox']">
                                <input v-if="!isConfirming" type="checkbox" name="check" v-model="item.isChecked" @change="changeCheck(item)">
                                <input v-else disabled="disabled" type="checkbox" name="check" v-model="item.isChecked">
                                {{item.text}}
                            </label>
                        </li>
                    </ul>
                    <template v-if="canConfirm">
                        <div class="dialog-action" v-if="!isConfirming">
                            <a href="javascript:void(0)" class="bk-button bk-primary bk-button-large dialog-btn" @click="confirm">{{confirmBtnText}}</a>
                            <a href="javascript:void(0)" class="bk-button bk-default bk-button-large dialog-btn" @click="cancel">{{cancelBtnText}}</a>
                        </div>
                        <div class="dialog-action" v-else>
                            <a href="javascript:void(0)" class="bk-button bk-primary bk-button-large dialog-btn disabled">{{confirmingBtnText}}</a>
                            <a href="javascript:void(0)" class="bk-button bk-default bk-button-large dialog-btn disabled">{{cancelingBtnText}}</a>
                        </div>
                    </template>
                    <template v-else>
                        <div class="dialog-action">
                            <bk-tooltip content="请确认以上内容，才可操作" placement="top">
                                <a href="javascript:void(0)" class="bk-button bk-primary bk-button-large dialog-btn disabled">{{confirmBtnText}}</a>
                            </bk-tooltip>
                            <a href="javascript:void(0)" class="bk-button bk-default bk-button-large dialog-btn" @click="cancel" style="margin-left: 10px;">{{cancelBtnText}}</a>
                        </div>
                    </template>
                </div>
            </div>
        </template>
    </bk-dialog>
</template>

<script>
    export default {
        props: {
            type: {
                type: String,
                default: 'default'
            },
            icon: {
                type: String,
                default: 'bk-icon icon-bk'
            },
            title: {
                type: String,
                default: '提示'
            },
            subTitle: {
                type: String,
                default: '提示'
            },
            checkList: {
                type: Array,
                default () {
                    return []
                }
            },
            confirmBtnText: {
                type: String,
                default: '确定'
            },
            confirmingBtnText: {
                type: String,
                default: '执行中'
            },
            cancelBtnText: {
                type: String,
                default: '取消'
            },
            cancelingBtnText: {
                type: String,
                default: '取消中'
            },
            confirmCallback: {
                type: Function
            },
            cancelCallback: {
                type: Function
            },
            showClose: {
                type: Boolean,
                default: true
            },
            isConfirming: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                tipDialogConf: {
                    isShow: false,
                    width: 600
                },
                noticeList: []
            }
        },
        computed: {
            canConfirm () {
                for (const item of this.noticeList) {
                    if (!item.isChecked) {
                        return false
                    }
                }
                return true
            }
        },
        created () {
            this.checkList.forEach(item => {
                item.isNeedCheck = item.isChecked
            })
            this.noticeList = JSON.parse(JSON.stringify(this.checkList))
        },
        methods: {
            show () {
                // this.checkList.forEach(item => {
                //     item.isNeedCheck = false
                //     item.isChecked = false
                // })
                this.noticeList = JSON.parse(JSON.stringify(this.checkList))
                this.tipDialogConf.isShow = true
            },
            hide () {
                this.tipDialogConf.isShow = false
            },
            changeCheck (item) {
                item.isNeedCheck = !item.isChecked
                this.noticeList = JSON.parse(JSON.stringify(this.noticeList))
            },
            async confirm () {
                const needCheck = []
                for (const item of this.noticeList) {
                    if (!item.isChecked) {
                        needCheck.push(item)
                        item.isNeedCheck = true
                    } else {
                        item.isNeedCheck = false
                    }
                }
                if (needCheck.length) {
                    this.noticeList = JSON.parse(JSON.stringify(this.noticeList))
                    return false
                }

                if (this.confirmCallback && typeof this.confirmCallback === 'function') {
                    await this.confirmCallback()
                }
                this.hide()
            },
            cancel () {
                this.cancelCallback && this.cancelCallback()
                this.hide()
            }
        }
    }
</script>
<style scoped lang="postcss">
    @import './index.css'
</style>
