<template>
    <component v-bind:is="currentView" ref="service"></component>
</template>

<script>
    import k8sService from './service/k8s'
    import mesosService from './service/mesos'
    import globalMixin from '@open/mixins/global'

    export default {
        beforeRouteLeave (to, from, next) {
            this.$refs.service && this.$refs.service.leaveCallback()
            next(true)
        },
        components: {
            k8sService,
            mesosService
        },
        mixins: [globalMixin],
        data () {
            return {
                currentView: k8sService
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
            this.$refs.service.leaveCallback()
        },
        methods: {
            /**
             * 根据项目类型动态设置service组件
             */
            setComponent () {
                if (this.curProject.kind === PROJECT_MESOS) {
                    this.currentView = 'mesosService'
                } else if (this.curProject.kind === PROJECT_K8S) {
                    this.currentView = 'k8sService'
                }
            }
        }
    }
</script>
