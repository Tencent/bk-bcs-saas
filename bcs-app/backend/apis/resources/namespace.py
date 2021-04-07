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

from backend.accounts import bcs_perm
from backend.apis.resources.serializers import CreateNamespaceParamsSLZ
from backend.apis.views import NoAccessTokenBaseAPIViewSet
from backend.apps.variable.models import NameSpaceVariable
from backend.resources.namespace import utils as ns_utils
from backend.resources.namespace.constants import K8S_PLAT_NAMESPACE, K8S_SYS_NAMESPACE
from backend.resources.project.constants import ProjectKind
from backend.utils.error_codes import error_codes


class NamespaceViewSet(NoAccessTokenBaseAPIViewSet):
    def list_by_cluster_id(self, request, project_id_or_code, cluster_id):
        namespaces = ns_utils.get_namespaces_by_cluster_id(
            request.user.token.access_token, request.project.project_id, cluster_id
        )
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

    def sync_namespaces(self, request, project_id_or_code, cluster_id):
        """同步集群下命名空间
        NOTE: 先仅处理k8s类型
        """
        project_id = request.project.project_id
        # 统一: 通过cc获取的数据，添加cc限制，区别于直接通过线上直接获取的命名空间
        cc_namespaces = ns_utils.get_namespaces_by_cluster_id(request.user.token.access_token, project_id, cluster_id)
        # 转换格式，方便其他系统使用
        cc_namespace_name_id = {info["name"]: info["id"] for info in cc_namespaces}
        # 获取线上的命名空间
        access_token = request.user.token.access_token
        namespaces = ns_utils.get_k8s_namespaces(access_token, project_id, cluster_id)
        # NOTE: 忽略k8s系统和平台自身的namespace
        namespace_name_list = [
            info["resourceName"]
            for info in namespaces
            if info["resourceName"] not in K8S_SYS_NAMESPACE and info["resourceName"] not in K8S_PLAT_NAMESPACE
        ]
        if not (cc_namespaces and namespaces):
            return Response()
        # 根据namespace和realtime namespace进行删除或创建
        # 删除命名空间
        delete_ns_name_list = set(cc_namespace_name_id.keys()) - set(namespace_name_list)
        delete_ns_id_list = [cc_namespace_name_id[name] for name in delete_ns_name_list]
        self.delete_cc_ns(request, project_id, cluster_id, delete_ns_id_list)

        # 添加命名空间
        add_ns_name_list = set(namespace_name_list) - set(cc_namespace_name_id.keys())
        self.add_cc_ns(request, project_id, cluster_id, add_ns_name_list)

        return Response()

    def add_cc_ns(self, request, project_id, cluster_id, ns_name_list):
        access_token = request.user.token.access_token
        creator = request.user.token.access_token
        perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES, cluster_id)
        for ns_name in ns_name_list:
            data = ns_utils.create_cc_namespace(access_token, project_id, cluster_id, ns_name, creator)
            perm.register(data["id"], f"{ns_name}({cluster_id})")

    def delete_cc_ns(self, request, project_id, cluster_id, ns_id_list):
        """删除存储在CC中的namespace"""
        for ns_id in ns_id_list:
            perm = bcs_perm.Namespace(request, project_id, ns_id)
            perm.delete()
            ns_utils.delete_cc_namespace(request.user.token.access_token, project_id, cluster_id, ns_id)
