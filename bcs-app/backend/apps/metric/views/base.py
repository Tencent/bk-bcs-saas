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
from backend.components import paas_cc


class MetricViewMixin:
    def get_node_ip_list(self, request, project_id, cluster_id):
        node_list = paas_cc.get_node_list(self.request.user.token.access_token, project_id, cluster_id)
        node_list = node_list.get("data", {}).get("results") or []
        node_ip_list = [i["inner_ip"] for i in node_list]
        return node_ip_list

    def get_node_ip_map(self, request, project_id, cluster_id):
        node_list = paas_cc.get_node_list(self.request.user.token.access_token, project_id, cluster_id)
        node_list = node_list.get("data", {}).get("results") or []
        node_ip_map = {i["inner_ip"]: i["id"] for i in node_list}
        return node_ip_map

    def get_validated_data(self, request):
        slz = self.serializer_class(data=request.GET)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        return data
