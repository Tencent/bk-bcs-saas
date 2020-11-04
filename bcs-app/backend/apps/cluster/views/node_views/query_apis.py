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
from io import BytesIO

from openpyxl import Workbook
from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from django.http import HttpResponse

from backend.accounts import bcs_perm
from backend.components import paas_cc
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer
from backend.resources.cluster import utils as node_utils
from backend.apps.cluster.utils import cluster_env_transfer
from backend.resources.project.constants import ProjectKind
from backend.apps.cluster import constants as node_constants
from backend.apps.cluster.models import NodeLabel, NodeStatus
from backend.apps.cluster import serializers as node_serializers
from backend.apps.cluster.views.node_views import serializers as node_slz


class QueryNodeBase:
    pass


class QueryNodeLabelKeys(QueryNodeBase, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_queryset(self, project_id, cluster_id):
        """filter the labels record
        """
        labels_queryset = NodeLabel.objects.filter(project_id=project_id)
        if cluster_id != node_constants.PROJECT_ALL_CLUSTER:
            labels_queryset = labels_queryset.filter(cluster_id=cluster_id)
        return labels_queryset

    def compose_data(self, labels_queryset, key_name=None):
        """compose the label keys or values
        """
        data = set([])
        for info in labels_queryset:
            labels = info.node_labels
            if not key_name:
                data.update(set(labels.keys()))
            elif key_name in labels:
                data.add(labels[key_name])

        return data

    def label_keys(self, request, project_id):
        """get node label keys
        """
        # cluster id may be 'all'
        slz = node_serializers.QueryLabelKeysSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        cluster_id = slz.validated_data['cluster_id']

        labels_queryset = self.get_queryset(project_id, cluster_id)
        keys = self.compose_data(labels_queryset)
        return response.Response(keys)

    def label_values(self, request, project_id):
        """get node label values
        """
        slz = node_serializers.QueryLabelValuesSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        labels_queryset = self.get_queryset(project_id, params['cluster_id'])
        values = self.compose_data(labels_queryset, key_name=params['key_name'])
        return response.Response(values)


class ExportNodes(viewsets.ViewSet):
    STATUS_MAP_NAME = {
        NodeStatus.Normal: "Ready",
        NodeStatus.ToRemoved: "SchedulingDisabled",
        NodeStatus.Removable: "SchedulingDisabled",
        NodeStatus.Initializing: "Initializing",
        NodeStatus.InitialFailed: "InitilFailed",
        NodeStatus.Removing: "Removing",
        NodeStatus.RemoveFailed: "RemoveFailed"
    }

    def get_nodes(self, request, project_id):
        req_data = request.data
        cluster_id = req_data.get("cluster_id")
        node_id_list = req_data.get("node_id_list")
        resp = paas_cc.get_node_list(request.user.token.access_token, project_id, cluster_id)
        if resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(f'get node error, {resp.get("message")}')
        data = resp.get('data') or {}
        results = data.get('results') or []
        node_data = []
        for node in results:
            if node["status"] == NodeStatus.Removed:
                continue
            if node_id_list and node["id"] not in node_id_list:
                continue
            node_data.append([node["cluster_id"], node["inner_ip"], self.STATUS_MAP_NAME.get(node["status"])])
        return node_data

    def export(self, request, project_id):
        # get node list
        nodes = self.get_nodes(request, project_id)
        # create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = 'nodes'
        # add sheet
        headers = ["Cluster ID", "Inner IP", "Status"]
        ws.append(headers)
        for node in nodes:
            ws.append(node)
        # output
        buffer = BytesIO()
        wb.save(buffer)
        response = HttpResponse(
            content=buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        # add username in filename
        response['Content-Disposition'] = f'attachment; filename=export-node-{request.user.username}.xlsx'

        return response


class ListNodelabelsViewSets(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def query_mesos_node_labels(self, access_token, project_id, data):
        node_labels = node_utils.query_mesos_node_labels(access_token, project_id, data)
        return node_labels.values()

    def query_k8s_node_labels(self):
        pass

    def list_labels(self, request, project_id):
        slz = node_slz.FilterNodeLabelsSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        cluster_nodes = {}
        for node in data["node_labels"]:
            if node["cluster_id"] in cluster_nodes:
                cluster_nodes[node["cluster_id"]].append(node["inner_ip"])
            else:
                cluster_nodes[node["cluster_id"]] = [node["inner_ip"]]

        # 查询节点labels
        project_kind_name = ProjectKind.get_choice_label(request.project.kind)
        labels = getattr(self, f"query_{project_kind_name.lower()}_node_labels")(
            request.user.token.access_token, project_id, cluster_nodes)

        return response.Response(labels)

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
                "cluster_name": cluster["name"]
            }
            for cluster in clusters
        }

    def compose_node_data(self, nodes, labels, cluster_id_map):
        """组装node数据，添加label、集群名称
        """
        for node in nodes:
            inner_ip = node["inner_ip"]
            cluster_id = node["cluster_id"]
            node["labels"] = labels.get(cluster_id, {}).get(inner_ip, [])
            node.update(cluster_id_map.get(cluster_id, {}))

    def list(self, request, project_id):
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
