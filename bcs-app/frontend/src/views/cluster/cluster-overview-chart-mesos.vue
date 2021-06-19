<template>
    <chart :options="renderChartOpts" ref="chartNode" auto-resize></chart>
</template>

<script>
    import moment from 'moment'

    import ECharts from 'vue-echarts/components/ECharts.vue'
    import 'echarts/lib/chart/line'
    import 'echarts/lib/component/tooltip'

    export default {
        components: {
            chart: ECharts
        },
        props: {
            chartType: {
                type: String
            },
            showLoading: {
                type: Boolean,
                default: true
            },
            usedData: {
                type: Array,
                default: () => []
            },
            totalData: {
                type: Array,
                default: () => []
            }
        },
        data () {
            return {
                cpuChartOpts: {
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'line',
                            animation: false,
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        }
                    },
                    grid: {
                        show: false,
                        top: '4%',
                        left: '4%',
                        right: '5%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: [
                        {
                            type: 'time',
                            boundaryGap: false,
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: '#dde4eb'
                                }
                            },
                            axisTick: {
                                alignWithLabel: true,
                                length: 5,
                                lineStyle: {
                                    color: '#ebf0f5'
                                }
                            },
                            axisLabel: {
                                color: '#868b97',
                                formatter (value, index) {
                                    if (String(parseInt(value, 10)).length === 10) {
                                        value = parseInt(value, 10) + '000'
                                    }
                                    return moment(parseInt(value, 10)).format('HH:mm')
                                }
                            },
                            splitLine: {
                                show: true,
                                lineStyle: {
                                    color: ['#ebf0f5'],
                                    type: 'dashed'
                                }
                            }
                        }
                    ],
                    yAxis: [
                        {
                            boundaryGap: [0, '2%'],
                            type: 'value',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: '#dde4eb'
                                }
                            },
                            axisTick: {
                                alignWithLabel: true,
                                length: 0,
                                lineStyle: {
                                    color: 'red'
                                }
                            },
                            axisLabel: {
                                color: '#868b97',
                                formatter (value, index) {
                                    return parseFloat(value).toFixed(1)
                                }
                            },
                            splitLine: {
                                show: true,
                                lineStyle: {
                                    color: ['#ebf0f5'],
                                    type: 'dashed'
                                }
                            }
                        }
                    ],
                    series: []
                },
                memChartOpts: {
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'line',
                            animation: false,
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        }
                    },
                    grid: {
                        show: false,
                        top: '4%',
                        left: '4%',
                        right: '5%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: [
                        {
                            type: 'time',
                            boundaryGap: false,
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: '#dde4eb'
                                }
                            },
                            axisTick: {
                                alignWithLabel: true,
                                length: 5,
                                lineStyle: {
                                    color: '#ebf0f5'
                                }
                            },
                            axisLabel: {
                                color: '#868b97',
                                formatter (value, index) {
                                    if (String(parseInt(value, 10)).length === 10) {
                                        value = parseInt(value, 10) + '000'
                                    }
                                    return moment(parseInt(value, 10)).format('HH:mm')
                                }
                            },
                            splitLine: {
                                show: true,
                                lineStyle: {
                                    color: ['#ebf0f5'],
                                    type: 'dashed'
                                }
                            }
                        }
                    ],
                    yAxis: [
                        {
                            boundaryGap: [0, '2%'],
                            type: 'value',
                            axisLine: {
                                show: true,
                                lineStyle: {
                                    color: '#dde4eb'
                                }
                            },
                            axisTick: {
                                alignWithLabel: true,
                                length: 0,
                                lineStyle: {
                                    color: 'red'
                                }
                            },
                            axisLabel: {
                                color: '#868b97',
                                formatter (value, index) {
                                    return parseFloat(value / 1024).toFixed(1)
                                }
                            },
                            splitLine: {
                                show: true,
                                lineStyle: {
                                    color: ['#ebf0f5'],
                                    type: 'dashed'
                                }
                            }
                        }
                    ],
                    series: [
                    ]
                },
                renderChartOpts: null
            }
        },
        computed: {
            curCluster () {
                return this.$store.state.cluster.curCluster
            },
            isEn () {
                return this.$store.state.isEn
            }
        },
        watch: {
            // showLoading: {
            //     handler (newVal, oldVal) {
            //         if (newVal === true) {
            //             const chartNode = this.$refs.chartNode
            //             chartNode && chartNode.showLoading({
            //                 text: this.$t('正在加载中...'),
            //                 color: '#30d878',
            //                 maskColor: 'rgba(255, 255, 255, 0.8)'
            //             })
            //         }
            //     },
            //     immediate: true
            // }
            usedData (v) {
                setTimeout(() => {
                    this.renderMatrixChart(this.usedData, 'used')
                }, 0)
            },
            totalData (v) {
                setTimeout(() => {
                    this.renderMatrixChart(this.totalData, 'total')
                }, 0)
            }
        },
        created () {
            if (this.chartType === 'cpu') {
                this.renderChartOpts = Object.assign({}, this.cpuChartOpts)
            }
            if (this.chartType === 'mem') {
                this.renderChartOpts = Object.assign({}, this.memChartOpts)
            }
        },
        mounted () {
            if (this.showLoading) {
                const chartNode = this.$refs.chartNode
                chartNode && chartNode.showLoading({
                    text: this.$t('正在加载中...'),
                    color: '#30d878',
                    maskColor: 'rgba(255, 255, 255, 0.8)'
                })
            } else {
                this.renderMatrixChart(this.usedData, 'used')
                this.renderMatrixChart(this.totalData, 'total')
            }
            window.addEventListener('resize', this.resizeHandler)
        },
        destroyed () {
            window.removeEventListener('resize', this.resizeHandler)
        },
        methods: {
            resizeHandler () {
                this.$refs.chartNode && this.$refs.chartNode.resize()
            },

            /**
             * 渲染 matrix 图表，数据为二维数组
             *
             * @param {Array} list 数据
             */
            renderMatrixChart (list, idx) {
                const chartNode = this.$refs.chartNode
                if (!chartNode) {
                    return
                }

                const renderChartOpts = Object.assign({}, this.renderChartOpts)

                const data = list.length ? list : [{
                    metric: { cluster_id: '--' },
                    values: [[parseInt(String(+new Date()).slice(0, 10), 10), '10']]
                }]

                // const data = list.length ? list : [{ values: [[parseInt(String(+new Date()).slice(0, 10), 10), '0']] }]

                data.forEach(item => {
                    item.values.forEach(d => {
                        d[0] = parseInt(d[0] + '000', 10)
                        d.push(idx)
                        d.push(item.metric.cluster_id)
                    })

                    let color = ''
                    if (this.chartType === 'cpu') {
                        color = '#30d878'
                    }

                    if (this.chartType === 'mem') {
                        color = '#3a84ff'
                    }

                    const series = {
                        type: 'line',
                        smooth: true,
                        showSymbol: false,
                        hoverAnimation: false,
                        itemStyle: {
                            normal: {
                                color: color
                            }
                        },
                        data: item.values
                    }

                    if (idx === 'total') {
                        series.itemStyle.normal.color = '#ea3636'
                    } else {
                        series.areaStyle = {
                            normal: {
                                opacity: 0.2
                            }
                        }
                    }

                    renderChartOpts.series.push(series)
                })

                const me = this
                chartNode.mergeOptions({
                    tooltip: {
                        formatter (params, ticket, callback) {
                            if (params[0].value[3] === '--') {
                                return '<div>No Data</div>'
                            }

                            let date = params[0].value[0]
                            if (String(parseInt(date, 10)).length === 10) {
                                date = parseInt(date, 10) + '000'
                            }

                            let ret = `<div>${moment(parseInt(date, 10)).format('YYYY-MM-DD HH:mm:ss')}</div>`
                            params.reverse().forEach(p => {
                                let label = ''
                                if (me.chartType === 'cpu') {
                                    if (p.value[2] === 'used') {
                                        label = me.$t('CPU使用(核)')
                                    } else {
                                        label = me.$t('CPU总量(核)')
                                    }
                                    ret += `<div>${p.value[3]} ${label}：${parseFloat(p.value[1]).toFixed(2)}</div>`
                                }

                                if (me.chartType === 'mem') {
                                    if (p.value[2] === 'used') {
                                        label = me.$t('内存使用(GB)')
                                    } else {
                                        label = me.$t('内存总量(GB)')
                                    }
                                    ret += `<div>${p.value[3]} ${label}：${parseFloat(p.value[1] / 1024).toFixed(2)}</div>`
                                }
                            })

                            return ret
                        }
                    }
                })

                chartNode.hideLoading()
            }
        }
    }
</script>
<style lang="postcss">
    .echarts {
        width: 100%;
        height: 250px;
    }
</style>
