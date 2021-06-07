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
"""
bcs helm2部署的release，是通过 helm template 渲染成yaml，然后 kubectl apply 部署到集群内；
集群内没有存储helm的release，bcs 平台db中存储了对应的release信息；
因此，需要通过bcs db中获取release及对应的详情信息
"""
from typing import Dict, List

from backend.container_service.clusters.base.models import CtxCluster
from backend.helm.app.models import App


def list_releases(ctx_cluster: CtxCluster, namespace: str = None) -> List[Dict]:
    """通过db中获取release信息"""
    apps = App.objects.filter(project_id=ctx_cluster.project_id, cluster_id=ctx_cluster.id, enable_helm=False)
    if namespace:
        apps = apps.filter(namespace=namespace)
    # 字段转换
    releases = []
    for app in apps:
        item = {
            "name": app.name,
            "namespace": app.namespace,
            "first_deployed": app.created,
            "last_deployed": app.updated,
            "transitioning_action": app.transitioning_action,
            "transitioning_message": app.transitioning_message,
            "transitioning_on": app.transitioning_on,
            "transitioning_result": app.transitioning_result,
            "chart_metadata": {"name": app.chart.name, "version": app.version},
        }
        releases.append(item)
    return releases
