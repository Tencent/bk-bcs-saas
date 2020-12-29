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
"""Test codes for backend.resources module"""
import pytest
from unittest import mock
from backend.resources.client import (
    BcsKubeAddressesProvider,
    BcsKubeConfigurationService,
)
from backend.utils.exceptions import ComponentError


@pytest.fixture(autouse=True)
def setup_settings(settings):
    """Setup required settings for unittests"""
    settings.BCS_API_ENV = {'stag': 'my_stag', 'prod': 'my_prod'}
    settings.BCS_SERVER_HOST = {
        'my_stag': 'https://my-stag-bcs-server.example.com',
        'my_prod': 'https://my-prod-bcs-server.example.com',
    }
    settings.BCS_API_PRE_URL = 'https://bcs-api.example.com'


fake_cc_get_cluster_result_ok = {'code': 0, 'result': True, 'data': {'environment': 'stag'}}
fake_cc_get_cluster_result_failed = {'code': 100, 'result': False}


class TestBcsKubeAddressesProvider:
    @mock.patch('backend.resources.client.paas_cc.get_cluster', return_value=fake_cc_get_cluster_result_ok)
    def test_normal(self, project_id, cluster_id):
        addresses = BcsKubeAddressesProvider('token', project_id, cluster_id)
        api_env_name = addresses._query_api_env_name()
        assert api_env_name == 'my_stag'
        assert addresses.get_api_base_url() == 'https://bcs-api.example.com/my_stag'
        assert addresses.get_clusters_base_url() == 'https://bcs-api.example.com/my_stag/rest/clusters'
        assert addresses.get_kube_apiservers_host() == 'https://my-stag-bcs-server.example.com'

    @mock.patch('backend.resources.client.paas_cc.get_cluster', return_value=fake_cc_get_cluster_result_failed)
    def test_failed(self, project_id, cluster_id):
        addresses = BcsKubeAddressesProvider('token', project_id, cluster_id)
        with pytest.raises(ComponentError):
            assert addresses.get_api_base_url()


class TestBcsKubeConfigurationService:
    @mock.patch('backend.resources.client.paas_cc.get_cluster', return_value=fake_cc_get_cluster_result_ok)
    def test_make_configuration(self, project_id, cluster_id):
        config_service = BcsKubeConfigurationService('token', project_id, cluster_id)

        with mock.patch('backend.resources.client.http_get') as http_get_mocker:
            http_get_mocker.side_effect = [
                {'id': '10000'},  # Query BKE Server ID
                {'server_address_path': '/foo', 'user_token': 'foo-token'},  # Query credentials
            ]
            config = config_service.make_configuration()

            assert http_get_mocker.call_count == 2
            assert (
                http_get_mocker.call_args[0][0]
                == 'https://bcs-api.example.com/my_stag/rest/clusters/10000/client_credentials'
            )
            assert config.host == 'https://my-stag-bcs-server.example.com/foo'
            assert config.api_key['authorization'] == 'Bearer foo-token'
