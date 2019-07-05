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

from backend.utils.renderers import BKAPIRenderer
from backend.apps.cluster.models import NodeLabel
from backend.apps.cluster import serializers as node_serializers
from backend.apps.cluster import constants as node_constants


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
