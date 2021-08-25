# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.utils.translation import ugettext_lazy as _
from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer

from backend.accounts import bcs_perm
from backend.bcs_web.audit_log import client
from backend.container_service.clusters import serializers as node_serializers
from backend.container_service.clusters.base import utils as node_utils
from backend.container_service.clusters.models import CommonStatus, NodeStatus
from backend.container_service.clusters.module_apis import get_cluster_node_mod
from backend.container_service.clusters.utils import cluster_env_transfer
from backend.container_service.clusters.views.node_views import serializers as node_slz
from backend.container_service.projects.base.constants import ProjectKind
from backend.iam.permissions.resources import ClusterPermCtx, ClusterPermission
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

from .base import ClusterPerm, Nodes

node = get_cluster_node_mod()


class DeleteNodeRecordViewSet(Nodes, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def delete(self, request, project_id, cluster_id, node_id):
        access_token = request.user.token.access_token
        node_info = self.get_node_by_id(access_token, project_id, cluster_id, node_id)
        # set current node status is removed
        self.update_nodes_in_cluster(
            access_token, project_id, cluster_id, [node_info['inner_ip']], CommonStatus.Removed
        )

        return response.Response()


class BatchReinstallNodes(ClusterPerm, Nodes, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    permission = ClusterPermission()

    def get_cluster_nodes(self, request, project_id, cluster_id):
        node_list = self.get_node_list(request, project_id, cluster_id)
        return {info['id']: info for info in node_list}

    def reinstall_nodes(self, request, project_id, cluster_id):
        """当初始化失败时，允许用户批量重装
        1. 检测节点必须为当前项目下的同一集群
        2. 检测节点状态必须为初始化失败状态
        3. 下发配置，并更改节点状态
        """
        # 权限校验
        perm_ctx = ClusterPermCtx(username=request.user.username, project_id=project_id, cluster_id=cluster_id)
        self.permission.can_manage(perm_ctx)

        # 获取集群下的节点
        cluster_nodes = self.get_cluster_nodes(request, project_id, cluster_id)
        # 获取请求参数
        slz = node_serializers.BatchReinstallNodesSLZ(data=request.data, context={'cluster_nodes': cluster_nodes})
        slz.is_valid(raise_exception=True)
        req_data = slz.validated_data
        # 获取集群信息
        cluster_info = self.get_cluster_info(request, project_id, cluster_id)
        # 获取节点IP
        node_id_ip_map = {id: cluster_nodes[id]['inner_ip'] for id in req_data['node_id_list']}
        # 下发继续初始化流程
        node_ip_list = node_id_ip_map.values()
        node_ips = ','.join(node_ip_list)
        with client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='node',
            resource=node_ips[:512],
            resource_id=','.join([str(id) for id in node_id_ip_map.keys()])[:256],
            description=_("集群: {}, batch reinstall nodes: {}").format(cluster_id, node_ips),
        ).log_modify():
            # 更改节点状态为初始化中
            self.update_nodes_in_cluster(
                request.user.token.access_token, project_id, cluster_id, node_ip_list, CommonStatus.Initializing
            )
            # 下发流程，触发重试任务
            node_client = node.BatchReinstallNodes(request, project_id, cluster_info, node_id_ip_map)
            node_client.reinstall()

        return response.Response()


class NodelabelsViewSets(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def set_mesos_node_labels(self, access_token, project_id, node_labels):
        # {"cluster_id": [{"inner_ip": ip1, "strings":{key: {"value": val}}}]}
        cluster_node_labels = {}
        for node_label in node_labels:
            cluster_id = node_label["cluster_id"]
            # 组装格式, 注意value必须为string
            item = {
                "strings": {key: {"value": str(val)} for label in node_label["labels"] for key, val in label.items()},
                "innerIP": node_label["inner_ip"],
            }
            if cluster_id in cluster_node_labels:
                cluster_node_labels[cluster_id].append(item)
            else:
                cluster_node_labels[cluster_id] = [item]

        node_utils.set_mesos_node_labels(access_token, project_id, cluster_node_labels)

    def set_k8s_node_labels(self, access_token, project_id, labels):
        pass

    def set_labels(self, request, project_id):
        slz = node_slz.SetNodeLabelsSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        project_kind_name = ProjectKind.get_choice_label(request.project.kind)
        getattr(self, f"set_{project_kind_name.lower()}_node_labels")(
            request.user.token.access_token, project_id, data["node_labels"]
        )

        return response.Response()

    def _mesos_node_labels(self, access_token, project_id, nodes):
        # 组装查询数据
        # 格式 {"cluster-id1": ["ip1", "ip2"], "cluster-id2": ["ip3", "ip4"]]
        # 节点ip为空时，查询所有节点的labels，避免每个IP匹配一次
        cluster_nodes = {node["cluster_id"]: [] for node in nodes}
        return node_utils.query_mesos_node_labels(access_token, project_id, cluster_nodes)

    def _cluster_id_map(self, access_token, project_id):
        clusters = node_utils.get_clusters(access_token, project_id)
        return {
            cluster["cluster_id"]: {
                "cluster_env": cluster_env_transfer(cluster["environment"]),
                "cluster_name": cluster["name"],
            }
            for cluster in clusters
        }

    def compose_node_data(self, nodes, labels, cluster_id_map):
        """组装node数据，添加label、集群名称"""
        for node_info in nodes:
            inner_ip = node_info["inner_ip"]
            cluster_id = node_info["cluster_id"]
            node_info["labels"] = labels.get(cluster_id, {}).get(inner_ip, [])
            node_info.update(cluster_id_map.get(cluster_id, {}))

    def list_labels(self, request, project_id):
        # TODO: 现阶段仅针对mesos
        if request.project.kind == ProjectKind.K8S.value:
            raise error_codes.NotOpen()

        access_token = request.user.token.access_token
        cluster_id = request.query_params.get("cluster_id")
        # cluster_id 为None时，查询项目下的所有集群的节点
        nodes = node_utils.get_cluster_nodes(access_token, project_id, cluster_id, raise_exception=False)
        # 排除状态为已删除的节点
        nodes = [node for node in nodes if node["status"] not in [NodeStatus.Removed]]
        project_kind_name = ProjectKind.get_choice_label(request.project.kind)
        labels = getattr(self, f"_{project_kind_name.lower()}_node_labels")(access_token, project_id, nodes)
        cluster_id_map = self._cluster_id_map(access_token, project_id)
        self.compose_node_data(nodes, labels, cluster_id_map)
        # 添加权限
        nodes_results = bcs_perm.Cluster.hook_perms(request, project_id, nodes)

        return response.Response({'count': len(nodes_results), 'results': nodes_results})
