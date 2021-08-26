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
from unittest.mock import patch

import pytest

from backend.container_service.clusters.base.models import CtxCluster
from backend.container_service.clusters.open_apis.namespace import NamespaceViewSet
from backend.resources.namespace import Namespace
from backend.tests.resources.conftest import FakeBcsKubeConfigurationService
from backend.tests.testing_utils.base import generate_random_string
from backend.tests.testing_utils.mocks import bcs_perm, paas_cc

fake_data = {"id": 1, "name": generate_random_string(8)}
pytestmark = pytest.mark.django_db


class TestNamespace:
    @pytest.fixture(autouse=True)
    def pre_patch(self):
        with patch("backend.accounts.bcs_perm.Namespace", new=bcs_perm.FakeNamespace), patch(
            "backend.bcs_web.permissions.bcs_perm.verify_project_by_user", new=lambda *args, **kwargs: True
        ), patch(
            "backend.resources.utils.kube_client.BcsKubeConfigurationService", new=FakeBcsKubeConfigurationService
        ), patch(
            "backend.resources.namespace.client.get_namespaces_by_cluster_id", new=lambda *args, **kwargs: [fake_data]
        ), patch(
            "backend.resources.namespace.utils.create_cc_namespace", new=lambda *args, **kwargs: fake_data
        ):
            yield

    @pytest.fixture(autouse=True)
    def patch_user_viewset(self):
        # 需要通过指定接口获取不同项目类型，覆盖conftest中的patch_user_viewset
        pass

    @patch(
        "backend.bcs_web.permissions.PaaSCCClient",
        new=paas_cc.StubPaaSCCClient,
    )
    def test_create_k8s_namespace(self, api_client):
        """创建k8s命名空间
        NOTE: 针对k8s会返回namespace_id字段
        """
        # project_id 与 cluster_id随机，防止项目的缓存，导致获取项目类型错误
        url = f"/apis/resources/projects/{generate_random_string(32)}/clusters/{generate_random_string(8)}/namespaces/"
        resp = api_client.post(url, data=fake_data)
        assert resp.json()["code"] == 0
        data = resp.json()["data"]
        assert "namespace_id" in data
        assert isinstance(data, dict)
        assert data["name"] == fake_data["name"]

    @patch(
        "backend.bcs_web.permissions.PaaSCCClient.get_project",
        new=paas_cc.StubPaaSCCClient().get_mesos_project,
    )
    def test_create_mesos_namespace(self, api_client):
        """创建k8s命名空间
        NOTE: 针对mesos不会返回namespace_id字段
        """
        # project_id 与 cluster_id随机，防止项目的缓存，导致获取项目类型错误
        url = f"/apis/resources/projects/{generate_random_string(32)}/clusters/{generate_random_string(8)}/namespaces/"
        resp = api_client.post(url, data=fake_data)
        assert resp.json()["code"] == 0
        data = resp.json()["data"]
        assert "namespace_id" not in data
        assert isinstance(data, dict)
        assert data["name"] == fake_data["name"]
