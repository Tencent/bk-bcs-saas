<template>
    <div class="biz-content">
        <div class="biz-top-bar">
            <div class="dashboard-top-title">
                {{$t('资源视图')}}
            </div>
            <dashboard-top-actions />
        </div>
    </div>
</template>
<script>
    import store from '@/store'
    import { defineComponent, reactive, toRefs, computed } from '@vue/composition-api'

    import DashboardTopActions from './dashboard-top-actions'

    export default defineComponent({
        name: 'About',
        components: { DashboardTopActions },
        setup (props, ctx) {
            console.error(props)
            console.error(ctx)

            const lang = computed(() => store.state.lang)
            console.error(lang)
            console.error(lang.value)

            const state = reactive({
                tableData: [
                    {
                        ip: '192.168.0.1',
                        source: 'QQ',
                        status: '创建中',
                        create_time: '2018-05-25 15:02:24',
                        children: [
                            {
                                name: '用户管理',
                                count: '23',
                                creator: 'person2',
                                create_time: '2017-10-10 11:12',
                                desc: '用户管理'
                            },
                            {
                                name: '模块管理',
                                count: '2',
                                creator: 'person1',
                                create_time: '2017-10-10 11:12',
                                desc: '无数据测试'
                            }
                        ]
                    },
                    {
                        ip: '192.168.0.2',
                        source: '微信',
                        status: '正常',
                        create_time: '2018-05-25 15:02:24',
                        children: [
                            {
                                name: '用户管理',
                                count: '23',
                                creator: 'person2',
                                create_time: '2017-10-10 11:12',
                                desc: '用户管理'
                            },
                            {
                                name: '模块管理',
                                count: '2',
                                creator: 'person1',
                                create_time: '2017-10-10 11:12',
                                desc: '无数据测试'
                            }
                        ]
                    },
                    {
                        ip: '192.168.0.3',
                        source: 'QQ',
                        status: '创建中',
                        create_time: '2018-05-25 15:02:24',
                        children: [
                            {
                                name: '用户管理',
                                count: '23',
                                creator: 'person2',
                                create_time: '2017-10-10 11:12',
                                desc: '用户管理'
                            },
                            {
                                name: '模块管理',
                                count: '2',
                                creator: 'person1',
                                create_time: '2017-10-10 11:12',
                                desc: '无数据测试'
                            }
                        ]
                    }
                ],
                pagination: {
                    current: 1,
                    count: 500,
                    limit: 20
                },
                size: 'small'
            })

            // const handlePageLimitChange = () => {
            //     console.log('handlePageLimitChange', arguments)
            // }

            // const toggleTableSize = () => {
            //     const sizeArr = ['small', 'medium', 'large']
            //     const index = (sizeArr.indexOf(state.size) + 1) % 3
            //     state.size = sizeArr[index]
            // }

            // const handlePageChange = (page) => {
            //     state.pagination.current = page
            // }

            // const remove = (row) => {
            //     const index = state.tableData.indexOf(row)
            //     if (index !== -1) {
            //         state.tableData.splice(index, 1)
            //     }
            // }

            // const reset = (row) => {
            //     row.status = '创建中'
            // }

            const { $router, $route } = ctx.root

            const projectId = computed(() => $route.params.projectId).value
            const projectCode = computed(() => $route.params.projectCode).value

            const goBCS = () => {
                setTimeout(() => {
                    const routerUrl = $router.resolve({
                        name: 'clusterMain',
                        params: {
                            projectId: projectId,
                            projectCode: projectCode
                        }
                    })
                    window.$syncUrl(routerUrl.href.replace(new RegExp(`^${SITE_URL}`), ''), true)
                }, 0)
            }

            return {
                ...toRefs(state),
                goBCS
            }
        }
    })
</script>
<style scoped>
    @import './index.css';
</style>
