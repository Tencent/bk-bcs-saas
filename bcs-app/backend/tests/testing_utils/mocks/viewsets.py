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
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.permissions import BasePermission

from backend.utils.renderers import BKAPIRenderer


class FakeProjectEnableBCS(BasePermission):
    """ 假的权限控制类，单元测试用 """

    def has_permission(self, request, view):
        self._set_ctx_project_cluster(request, view.kwargs.get('project_id', ''), view.kwargs.get('cluster_id', ''))
        return True

    def _set_ctx_project_cluster(self, request, project_id: str, cluster_id: str):
        from backend.resources.cluster.models import CtxCluster
        from backend.resources.project.models import CtxProject
        access_token = 'access_token_for_test'
        request.ctx_project = CtxProject.create(token=access_token, id=project_id)
        if cluster_id:
            request.ctx_cluster = CtxCluster.create(token=access_token, id=cluster_id, project_id=project_id)
        else:
            request.ctx_cluster = None


class FakeSystemViewSet(viewsets.ViewSet):
    """ 假的基类 ViewSet，单元测试用 """
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    # 替换掉原有的权限控制类
    permission_classes = (FakeProjectEnableBCS, )
