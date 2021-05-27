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
from typing import Dict

from rest_framework.decorators import action
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.dashboard.utils.resp import ListApiRespBuilder, RetrieveApiRespBuilder
from backend.dashboard.workloads.serializers import ListPodsSLZ
from backend.resources.configs.configmap import ConfigMap
from backend.resources.configs.secret import Secret
from backend.resources.storages.persistent_volume_claim import PersistentVolumeClaim
from backend.resources.workloads.pod import Pod


class PodViewSet(SystemViewSet):

    lookup_field = 'pod_name'

    def list(self, request, project_id, cluster_id, namespace=None):
        """ 获取 Pod 列表，支持 labelSelector """
        params = self.params_validate(ListPodsSLZ)
        client = Pod(request.ctx_cluster)
        response_data = ListApiRespBuilder(client, **params).build()
        return Response(response_data)

    def retrieve(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取单个 Pod 详细信息 """
        client = Pod(request.ctx_cluster)
        response_data = RetrieveApiRespBuilder(client, namespace, pod_name).build()
        return Response(response_data)

    @action(methods=['GET'], url_path='pvcs', detail=True)
    def persistent_volume_claims(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取 Pod Persistent Volume Claim 信息 """
        response_data = Pod(request.ctx_cluster).filter_related_resources(
            PersistentVolumeClaim(request.ctx_cluster), namespace, pod_name
        )
        return Response(response_data)

    @action(methods=['GET'], url_path='configmaps', detail=True)
    def configmaps(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取 Pod ConfigMap 信息 """
        response_data = Pod(request.ctx_cluster).filter_related_resources(
            ConfigMap(request.ctx_cluster), namespace, pod_name
        )
        return Response(response_data)

    @action(methods=['GET'], url_path='secrets', detail=True)
    def secrets(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取 Pod Secret 信息 """
        response_data = Pod(request.ctx_cluster).filter_related_resources(
            Secret(request.ctx_cluster), namespace, pod_name
        )
        return Response(response_data)
