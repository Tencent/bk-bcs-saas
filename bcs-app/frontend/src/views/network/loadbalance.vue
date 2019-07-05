<template>
    <component v-bind:is="currentView" v-if="curProject.project_id" ref="loadbalance"></component>
</template>

<script>
    import k8sLoadBalance from './loadbalance/k8s/index'
    import mesosLoadBalance from './loadbalance/mesos/index'
    import globalMixin from '@open/mixins/global'

    export default {
        components: {
            k8sLoadBalance,
            mesosLoadBalance
        },
        mixins: [globalMixin],
        data () {
            return {
                curProject: {},
                currentView: k8sLoadBalance
            }
        },
        computed: {
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            }
        },
        mounted () {
            this.curProject = this.initCurProject()
            this.setComponent()
        },
        beforeDestroy () {
            this.$refs.loadbalance.leaveCallback()
        },
        beforeRouteLeave (to, from, next) {
            this.$refs.loadbalance.leaveCallback()
            next(true)
        },
        methods: {
            /**
             * 根据项目类型动态设置service组件
             */
            setComponent () {
                this.$store.commit('network/updateLoadBalanceList', [])
                // mesos
                if (this.curProject.kind === PROJECT_MESOS) {
                    this.currentView = 'mesosLoadBalance'
                } else if (this.curProject.kind === PROJECT_K8S) {
                    this.currentView = 'k8sLoadBalance'
                }
            }
        }
    }
</script>
