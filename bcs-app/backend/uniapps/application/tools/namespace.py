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

from backend.components.base import ComponentAuth
from backend.components.paas_cc import PaaSCCClient
from backend.container_service.clusters.base import CtxCluster
from backend.utils.error_codes import error_codes


def get_namespace_id(ctx_cluster: CtxCluster, namespace: str) -> int:
    """通过集群ID+命名空间名称获取命名空间ID"""
    client = PaaSCCClient(ComponentAuth(ctx_cluster.context.auth.access_token))
    cluster_ns_data = client.get_cluster_namespace_list(project_id=ctx_cluster.project_id, cluster_id=ctx_cluster.id)
    for ns in cluster_ns_data.get("results") or []:
        if ns["name"] == namespace:
            return ns["id"]
    # TODO: 错误的返回是否需要规定下状态码
    raise error_codes.ResNotFoundError(_("集群:{}-命名空间:{}不存在").format(ctx_cluster.id, namespace))
