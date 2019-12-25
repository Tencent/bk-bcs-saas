# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
# Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
"""普罗米修斯接口封装
"""
import logging

import arrow
from django.conf import settings

from backend.components.utils import http_get
from backend.utils.basic import normalize_metric

logger = logging.getLogger(__name__)


def query_range(query, start, end, step):
    """范围请求API
    """
    url = '{host}/api/v1/query_range'.format(host=settings.THANOS_HOST)
    params = {'query': query, 'start': start, 'end': end, 'step': step}
    logger.info('prometheus query_range: %s', query)
    resp = http_get(url, params=params, timeout=10)
    return resp


def query(_query):
    """查询API
    """
    url = '{host}/api/v1/query'.format(host=settings.THANOS_HOST)
    params = {'query': _query}
    logger.info('prometheus query: %s', query)
    resp = http_get(url, params=params, timeout=10)
    return resp


def get_node_cpu_usage(ip, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    porm_query = f'avg by (instance) (sum by (cpu,instance) (irate(node_cpu{{job="node-exporter", mode!="idle", instance=~"{ ip }:9100"}}[2m])))'  # noqa
    resp = query_range(porm_query, start, end, step)
    if resp.get('status') != 'success':
        return []

    if not resp['data']['result']:
        return []

    data = []
    for i in resp['data']['result'][0]['values']:
        data.append({
            'time': i[0] * 1000,
            'usage': normalize_metric(float(i[1]) * 100)})
    return data


def get_node_memory_usage(ip, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    porm_query = f'node_memory_MemTotal{{job="node-exporter", instance=~"{ ip }:9100"}}'
    total = query_range(porm_query, start, end, step)
    if total.get('status') != 'success':
        return []

    porm_query = f"""
        node_memory_MemTotal{{job="node-exporter", instance=~"{ ip }:9100"}} -
        node_memory_MemFree{{job="node-exporter", instance=~"{ ip }:9100"}} -
        node_memory_Buffers{{job="node-exporter", instance=~"{ ip }:9100"}} -
        node_memory_Cached{{job="node-exporter", instance=~"{ ip }:9100"}}"""
    usage = query_range(porm_query, start, end, step)
    if usage.get('status') != 'success':
        return []

    if not total['data']['result'] or not usage['data']['result']:
        return []

    data = []
    total_dict = dict(total['data']['result'][0]['values'])
    usage_dict = dict(usage['data']['result'][0]['values'])
    for k, v in total_dict.items():
        data.append({
            'time': k * 1000,
            'total': normalize_metric(total_dict.get(k, 0)),
            'used': normalize_metric(usage_dict.get(k, 0))
        })
    return data


def get_node_network_usage(ip, start, end):
    """获取网络数据
    start, end单位为毫秒，和数据平台保持一致
    数据单位KB/s
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    porm_query = f'max by (instance) (rate(node_network_receive_bytes{{job="node-exporter", instance=~"{ ip }:9100"}}[5m]))'  # noqa
    receive = query_range(porm_query, start, end, step)
    if receive.get('status') != 'success':
        return []

    porm_query = f'max by (instance) (rate(node_network_transmit_bytes{{job="node-exporter", instance=~"{ ip }:9100"}}[5m]))'  # noqa
    transmit = query_range(porm_query, start, end, step)
    if transmit.get('status') != 'success':
        return []

    if not receive['data']['result'] or not transmit['data']['result']:
        return []

    data = []
    receive_dict = dict(receive['data']['result'][0]['values'])
    transmit_dict = dict(transmit['data']['result'][0]['values'])
    for k, v in receive_dict.items():
        data.append({
            'time': k * 1000,
            'speedRecv': normalize_metric(float(receive_dict.get(k, 0)) / 1024),
            'speedSent': normalize_metric(float(transmit_dict.get(k, 0)) / 1024)
        })
    return data


def get_node_diskio_usage(ip, start, end):
    """获取磁盘IO数据
    start, end单位为毫秒，和数据平台保持一致
    数据单位KB/s
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    porm_query = f'max by (instance) (rate(node_disk_bytes_read{{job="node-exporter", instance=~"{ ip }:.*"}}[5m]))'
    read = query_range(porm_query, start, end, step)
    if read.get('status') != 'success':
        return []

    porm_query = f'max by (instance) (rate(node_disk_bytes_written{{job="node-exporter", instance=~"{ ip }:.*"}}[5m]))'
    written = query_range(porm_query, start, end, step)
    if written.get('status') != 'success':
        return []

    if not read['data']['result'] or not written['data']['result']:
        return []

    read_dict = dict(read['data']['result'][0]['values'])
    written_dict = dict(written['data']['result'][0]['values'])
    data = []
    for k, v in read_dict.items():
        data.append({
            'time': k * 1000,
            'rkb_s': normalize_metric(float(read_dict.get(k, 0)) / 1024),
            'wkb_s': normalize_metric(float(written_dict.get(k, 0)) / 1024)
        })
    return data


def get_node_disk_io_utils(ip, start, end):
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    porm_query = f'max by (instance) (rate(node_disk_io_time_seconds_total{{job="node-exporter", instance=~"{ ip }:9100"}}[5m]) * 100)'  # noqa
    io_utils = query_range(porm_query, start, end, step)
    if io_utils.get('status') != 'success':
        return []

    if not io_utils['data']['result']:
        return []

    data = []

    for i in io_utils['data']['result'][0]['values']:
        data.append({
            'time': i[0] * 1000,
            'usage': normalize_metric(i[1])})

    return data


def get_container_cpu_usage(docker_id, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    if isinstance(docker_id, list):
        docker_id_list = '|'.join('.*%s.*' % i for i in docker_id)
    else:
        docker_id_list = '.*%s.*' % docker_id

    porm_query = f'sum by (id, name) (rate(container_cpu_usage_seconds_total{{id=~"{ docker_id_list }"}}[1m]))'
    resp = query_range(porm_query, start, end, step)
    if resp.get('status') != 'success':
        return []

    if not resp['data']['result']:
        return []

    data = []
    for res in resp['data']['result']:
        _data = res['metric']
        _data['container_name'] = res['metric']['name']
        metrics = []
        for i in res['values']:
            metrics.append({
                'time': i[0] * 1000,
                'container_name': res['metric']['name'],
                'usage': normalize_metric(float(i[1]) * 100)})
        _data['metrics'] = metrics
        data.append(_data)

    # 单个直接返回metrics的值
    if isinstance(docker_id, list):
        return data
    else:
        return data[0]['metrics']


def get_container_memory_usage(docker_id, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    if isinstance(docker_id, list):
        docker_id_list = '|'.join('.*%s.*' % i for i in docker_id)
    else:
        docker_id_list = '.*%s.*' % docker_id

    porm_query = f'container_memory_usage_bytes{{id=~"{ docker_id_list }"}}'
    total = query_range(porm_query, start, end, step)
    if total.get('status') != 'success':
        return []

    if not total['data']['result']:
        return []

    data = []

    for res in total['data']['result']:
        _data = res['metric']
        _data['container_name'] = res['metric']['name']
        metrics = []
        for i in res['values']:
            metrics.append({
                'time': i[0] * 1000,
                'rss_pct': 0,
                'container_name': res['metric']['name'],
                'used': normalize_metric(float(i[1]) / 1024 / 1024),
                'unit': 'MB'})

        _data['metrics'] = metrics
        data.append(_data)

    # 单个直接返回metrics的值
    if isinstance(docker_id, list):
        return data
    else:
        return data[0]['metrics']


def get_container_network_usage(docker_id, start, end):
    """获取网络数据
    start, end单位为毫秒，和数据平台保持一致
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    porm_query = f'sum by (id, name) (rate(container_network_receive_bytes_total{{id=~".*{ docker_id }.*"}}[1m]))'
    receive = query_range(porm_query, start, end, step)
    if receive.get('status') != 'success':
        return []

    porm_query = f'sum by (id, name) (rate(container_network_transmit_bytes_total{{id=~".*{ docker_id }.*"}}[1m]))'
    transmit = query_range(porm_query, start, end, step)
    if transmit.get('status') != 'success':
        return []

    if not receive['data']['result'] or not transmit['data']['result']:
        return []

    data = []
    metric = receive['data']['result'][0]['metric']
    receive_dict = dict(receive['data']['result'][0]['values'])
    transmit_dict = dict(transmit['data']['result'][0]['values'])
    for k, v in receive_dict.items():
        data.append({
            'time': k * 1000,
            'container_name': metric['name'],
            'rxbytes': normalize_metric(receive_dict.get(k, 0)),
            'txbytes': normalize_metric(transmit_dict.get(k, 0))
        })
    return data


def get_container_diskio_usage(docker_id, start, end):
    """获取磁盘IO数据
    start, end单位为毫秒，和数据平台保持一致
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    porm_query = f'sum by (id, name) (rate(container_fs_reads_bytes_total{{id=~".*{ docker_id }.*"}}[1m]))'
    read = query_range(porm_query, start, end, step)
    if read.get('status') != 'success':
        return []

    porm_query = f'sum by (id, name) (rate(container_fs_writes_bytes_total{{id=~".*{ docker_id }.*"}}[1m]))'
    writes = query_range(porm_query, start, end, step)
    if writes.get('status') != 'success':
        return []

    if not read['data']['result'] or not writes['data']['result']:
        return []

    data = []
    metric = read['data']['result'][0]['metric']
    read_dict = dict(read['data']['result'][0]['values'])
    writes_dict = dict(writes['data']['result'][0]['values'])
    for k, v in read_dict.items():
        data.append({
            'time': k * 1000,
            'used_pct': 0,  # 兼容字段
            'container_name': metric['name'],
            'read_bytes': normalize_metric(read_dict.get(k, 0)),  # 转化为Bytes
            'write_bytes': normalize_metric(writes_dict.get(k, 0))  # 转化为Bytes
        })
    return data


def get_cluster_disk_usage(cluster_list: list, start: int, end: int) -> tuple:
    """获取k8s集群磁盘使用率
    """
    start = start // 1000
    end = end // 1000
    step = (end - start) // 60
    cluster_id = '|'.join(cluster_list)

    #  为空直接返回
    if not cluster_list:
        return ({}, {})

    porm_query = f'sum(node_filesystem_free_bytes{{device!="rootfs", device!="tmpfs", cluster_id=~"{ cluster_id }"}}) by (cluster_id)'  # noqa

    free_result = query_range(porm_query, start, end, step)
    if free_result.get('status') != 'success' or not free_result['data']['result']:
        free = {}
    else:
        free = {i['metric']['cluster_id']: i['values'] for i in free_result['data']['result']}

    porm_query = f'sum(node_filesystem_size_bytes{{device!="rootfs", device!="tmpfs", cluster_id=~"{ cluster_id }"}}) by (cluster_id)'  # noqa
    total_result = query_range(porm_query, start, end, step)
    if total_result.get('status') != 'success' or not total_result['data']['result']:
        total = {}
    else:
        total = {i['metric']['cluster_id']: i['values'] for i in total_result['data']['result']}

    return (total, free)


def fixed_disk_usage(cluster_data):
    """k8s磁盘使用率
    单位是 GB
    """
    end = arrow.now().timestamp * 1000
    start = end - 15 * 60 * 1000
    cluster_list = [i['cluster_id'] for i in cluster_data]
    total, free = get_cluster_disk_usage(cluster_list, start, end)

    for cluster in cluster_data:
        total_dist = total.get(cluster['cluster_id']) or []
        total_dist = total_dist[-1][1] if total_dist else 0
        total_disk = normalize_metric(float(total_dist) / (1024 * 1024 * 1024))

        free_dist = free.get(cluster['cluster_id']) or []
        free_dist = free_dist[-1][1] if free_dist else 0
        free_disk = normalize_metric(float(free_dist) / (1024 * 1024 * 1024))

        cluster['total_disk'] = total_disk
        cluster['remain_disk'] = free_disk

    return cluster_data


def fixed_disk_usage_history(cluster_id):
    """k8s磁盘使用率
    单位是 GB
    """
    end = arrow.now().timestamp * 1000
    start = end - 60 * 60 * 1000
    cluster_list = [cluster_id]
    total, free = get_cluster_disk_usage(cluster_list, start, end)

    total_dist = total.get(cluster_id) or []
    free_dist = free.get(cluster_id) or []

    total_dict = dict(total_dist)
    free_dict = dict(free_dist)
    data = []
    for k, v in total_dict.items():
        data.append({
            'time': k * 1000,
            'total_disk': normalize_metric(float(total_dict.get(k, 0)) / (1024 * 1024 * 1024)),
            'remain_disk': normalize_metric(float(free_dict.get(k, 0)) / (1024 * 1024 * 1024))
        })
    return data
