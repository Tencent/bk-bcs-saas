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

from backend.bcs_web.viewsets import SystemViewSet
from backend.dashboard.custom_object_v2.constants import CRD_NAME_REGEX_EXP
from backend.dashboard.utils.resp import ListApiRespBuilder, RetrieveApiRespBuilder
from backend.resources.custom_object import CustomResourceDefinition


class CRDViewSet(SystemViewSet):
    """ 自定义资源定义 """

    lookup_field = 'crd_name'
    # 指定符合 CRD 名称规范的
    lookup_value_regex = CRD_NAME_REGEX_EXP

    def list(self, request, project_id, cluster_id):
        """ 获取所有自定义资源列表 """
        client = CustomResourceDefinition(request.ctx_cluster)
        response_data = ListApiRespBuilder(client).build()
        return Response(response_data)

    def retrieve(self, request, project_id, cluster_id, crd_name):
        """ 获取单个自定义资源详情 """
        client = CustomResourceDefinition(request.ctx_cluster)
        response_data = RetrieveApiRespBuilder(client, namespace=None, name=crd_name).build()
        return Response(response_data)


class CustomObjectViewSet(SystemViewSet):
    """ 自定义资源对象 """

    lookup_field = 'cus_obj_name'

    def list(self, request, project_id, cluster_id, crd_name):
        pass

    def retrieve(self, request, project_id, cluster_id, crd_name, cus_obj_name):
        pass

    def create(self, request, project_id, cluster_id, crd_name):
        pass

    def update(self, request, project_id, cluster_id, crd_name, cus_obj_name):
        pass

    def destroy(self, request, project_id, cluster_id, crd_name):
        pass
