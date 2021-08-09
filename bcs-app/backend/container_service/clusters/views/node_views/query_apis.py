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
from io import BytesIO

from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer

from backend.components import paas_cc
from backend.container_service.clusters import constants as node_constants
from backend.container_service.clusters import serializers as node_serializers
from backend.container_service.clusters.base import utils as node_utils
from backend.container_service.clusters.models import NodeLabel, NodeStatus
from backend.container_service.clusters.views.node_views import serializers as node_slz
from backend.container_service.projects.base.constants import ProjectKind
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

from .utils import get_label_querier


class QueryNodeBase:
    pass


class QueryNodeLabelKeys(QueryNodeBase, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_queryset(self, project_id, cluster_id):
        """filter the labels record"""
        labels_queryset = NodeLabel.objects.filter(project_id=project_id)
        if cluster_id != node_constants.PROJECT_ALL_CLUSTER:
            labels_queryset = labels_queryset.filter(cluster_id=cluster_id)
        return labels_queryset

    def compose_data(self, labels_queryset, key_name=None):
        """compose the label keys or values"""
        data = set([])
        for info in labels_queryset:
            labels = info.node_labels
            if not key_name:
                data.update(set(labels.keys()))
            elif key_name in labels:
                data.add(labels[key_name])

        return data

    def label_keys(self, request, project_id):
        """get node label keys"""
        # cluster id may be 'all'
        slz = node_serializers.QueryLabelKeysSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        cluster_id = slz.validated_data['cluster_id']

        labels_queryset = self.get_queryset(project_id, cluster_id)
        keys = self.compose_data(labels_queryset)
        return response.Response(keys)

    def label_values(self, request, project_id):
        """get node label values"""
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
        NodeStatus.RemoveFailed: "RemoveFailed",
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
            content=buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        # add username in filename
        response['Content-Disposition'] = f'attachment; filename=export-node-{request.user.username}.xlsx'

        return response


class ListNodelabelsViewSets(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def query_mesos_node_labels(self, access_token, project_id, data):
        node_labels = node_utils.query_mesos_node_labels(access_token, project_id, data)
        return node_labels.values()

    def query_k8s_node_labels(self, access_token, project_id, data):
        pass

    def list_labels_details(self, request, project_id):
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
            request.user.token.access_token, project_id, cluster_nodes
        )

        return response.Response(labels)


class QueryNodeLabelsViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def query_labels(self, request, project_id):
        """查询节点下的labels
        NOTE: 允许查询项目下所有集群中的节点的label
        """
        access_token = request.user.token.access_token
        cluster_id = request.query_params.get("cluster_id")
        if not cluster_id:
            clusters = node_utils.get_clusters(access_token, project_id)
            cluster_id_list = [cluster["cluster_id"] for cluster in clusters]
        else:
            cluster_id_list = [cluster_id]
        # 查询label对应的key-val
        querier = get_label_querier(request.project.kind, access_token, project_id)
        labels = querier.query_labels(cluster_id_list)

        return response.Response(labels)
