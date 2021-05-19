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

from backend.apis.views import BaseAPIViewSet
from backend.resources.deployment import Deployment


class DeploymentViewSet(BaseAPIViewSet):
    def list_by_namespace(self, request, project_id_or_code, cluster_id, namespace):
        # TODO 增加用户对层级资源project/cluster/namespace的权限校验
        deploy = Deployment(request.user.access_token, request.project.project_id, cluster_id, namespace)
        deployments = deploy.get_deployments_by_namespace()
        return Response(deployments)

    def list_pods_by_deployment(self, request, project_id_or_code, cluster_id, namespace, deploy_name):
        # TODO 增加用户对层级资源project/cluster/namespace的权限校验(由于粒度没有细化到Deployment)
        deploy = Deployment(request.user.access_token, request.project.project_id, cluster_id, namespace)
        pods = deploy.get_pods_by_deployment(deploy_name)
        return Response(pods)
