<template>
    <bk-dialog
        class='devops-ask-permission-dialog'
        :is-show.sync='showDialog'
        :width='width'
        :title='setting.title'
        :confirm="setting.confirmBtn"
        @confirm='toApplyPermission'
        @cancel='handleClose'
    >
        <main slot='content' class='ask-permission-table'>
            <table class='devops-table'>
                    <thead>
                        <tr>
                            <th>{{ setting.resource }}</th>
                            <th>{{ setting.toApply }}</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for='(permission, index) in noPermissionList' :key='index'>
                            <td>{{permission.resource}}</td>
                            <td>{{permission.option}}</td>
                        </tr>
                    </tbody>
            </table>
        </main>
    </bk-dialog>
</template>

<script lang='ts'>
    import Vue from 'vue'
    import { Component, Prop, Watch } from 'vue-property-decorator'
    import { State, Action, Getter } from 'vuex-class'
    import eventBus from '../../utils/eventBus'

    @Component
    export default class AskPermissionDialog extends Vue {

        @Prop({ default: 640 })
        width: number | string

        // @Prop({ default: '无权限操作' })
        // title: string

        @Prop({default: []})
        noPermissionList: Permission[]

        @Prop({default: '/console/perm/apply-perm'})
        applyPermissionUrl: string

        showDialog: boolean = false

        get setting() {
            return {
                // @ts-ignore
                title: window.devops.$i18n.t('noPermission'),
                // @ts-ignore
                confirmBtn: window.devops.$i18n.t('toApply'),
                // @ts-ignore
                resource: window.devops.$i18n.t('resource'),
                // @ts-ignore
                toApply: window.devops.$i18n.t('permissionToApply')
            }
        }

        created () {
            eventBus.$on('update-permission-props', props => {
                Object.keys(props).map(prop => {
                    this[prop] = props[prop]
                })
                this.showDialog = true
            })
        }

        handleClose (done) {
            done()
        }

        toApplyPermission (done) {
            window.open(this.applyPermissionUrl, '_blank')
            done()
            this.showDialog = false
        }

    }
</script>

<style lang="scss">
    .ask-permission-table {
        .devops-table {
            width: 100%;
        }
    }
</style>
