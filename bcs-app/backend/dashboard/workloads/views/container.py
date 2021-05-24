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

from rest_framework.decorators import action
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.dashboard.workloads.utils.resp import ContainerRespBuilder
from backend.resources.workloads.pod import Pod
from backend.web_console.api import exec_command

logger = logging.getLogger(__name__)


class ContainerViewSet(SystemViewSet):

    lookup_field = 'container_id'

    def list(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取 Pod 下所有的容器信息 """
        pod_manifest = Pod(request.ctx_cluster).fetch_manifest(namespace, pod_name)
        response_data = ContainerRespBuilder(pod_manifest).build_list()
        return Response(response_data)

    def retrieve(self, request, project_id, cluster_id, namespace, pod_name, container_id):
        """ 获取 Pod 下单个容器详细信息 """
        pod_manifest = Pod(request.ctx_cluster).fetch_manifest(namespace, pod_name)
        response_data = ContainerRespBuilder(pod_manifest, container_id).build()
        return Response(response_data)

    @action(methods=['GET'], url_path='env_info', detail=True)
    def env_info(self, request, project_id, cluster_id, namespace, pod_name, container_id):
        """ 获取 Pod 环境变量配置信息 """
        env_resp = exec_command(request.user.token.access_token, project_id, cluster_id, container_id, 'env')

        try:
            # docker 环境变量格式: key=val
            response_data = []
            for info in env_resp.splitlines():
                if not info:
                    continue
                partition_ret = info.partition('=')
                response_data.append({'name': partition_ret[0], 'value': partition_ret[2]})
        except Exception as e:
            # 若解析失败，仅保留错误信息，不抛出异常
            logger.error('解析容器环境变量失败: %s', e)
            response_data = []

        return Response(response_data)
