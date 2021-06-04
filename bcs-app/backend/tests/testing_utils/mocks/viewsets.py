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
from rest_framework import viewsets
from rest_framework.permissions import BasePermission
from rest_framework.renderers import BrowsableAPIRenderer

from backend.utils.renderers import BKAPIRenderer


class FakeProjectEnableBCS(BasePermission):
    """ 假的权限控制类，单元测试用 """

    def has_permission(self, request, view):
        self._set_ctx_project_cluster(request, view.kwargs.get('project_id', ''), view.kwargs.get('cluster_id', ''))
        return True

    def _set_ctx_project_cluster(self, request, project_id: str, cluster_id: str):
        from backend.container_service.clusters.base.models import CtxCluster
        from backend.container_service.projects.base.models import CtxProject

        access_token = 'access_token_for_test'
        request.ctx_project = CtxProject.create(token=access_token, id=project_id)
        if cluster_id:
            request.ctx_cluster = CtxCluster.create(token=access_token, id=cluster_id, project_id=project_id)
        else:
            request.ctx_cluster = None


class SimpleGenericMixin:
    """
    backend.bcs_web.viewsets.GenericMixin 精简版
    根据实际需要，挪相关方法用于单元测试 Mock
    """

    def params_validate(self, serializer, params=None):
        """
        检查参数是够符合序列化器定义的通用逻辑

        :param serializer: 序列化器
        :param params: 指定的参数
        :return: 校验的结果
        """
        # 获取 Django request 对象
        _request = self.request

        if params is None:
            if _request.method in ['GET']:
                params = _request.query_params
            else:
                params = _request.data

        # 参数校验，如不符合直接抛出异常
        slz = serializer(data=params)
        slz.is_valid(raise_exception=True)
        return slz.validated_data


class FakeSystemViewSet(SimpleGenericMixin, viewsets.ViewSet):
    """ 假的基类 ViewSet，单元测试用 """

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    # 替换掉原有的权限控制类
    permission_classes = (FakeProjectEnableBCS,)
