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
from unittest.mock import patch

import pytest

from backend.container_service.clusters import cm, constants
from backend.container_service.clusters.models import CommonStatus
from backend.tests.testing_utils.base import generate_random_string
from backend.tests.testing_utils.mocks import bcs_api, paas_cc

fake_biz_id = 1
fake_coes = "k8s"
fake_cluster_name = "test-cluster"
fake_cluster_data = {
    "creator": "admin",
    "environment": "test",
    "name": fake_cluster_name,
    "coes": fake_coes,
    "area_id": 1,
    "version": "1.12",
}


@pytest.fixture(autouse=True)
def pre_patch():
    with patch("backend.container_service.clusters.cm.paas_cc.PaaSCCClient", new=paas_cc.StubPaaSCCClient), patch(
        "backend.container_service.clusters.cm.bcs_api.BcsApiClient", new=bcs_api.StubBcsApiClient
    ):
        yield


def test_create_cluster(project_id, cluster_id, request_user):
    cluster_data = cm.create_cluster(request_user.token.access_token, project_id, fake_biz_id, fake_cluster_data)
    assert cluster_data["type"] == fake_coes


def test_update_cluster(project_id, cluster_id, request_user):
    cluster_data = cm.update_cluster(
        request_user.token.access_token, project_id, cluster_id, {"name": fake_cluster_name}
    )
    assert cluster_data["name"] == fake_cluster_name


def test_delete_cluster(project_id, cluster_id, request_user):
    cluster_data = cm.delete_cluster(request_user.token.access_token, project_id, cluster_id)
    assert cluster_data["status"] == CommonStatus.Removing
