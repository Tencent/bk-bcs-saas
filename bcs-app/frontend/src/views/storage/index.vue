<template>
    <router-view :key="$route.path"></router-view>
</template>

<script>
    export default {
        data () {
            return {
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            curProject () {
                return this.$store.state.curProject
            }
        },
        watch: {
        },
        created () {
            // 如果不是mesos类型的项目，无法访问页面，重定向回集群首页
            if (this.curProject && this.curProject.kind === PROJECT_MESOS) {
                this.$router.push({
                    name: 'clusterMain',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
                return false
            }
        },
        methods: {
        }
    }
</script>
