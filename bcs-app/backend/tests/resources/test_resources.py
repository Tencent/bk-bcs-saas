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
from backend.components.bcs.k8s import K8SClient
from backend.components.bcs.resources.namespace import Namespace


class TestNamespace:
    def test_get_namespace(self, cluster_id, testing_kubernetes_apiclient):
        namespace = Namespace(testing_kubernetes_apiclient)
        resp = namespace.get_namespace({'cluster_id': cluster_id})
        assert resp.get("code") == 0


class TestK8SClient:
    def test_normal(self, cluster_id, project_id, use_fake_k8sclient):
        client = K8SClient('token', project_id, cluster_id, None)
        client.get_namespace()
