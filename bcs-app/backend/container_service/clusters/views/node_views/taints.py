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
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.container_service.clusters.tools import taint
from backend.utils.async_run import AsyncRunException
from backend.utils.error_codes import error_codes

from .serializers import NodeTaintListSLZ, QueryNodeListSLZ


class NodeTaintsViewSet(SystemViewSet):
    def query_taints(self, request, project_id, cluster_id):
        """查询node的污点"""
        params = self.params_validate(QueryNodeListSLZ)
        taints = taint.query_taints(request.ctx_cluster, params["node_name_list"])
        return Response(taints)

    def set_taints(self, request, project_id, cluster_id):
        """设置污点"""
        params = self.params_validate(NodeTaintListSLZ)
        try:
            taint.set_taints(request.ctx_cluster, params["node_taint_list"])
        except AsyncRunException as e:
            raise error_codes.APIError(_("节点设置污点失败，{}").format(str(e)))
        return Response()
