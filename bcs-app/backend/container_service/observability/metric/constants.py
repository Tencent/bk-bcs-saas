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
import re

from backend.components.prometheus import (
    get_cluster_cpu_usage,
    get_cluster_disk_usage,
    get_cluster_memory_usage,
    get_node_cpu_usage,
    get_node_disk_usage,
    get_node_diskio_usage,
    get_node_memory_usage,
)
from backend.packages.blue_krill.data_types.enum import EnumField, StructuredEnum

# 没有指定时间范围的情况下，默认获取一小时的数据
METRICS_DEFAULT_TIMEDELTA = 3600

# 默认查询的命名空间（所有）
METRICS_DEFAULT_NAMESPACE = '.*'

# 默认查询 POD 下所有的容器
METRICS_DEFAULT_CONTAINER_LIST = ['.*']


class MetricDimension(str, StructuredEnum):
    """ 指标维度 """

    CpuUsage = EnumField('cpu_usage', label='CPU 使用率')
    MemoryUsage = EnumField('memory_usage', label='内存使用率')
    DiskUsage = EnumField('disk_usage', label='磁盘使用率')
    DiskIOUsage = EnumField('diskio_usage', label='磁盘 IO 使用率')


# 节点各指标维度获取方法
NODE_DIMENSIONS_FUNC = {
    MetricDimension.CpuUsage: get_node_cpu_usage,
    MetricDimension.MemoryUsage: get_node_memory_usage,
    MetricDimension.DiskUsage: get_node_disk_usage,
    MetricDimension.DiskIOUsage: get_node_diskio_usage,
}

# 集群各指标维度获取方法
CLUSTER_DIMENSIONS_FUNC = {
    MetricDimension.CpuUsage: get_cluster_cpu_usage,
    MetricDimension.MemoryUsage: get_cluster_memory_usage,
    MetricDimension.DiskUsage: get_cluster_disk_usage,
}

# 节点普通指标
NODE_UNAME_METRIC = [
    'dockerVersion',
    'osVersion',  # from cadvisor
    'domainname',
    'machine',
    'nodename',
    'release',
    'sysname',
    'version',  # from node-exporter
]

# 节点使用率类指标
NODE_USAGE_METRIC = ['cpu_count', 'memory', 'disk']

# 需要被过滤的注解 匹配器
FILTERED_ANNOTATION_PATTERN = re.compile(r"__meta_kubernetes_\w+_annotation")

# Job 名称 匹配器
JOB_PATTERN = re.compile(r"^(?P<namespace>[\w-]+)/(?P<name>[\w-]+)/(?P<port_idx>\d+)$")


# Service 不返回给前端的字段
INNER_USE_SERVICE_METADATA_FIELDS = [
    "annotations",
    "selfLink",
    "uid",
    "resourceVersion",
    "initializers",
    "generation",
    "deletionTimestamp",
    "deletionGracePeriodSeconds",
    "clusterName",
]

# 不展示给前端的 Label（符合前缀的）
INNER_USE_LABEL_PREFIX = [
    'io_tencent_bcs_',
    'io.tencent.paas.',
    'io.tencent.bcs.',
    'io.tencent.bkdata.',
    'io.tencent.paas.',
]
