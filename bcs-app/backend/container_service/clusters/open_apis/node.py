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
from rest_framework.response import Response

from backend.bcs_web.apis.views import NoAccessTokenBaseAPIViewSet
from backend.container_service.clusters.base.utils import set_mesos_node_labels
from backend.container_service.clusters.open_apis.serializers import CreateNodeLabelsSLZ


class NodeLabelsViewSet(NoAccessTokenBaseAPIViewSet):
    def set_labels(self, request, project_id_or_code, cluster_id):
        slz = CreateNodeLabelsSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        project_id = request.project.project_id

        # 组装数据
        node_labels = data["node_labels"]
        for node_label in node_labels:
            labels = node_label.pop("labels", {})
            inner_ip = node_label.pop("inner_ip", "")
            node_label["strings"] = labels
            node_label["innerIP"] = inner_ip

        set_mesos_node_labels(request.user.token.access_token, project_id, {cluster_id: node_labels})

        return Response()
