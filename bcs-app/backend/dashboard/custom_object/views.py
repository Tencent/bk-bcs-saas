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
from backend.resources.custom_object import CustomResourceDefinition, CustomObject

from .serializers import PatchCustomObjectSLZ, PatchCustomObjectScaleSLZ
from .utils import to_table_format


class CRDViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id, cluster_id):
        crd_client = CustomResourceDefinition(
            access_token=request.user.token.access_token, project_id=project_id, cluster_id=cluster_id,
        )
        crds = crd_client.list_custom_resource_definition()
        return Response([{"name": crd.metadata.name, "scope": crd.spec.scope} for crd in crds.items])


class CustomObjectViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list_custom_objects(self, request, project_id, cluster_id, crd_name):
        crd_client = CustomResourceDefinition(
            access_token=request.user.token.access_token, project_id=project_id, cluster_id=cluster_id,
        )
        crd = crd_client.get_custom_resource_definition(crd_name)

        cobj_client = CustomObject(
            access_token=request.user.token.access_token,
            project_id=project_id,
            cluster_id=cluster_id,
            crd_name=crd_name,
        )
        query_ns = request.query_params.get("namespace")
        if query_ns:
            cobjs = cobj_client.list_namespaced_custom_object(query_ns)
        else:
            cobjs = cobj_client.list_cluster_custom_object()

        return Response(to_table_format(crd, cobjs, cluster_id=cluster_id))

    def get_custom_object(self, request, project_id, cluster_id, crd_name, name):
        cobj_client = CustomObject(
            access_token=request.user.token.access_token,
            project_id=project_id,
            cluster_id=cluster_id,
            crd_name=crd_name,
        )
        query_ns = request.query_params.get("namespace")
        if query_ns:
            cobj = cobj_client.get_namespaced_custom_object(query_ns, name)
        else:
            cobj = cobj_client.get_cluster_custom_object(name)
        return Response(cobj)

    def patch_custom_object(self, request, project_id, cluster_id, crd_name, name):
        serializer = PatchCustomObjectSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        cobj_client = CustomObject(
            access_token=request.user.token.access_token,
            project_id=project_id,
            cluster_id=cluster_id,
            crd_name=crd_name,
        )
        namespace = validated_data.get("namespace")

        if namespace:
            cobj_client.patch_namespaced_custom_object(namespace, name, validated_data["body"])
        else:
            cobj_client.patch_cluster_custom_object(name, validated_data["body"])

        return Response()

    def patch_custom_object_scale(self, request, project_id, cluster_id, crd_name, name):
        req_data = request.data.copy()
        req_data["crd_name"] = crd_name
        serializer = PatchCustomObjectScaleSLZ(data=req_data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        cobj_client = CustomObject(
            access_token=request.user.token.access_token,
            project_id=project_id,
            cluster_id=cluster_id,
            crd_name=crd_name,
        )
        # TODO 支持 cluster scope 的 custom object 扩缩容
        cobj_client.patch_namespaced_custom_object_scale(validated_data["namespace"], name, validated_data["body"])
        return Response()

    def delete_custom_object(self, request, project_id, cluster_id, crd_name, name):
        cobj_client = CustomObject(
            access_token=request.user.token.access_token,
            project_id=project_id,
            cluster_id=cluster_id,
            crd_name=crd_name,
        )
        namespace = request.query_params.get("namespace")
        if namespace:
            cobj_client.delete_namespaced_custom_object(namespace, name)
        else:
            cobj_client.delete_cluster_custom_object(name)
        return Response()
