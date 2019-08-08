<template>
    <div
        :class="['bk-dropdown-menu biz-terminal active', { 'active': isActive }]"
        v-if="curProject && curProject.kind === 1 && clusterList.length"
        @mouseover="handlerMouseover"
        @mouseout="handlerMouseout">
        <div class="bk-dropdown-trigger">
            <div class="biz-terminal-trigger">
                <img src="@open/images/terminal.svg" class="icon">
                <span class="text">WebConsole</span>
                <a :href="PROJECT_CONFIG.doc.webConsole" target="_blank" class="terminal-helper bk-text-icon">
                    <i class="bk-icon icon-helper"></i>
                </a>
            </div>
            <transition name="fade">
                <div :class="['bk-dropdown-content is-show']" style="bottom: 44px; right: 0;" v-if="isShow">
                    <ul class="bk-dropdown-list">
                        <li>
                            <a href="javascript:;" v-for="(cluster, index) in clusterList" :key="index" @click="goWebConsole(cluster)" style="padding: 0 10px;">{{cluster.name}}</a>
                        </li>
                    </ul>
                </div>
            </transition>
        </div>
    </div>
</template>

<script>
    export default {
        data () {
            return {
                terminalWins: null,
                isActive: false,
                isShow: false,
                showTimer: 0,
                activeTimer: 0
            }
        },
        computed: {
            clusterList () {
                const clusterList = []
                this.$store.state.cluster.clusterList.forEach(item => {
                    clusterList.push(item)
                })

                return clusterList
            },
            curProject () {
                return this.$store.state.curProject
            },
            projectId () {
                return this.$route.params.projectId
            },
            routeName () {
                return this.$route.name
            }
        },
        mounted () {
            if (!this.clusterList.length && this.routeName !== 'clusterMain') {
                this.getClusters()
            }
        },
        methods: {
            handlerMouseover () {
                clearTimeout(this.showTimer)
                clearTimeout(this.activeTimer)
                this.isActive = true
                this.showTimer = setTimeout(() => {
                    this.isShow = true
                }, 200)
            },
            handlerMouseout () {
                clearTimeout(this.showTimer)
                clearTimeout(this.activeTimer)
                this.showTimer = setTimeout(() => {
                    this.isShow = false
                }, 100)
                this.activeTimer = setTimeout(() => {
                    this.isActive = false
                }, 400)
            },
            async getClusters (notLoading) {
                try {
                    const res = await this.$store.dispatch('cluster/getClusterList', this.projectId)
                    this.permissions = JSON.parse(JSON.stringify(res.permissions || {}))

                    const list = res.data.results || []
                    this.$store.commit('cluster/forceUpdateClusterList', list)
                } finally {
                    this.showLoading = false
                }
            },
            async goWebConsole (cluster) {
                if (!cluster.permissions.use) {
                    const type = `cluster_${cluster.environment === 'stag' ? 'test' : 'prod'}`
                    const params = {
                        project_id: this.projectId,
                        policy_code: 'use',
                        resource_code: cluster.cluster_id,
                        resource_name: cluster.name,
                        resource_type: type
                    }
                    await this.$store.dispatch('getResourcePermissions', params)
                }
                const clusterId = cluster.cluster_id
                const url = `${DEVOPS_BCS_API_URL}/web_console/projects/${this.projectId}/mgr/#cluster=${clusterId}`
                const urlMetadata = DEVOPS_BCS_API_URL.split('/')
                let backendHost = ''
                if (urlMetadata[2]) {
                    backendHost = `${urlMetadata[0]}://${urlMetadata[2]}`
                }
                if (this.terminalWins) {
                    if (!this.terminalWins.closed) {
                        this.terminalWins.postMessage({
                            clusterId: clusterId,
                            clusterName: cluster.name
                        }, backendHost)
                        this.terminalWins.focus()
                    } else {
                        this.terminalWins = window.open(url, '')
                    }
                } else {
                    this.terminalWins = window.open(url, '')
                }
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import "../../css/mixins/ellipsis.css";

    .biz-terminal {
        position: fixed;
        right: 10px;
        bottom: 10px;
        z-index: 1100;
        &.active {
            .biz-terminal-trigger {
                width: 142px;
                border-radius: 2px;
                .text {
                    display: inline-block;
                }
                .terminal-helper {
                    display: inline-block;
                }
            }
        }
        .biz-terminal-trigger {
            width: 42px;
            height: 42px;
            text-align: center;
            line-height: 40px;
            background: #fff;
            overflow: hidden;
            border-radius: 50%;
            transition: all ease 0.3s;
            box-shadow: 0 0 12px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            z-index: 10;
            .icon {
                width: 16px;
                vertical-align: middle;
            }
            .terminal-helper {
                display: none;
            }
            .text {
                color: #333;
                font-size: 14px;
                vertical-align: middle;
                display: inline-block;
                overflow: hidden;
                display: none;

            }
        }

        .terminal-helper {
            vertical-align: middle;
            &:hover {
                color: red;
                .bk-icon {
                    color: red !important;
                }
            }
        }

        .bk-dropdown-list {
            > li {
                width: 140px;
                a {
                    display: block;
                    vertical-align: middle;
                    width: 140px;
                    @mixin ellipsis 140px;
                }
            }
        }
    }
</style>
