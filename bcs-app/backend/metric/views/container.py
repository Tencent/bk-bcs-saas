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
from typing import Callable, Dict

from rest_framework.decorators import list_route
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.components.prometheus import (
    get_container_cpu_usage_range,
    get_container_disk_read,
    get_container_disk_write,
    get_container_memory_usage_range,
)
from backend.metric.constants import METRICS_DEFAULT_CONTAINER_LIST, METRICS_DEFAULT_NAMESPACE
from backend.metric.serializers import FetchContainerMetricSLZ


class ContainerMetricViewSet(SystemViewSet):

    serializer_class = FetchContainerMetricSLZ

    def _common_query_handler(self, query_metric_func: Callable, cluster_id: str, params: Dict) -> Dict:
        """
        查询容器指标通用逻辑

        :param query_metric_func: 指标查询方法
        :param cluster_id: 集群ID
        :param params: 接口请求参数
        :return: 指标查询结果
        """
        return query_metric_func(
            cluster_id,
            METRICS_DEFAULT_NAMESPACE,
            params['pod_name'],
            METRICS_DEFAULT_CONTAINER_LIST,
            params['start_at'],
            params['end_at'],
        )

    @list_route(methods=['GET'], url_path='cpu_usage')
    def cpu_usage(self, request, project_id, cluster_id):
        """ 获取指定 容器 CPU 使用情况 """
        params = self.params_validate(self.serializer_class)
        response_data = self._common_query_handler(get_container_cpu_usage_range, cluster_id, params)
        return Response(response_data)

    @list_route(methods=['GET'], url_path='memory_usage')
    def memory_usage(self, request, project_id, cluster_id):
        """ 获取 容器内存 使用情况 """
        params = self.params_validate(self.serializer_class)
        response_data = self._common_query_handler(get_container_memory_usage_range, cluster_id, params)
        return Response(response_data)

    @list_route(methods=['GET'], url_path='disk_read')
    def disk_read(self, request, project_id, cluster_id):
        """ 获取 磁盘读 情况 """
        params = self.params_validate(self.serializer_class)
        response_data = self._common_query_handler(get_container_disk_read, cluster_id, params)
        return Response(response_data)

    @list_route(methods=['GET'], url_path='disk_write')
    def disk_write(self, request, project_id, cluster_id):
        """ 获取 磁盘写 情况 """
        params = self.params_validate(self.serializer_class)
        response_data = self._common_query_handler(get_container_disk_write, cluster_id, params)
        return Response(response_data)
