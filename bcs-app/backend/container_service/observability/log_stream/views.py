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
from urllib import parse

import arrow
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.resources.pod.constants import LogFilter
from backend.resources.pod.log import LogClient

from . import constants, serializers

logger = logging.getLogger(__name__)


class LogStreamViewSet(SystemViewSet):
    """k8s 原生日志流"""

    def calc_previous_page(self, logs: list, slz_data: dict, previous_url: str):
        """计算上一页的请求链接"""
        if len(logs) < 2:
            return None

        previous_params = {
            "container_name": slz_data["container_name"],
            'previous': slz_data['previous'],
            "first_time": logs[0]['time'],
            "last_time": logs[-1]['time'],
        }
        previous = previous_url + "?" + parse.urlencode(previous_params)
        return previous

    def calc_since_time(self, first_time: str, last_time: str):
        """计算下一次的开始时间
        简单场景, 认为日志打印量是均衡的，通过计算时间差获取
        """
        _first_time = arrow.get(first_time)
        _last_time = arrow.get(last_time)
        span = _last_time - _first_time
        offset = _first_time - span
        # 返回纳秒级别时间
        new_since_time = offset.format("YYYY-MM-DDTHH:mm:ss.SSSSSSSSS") + "Z"
        return new_since_time

    def fetch(self, request, project_id: str, cluster_id: str, namespace: str, pod: str):
        """获取日志"""
        data = self.params_validate(serializers.FetchLogsSLZ)

        filter = LogFilter(container_name=data["container_name"], previous=data["previous"])

        if data["first_time"] and data['last_time']:
            filter.since_time = self.calc_since_time(data["first_time"], data['last_time'])
        else:
            filter.tail_lines = data["tail_lines"]

        client = LogClient(request.ctx_cluster, namespace, pod)

        content = client.fetch_log(filter)
        raw_logs = content.splitlines()
        logs = []
        for i in raw_logs:
            t, msg = i.split(maxsplit=1)
            # 只返回当前历史数据
            if data['first_time'] and t == data['first_time']:
                break
            logs.append({"time": t, "log": msg})

        previous_url = f"{settings.DEVOPS_BCS_API_URL}/api/logs/projects/{project_id}/clusters/{cluster_id}/namespaces/{namespace}/pods/{pod}/stdlogs/"  # noqa
        previous = self.calc_previous_page(logs, data, previous_url)

        data = {"logs": logs, "previous": previous}
        return Response(data)

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
