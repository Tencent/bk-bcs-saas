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
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.dashboard.utils.resp import ListApiRespBuilder, RetrieveApiRespBuilder


class ListAndRetrieveMixin:
    """ Dashboard 查看类接口通用逻辑 """

    def list(self, request, project_id, cluster_id, namespace=None):
        client = self.resource_client(request.ctx_cluster)
        response_data = ListApiRespBuilder(client).build()
        return Response(response_data)

    def retrieve(self, request, project_id, cluster_id, namespace, name):
        client = self.resource_client(request.ctx_cluster)
        response_data = RetrieveApiRespBuilder(client, namespace, name).build()
        return Response(response_data)


class DestroyMixin:
    """ Dashboard 删除类接口通用逻辑 """

    def destroy(self, request, project_id, cluster_id, namespace, name):
        client = self.resource_client(request.ctx_cluster)
        response_data = client.delete(name=name, namespace=namespace).to_dict()
        return Response(response_data)


class DashboardViewSet(ListAndRetrieveMixin, DestroyMixin, SystemViewSet):
    """
    资源视图通用 ViewSet，抽层一些通用方法
    """

    lookup_field = 'name'
