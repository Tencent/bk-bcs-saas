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
import os
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from kubernetes import client
from rest_framework.test import APIClient

from backend.resources.project.constants import ProjectKind
from backend.tests.testing_utils.base import generate_random_string
from backend.utils import FancyDict

TESTING_API_SERVER_URL = os.environ.get("TESTING_API_SERVER_URL", 'http://localhost:28180')


@pytest.fixture
def cluster_id():
    """使用环境变量或者生成一个随机集群 ID"""
    return os.environ.get("TEST_CLUSTER_ID", generate_random_string(8))


@pytest.fixture
def project_id():
    """使用环境变量或者生成一个随机项目 ID"""
    return os.environ.get("TEST_PROJECT_ID", generate_random_string(32))


@pytest.fixture
def request_user():
    return FancyDict({"username": "admin", "token": FancyDict({"access_token": "test_access_token"})})


@pytest.fixture
def random_name():
    """生成一个随机 name"""
    return generate_random_string(8)


@pytest.fixture
def bk_user():
    User = get_user_model()
    user = User.objects.create(username=generate_random_string(6))

    # Set token attribute
    user.token = mock.MagicMock()
    user.token.access_token = generate_random_string(12)
    user.token.expires_soon = lambda: False

    user.project_kind = ProjectKind.K8S.value
    return user


@pytest.fixture
def api_client(request, bk_user):
    """Return an authenticated client"""
    client = APIClient()
    client.force_authenticate(user=bk_user)
    return client


@pytest.fixture
def testing_kubernetes_apiclient():
    """返回连接单元测试 apiserver 的 ApiClient 实例"""
    configuration = client.Configuration()
    configuration.api_key = {"authorization": f'Bearer {os.environ.get("TESTING_SERVER_API_KEY")}'}
    configuration.verify_ssl = False
    configuration.host = TESTING_API_SERVER_URL
    return client.ApiClient(configuration)


@pytest.fixture
def use_fake_k8sclient(cluster_id):
    """替换代码中所有的 k8s.K8SClient() 调用，使其连接用于测试的 apiserver"""
    fake_cluster_info = {
        'id': cluster_id,
        'provider': 2,
        'creator_id': 100,
        'identifier': f'{cluster_id}-x',
        'created_at': '2020-01-01T00:00:00',
    }
    fake_credentials = {'server_address_path': '', 'user_token': 'fake_user_token'}
    with mock.patch(
        'backend.components.bcs.k8s_client.K8SAPIClient.query_cluster', return_value=fake_cluster_info
    ), mock.patch(
        'backend.components.bcs.k8s_client.K8SAPIClient.get_client_credentials', return_value=fake_credentials
    ), mock.patch(
        'backend.components.bcs.BCSClientBase._bcs_server_host',
        new_callable=mock.PropertyMock,
        return_value=TESTING_API_SERVER_URL,
    ):
        yield
