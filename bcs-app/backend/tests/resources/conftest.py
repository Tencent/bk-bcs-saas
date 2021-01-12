# -*- coding: utf-8 -*-
import pytest
from kubernetes import client

from backend.tests.testing_utils.base import generate_random_string

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
