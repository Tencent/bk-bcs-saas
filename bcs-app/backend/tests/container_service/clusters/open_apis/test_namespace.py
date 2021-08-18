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
            "backend.bcs_web.permissions.PaaSCCClient", new=paas_cc.StubPaaSCCClient
        ), patch(
            "backend.bcs_web.permissions.bcs_perm.verify_project_by_user", new=lambda *args, **kwargs: True
        ), patch(
            "backend.resources.utils.kube_client.BcsKubeConfigurationService", new=FakeBcsKubeConfigurationService
        ), patch(
            "backend.resources.namespace.client.get_namespaces_by_cluster_id", new=lambda *args, **kwargs: [fake_data]
        ), patch(
            "backend.resources.namespace.utils.create_cc_namespace", new=lambda *args, **kwargs: fake_data
        ):
            yield

    def test_create_mesos_namespace(self, cluster_id, project_id, request_user):
        ns_perm_client = bcs_perm.FakeNamespace()
        ns_data = NamespaceViewSet().create_mesos_namespace(
            request_user.token.access_token,
            request_user.username,
            project_id,
            cluster_id,
            fake_data["name"],
            ns_perm_client,
        )
        assert "id" in ns_data
        assert ns_data["id"] == 1

    def test_create_kubernetes_namespace(self, cluster_id, project_id, request_user):
        ns_perm_client = bcs_perm.FakeNamespace()
        ns_data = NamespaceViewSet().create_kubernetes_namespace(
            request_user.token.access_token,
            request_user.username,
            project_id,
            cluster_id,
            fake_data["name"],
            ns_perm_client,
        )
        assert "namespace_id" in ns_data
        assert ns_data["namespace_id"] == 1

    def test_create_namespace(self, cluster_id, project_id, api_client):
        url = f"/apis/resources/projects/{project_id}/clusters/{cluster_id}/namespaces/"
        resp = api_client.post(url, data=fake_data)
        assert resp.json()["code"] == 0
        data = resp.json()["data"]
        assert isinstance(data, dict)
        assert data["name"] == fake_data["name"]
