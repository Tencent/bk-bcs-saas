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
from requests_mock import ANY

from backend.components.base import ComponentAuth
from backend.components.bcs_api import project

SUCCESS_CODE = 0


class TestBcsApiProjectClient:
    def test_query_project(self, project_id, request_user, requests_mock):
        expected_data = {"project_id": project_id}
        requests_mock.get(ANY, json={"code": SUCCESS_CODE, "data": expected_data})

        client = project.BcsProjectApiClient(ComponentAuth(request_user.token.access_token))
        resp = client.query_project(project_id)
        assert resp == expected_data

    def test_create_project(self, project_id, request_user, random_name, requests_mock):
        requests_mock.post(ANY, json={"code": SUCCESS_CODE, "message": "success"})

        client = project.BcsProjectApiClient(ComponentAuth(request_user.token.access_token))
        basic_config = project.ProjectBasicConfig(
            projectID=project_id, name=random_name, englishName=random_name, kind="k8s", businessID="1", description=""
        )
        reserved_config = project.ProjectReservedConfig()
        project_config = project.ProjectConfig(
            creator=request_user.username, basic_config=basic_config, reserved_config=reserved_config
        )
        resp = client.create_project(project_config)
        assert resp["code"] == SUCCESS_CODE

    def test_update_project(self, project_id, request_user, random_name, requests_mock):
        expected_data = {"project_id": project_id}
        requests_mock.put(ANY, json={"code": SUCCESS_CODE, "data": expected_data})

        client = project.BcsProjectApiClient(ComponentAuth(request_user.token.access_token))
        project_config = project.UpdatedProjectConfig(
            projectID=project_id,
            updater=request_user.username,
            name=random_name,
            kind="k8s",
            businessID=1,
        )
        resp = client.update_project(project_config)
        assert resp["code"] == SUCCESS_CODE
