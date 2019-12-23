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
from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer

from .base import Nodes, ClusterPerm
from backend.utils.renderers import BKAPIRenderer
from backend.utils.error_codes import error_codes
from backend.apps.cluster.models import CommonStatus
from backend.apps.cluster import serializers as node_serializers

NotReadyNodeStatus = ['not_ready', CommonStatus.DeleteFailed]


class DeleteNotReadyNode(Nodes, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def delete(self, request, project_id, cluster_id, node_id):
        access_token = request.user.token.access_token
        node_info = self.get_node_by_id(access_token, project_id, cluster_id, node_id)
        # check node allow operation
        if node_info.get('status') not in NotReadyNodeStatus:
            raise error_codes.CheckFailed(
                'current node does not allow delete operation, please check node status!')
        # set current node status is removed
        self.update_nodes_in_cluster(
            access_token, project_id, cluster_id, [node_info['inner_ip']], CommonStatus.Removed)

        return response.Response()


class BatchReinstallNodes(ClusterPerm, Nodes, viewsets.viewsets):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_cluster_nodes(self, request, project_id, cluster_id):
        node_list = self.get_node_list(request, project_id, cluster_id)
        return {info['id']: info['inner_ip'] for info in node_list}

    def get_initial_failed_status_list(self):
        pass

    def validated_nodes(self, cluster_nodes, id_list):
        not_exist_node = set(id_list) - set(cluster_nodes.keys())
        if not_exist_node:
            pass

    def reinstall_nodes(self, request, project_id, cluster_id):
        """当初始化失败时，允许用户批量重装
        1. 检测节点必须为当前项目下的同一集群
        2. 检测节点状态必须为初始化失败状态
        3. 下发配置，并更改节点状态
        """
        # 校验集群的编辑权限
        self.can_edit_cluster(request, project_id, cluster_id)
        # 获取请求参数
        slz = node_serializers.BatchUpdateNodesSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        # req_data = slz.validated_data
        # 检测节点必须为当前项目下的同一集群
        # cluster_nodes = self.get_cluster_nodes(request, project_id, cluster_id)
