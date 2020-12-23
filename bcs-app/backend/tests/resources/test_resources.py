# -*- coding: utf-8 -*-
from _pytest.config import Config
import pytest
from pprint import pprint
from unittest import mock
from backend.components.bcs.k8s import K8SClient
from backend.components.bcs.resources.namespace import Namespace

from backend.tests.testing_utils.base import generate_random_string

from kubernetes import client

# 由项目 dev_utils 启动的测试用 apiserver 服务
TESTING_API_SERVER_URL = 'http://localhost:28180'


@pytest.fixture
def cluster_id():
    """生成一个随机集群 ID"""
    return generate_random_string(8)


@pytest.fixture
def project_id():
    """生成一个随机项目 ID"""
    return generate_random_string(8)


@pytest.fixture
def testing_kubernetes_apiclient():
    """返回连接单元测试 apiserver 的 ApiClient 实例"""
    configuration = client.Configuration()
    configuration.verify_ssl = False
    configuration.host = TESTING_API_SERVER_URL
    return client.ApiClient(configuration)


class TestNamespace:
    def test_get_namespace(self, cluster_id, testing_kubernetes_apiclient):
        namespace = Namespace(testing_kubernetes_apiclient)
        namespace.get_namespace({'cluster_id': cluster_id})


class TestK8SClient:
    def test_normal(cluster_id, project_id):
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
