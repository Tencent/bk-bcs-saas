<template>
    <component v-bind:is="currentView"></component>
</template>

<script>
    import k8sLoadBalance from './loadbalance/k8s/detail'
    import mesosLoadBalance from './loadbalance/mesos/detail'
    import globalMixin from '@open/mixins/global'

    export default {
        components: {
            k8sLoadBalance,
            mesosLoadBalance
        },
        mixins: [globalMixin],
        data () {
            return {
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
        methods: {
            /**
             * 根据项目类型动态设置service组件
             */
            setComponent () {
                this.$store.commit('network/updateLoadBalanceList', [])
                // mesos
                if (this.curProject.kind === PROJECT_MESOS) {
                    this.currentView = 'mesosLoadBalance'
                } else {
                    this.currentView = 'k8sLoadBalance'
                }
            }
        }
    }
</script>
