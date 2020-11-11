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
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer

from backend.utils.renderers import BKAPIRenderer
from backend.apps.network.views.lb import serializers as lb_slz
from backend.apps.network.models import MesosLoadBlance as MesosLoadBalancer

class LoadBalancersViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id):
        cluster_id = request.query_params.get("cluster_id")
        qs = MesosLoadBalancer.objects.filter(project_id=project_id)
        if cluster_id:
            qs = qs.filter(cluster_id=cluster_id)
        slz = lb_slz.MesosLBSLZ(qs, many=True)
        return Response(slz.data)

    def create(self, request, project_id):
        pass
