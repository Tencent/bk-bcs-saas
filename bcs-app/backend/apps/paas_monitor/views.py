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
import json
import logging

from rest_framework import views
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.apps.configuration.models import Template
from backend.apps.instance.models import InstanceConfig, VersionInstance
from backend.utils.authentication import JWTAuthentication
from backend.utils.renderers import BKAPIRenderer

logger = logging.getLogger(__name__)


class ControllerList(views.APIView):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    authentication_classes = (JWTAuthentication,)
    permission_classes = ()

    def get(self, request, project_id):
        """获取controller
        """
        # 先获取所有模板
        template_ids = Template.objects.filter(project_id=project_id).values_list('id', flat=True)
        # 所有实例ID
        instance_ids = VersionInstance.objects.filter(template_id__in=template_ids).values_list('id', flat=True)
        # 分组查询所有controller
        controllers = InstanceConfig.objects.filter(
            status="Running",
            instance_id__in=instance_ids,
        ).values('category', 'name', 'config')

        data = []

        for controller in controllers:
            try:
                config = json.loads(controller['config'])
                cluster_id = config['metadata']['labels']['io.tencent.bcs.clusterid']
                namespace = config['metadata']['labels']['io.tencent.bcs.namespace']

                data.append({
                    'name': controller['name'],
                    'category': controller['category'],
                    'cluster_id': cluster_id,
                    'namespace': namespace
                })
            except Exception as error:
                # 没有获取到，直接跳过
                logger.error('get controller list, %s, %s', error, controller)
                continue

        return Response(data)
