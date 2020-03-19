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
import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import response, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import BrowsableAPIRenderer

from backend.apps.metric import serializers
from backend.apps.metric.views import base
from backend.components import prometheus
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)


class Cluster(base.MetricViewMixin, viewsets.ViewSet):
    """集群相关metrics数据
    """

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def overview(self, request, project_id, cluster_id):
        node_list = self.get_node_ip_list(request, project_id, cluster_id)
        cpu_usage = prometheus.get_cluster_cpu_usage(cluster_id, node_list)
        mem_usage = prometheus.get_cluster_memory_usage(cluster_id, node_list)
        disk_usage = prometheus.get_cluster_disk_usage(cluster_id, node_list)
        data = {"cpu_usage": cpu_usage, "mem_usage": mem_usage, "disk_usage": disk_usage}
        return response.Response(data)

    def cpu_usage(self, request, project_id, cluster_id):
        node_list = self.get_node_ip_list(request, project_id, cluster_id)
        result = prometheus.get_cluster_cpu_usage_range(cluster_id, node_list)
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        node_list = self.get_node_ip_list(request, project_id, cluster_id)
        result = prometheus.get_cluster_memory_usage_range(cluster_id, node_list)
        return response.Response(result)

    def disk_usage(self, request, project_id, cluster_id):
        node_list = self.get_node_ip_list(request, project_id, cluster_id)
        result = prometheus.get_cluster_disk_usage_range(cluster_id, node_list)
        return response.Response(result)


class Node(base.MetricViewMixin, viewsets.ViewSet):
    """节点相关Metrics
    """

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    serializer_class = serializers.PromMetricSLZ

    def overview(self, request, project_id, cluster_id):
        """节点列表快照数据
        """
        data = self.get_validated_data(request)
        ip = data["res_id"]

        cpu_usage = prometheus.get_node_cpu_usage(cluster_id, ip)
        memory_usage = prometheus.get_node_memory_usage(cluster_id, ip)
        disk_usage = prometheus.get_node_disk_usage(cluster_id, ip)
        diskio_usage = prometheus.get_node_diskio_usage(cluster_id, ip)
        data = {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "diskio_usage": diskio_usage,
        }
        return response.Response(data)

    def info(self, request, project_id, cluster_id):
        node_ip_map = self.get_node_ip_map(request, project_id, cluster_id)
        data = self.get_validated_data(request)

        if data["res_id"] not in node_ip_map:
            raise error_codes.ValidateError(_("IP地址不合法或不属于当前集群"))

        metric = {"provider": "Prometheus", "id": node_ip_map[data["res_id"]]}

        uname_metric = [
            "dockerVersion",
            "osVersion",  # from cadvisor
            "domainname",
            "machine",
            "nodename",
            "release",
            "sysname",
            "version",  # from node-exporter
        ]

        usage_metric = ["cpu_count", "memory", "disk"]

        for info in prometheus.get_node_info(cluster_id, data["res_id"]).get("result") or []:
            for k, v in info["metric"].items():
                if k in uname_metric:
                    metric[k] = v
                elif k == "metric_name" and v in usage_metric:
                    metric[v] = info["value"][1] if info["value"] else "0"

        return response.Response(metric)

    def cpu_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_node_cpu_usage_range(cluster_id, data["res_id"], data["start_at"], data["end_at"])
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_node_memory_usage_range(cluster_id, data["res_id"], data["start_at"], data["end_at"])
        return response.Response(result)

    def network_receive(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_node_network_receive(cluster_id, data["res_id"], data["start_at"], data["end_at"])
        return response.Response(result)

    def network_transmit(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_node_network_transmit(cluster_id, data["res_id"], data["start_at"], data["end_at"])
        return response.Response(result)

    def diskio_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_node_diskio_usage_range(cluster_id, data["res_id"], data["start_at"], data["end_at"])
        return response.Response(result)


class Pod(base.MetricViewMixin, viewsets.ViewSet):
    """Pod相关
    """

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    serializer_class = serializers.PromContainerMetricSLZ

    def cpu_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_pod_cpu_usage_range(cluster_id, data["res_id_list"], data["start_at"], data["end_at"])
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_pod_memory_usage_range(
            cluster_id, data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)

    def network_receive(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_pod_network_receive(cluster_id, data["res_id_list"], data["start_at"], data["end_at"])
        return response.Response(result)

    def network_transmit(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_pod_network_transmit(cluster_id, data["res_id_list"], data["start_at"], data["end_at"])
        return response.Response(result)


class Container(base.MetricViewMixin, viewsets.ViewSet):
    """容器相关Metrics
    """

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    serializer_class = serializers.PromContainerMetricSLZ

    def cpu_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_cpu_usage_range(
            cluster_id, data["pod_name"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)

    def cpu_limit(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_cpu_limit(cluster_id, data["pod_name"], data["res_id_list"])
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_memory_usage_range(
            cluster_id, data["pod_name"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)

    def memory_limit(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_memory_limit(cluster_id, data["pod_name"], data["res_id_list"])
        return response.Response(result)

    def disk_read(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_disk_read(
            cluster_id, data["pod_name"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)

    def disk_write(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_disk_write(
            cluster_id, data["pod_name"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)
