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
import datetime
import logging
from urllib import parse

import arrow
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.resources.pod import log

from . import constants, serializers

logger = logging.getLogger(__name__)


class LogStream(SystemViewSet):
    """k8s 原生日志流"""

    def calc_previous_page(self, logs, slz_data, previous_url):
        """计算上一页的请求链接
        简单场景, 认为日志打印量是均衡的，通过计算时间差获取
        """

        oldest = arrow.get(logs[0]["time"])
        if slz_data["span"]:
            span = datetime.timedelta(microseconds=slz_data["span"])
        else:
            latest = arrow.get(logs[-1]["time"])
            span = oldest - latest

        offset = oldest + span
        # 返回纳秒级别时间
        since_time = offset.format("YYYY-MM-DDTHH:mm:ss.SSSSSSSSS") + "Z"

        previous_params = {
            "container_name": slz_data["container_name"],
            "since_time": since_time,
            "span": span.microseconds,
            'previous': slz_data['previous'],
        }
        previous = previous_url + "?" + parse.urlencode(previous_params)
        return previous

    def fetch(self, request, project_id: str, cluster_id: str, namespace: str, pod: str):
        """获取日志"""
        data = self.params_validate(serializers.FetchLogsSLZ)

        params = {
            "container": data["container_name"],
            "previous": data["previous"],
        }

        if data["since_time"]:
            params["sinceTime"] = data["since_time"]
        else:
            params["tailLines"] = data["tail_lines"]

        client = log.Log(request.ctx_cluster, namespace, pod)

        content = client.fetch_log(params)
        raw_logs = content.splitlines()
        logs = []
        for i in raw_logs:
            t, msg = i.split(maxsplit=1)
            logs.append({"time": t, "log": msg})

        previous_url = f"{settings.DEVOPS_BCS_API_URL}/api/logstream/projects/{project_id}/clusters/{cluster_id}/namespaces/{namespace}/pods/{pod}/"  # noqa
        previous = self.calc_previous_page(logs, data, previous_url)

        data = {"logs": logs, "previous": previous}
        return Response(data)

    def download(self, request, project_id: str, cluster_id: str, namespace: str, pod: str):
        """下载日志"""
        data = self.params_validate(serializers.DownloadLogsSLZ)

        params = {
            "container": data["container_name"],
            "previous": data["previous"],
            "tailLines": constants.DEFAULT_TAIL_LINES,
        }

        client = log.Log(request.ctx_cluster, namespace, pod)

        content = client.fetch_log(params)

        ts = timezone.now().strftime("%Y%m%d%H%M%S")
        filename = f"{pod}-{data['container_name']}-{ts}.log"
        response = HttpResponse(content=content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
