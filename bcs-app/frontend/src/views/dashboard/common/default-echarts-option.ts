import { formatBytes } from '@/common/util'
import { Decimal } from 'decimal.js'

export default function (unit) {
    return {
        tooltip: {
            trigger: 'axis',
            confine: true,
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
                    color: '#868b97'
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
                        let axisLabel = value
                        switch (unit) {
                            // 字节类型纵坐标
                            case 'byte':
                                axisLabel = `${formatBytes(value, 2)}`
                                break
                            // 百分比类型纵坐标
                            case 'percent':
                                const valueLen = String(value).length > 3 ? 3 : String(value).length
                                axisLabel = `${new Decimal(value).toPrecision(valueLen)}%`
                                break
                        }
                        return axisLabel
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
        ]
    }
}
