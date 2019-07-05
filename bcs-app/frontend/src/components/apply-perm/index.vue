<template>
    <bk-dialog
        :ext-cls="'apply-perm-dialog'"
        :is-show.sync="dialogConf.isShow"
        :width="dialogConf.width"
        :quick-close="false"
        @cancel="hide"
        :title="dialogConf.title">
        <template slot="content">
            <table class="bk-table has-table-hover biz-table biz-apply-perm-table">
                <thead>
                    <tr>
                        <th style="width: 260px; padding-left: 20px;">资源</th>
                        <th style="width: 180px;">需要的权限</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(perm, index) in permList" :key="index">
                        <td style="padding-left: 20px;">
                            <span v-if="perm.policy_code !== 'create'">{{perm.resource_type_name}}：</span>{{perm.resource_name || perm.resource_type_name}}
                        </td>
                        <td>{{perm.policy_name}}</td>
                    </tr>
                </tbody>
            </table>
        </template>
        <template slot="footer">
            <div class="bk-dialog-outer">
                <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary" @click="goApplyUrl">去申请</button>
                <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="hide">取消</button>
            </div>
        </template>
    </bk-dialog>
</template>

<script>
    export default {
        name: 'apply-perm',
        data () {
            return {
                dialogConf: {
                    isShow: false,
                    width: 640,
                    title: '无权限操作',
                    closeIcon: false
                },
                applyUrl: '',
                permList: []
            }
        },
        destroyed () {
            this.applyUrl = ''
        },
        methods: {
            hide () {
                this.dialogConf.isShow = false
            },
            show (projectCode, data) {
                this.applyUrl = `${data.apply_url}`

                this.permList.splice(0, this.permList.length, ...(data.perms || []))
                this.$nextTick(() => {
                    this.dialogConf.isShow = true
                })
            },
            goApplyUrl () {
                this.hide()
                setTimeout(() => {
                    window.open(this.applyUrl)
                }, 300)
            }
        }
    }
</script>

<style>
    @import './index.css';
</style>
