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
from dataclasses import dataclass, field
from typing import Dict, List, Union

from backend.components.bcs.mesos import MesosClient
from backend.container_service.clusters.base import CtxCluster
from backend.templatesets.legacy_apps.configuration.constants import MesosResourceName
from backend.utils.decorators import parse_response_data


@dataclass
class InstanceData:
    """Mesos 资源属性数据
    kind: 资源类型
    namespace: 命名空间名称
    name: 资源名称
    manifest: 资源的配置信息
    variables: 变量信息
    """

    kind: str
    namespace: str
    name: str
    manifest: dict = field(default_factory=dict)
    variables: dict = field(default_factory=dict)


class InstanceController:
    def __init__(self, ctx_cluster: CtxCluster, instance_data: InstanceData):
        self.ctx_cluster = ctx_cluster
        self.instance_data = instance_data

    def scale_resource(self):
        client = MesosClient(
            access_token=self.ctx_cluster.context.auth.access_token,
            project_id=self.ctx_cluster.project_id,
            cluster_id=self.ctx_cluster.id,
            env=None,
        )
        # 参数标识只更新应用的资源
        params = {"args": "resource"}
        if self.instance_data.kind == MesosResourceName.application.value:
            return self.update_application(client, params)
        return self.update_deployment(client, params)

    @parse_response_data()
    def update_application(self, client: MesosClient, params: Union[Dict]) -> Dict:
        return client.update_application(self.instance_data.namespace, self.instance_data.manifest, params=params)

    @parse_response_data()
    def update_deployment(self, client: MesosClient, params: Union[Dict]) -> Dict:
        return client.update_deployment(self.instance_data.namespace, self.instance_data.manifest, params=params)
