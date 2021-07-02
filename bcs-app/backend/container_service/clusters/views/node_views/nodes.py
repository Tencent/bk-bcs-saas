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
from backend.container_service.clusters.base.utils import get_cluster
from backend.container_service.clusters.tools import node


class NodeViewSets(SystemViewSet):
    def list_nodes(self, request, project_id, cluster_id):
        """查询集群下nodes
        NOTE: 限制查询一个集群下的节点
        """
        # 以集群中节点为初始数据，如果bcs cc中节点不在集群中，处于初始化中或者初始化失败，也需要展示
        cluster_nodes = node.query_cluster_nodes(request.ctx_cluster)
        bcs_cc_nodes = node.query_bcs_cc_nodes(request.ctx_cluster)
        # 组装数据
        cluster = get_cluster(request.user.token.access_token, request.project.project_id, cluster_id)
        client = node.NodesData(bcs_cc_nodes, cluster_nodes, cluster_id, cluster.get("name", ""))
        return Response(client.nodes())
