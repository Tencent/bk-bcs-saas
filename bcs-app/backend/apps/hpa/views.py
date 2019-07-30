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
            cluster_id = cluster_info.get('cluster_id')
            cluster_env = cluster_info.get('environment')
            client = k8s.K8SClient(access_token, project_id, cluster_id, env=cluster_env)
            hpa = client.list_hpa().to_dict()['items']

            for _config in hpa:
                labels = _config.get('metadata', {}).get('labels') or {}
                # 获取模板集信息
                template_id = labels.get(instance_constants.LABLE_TEMPLATE_ID)
                # 资源来源
                source_type = labels.get(instance_constants.SOURCE_TYPE_LABEL_KEY)
                if not source_type:
                    source_type = "template" if template_id else "other"

                annotations = _config.get('metadata', {}).get('annotations') or {}

                data = {
                    'cluster_name': cluster_info['name'],
                    'cluster_id': cluster_id,
                    'name': _config['metadata']['name'],
                    'namespace': _config['metadata']['namespace'],
                    'max_replicas': _config['spec']['max_replicas'],
                    'min_replicas': _config['spec']['min_replicas'],
                    'current_replicas': _config['status']['current_replicas'],
                    'current_metrics_display': utils.get_current_metrics_display(_config),
                    'current_metrics': utils.get_current_metrics(_config),
                    'source_type': application_constants.SOURCE_TYPE_MAP.get(source_type),
                    'creator': annotations.get(instance_constants.ANNOTATIONS_CREATOR, ''),
                    'create_time': annotations.get(instance_constants.ANNOTATIONS_CREATE_TIME, ''),
                }

                data['update_time'] = annotations.get(instance_constants.ANNOTATIONS_UPDATE_TIME, data['create_time'])
                data['updator'] = annotations.get(instance_constants.ANNOTATIONS_UPDATOR, data['creator'])
                k8s_hpa_list.append(data)

        return Response(k8s_hpa_list)


class HPAMetrics(views.APIView):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get(self, request, project_id):
        """获取支持的HPA metric列表
        """
        return Response(constants.HPA_METRICS)
