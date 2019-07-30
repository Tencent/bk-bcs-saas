# -*- coding: utf-8 -*-

# metric server 支持的 metric
HPA_METRICS = {
    'cpu_util': {
        'unit': '%',
        'aggregation': 'utilization',
        'description': "CPU平均使用率"
    },
    'memory_util': {
        'unit': '%',
        'aggregation': 'utilization',
        'description': '内存平均使用率'
    }
}
