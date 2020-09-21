/**
 * @file 申请权限的 mixin
 */

export default {
    methods: {
        createApplyPermUrl ({ policy, projectCode, idx }) {
            const url = `${BK_IAM_APP_URL}/perm-apply/`
            return url
        },
        checkPermission (params) {
            this.$store.dispatch('getResourcePermissions', params)
        }
    }
}
