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

from backend.resources.custom_object import CustomResourceDefinition, get_custom_object_api
from backend.resources.utils.kube_client import get_dynamic_client

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
        dynamic_client = get_dynamic_client(request.user.token.access_token, project_id, cluster_id)
        crd_api = dynamic_client.resources.get_preferred_resource(kind="CustomResourceDefinition")
        crd = crd_api.get(name=crd_name)
        cobj_api = dynamic_client.resources.get(kind=crd.spec.names.kind)

        query_ns = request.query_params.get("namespace")
        if query_ns:
            cobjs = cobj_api.get(namespace=query_ns)
        else:
            cobjs = cobj_api.get()

        return Response(to_table_format(crd, cobjs, cluster_id=cluster_id))

    def get_custom_object(self, request, project_id, cluster_id, crd_name, name):
        cobj_api = get_custom_object_api(request.user.token.access_token, project_id, cluster_id, crd_name)
        query_ns = request.query_params.get("namespace")
        if query_ns:
            cobj = cobj_api.get(namespace=query_ns, name=name)
        else:
            cobj = cobj_api.get(name=name)
        return Response(cobj)

    def patch_custom_object(self, request, project_id, cluster_id, crd_name, name):
        serializer = PatchCustomObjectSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        cobj_api = get_custom_object_api(request.user.token.access_token, project_id, cluster_id, crd_name)
        namespace = validated_data.get("namespace")

        if namespace:
            cobj_api.patch(namespace=namespace, name=name, body=validated_data["body"])
        else:
            cobj_api.patch(name=name, body=validated_data["body"])

        return Response()

    def patch_custom_object_scale(self, request, project_id, cluster_id, crd_name, name):
        req_data = request.data.copy()
        req_data["crd_name"] = crd_name
        serializer = PatchCustomObjectScaleSLZ(data=req_data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        cobj_api = get_custom_object_api(request.user.token.access_token, project_id, cluster_id, crd_name)
        # TODO 支持 cluster scope 的 custom object 扩缩容
        cobj_api.patch(name=name, namespace=validated_data["namespace"], body=validated_data["body"])

        return Response()

    def delete_custom_object(self, request, project_id, cluster_id, crd_name, name):
        cobj_api = get_custom_object_api(request.user.token.access_token, project_id, cluster_id, crd_name)
        namespace = request.query_params.get("namespace")
        if namespace:
            cobj_api.delete_ignore_nonexistent(namespace=namespace, name=name)
        else:
            cobj_api.delete_ignore_nonexistent(name=name)
        return Response()
