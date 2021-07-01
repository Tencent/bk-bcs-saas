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
from backend.container_service.clusters.tools import label
from backend.utils.async_run import AsyncRunException
from backend.utils.error_codes import error_codes

from .serializers import NodeLabelListSLZ, QueryNodeListSLZ


class NodeLabelsViewSet(SystemViewSet):
    def query_labels(self, request, project_id, cluster_id):
        """查询node的标签"""
        params = self.params_validate(QueryNodeListSLZ)
        taints = label.query_labels(request.ctx_cluster, params["node_name_list"])
        return Response(taints)

    def set_labels(self, request, project_id, cluster_id):
        """设置节点标签"""
        params = self.params_validate(NodeLabelListSLZ)
        try:
            label.set_labels(request.ctx_cluster, params["node_label_list"])
        except AsyncRunException as e:
            raise error_codes.APIError(_("节点设置标签失败，{}").format(str(e)))
        return Response()
