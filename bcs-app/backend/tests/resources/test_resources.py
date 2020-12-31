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
from unittest import mock

from backend.components.bcs.k8s import K8SClient
from backend.components.bcs.resources.namespace import Namespace

from .conftest import TESTING_API_SERVER_URL


class TestNamespace:
    def test_get_namespace(self, cluster_id, testing_kubernetes_apiclient):
        namespace = Namespace(testing_kubernetes_apiclient)
        resp = namespace.get_namespace({'cluster_id': cluster_id})
        assert resp.get("code") == 0


class TestK8SClient:
    def test_normal(self, cluster_id, project_id):
        fake_cluster_info = {
            'id': cluster_id,
            'provider': 2,
            'creator_id': 100,
            'identifier': f'{cluster_id}-x',
            'created_at': '2020-0101T00:00:00',
        }
        fake_credentials = {
            'server_address_path': '',
            'user_token': 'fake_user_token',
        }
        with mock.patch(
            'backend.components.bcs.k8s_client.K8SAPIClient.query_cluster', return_value=fake_cluster_info
        ), mock.patch(
            'backend.components.bcs.k8s_client.K8SAPIClient.get_client_credentials', return_value=fake_credentials
        ), mock.patch(
            'backend.components.bcs.BCSClientBase._bcs_server_host',
            new_callable=mock.PropertyMock,
            return_value=TESTING_API_SERVER_URL,
        ):
            access_token = 'foo'
            client = K8SClient(access_token, project_id, cluster_id, None)
            client.get_namespace()
