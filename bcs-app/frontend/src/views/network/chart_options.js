/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import moment from 'moment'

export default {
    tooltip: {
        trigger: 'axis',
        confine: true,
        extraCssText: 'width: 300px;',
        axisPointer: {
            type: 'line',
            animation: false,
            label: {
                backgroundColor: '#6a7985'
            }
        },
        formatter (params, ticket, callback) {
            let ret = `<div>${moment(params[0].value[0]).format('YYYY-MM-DD HH:mm:ss')}</div>`
            params.forEach(item => {
                ret += `<div style="text-align: left; white-space: normal;word-break: break-all;">`
                    + `${item.seriesName}：<span style="font-weight: 700; color: #30d873;">`
                    + `${(item.value[1]).toFixed(2)}%</span></div>`
            })
            return ret
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
                    // color: '#868b97'
                }
            },
            axisLabel: {
                color: '#868b97',
                formatter (value, index) {
                    return moment(value).format('HH:mm')
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
                    return `${value}%`
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
