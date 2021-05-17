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

from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.components.bcs import k8s
from backend.container_service.observability.logstream import serializers
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)

DEFAULT_PARAMS = {"timestamps": True}


class LogStream(viewsets.ViewSet):
    """k8s 原生日志流"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get(self, request, project_id: str, cluster_id: str, namespace: str, pod: str):
        """获取日志"""
        slz = serializers.GetLogStreamSLZ(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        params = {
            'container': data['container_name'],
            'tailLines': data['tail_lines'],
        }
        params.update(DEFAULT_PARAMS)

        access_token = request.user.token.access_token
        client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
        result = client.get_log_stream(namespace, pod, params)

        data1 = result.text.splitlines()
        data2 = []
        for i in data1:
            data2.append(i.split(maxsplit=1))
        data = {"log": data2}
        return Response(data)
