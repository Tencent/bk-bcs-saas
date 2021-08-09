# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from django.utils.translation import ugettext_lazy as _
from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer

from backend.components import prometheus
from backend.container_service.observability.metric_mesos import serializers
from backend.container_service.observability.metric_mesos.views import base
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)


class Cluster(base.MetricViewMixin, viewsets.ViewSet):
    """集群相关metrics数据"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def overview(self, request, project_id, cluster_id):
        node_list = self.get_node_ip_list(request, project_id, cluster_id)

        # 默认3个维度, 和老接口兼容
        dimensions = request.GET.get("dimensions")
        if not dimensions:
            dimensions = ["cpu_usage", "mem_usage", "disk_usage"]
        else:
            dimensions = dimensions.split(",")

        data = {}

        # 其他维度数据动态请求
        dimensions_func = {
            "cpu_usage": prometheus.get_cluster_cpu_usage,
            "mem_usage": prometheus.get_cluster_memory_usage,
            "disk_usage": prometheus.get_cluster_disk_usage,
            "mesos_memory_usage": prometheus.mesos_cluster_memory_usage,
            "mesos_cpu_usage": prometheus.mesos_cluster_cpu_usage,
        }

        for dimension in dimensions:
            if dimension not in dimensions_func:
                raise error_codes.APIError(_("dimension not valid"))

            func = dimensions_func[dimension]
            result = func(cluster_id, node_list)
            data[dimension] = result

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


class MesosCluster(base.MetricViewMixin, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    serializer_class = serializers.PromMetricSLZBase

    def mesos_cpu_resource_remain(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.mesos_cluster_cpu_resource_remain_range(cluster_id, data["start_at"], data["end_at"])
        return response.Response(result)

    def mesos_cpu_resource_total(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.mesos_cluster_cpu_resource_total_range(cluster_id, data["start_at"], data["end_at"])
        return response.Response(result)

    def mesos_memory_resource_remain(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.mesos_cluster_memory_resource_remain_range(cluster_id, data["start_at"], data["end_at"])
        return response.Response(result)

    def mesos_memory_resource_total(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.mesos_cluster_memory_resource_total_range(cluster_id, data["start_at"], data["end_at"])
        return response.Response(result)

    def mesos_cpu_resource_used(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.mesos_cluster_cpu_resource_used_range(cluster_id, data["start_at"], data["end_at"])
        return response.Response(result)

    def mesos_memory_resource_used(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.mesos_cluster_memory_resource_used_range(cluster_id, data["start_at"], data["end_at"])
        return response.Response(result)


class Node(base.MetricViewMixin, viewsets.ViewSet):
    """节点相关Metrics"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    serializer_class = serializers.PromMetricSLZ

    def overview(self, request, project_id, cluster_id):
        """节点列表快照数据"""
        data = self.get_validated_data(request)
        ip = data["res_id"]

        # 默认包含container_count, pod_count
        data = {
            "container_count": "0",
            "pod_count": "0",
        }

        container_pod_count = prometheus.get_container_pod_count(cluster_id, ip)
        for count in container_pod_count.get("result") or []:
            for k, v in count["metric"].items():
                if k == "metric_name" and count["value"]:
                    data[v] = count["value"][1]

        # 其他维度数据动态请求
        dimensions_func = {
            "cpu_usage": prometheus.get_node_cpu_usage,
            "memory_usage": prometheus.get_node_memory_usage,
            "disk_usage": prometheus.get_node_disk_usage,
            "diskio_usage": prometheus.get_node_diskio_usage,
            "mesos_memory_usage": prometheus.mesos_agent_memory_usage,
            "mesos_cpu_usage": prometheus.mesos_agent_cpu_usage,
            "mesos_ip_remain_count": prometheus.mesos_agent_ip_remain_count,
        }

        # 默认4个维度, 和老接口兼容
        dimensions = request.GET.get("dimensions")
        if not dimensions:
            dimensions = ["cpu_usage", "memory_usage", "disk_usage", "diskio_usage"]
        else:
            dimensions = dimensions.split(",")

        for dimension in dimensions:
            if dimension not in dimensions_func:
                raise error_codes.APIError(_("dimension not valid"))

            func = dimensions_func[dimension]
            result = func(cluster_id, ip)
            data[dimension] = result

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
    """Pod相关"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    serializer_class = serializers.PromContainerMetricSLZ

    def _update_result(self, result, res_id_map):
        """mesos转换pod_name"""
        if not res_id_map:
            return result

        _result = result.get("result") or []
        for i in _result:
            pod_name = i["metric"]["pod_name"]
            i["metric"]["pod_name"] = res_id_map.get(pod_name, pod_name)
        result["result"] = _result
        return result

    def cpu_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_pod_cpu_usage_range(
            cluster_id, data["namespace"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        result = self._update_result(result, data["res_id_map"])
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_pod_memory_usage_range(
            cluster_id, data["namespace"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        result = self._update_result(result, data["res_id_map"])
        return response.Response(result)

    def network_receive(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_pod_network_receive(
            cluster_id, data["namespace"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        result = self._update_result(result, data["res_id_map"])
        return response.Response(result)

    def network_transmit(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_pod_network_transmit(
            cluster_id, data["namespace"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        result = self._update_result(result, data["res_id_map"])
        return response.Response(result)


class Container(base.MetricViewMixin, viewsets.ViewSet):
    """容器相关Metrics"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    serializer_class = serializers.PromContainerMetricSLZ

    def cpu_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_cpu_usage_range(
            cluster_id, data["namespace"], data["pod_name"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)

    def cpu_limit(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_cpu_limit(
            cluster_id, data["namespace"], data["pod_name"], data["res_id_list"]
        )
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_memory_usage_range(
            cluster_id, data["namespace"], data["pod_name"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)

    def memory_limit(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_memory_limit(
            cluster_id, data["namespace"], data["pod_name"], data["res_id_list"]
        )
        return response.Response(result)

    def disk_read(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_disk_read(
            cluster_id, data["namespace"], data["pod_name"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)

    def disk_write(self, request, project_id, cluster_id):
        data = self.get_validated_data(request)
        result = prometheus.get_container_disk_write(
            cluster_id, data["namespace"], data["pod_name"], data["res_id_list"], data["start_at"], data["end_at"]
        )
        return response.Response(result)
