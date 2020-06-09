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
import time

import arrow
from django.conf import settings

from backend.components.utils import http_get, http_post
from backend.utils.basic import normalize_metric

logger = logging.getLogger(__name__)

# thanos鉴权, 格式如 ('admin', 'admin')
AUTH = getattr(settings, "THANOS_AUTH", None)


def query_range(query, start, end, step, project_id=None):
    """范围请求API
    """
    url = f"{settings.THANOS_HOST}/api/v1/query_range"
    data = {"query": query, "start": start, "end": end, "step": step}
    headers = {"X-Tenant-Project-Id": project_id}
    logger.info("prometheus query_range: %s", data)
    resp = http_post(url, data=data, timeout=120, auth=AUTH, headers=headers, raise_for_status=False)
    return resp


def query(_query, time=None, project_id=None):
    """查询API
    """
    url = f"{settings.THANOS_HOST}/api/v1/query"
    data = {"query": _query, "time": time}
    headers = {"X-Tenant-Project-Id": project_id}
    logger.info("prometheus query: %s", data)
    resp = http_post(url, data=data, timeout=120, auth=AUTH, headers=headers, raise_for_status=False)
    return resp


def get_series(match, start, end, project_id=None):
    """查询series, Querying metadata
    """
    url = f"{settings.THANOS_HOST}/api/v1/series"
    headers = {"X-Tenant-Project-Id": project_id}
    data = {"match[]": match, "start": start, "end": end}
    logger.info("prometheus series: %s", data)
    resp = http_post(url, data=data, timeout=120, auth=AUTH, headers=headers, raise_for_status=False)
    return resp


def get_targets(project_id, cluster_id, dedup=True):
    """获取集群的targets
    """
    url = "{host}/api/v1/targets".format(host=settings.THANOS_HOST)
    # 同时限制项目ID，集群ID，防止越权
    headers = {"X-Tenant-Project-Id": project_id, "X-Tenant-Cluster-Id": cluster_id}
    params = {"dedup": dedup, "state": "active"}
    resp = http_get(url, params=params, headers=headers, timeout=30, auth=AUTH)
    return resp


def get_first_value(prom_resp, fill_zero=True):
    """获取返回的第一个值
    """
    data = prom_resp.get("data") or {}
    result = data.get("result") or []
    if not result:
        if fill_zero:
            # 返回0字符串, 和promtheus保存一致
            return "0"
        return None

    value = result[0]["value"]
    if not value:
        if fill_zero:
            return "0"
        return None

    return value[1]


def get_cluster_cpu_usage(cluster_id, node_ip_list):
    """获取集群nodeCPU使用率
    """
    node_ip_list = "|".join(f"{ip}:9100" for ip in node_ip_list)
    cpu_used_prom_query = f"""
        sum(irate(node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode!="idle", instance=~"{node_ip_list}"}}[2m]))
    """  # noqa

    cpu_count_prom_query = f"""
       sum(count without(cpu, mode) (node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode="idle", instance=~"{node_ip_list}"}}))
    """  # noqa

    data = {"used": get_first_value(query(cpu_used_prom_query)), "total": get_first_value(query(cpu_count_prom_query))}
    return data


def get_cluster_cpu_usage_range(cluster_id, node_ip_list):
    """获取集群nodeCPU使用率
    """
    end = time.time()
    start = end - 3600
    step = 60

    node_ip_list = "|".join(f"{ip}:9100" for ip in node_ip_list)
    prom_query = f"""
        sum(irate(node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode!="idle", instance=~"{node_ip_list}"}}[2m])) /
        sum(count without(cpu, mode) (node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode="idle", instance=~"{node_ip_list}"}})) *
        100"""  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_cluster_memory_usage(cluster_id, node_ip_list):
    """获取集群nodeCPU使用率
    """
    node_ip_list = "|".join(f"{ip}:9100" for ip in node_ip_list)
    memory_total_prom_query = f"""
        sum(node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}})
    """

    memory_used_prom_query = f"""
        (sum(node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_MemFree_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_Buffers_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_Cached_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) +
        sum(node_memory_Shmem_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}))
    """  # noqa

    data = {
        "used_bytes": get_first_value(query(memory_used_prom_query)),
        "total_bytes": get_first_value(query(memory_total_prom_query)),
    }
    return data


def get_cluster_memory_usage_range(cluster_id, node_ip_list):
    """获取集群nodeCPU使用率
    """
    end = time.time()
    start = end - 3600
    step = 60

    node_ip_list = "|".join(f"{ip}:9100" for ip in node_ip_list)
    prom_query = f"""
        (sum(node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_MemFree_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_Buffers_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_Cached_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) +
        sum(node_memory_Shmem_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}})) /
        sum(node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) *
        100
    """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_cluster_disk_usage(cluster_id, node_ip_list):
    """获取集群nodeCPU使用率
    """
    node_ip_list = "|".join(f"{ip}:9100" for ip in node_ip_list)

    disk_total_prom_query = f"""
        sum(node_filesystem_size_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}})
    """  # noqa

    disk_used_prom_query = f"""
        sum(node_filesystem_size_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}}) -
        sum(node_filesystem_free_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}})
    """  # noqa

    data = {
        "used_bytes": get_first_value(query(disk_used_prom_query)),
        "total_bytes": get_first_value(query(disk_total_prom_query)),
    }
    return data


def get_cluster_disk_usage_range(cluster_id, node_ip_list):
    """获取k8s集群磁盘使用率
    """
    end = time.time()
    start = end - 3600
    step = 60

    node_ip_list = "|".join(f"{ip}:9100" for ip in node_ip_list)

    prom_query = f"""
        (sum(node_filesystem_size_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}}) -
        sum(node_filesystem_free_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}})) /
        sum(node_filesystem_size_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}}) *
        100
    """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_node_info(cluster_id, ip):
    prom_query = f"""
        cadvisor_version_info{{cluster_id="{cluster_id}", instance=~"{ip}:\\\\d+"}} or
        node_uname_info{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ip}:\\\\d+"}} or
        label_replace(sum by (instance) (count without(cpu, mode) (node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode="idle", instance=~"{ip}:\\\\d+"}})), "metric_name", "cpu_count", "instance", ".*") or
        label_replace(sum by (instance) (node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ip}:\\\\d+"}}), "metric_name", "memory", "instance", ".*") or
        label_replace(sum by (instance) (node_filesystem_size_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ip}:\\\\d+", fstype=~"ext[234]|btrfs|xfs|zfs"}}), "metric_name", "disk", "instance", ".*")
    """  # noqa

    resp = query(prom_query)
    return resp.get("data") or {}


def get_node_cpu_usage(cluster_id, ip):
    """获取CPU总使用率
    """
    prom_query = f"""
        sum(irate(node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode!="idle", instance="{ip}:9100"}}[2m])) /
        sum(count without(cpu, mode) (node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode="idle", instance="{ip}:9100"}})) *
        100"""  # noqa

    resp = query(prom_query)
    value = get_first_value(resp)
    return value


def get_node_cpu_usage_range(cluster_id, ip, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    step = (end - start) // 60

    prom_query = f"""
        sum(irate(node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode!="idle", instance="{ip}:9100"}}[2m])) /
        sum(count without(cpu, mode) (node_cpu_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", mode="idle", instance="{ip}:9100"}})) *
        100"""  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_node_memory_usage(cluster_id, ip):
    """获取节点内存使用率
    """
    node_ip_list = f"{ip}:9100"
    prom_query = f"""
        (sum(node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_MemFree_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_Buffers_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_Cached_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) +
        sum(node_memory_Shmem_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}})) /
        sum(node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) *
        100
    """  # noqa

    resp = query(prom_query)
    value = get_first_value(resp)
    return value


def get_node_memory_usage_range(cluster_id, ip, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    step = (end - start) // 60

    node_ip_list = f"{ip}:9100"
    prom_query = f"""
        (sum(node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_MemFree_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_Buffers_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) -
        sum(node_memory_Cached_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) +
        sum(node_memory_Shmem_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}})) /
        sum(node_memory_MemTotal_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ node_ip_list }"}}) *
        100
    """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_node_disk_usage(cluster_id, ip):
    node_ip_list = f"{ip}:9100"

    prom_query = f"""
        (sum(node_filesystem_size_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}}) -
        sum(node_filesystem_free_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}})) /
        sum(node_filesystem_size_bytes{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{node_ip_list}", fstype=~"ext[234]|btrfs|xfs|zfs"}}) *
        100
    """  # noqa

    value = get_first_value(query(prom_query))
    return value


def get_node_network_receive(cluster_id, ip, start, end):
    """获取网络数据
    start, end单位为毫秒，和数据平台保持一致
    数据单位KB/s
    """
    step = (end - start) // 60
    prom_query = f"""
        max(rate(node_network_receive_bytes_total{{cluster_id="{cluster_id}",job="node-exporter", instance=~"{ ip }:9100"}}[5m]))
        """  # noqa
    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_node_network_transmit(cluster_id, ip, start, end):
    step = (end - start) // 60
    prom_query = f"""
        max(rate(node_network_transmit_bytes_total{{cluster_id="{cluster_id}",job="node-exporter", instance=~"{ ip }:9100"}}[5m]))
        """  # noqa
    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_node_diskio_usage(cluster_id, ip):
    """获取当前磁盘IO
    """
    prom_query = f"""
        max(rate(node_disk_io_time_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ ip }:9100"}}[2m]) * 100)
        """  # noqa

    value = get_first_value(query(prom_query))
    return value


def get_node_diskio_usage_range(cluster_id, ip, start, end):
    """获取磁盘IO数据
    start, end单位为毫秒，和数据平台保持一致
    数据单位KB/s
    """
    step = (end - start) // 60
    prom_query = f"""
        max(rate(node_disk_io_time_seconds_total{{cluster_id="{cluster_id}", job="node-exporter", instance=~"{ ip }:9100"}}[2m]) * 100)
        """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_pod_cpu_usage_range(cluster_id, namespace, pod_name_list, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    step = (end - start) // 60
    pod_name_list = "|".join(pod_name_list)

    porm_query = f"""
        sum by (pod_name) (rate(container_cpu_usage_seconds_total{{cluster_id="{cluster_id}", namespace=~"{ namespace }",
        pod_name=~"{ pod_name_list }", container_name!="", container_name!="POD"}}[1m])) * 100
        """  # noqa
    resp = query_range(porm_query, start, end, step)

    return resp.get("data") or {}


def get_pod_memory_usage_range(cluster_id, namespace, pod_name_list, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    step = (end - start) // 60
    pod_name_list = "|".join(pod_name_list)

    porm_query = f"""
        sum by (pod_name) (container_memory_rss{{cluster_id="{cluster_id}", namespace=~"{ namespace }", pod_name=~"{ pod_name_list }",
        container_name!="", container_name!="POD"}})
        """  # noqa
    resp = query_range(porm_query, start, end, step)

    return resp.get("data") or {}


def get_pod_network_receive(cluster_id, namespace, pod_name_list, start, end):
    """获取网络数据
    start, end单位为毫秒，和数据平台保持一致
    """
    step = (end - start) // 60
    pod_name_list = "|".join(pod_name_list)

    prom_query = f"""
        sum by(pod_name) (rate(container_network_receive_bytes_total{{cluster_id="{cluster_id}", namespace=~"{ namespace }", pod_name=~"{ pod_name_list }"}}[1m]))
        """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_pod_network_transmit(cluster_id, namespace, pod_name_list, start, end):
    step = (end - start) // 60
    pod_name_list = "|".join(pod_name_list)

    prom_query = f"""
        sum by(pod_name) (rate(container_network_transmit_bytes_total{{cluster_id="{cluster_id}",  namespace=~"{ namespace }", pod_name=~"{ pod_name_list }"}}[1m]))
        """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_container_cpu_usage_range(cluster_id, namespace, pod_name, container_id_list, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    step = (end - start) // 60
    container_id_list = "|".join(f".*{i}.*" for i in container_id_list)

    prom_query = f"""
        sum by(container_name) (rate(container_cpu_usage_seconds_total{{cluster_id="{cluster_id}", namespace=~"{ namespace }", pod_name=~"{pod_name}",
        container_name!="", container_name!="POD", BcsNetworkContainer!="true", id=~"{ container_id_list }"}}[1m])) * 100
        """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_container_cpu_limit(cluster_id, namespace, pod_name, container_id_list):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """

    container_id_list = "|".join(f".*{i}.*" for i in container_id_list)

    prom_query = f"""
        max by(container_name) (container_spec_cpu_quota{{cluster_id="{cluster_id}", namespace=~"{ namespace }", pod_name=~"{pod_name}",
        container_name!="", container_name!="POD", BcsNetworkContainer!="true", id=~"{ container_id_list }"}})
        """  # noqa

    resp = query(prom_query)
    return resp.get("data") or {}


def get_container_memory_usage_range(cluster_id, namespace, pod_name, container_id_list, start, end):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """
    step = (end - start) // 60
    container_id_list = "|".join(f".*{i}.*" for i in container_id_list)

    prom_query = f"""
        sum by(container_name) (container_memory_rss{{cluster_id="{cluster_id}", namespace=~"{ namespace }",pod_name=~"{pod_name}",
        container_name!="", container_name!="POD", BcsNetworkContainer!="true", id=~"{ container_id_list }"}})
        """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_container_memory_limit(cluster_id, namespace, pod_name, container_id_list):
    """获取CPU总使用率
    start, end单位为毫秒，和数据平台保持一致
    """

    container_id_list = "|".join(f".*{i}.*" for i in container_id_list)

    prom_query = f"""
        max by(container_name) (container_spec_memory_limit_bytes{{cluster_id="{cluster_id}", namespace=~"{ namespace }", pod_name=~"{pod_name}",
        container_name!="", container_name!="POD", BcsNetworkContainer!="true", id=~"{ container_id_list }"}}) > 0
        """  # noqa

    resp = query(prom_query)
    return resp.get("data") or {}


def get_container_disk_read(cluster_id, namespace, pod_name, container_id_list, start, end):
    step = (end - start) // 60
    container_id_list = "|".join(f".*{i}.*" for i in container_id_list)

    prom_query = f"""
        sum by(container_name) (container_fs_reads_bytes_total{{cluster_id="{cluster_id}", namespace=~"{ namespace }", pod_name=~"{pod_name}",
        container_name!="", container_name!="POD", BcsNetworkContainer!="true", id=~"{container_id_list}"}})
        """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}


def get_container_disk_write(cluster_id, namespace, pod_name, container_id_list, start, end):
    step = (end - start) // 60
    container_id_list = "|".join(f".*{i}.*" for i in container_id_list)

    prom_query = f"""
        sum by(container_name) (container_fs_writes_bytes_total{{cluster_id="{cluster_id}", namespace=~"{ namespace }", pod_name=~"{pod_name}",
        container_name!="", container_name!="POD", BcsNetworkContainer!="true", id=~"{container_id_list}"}})
        """  # noqa

    resp = query_range(prom_query, start, end, step)
    return resp.get("data") or {}
