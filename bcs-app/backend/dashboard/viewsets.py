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
from kubernetes.dynamic.exceptions import DynamicApiError
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.dashboard.serializers import CreateResourceSLZ, ListResourceSLZ, UpdateResourceSLZ
from backend.dashboard.utils.resp import ListApiRespBuilder, RetrieveApiRespBuilder
from backend.utils.error_codes import error_codes


class ListAndRetrieveMixin:
    """ Dashboard 查看类接口通用逻辑 """

    def list(self, request, project_id, cluster_id, namespace=None):
        params = self.params_validate(ListResourceSLZ)
        client = self.resource_client(request.ctx_cluster)
        response_data = ListApiRespBuilder(client, namespace=namespace, **params).build()
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


class CreateMixin:
    """ Dashboard 创建类接口通用逻辑 """

    def create(self, request, project_id, cluster_id, namespace=None):
        params = self.params_validate(CreateResourceSLZ)
        client = self.resource_client(request.ctx_cluster)
        try:
            response_data = client.create(body=params, is_format=False).to_dict()
        except DynamicApiError as e:
            raise error_codes.APIError(e.summary())
        return Response(response_data)


class UpdateMixin:
    """ Dashboard 更新类接口通用逻辑 """

    def update(self, request, project_id, cluster_id, namespace, name):
        params = self.params_validate(UpdateResourceSLZ)
        client = self.resource_client(request.ctx_cluster)
        try:
            response_data = client.replace(body=params, namespace=namespace, name=name, is_format=False).to_dict()
        except DynamicApiError as e:
            raise error_codes.APIError(e.summary())
        return Response(response_data)


class DashboardViewSet(ListAndRetrieveMixin, DestroyMixin, CreateMixin, UpdateMixin, SystemViewSet):
    """
    资源视图通用 ViewSet，抽层一些通用方法
    """

    lookup_field = 'name'
