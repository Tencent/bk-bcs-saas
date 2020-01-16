<template>
    <component v-bind:is="currentView" v-if="curProject.project_id" ref="ingress"></component>
</template>

<script>
    import k8sIngress from './ingress/k8s/index'
    import mesosIngress from './ingress/mesos/index'
    import globalMixin from '@open/mixins/global'

    export default {
        components: {
            k8sIngress,
            mesosIngress
        },
        mixins: [globalMixin],
        data () {
            return {
                curProject: {},
                currentView: k8sIngress
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
        // beforeDestroy () {
        //     this.$refs.ingress.leaveCallback()
        // },
        // beforeRouteLeave (to, from, next) {
        //     this.$refs.ingress.leaveCallback()
        //     next(true)
        // },
        methods: {
            setComponent () {
                this.$store.commit('network/updateIngressList', [])
                // mesos
                if (this.curProject.kind === PROJECT_MESOS) {
                    this.currentView = 'mesosIngress'
                } else if (this.curProject.kind === PROJECT_K8S) {
                    this.currentView = 'k8sIngress'
                }
            }
        }
    }
</script>
