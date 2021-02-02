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
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.resources.custom_object import CustomResourceDefinition, get_cobj_client_by_crd
from backend.resources.utils.auths import ClusterAuth
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

from .serializers import PatchCustomObjectScaleSLZ, PatchCustomObjectSLZ
from .utils import to_table_format


class CRDViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id, cluster_id):
        crd_client = CustomResourceDefinition(ClusterAuth(request.user.token.access_token, project_id, cluster_id))
        return Response(crd_client.list())


class CustomObjectViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list_custom_objects(self, request, project_id, cluster_id, crd_name):
        cluster_auth = ClusterAuth(request.user.token.access_token, project_id, cluster_id)
        # 指定api_version是因为当前to_table_format解析的是apiextensions.k8s.io/v1beta1版本的结构
        crd_client = CustomResourceDefinition(
            cluster_auth,
            api_version="apiextensions.k8s.io/v1beta1",
        )
        crd = crd_client.get(name=crd_name, is_format=False)
        if not crd:
            raise error_codes.ResNotFoundError(_("集群({})中未注册自定义资源({})").format(cluster_id, crd_name))

        cobj_client = get_cobj_client_by_crd(cluster_auth, crd_name)
        cobj_list = cobj_client.list(namespace=request.query_params.get("namespace"))
        return Response(to_table_format(crd.to_dict(), cobj_list))

    def get_custom_object(self, request, project_id, cluster_id, crd_name, name):
        cobj_client = get_cobj_client_by_crd(
            ClusterAuth(request.user.token.access_token, project_id, cluster_id), crd_name
        )
        cobj_dict = cobj_client.get(namespace=request.query_params.get("namespace"), name=name)
        return Response(cobj_dict)

    def patch_custom_object(self, request, project_id, cluster_id, crd_name, name):
        serializer = PatchCustomObjectSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        cobj_client = get_cobj_client_by_crd(
            ClusterAuth(request.user.token.access_token, project_id, cluster_id), crd_name
        )
        cobj_client.patch(
            name=name,
            namespace=validated_data.get("namespace"),
            body=validated_data["body"],
            content_type=validated_data["patch_type"],
        )

        return Response()

    def patch_custom_object_scale(self, request, project_id, cluster_id, crd_name, name):
        req_data = request.data.copy()
        req_data["crd_name"] = crd_name
        serializer = PatchCustomObjectScaleSLZ(data=req_data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        cobj_client = get_cobj_client_by_crd(
            ClusterAuth(request.user.token.access_token, project_id, cluster_id), crd_name
        )
        cobj_client.patch(
            name=name,
            namespace=validated_data.get("namespace"),
            body=validated_data["body"],
            content_type=validated_data["patch_type"],
        )

        return Response()

    def delete_custom_object(self, request, project_id, cluster_id, crd_name, name):
        cobj_client = get_cobj_client_by_crd(
            ClusterAuth(request.user.token.access_token, project_id, cluster_id), crd_name
        )
        cobj_client.delete_ignore_nonexistent(namespace=request.query_params.get("namespace"), name=name)
        return Response()
