
<template>
    <div class="metric-item" v-bkloading="{ isLoading }">
        <div class="metric-item-title">
            <span>{{ title }}</span>
            <bk-dropdown-menu trigger="click" @show="isDropdownShow = true" @hide="isDropdownShow = false">
                <div class="dropdown-trigger-text" slot="dropdown-trigger">
                    <span class="name">{{ activeTime.name }}</span>
                    <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                </div>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                    <li v-for="(item, index) in timeRange" :key="index" @click="handleTimeRangeChange(item)">
                        {{ item.name }}
                    </li>
                </ul>
            </bk-dropdown-menu>
        </div>
        <ECharts class="vue-echarts" :options="echartsOptions" auto-resize></ECharts>
    </div>
</template>
<script lang="ts">
    import { defineComponent, reactive, toRefs, onMounted, ref, watch } from '@vue/composition-api'
    import moment from 'moment'
    import { createChartOption } from '@/views/cluster/node-overview-chart-opts'
    import ECharts from 'vue-echarts'
    import 'echarts/lib/chart/line'
    import 'echarts/lib/component/tooltip'
    import 'echarts/lib/component/legend'

    export default defineComponent({
        name: 'Metric',
        components: {
            ECharts
        },
        props: {
            title: {
                type: String,
                default: ''
            },
            timeRange: {
                type: Array,
                default: () => [
                    {
                        name: window.i18n.t('1小时'),
                        range: 60 * 60 * 1000
                    },
                    {
                        name: window.i18n.t('24小时'),
                        range: 60 * 24 * 60 * 1000
                    },
                    {
                        name: window.i18n.t('近7天'),
                        range: 7 * 24 * 60 * 60 * 1000
                    }
                ]
            },
            options: {
                type: Object,
                default: () => (createChartOption())
            },
            category: {
                type: String,
                default: '',
                required: true
            },
            metric: {
                type: [String, Array],
                default: '',
                required: true
            },
            params: {
                type: Object,
                default: () => ({})
            },
            colors: {
                type: [String, Array],
                default: '#3a84ff'
            }
        },
        setup (props, ctx) {
            const { $i18n, $store } = ctx.root

            const state = reactive({
                isDropdownShow: false,
                activeTime: {
                    name: $i18n.t('1小时'),
                    range: 60 * 60 * 1000
                },
                isLoading: false
            })
            const echartsOptions = ref<any>({})

            const handleTimeRangeChange = (item) => {
                if (state.activeTime.range === item.range) return

                state.activeTime = item
                handleGetMetricData()
            }
            // 设置图表options
            const handleSetChartOptions = (data) => {
                if (!data) return

                const series: any[] = []
                data.forEach(item => {
                    const list = item?.result.map((item, index) => {
                        // series 配置
                        return {
                            type: 'line',
                            showSymbol: false,
                            smooth: true,
                            hoverAnimation: false,
                            areaStyle: {
                                normal: {
                                    opacity: 0.2
                                }
                            },
                            itemStyle: {
                                normal: {
                                    color: Array.isArray(props.colors)
                                        ? props.colors[(index % (props.colors.length) - 1)]
                                        : props.colors
                                }
                            },
                            data: item?.values || []
                        }
                    }) || []
                    series.push(...list)
                })
                echartsOptions.value = Object.assign({}, props.options, { series })
            }
            // 获取图表数据
            const handleGetMetricData = async () => {
                const timeRange = {
                    start_at: moment().subtract(state.activeTime.range, 'ms').format('YYYY-MM-DD HH:mm:ss'),
                    end_at: moment().format('YYYY-MM-DD HH:mm:ss')
                }

                let action = ''
                switch (props.category) {
                    case 'pods':
                        if (!props.params) break
                        action = 'dashboard/podMetric'
                        break
                    case 'containers':
                        if (!props.params) break
                        action = 'dashboard/containerMetric'
                }
                if (!action) return []

                const metrics = Array.isArray(props.metric) ? props.metric : [props.metric]
                const promises: Promise<any>[] = []
                metrics.forEach(metric => {
                    const params = {
                        $metric: metric,
                        ...timeRange,
                        ...props.params
                    }
                    promises.push($store.dispatch(action, params))
                })

                state.isLoading = true
                const metricData = await Promise.all(promises)
                state.isLoading = false

                handleSetChartOptions(metricData)

                return metricData
            }

            const { params } = toRefs(props)
            watch(params, handleGetMetricData)

            onMounted(async () => {
                await handleGetMetricData()
            })

            return {
                echartsOptions,
                ...toRefs(state),
                handleTimeRangeChange,
                handleGetMetricData,
                handleSetChartOptions
            }
        }
    })
</script>
<style lang="postcss" scoped>
.metric-item {
    width: 100%;
    padding: 20px 18px;
    &-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 14px;
        /deep/ .dropdown-trigger-text {
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            .icon-angle-down {
                font-size: 20px;
            }
        }
        /deep/ .bk-dropdown-list {
            li {
                height: 32px;
                line-height: 32px;
                padding: 0 16px;
                color: #63656e;
                font-size: 12px;
                white-space: nowrap;
                cursor: pointer;
                &:hover {
                    background-color: #eaf3ff;
                    color: #3a84ff;
                }
            }
        }
    }
    .vue-echarts {
        padding-top: 12px;
        width: 100% !important;
        height: 180px;
    }
}
</style>
