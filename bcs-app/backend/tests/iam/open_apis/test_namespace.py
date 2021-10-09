# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import mock
import pytest
from rest_framework.test import APIRequestFactory

from backend.iam.open_apis.views import ResourceAPIView
from backend.tests.testing_utils.mocks.paas_cc import StubPaaSCCClient

factory = APIRequestFactory()


@pytest.fixture(autouse=True)
def patch_paas_cc():
    with mock.patch('backend.iam.open_apis.provider.namespace.PaaSCCClient', new=StubPaaSCCClient):
        yield


class TestNamespaceAPI:
    def test_list_instance(self, project_id):
        request = factory.post(
            '/apis/iam/v1/namespaces/',
            {
                'method': 'list_instance',
                'type': 'namespace',
                'page': {'offset': 0, 'limit': 1},
                'filter': {'parent': {'id': project_id}},
            },
        )
        p_view = ResourceAPIView.as_view()
        response = p_view(request)
        data = response.data
        assert data['count'] == 1
        assert data['results'][0]['display_name'] == 'default'

    def test_fetch_instance_info(self, cluster_id):
        fetch_id = f'{cluster_id}:default'
        request = factory.post(
            '/apis/iam/v1/namespaces/',
            {
                'method': 'fetch_instance_info',
                'type': 'namespace',
                'filter': {'ids': [fetch_id], 'parent': {'id': cluster_id}},
            },
        )
        p_view = ResourceAPIView.as_view()
        response = p_view(request)
        data = response.data
        assert len(data) == 1
        assert data[0]['id'] == fetch_id
        assert data[0]['display_name'] == 'default'
