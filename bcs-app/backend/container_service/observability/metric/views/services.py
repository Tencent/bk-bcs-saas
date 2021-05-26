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
import logging

from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.apps.constants import ProjectKind
from backend.components.bcs import k8s, mesos
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)

# 不返回给前端的字段
FILTERED_METADATA = [
    "annotations",
    "selfLink",
    "uid",
    "resourceVersion",
    "initializers",
    "generation",
    "deletionTimestamp",
    "deletionGracePeriodSeconds",
    "clusterName",
]


class ServiceViewSet(viewsets.ViewSet):
    """可监控的services"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    filtered_label_prefix = [
        "io_tencent_bcs_",
        "io.tencent.paas.",
        "io.tencent.bcs.",
        "io.tencent.bkdata.",
        "io.tencent.paas.",
    ]

    def _filter_label(self, label_key):
        if label_key in ["io.tencent.bcs.controller.name"]:
            return True

        for prefix in self.filtered_label_prefix:
            if label_key.startswith(prefix):
                return False

        return True

    def _filter_service(self, service_list):
        for service in service_list:
            service["data"]["metadata"] = {
                k: v for k, v in service["data"]["metadata"].items() if k not in FILTERED_METADATA
            }

            labels = service["data"]["metadata"].get("labels")
            if not labels:
                continue

            service["data"]["metadata"]["labels"] = dict(
                sorted([(k, v) for k, v in labels.items() if self._filter_label(k)])
            )
        return service_list

    def list(self, request, project_id, cluster_id):
        """获取targets列表"""
        access_token = request.user.token.access_token

        if request.project.kind == ProjectKind.MESOS.value:
            client = mesos.MesosClient(access_token, project_id, cluster_id, env=None)
            resp = client.get_services({"env": "mesos"})
        else:
            client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
            resp = client.get_service({"env": "k8s"})

        data = self._filter_service(resp.get("data") or [])

        return Response(data)
