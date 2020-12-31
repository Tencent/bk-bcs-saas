# -*- coding: utf-8 -*-
import os

import pytest
from kubernetes import client

from backend.tests.testing_utils.base import generate_random_string

TESTING_API_SERVER_URL = os.environ.get("TESTING_API_SERVER_URL", 'http://localhost:28180')


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
    configuration.api_key = {"authorization": f'Bearer {os.environ.get("api_key")}'}
    configuration.verify_ssl = False
    configuration.host = TESTING_API_SERVER_URL
    return client.ApiClient(configuration)
