<template src="./cloudloadbalance-detail.html"></template>

<script>
    import mixinBaseInstance from '@open/views/app/mixins/mixin-base-instance'

    export default {
        mixins: [mixinBaseInstance],
        data () {
            return {
                editorConfig: {
                    width: '100%',
                    height: '100%',
                    lang: 'json',
                    readOnly: true,
                    fullScreen: false,
                    value: '',
                    editor: null,
                    listenerStatus: ''
                },
                killData: {},
                listenerLoading: true,
                cloudLoadBalanceListener: []
            }
        },
        computed: {
            curProject () {
                return this.$store.state.curProject
            },
            isDev () {
                return window.location.host.indexOf('dev.bcs.devops') > -1
            }
        },
        watch: {
            tabActiveName: {
                immediate: true,
                handler (value) {
                    if (value === 'status') {
                        this.listenerStatus = ''
                        this.getCloudLoadBalanceListener()
                    }
                }
            }
        },
        created () {
            // 如果不是mesos类型的项目，无法访问页面，重定向回集群首页
            if (this.curProject && this.curProject.kind !== PROJECT_MESOS) {
                this.$router.push({
                    name: 'clusterMain',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
                return false
            }

            this.getCloudLoadBalanceListener()
        },
        methods: {
            goCloudLoadBalances () {
                this.$router.push({
                    name: 'cloudLoadBalance',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })
            },

            async getCloudLoadBalanceListener () {
                try {
                    this.listenerLoading = true
                    const res = await this.$store.dispatch('network/getCloudLoadBalanceListener', {
                        projectId: this.projectId,
                        loadBalanceId: this.$route.query.clb_id
                    })
                    this.cloudLoadBalanceListener = res.data
                } catch (err) {
                    this.listenerStatus = err.message
                } finally {
                    this.listenerLoading = false
                }
            }
        }
    }
</script>

<style scoped>
    @import './cloudloadbalance-detail.css';
</style>
