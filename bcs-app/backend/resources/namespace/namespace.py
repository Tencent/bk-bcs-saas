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
from backend.resources.client import K8SClient

from . import utils


class Namespace(K8SClient):
    def get_namespace(self, name):
        # 假定cc中有，集群中也存在
        cc_namespaces = utils.get_namespaces_by_cluster_id(self.access_token, self.project_id, self.cluster_id)
        if not cc_namespaces:
            return {}

        for ns in cc_namespaces:
            if ns["name"] == name:
                return {"name": name, "namespace_id": ns["id"]}
        return {}

    def _create_namespace(self, name):
        return self.client.create_namespace({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": name}})

    def create_namespace(self, creator, name):
        # TODO 补充imagepullsecrets和命名空间变量的创建?
        # TODO 操作审计
        self._create_namespace(name)
        ns = utils.create_cc_namespace(self.access_token, self.project_id, self.cluster_id, name, creator)
        return {"name": name, "namespace_id": ns["id"]}
