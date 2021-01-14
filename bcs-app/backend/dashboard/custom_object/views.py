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
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer

from backend.utils.renderers import BKAPIRenderer
from backend.resources.custom_object import CustomResourceDefinition, get_custom_object_api_by_crd

from .serializers import PatchCustomObjectSLZ, PatchCustomObjectScaleSLZ
from .utils import to_table_format


class CRDViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id, cluster_id):
        crd_api = CustomResourceDefinition(request.user.token.access_token, project_id, cluster_id)
        return Response(crd_api.list(is_format=True))


class CustomObjectViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list_custom_objects(self, request, project_id, cluster_id, crd_name):
        # 指定api_version是因为当前to_table_format解析的是apiextensions.k8s.io/v1beta1版本的结构
        crd_api = CustomResourceDefinition(
            request.user.token.access_token, project_id, cluster_id, api_version="apiextensions.k8s.io/v1beta1"
        )
        crd_dict = crd_api.get(name=crd_name, is_format=True)

        cobj_api = get_custom_object_api_by_crd(request.user.token.access_token, project_id, cluster_id, crd_name)
        cobj_list = cobj_api.list(namespace=request.query_params.get("namespace"), is_format=True)

        return Response(to_table_format(crd_dict, cobj_list))

    def get_custom_object(self, request, project_id, cluster_id, crd_name, name):
        cobj_api = get_custom_object_api_by_crd(request.user.token.access_token, project_id, cluster_id, crd_name)
        cobj_dict = cobj_api.get(namespace=request.query_params.get("namespace"), name=name, is_format=True)
        return Response(cobj_dict)

    def patch_custom_object(self, request, project_id, cluster_id, crd_name, name):
        serializer = PatchCustomObjectSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        cobj_api = get_custom_object_api_by_crd(request.user.token.access_token, project_id, cluster_id, crd_name)
        cobj_api.patch(
            namespace=validated_data.get("namespace"),
            name=name,
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
        cobj_api = get_custom_object_api_by_crd(request.user.token.access_token, project_id, cluster_id, crd_name)
        cobj_api.patch(
            name=name,
            namespace=validated_data.get("namespace"),
            body=validated_data["body"],
            content_type=validated_data["patch_type"],
        )

        return Response()

    def delete_custom_object(self, request, project_id, cluster_id, crd_name, name):
        cobj_api = get_custom_object_api_by_crd(request.user.token.access_token, project_id, cluster_id, crd_name)
        cobj_api.delete_ignore_nonexistent(namespace=request.query_params.get("namespace"), name=name)
        return Response()
