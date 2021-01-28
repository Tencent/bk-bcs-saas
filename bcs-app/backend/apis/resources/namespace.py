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

from backend.apis.resources.serializers import CreateNamespaceParamsSLZ
from backend.apis.views import NoAccessTokenBaseAPIViewSet
from backend.apps.variable.models import NameSpaceVariable
from backend.resources.namespace import utils as ns_utils
from backend.resources.project.constants import ProjectKind
from backend.utils.error_codes import error_codes


class NamespaceViewSet(NoAccessTokenBaseAPIViewSet):
    def list_by_cluster_id(self, request, project_id, cluster_id):
        namespaces = ns_utils.get_namespaces_by_cluster_id(request.user.token.access_token, project_id, cluster_id)
        return Response(namespaces)

    def create_mesos_namespace(self, access_token, username, project_id, cluster_id, ns_name):
        """创建mesos命名空间
        注意: mesos中namespace只是一个概念，不是一个资源；因此，不需要在mesos集群创建
        """
        namespace = ns_utils.create_cc_namespace(access_token, project_id, cluster_id, ns_name, username)
        # TODO: 现阶段不向权限中心注入
        return namespace

    def create_k8s_namespace(self, access_token, username, project_id, cluster_id, ns_name):
        raise error_codes.NotOpen()

    def create_namespace(self, request, project_id_or_code, cluster_id):
        project_id = request.project.project_id
        slz = CreateNamespaceParamsSLZ(data=request.data, context={"project_id": project_id})
        slz.is_valid(raise_exception=True)
        data = slz.data

        access_token = request.user.token.access_token
        username = request.user.username
        project_id = request.project.project_id

        project_kind_name = ProjectKind.get_choice_label(request.project.kind)
        namespace = getattr(self, f"create_{project_kind_name.lower()}_namespace")(
            access_token, username, project_id, cluster_id, data["name"]
        )
        # 创建命名空间下的变量值
        ns_id = namespace["id"]
        NameSpaceVariable.batch_save(ns_id, data["variables"])
        namespace["variables"] = data["variables"]

        return Response(namespace)
