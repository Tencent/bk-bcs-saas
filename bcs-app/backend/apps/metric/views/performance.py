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

from backend.apps.cluster import serializers
from backend.components import paas_cc, prometheus
from backend.utils.renderers import BKAPIRenderer
from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer

logger = logging.getLogger(__name__)

class Cluster(viewsets.ViewSet):
    """集群相关metrics数据
    """
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_node_ip_list(self, request, project_id, cluster_id):
        node_list = paas_cc.get_node_list(self.request.user.token.access_token, project_id, cluster_id)
        node_list = node_list.get('data', {}).get('results') or []
        node_list = [i['inner_ip'] for i in node_list]
        return node_list

    def overview(self, request, project_id, cluster_id):
        node_list = self.get_node_ip_list(request, project_id, cluster_id)
        cpu = prometheus.get_cluster_cpu_usage(cluster_id, node_list)
        mem = prometheus.get_cluster_memory_usage(cluster_id, node_list)
        disk_usage = prometheus.get_cluster_disk_usage(cluster_id, node_list)
        data = {
            'cpu_usage': cpu,
            'mem': mem,
            'disk_usage': disk_usage
        }
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


class Node(viewsets.ViewSet):
    """节点相关Metrics
    """
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def overview(self, request, project_id, cluster_id):
        """节点列表快照数据
        """
        res_id = request.GET.get('res_id')
        cpu = prometheus.get_node_cpu_usage(cluster_id, res_id)
        mem = prometheus.get_node_memory_usage(cluster_id, res_id)
        diskio = prometheus.get_node_disk_io(cluster_id, res_id)
        data = {
            'mem': mem,
            'io': diskio,
            'cpu': cpu
        }
        return response.Response(data)

    def cpu_usage(self, request, project_id, cluster_id):
        slz = serializers.MetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_node_cpu_usage_range(cluster_id, data['res_id'], data['start_at'], data['end_at'])
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        slz = serializers.MetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_node_memory_usage_range(cluster_id, data['res_id'], data['start_at'], data['end_at'])
        return response.Response(result)

    def network_usage(self, request, project_id, cluster_id):
        slz = serializers.MetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_node_network_usage_range(cluster_id, data['res_id'], data['start_at'], data['end_at'])
        return response.Response(result)

    def diskio_usage(self, request, project_id, cluster_id):
        slz = serializers.MetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_node_cpu_usage_range(cluster_id, data['res_id'], data['start_at'], data['end_at'])
        return response.Response(result)

class Pod(viewsets.ViewSet):
    """Pod相关
    """
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def cpu_usage(self, request, project_id, cluster_id):
        slz = serializers.PromPodMetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_pod_cpu_usage_range(
            cluster_id, data['res_id_list'], data['start_at'], data['end_at'])
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        slz = serializers.PromPodMetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_pod_memory_usage_range(
            cluster_id, data['res_id_list'], data['start_at'], data['end_at'])
        return response.Response(result)


class Container(viewsets.ViewSet):
    """容器相关Metrics
    """
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def cpu_usage(self, request, project_id, cluster_id):
        slz = serializers.PromMetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_container_cpu_usage_range(
            cluster_id, data['res_id_list'], data['start_at'], data['end_at'])
        return response.Response(result)

    def memory_usage(self, request, project_id, cluster_id):
        slz = serializers.PromMetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_container_memory_usage_range(
            cluster_id, data['res_id_list'], data['start_at'], data['end_at'])
        return response.Response(result)

    def network_usage(self, request, project_id, cluster_id):
        slz = serializers.PromMetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_container_network_usage_range(
            cluster_id, data['res_id_list'][0], data['start_at'], data['end_at'])
        return response.Response(result)

    def diskio_usage(self, request, project_id, cluster_id):
        slz = serializers.PromMetricSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        result = prometheus.get_container_diskio_usage_range(
            cluster_id, data['res_id_list'][0], data['start_at'], data['end_at'])
        return response.Response(result)
