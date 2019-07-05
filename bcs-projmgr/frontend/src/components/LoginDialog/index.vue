<template>
    <bk-dialog 
        class='devops-login-dialog'
        :is-show.sync='showLoginDialog'
        :width='width'
        :has-footer='false'
        :has-header='false'
        :padding='0'
        @confirm='toApplyPermission'>
        <main class='devops-login-iframe-container' slot='content'>
            <iframe :src="iframeSrc" scrolling="no" border="0" width="500" height="500"></iframe>
        </main>
    </bk-dialog>
</template>

<script lang='ts'>
    import Vue from 'vue'
    import auth from '../../utils/auth'
    import { Component, Prop } from 'vue-property-decorator'
    import { Action } from 'vuex-class'

    @Component
    export default class LoginDialog extends Vue {
        @Action setUserInfo
        iframeSrc: string = `${LOGIN_SERVICE_URL}/plain?app_code=1&c_url=${location.origin}/console/static/login_success.html?is_ajax=1`
        showLoginDialog: boolean = true
        width: number = 500
        async beforeDestroy () {
            const user = await auth.requestCurrentUser(true)
            this.setUserInfo({
                user
            })
        }
    }
</script>

<style lang="scss">
    @import '../../assets/scss/conf';

    .devops-login-dialog {
        .devops-login-iframe-container {
            height: 500px;
        }
    }
</style>
