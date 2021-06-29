<template>
    <div v-show="value" v-bk-clickoutside="handleHideClusterSelector" class="biz-cluster-selector">
        <div class="biz-cluster-search">
            <bk-input
                ref="searchInput"
                :placeholder="$t('请输入关键字')"
                behavior="simplicity"
                v-model="searchValue"
                :clearable="true"
                :show-word-limit="true"
                right-icon="bk-icon icon-search"
                @change="handleChangeSearchValue">
            </bk-input>
        </div>
        <div class="biz-cluster-list">
            <ul v-if="filterClusterList.length">
                <li
                    v-for="(cluster, index) in filterClusterList"
                    :key="index"
                    :class="{ 'active': activeCluster === cluster.name }"
                    @click="handleToggleCluster(cluster)">
                    {{ cluster.name }}
                    <p style="color: #979ba5;">{{ cluster.cluster_id }}</p>
                </li>
            </ul>
            <div v-else class="cluster-nodata">{{ $t('暂无数据') }}</div>
        </div>
        <div class="biz-cluster-action" v-if="curViewType === 'cluster'">
            <span class="action-item" @click="gotCreateCluster">
                <i class="bcs-icon bcs-icon-plus-circle"></i>
                {{ $t('新增集群') }}
            </span>
            <span class="line">|</span>
            <span class="action-item" @click="handleToggleCluster({
                name: $t('全部集群'),
                cluster_id: ''
            })">
                <i class="bcs-icon bcs-icon-quanbujiqun"></i>
                {{ $t('全部集群') }}
            </span>
        </div>
    </div>
</template>

<script>
    import { bus } from '@open/common/bus'
    import { catchErrorHandler } from '@open/common/util'

    const BCS_CLUSTER = 'bcs-cluster'
    const BCS_CLUSTER_NAME = 'bcs-cluster-name'

    export default {
        name: 'cluster-selector',
        props: {
            value: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                searchValue: '',
                clusterList: [],
                filterClusterList: [],
                permissions: {},
                activeCluster: localStorage[BCS_CLUSTER_NAME] || ''
            }
        },
        computed: {
            projectId () {
                return this.$route.params.projectId
            },
            projectCode () {
                return this.$route.params.projectCode
            },
            curClusterList () {
                return this.$store.state.cluster.clusterList
            },
            curViewType () {
                return this.$route.path.indexOf('dashboard') > -1 ? 'dashboard' : 'cluster'
            }
        },
        watch: {
            value (n) {
                if (n) {
                    this.filterClusterList = this.clusterList
                    this.$nextTick(() => {
                        this.$refs.searchInput.focus()
                    })
                } else {
                    this.searchValue = ''
                }
            },
            curClusterList (n) {
                this.clusterList = n
            }
        },
        created () {
            this.clusterList = this.curClusterList
            this.getClusters()
        },
        methods: {
            /**
             * 获取所有的集群
             */
            getClusters () {
                this.$nextTick(async () => {
                    try {
                        const res = await this.$store.dispatch('cluster/getClusterList', this.projectId)
                        this.clusterList = res.data.results
                        if (!this.$store.state.cluster.clusterList.length) {
                            this.$store.commit('cluster/forceUpdateClusterList', this.clusterList)
                        }
                    } catch (e) {
                        catchErrorHandler(e, this)
                    }
                })
            },

            /**
             * 点击除自身元素外，关闭集群选择弹窗
             */
            handleHideClusterSelector (e) {
                this.$emit('input', false)
            },

            /**
             * 搜索过滤集群列表
             */
            handleChangeSearchValue () {
                if (this.searchValue === '') {
                    this.filterClusterList = this.clusterList
                } else {
                    this.filterClusterList = this.clusterList.filter(item => {
                        if (item.name.includes(this.searchValue)) {
                            return item
                        }
                    })
                }
            },

            /**
             * 集群切换
             * @param {Object} cluster 集群信息
             */
            handleToggleCluster (cluster) {
                this.activeCluster = cluster.name
                this.handleSaveClusterInfo(cluster)
                // 抛出选中的集群信息
                this.$emit('change', cluster)
                // 关闭集群选择弹窗
                this.$emit('input', false)
                if (!cluster.cluster_id) {
                    sessionStorage.removeItem('bcs-selected-menu-data')
                    if (this.$route.meta.isDashboard) {
                        this.$router.push({
                            name: 'dashboard',
                            params: {
                                projectId: this.projectId,
                                projectCode: this.projectCode
                            }
                        })
                    } else {
                        this.$router.push({
                            name: 'clusterMain',
                            params: {
                                needCheckPermission: true
                            }
                        })
                    }
                } else {
                    const data = this.$route.meta.isDashboard
                        ? {
                            isChild: true,
                            item: {
                                name: this.$t('命名空间'),
                                isSaveData: true,
                                icon: "bcs-icon-namespace",
                                roleId: "workload:menu",
                                pathName: ["dashboardNamespace"],
                                isSelected: true,
                                isOpen: false
                            },
                            itemIndex: 0
                        }
                        : {
                            isChild: false,
                            item: {
                                icon: 'bcs-icon-jq-colony',
                                name: this.$t('概览'),
                                pathName: ['clusterOverview', 'clusterNode', 'clusterInfo'],
                                roleId: 'overview:menu'
                            },
                            itemIndex: 0
                        }
                    bus.$emit('cluster-change', data)
                }
            },

            /**
             * 保存cluster信息
             */
            handleSaveClusterInfo (cluster) {
                localStorage.setItem(BCS_CLUSTER, cluster.cluster_id)
                localStorage.setItem(BCS_CLUSTER_NAME, cluster.name)
            },

            /**
             * 新建集群
             */
            async gotCreateCluster () {
                if (!this.permissions.create) {
                    await this.$store.dispatch('getMultiResourcePermissions', {
                        project_id: this.projectId,
                        operator: 'or',
                        resource_list: [
                            {
                                policy_code: 'create',
                                resource_type: 'cluster_test'
                            },
                            {
                                policy_code: 'create',
                                resource_type: 'cluster_prod'
                            }
                        ]
                    })
                }

                this.$router.push({
                    name: 'clusterCreate',
                    params: {
                        projectId: this.projectId,
                        projectCode: this.projectCode
                    }
                })

                // 关闭集群选择弹窗
                this.$emit('input', false)
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
