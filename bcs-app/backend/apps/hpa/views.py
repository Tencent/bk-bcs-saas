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
from rest_framework import views
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.accounts import bcs_perm
from backend.apps.application.base_views import BaseAPI
from backend.components.bcs import k8s, paas_cc
from backend.utils.renderers import BKAPIRenderer
from backend.apps.instance import constants as instance_constants
from backend.apps.application import constants as application_constants
from backend.apps.hpa import utils
from backend.apps.hpa import constants

logger = logging.getLogger(__name__)

class HPA(viewsets.ViewSet, BaseAPI):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id):
        """获取所有HPA数据
        """
        cluster_dicts = self.get_project_cluster_info(request, project_id)
        cluster_data = cluster_dicts.get('results', {}) or {}
        access_token = request.user.token.access_token
        k8s_hpa_list = []

        for cluster_info in cluster_data:

            cluster_id = cluster_info['cluster_id']
            cluster_env = cluster_info.get('environment')
            cluster_name = cluster_info['name']
            hpa_list = utils.get_cluster_hpa_list(access_token, project_id, cluster_id, cluster_env, cluster_name)
            k8s_hpa_list.extend(hpa_list)

        return Response(k8s_hpa_list)

class HPAMetrics(views.APIView):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get(self, request, project_id):
        """获取支持的HPA metric列表
        """
        return Response(constants.HPA_METRICS)
