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

from backend.container_service.projects.cm import update_or_create_project
from backend.tests.testing_utils.mocks import bcs_api, paas_cc

fake_project_kind = 1
fake_project_data = {"updator": "admin", "kind": fake_project_kind, "cc_app_id": 1}


@patch("backend.container_service.projects.cm.paas_cc.PaaSCCClient", new=paas_cc.StubPaaSCCClient)
@patch("backend.container_service.projects.cm.bcs_api.BcsApiClient", new=bcs_api.StubBcsApiClient)
def test_update_project(request_user, project_id):
    """更新项目信息
    项目已经存在于clustermanager中
    """
    project_data = update_or_create_project(request_user.token.access_token, project_id, fake_project_data)
    assert project_data["kind"] == fake_project_kind


@patch("backend.container_service.projects.cm.paas_cc.PaaSCCClient", new=paas_cc.StubPaaSCCClient)
@patch(
    "backend.container_service.projects.cm.bcs_api.BcsApiClient.create_project",
    new=bcs_api.StubBcsApiClient().create_project,
)
@patch(
    "backend.container_service.projects.cm.bcs_api.BcsApiClient.update_project",
    new=bcs_api.StubBcsApiClient().update_project_not_exist,
)
def test_create_project(request_user, project_id):
    project_data = update_or_create_project(request_user.token.access_token, project_id, fake_project_data)
    assert project_data["kind"] == fake_project_kind
