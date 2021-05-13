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
from backend.dashboard.utils.resp import DashboardListApiRespBuilder, DashboardRetrieveApiRespBuilder
from backend.resources.workloads.deployment import Deployment


class DeploymentViewSet(SystemViewSet):

    lookup_field = 'deployment_id'

    def list(self, request, project_id, cluster_id, namespace=None):
        client = Deployment(request.ctx_cluster)
        response_data = DashboardListApiRespBuilder(client).build()
        return Response(response_data)

    def retrieve(self, request, project_id, cluster_id, deployment_id):
        client = Deployment(request.ctx_cluster)
        response_data = DashboardRetrieveApiRespBuilder(client, deployment_id).build()
        return Response(response_data)
