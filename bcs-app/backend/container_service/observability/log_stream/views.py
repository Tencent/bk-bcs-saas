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
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.resources.pod.constants import LogFilter
from backend.resources.pod.log import LogClient

from . import constants, serializers, utils

logger = logging.getLogger(__name__)


class LogStreamViewSet(SystemViewSet):
    """k8s 原生日志流"""

    def fetch(self, request, project_id: str, cluster_id: str, namespace: str, pod: str):
        """获取日志"""
        data = self.params_validate(serializers.FetchLogsSLZ)

        filter = LogFilter(container_name=data["container_name"], previous=data["previous"])
        if data["started_at"] and data['finished_at']:
            filter.since_time = utils.calc_since_time(data["started_at"], data['finished_at'])
        else:
            filter.tail_lines = data["tail_lines"]

        client = LogClient(request.ctx_cluster, namespace, pod)
        content = client.fetch_log(filter)
        logs = utils.refine_k8s_logs(content, data['started_at'])

        url_prefix = f"{settings.DEVOPS_BCS_API_URL}/api/logs/projects/{project_id}/clusters/{cluster_id}/namespaces/{namespace}/pods/{pod}/stdlogs/"  # noqa
        previous = utils.calc_previous_page(logs, data, url_prefix)

        result = {"logs": logs, "previous": previous}
        return Response(result)

    def download(self, request, project_id: str, cluster_id: str, namespace: str, pod: str):
        """下载日志"""
        data = self.params_validate(serializers.DownloadLogsSLZ)

        filter = LogFilter(
            container_name=data["container_name"], previous=data["previous"], tail_lines=constants.DEFAULT_TAIL_LINES
        )

        client = LogClient(request.ctx_cluster, namespace, pod)
        content = client.fetch_log(filter)

        ts = timezone.now().strftime("%Y%m%d%H%M%S")
        filename = f"{pod}-{data['container_name']}-{ts}.log"
        response = HttpResponse(content=content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
