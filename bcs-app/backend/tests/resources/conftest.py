# -*- coding: utf-8 -*-
import os
import uuid
from unittest import mock

import pytest
from kubernetes import client

from backend.tests.conftest import TESTING_API_SERVER_URL
from backend.tests.testing_utils.mocks.collection import StubComponentCollection


class FakeBcsKubeConfigurationService:
    """Fake configuration service which return local apiserver as config"""

    def __init__(self, *args, **kwargs):
        pass

    def make_configuration(self):
        configuration = client.Configuration()
        configuration.api_key = {"authorization": f'Bearer {os.environ.get("TESTING_SERVER_API_KEY")}'}
        configuration.verify_ssl = False
        configuration.host = TESTING_API_SERVER_URL
        return configuration


@pytest.fixture(autouse=True)
def setup_fake_cluster_dependencies():
    # 替换所有 Comp 系统为测试专用的 Stub 系统；替换集群地址为测试用 API Server
    with mock.patch(
        'backend.container_service.core.ctx_models.ComponentCollection', new=StubComponentCollection
    ), mock.patch(
        'backend.resources.utils.kube_client.BcsKubeConfigurationService', new=FakeBcsKubeConfigurationService
    ):
        yield
