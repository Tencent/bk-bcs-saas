<template>
    <div class="bk-login-dialog" v-if="isShow">
        <div class="bk-login-wrapper">
            <iframe :src="iframeSrc" scrolling="no" border="0" width="500" height="500"></iframe>
            <!-- <a class="close-btn" @click="hideLoginModal">
                <i class="bk-icon icon-close"></i>
            </a> -->
        </div>
    </div>
</template>

<script>
    /**
     * app-auth
     * @desc 统一登录
     * @example1 <app-auth type="404"></app-auth>
     */

    export default {
        name: 'app-auth',
        data () {
            return {
                loginCallbackURL: `${DEVOPS_BCS_API_URL}/login_success.html?is_ajax=1`,
                iframeSrc: '',
                isShow: false
            }
        },
        methods: {
            hideLoginModal () {
                this.isShow = false
            },
            showLoginModal (data) {
                setTimeout(() => {
                    window.$syncUrl(this.$route.fullPath.replace(new RegExp(`^${SITE_URL}`), ''), true)
                }, 10)
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
