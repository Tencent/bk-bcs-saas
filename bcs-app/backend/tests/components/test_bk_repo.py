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
from requests_mock import ANY

from backend.components import bk_repo

fake_access_token = "access_token"
fake_username = "admin"
fake_pwd = "pwd"
fake_project_code = "project_code"
fake_project_name = "project_name"
fake_project_description = "this is a test"
fake_chart_name = "chart_name"
fake_chart_version = "0.0.1"


class TestBkRepoClient:
    def test_create_project(self, requests_mock):
        requests_mock.post(ANY, json={"foo": "bar"})

        client = bk_repo.BkRepoClient(fake_access_token, fake_username)
        resp_data = client.create_project(fake_project_code, fake_project_name, fake_project_description)
        assert resp_data == {"foo": "bar"}
        assert requests_mock.called

    def test_create_chart_repo(self, requests_mock):
        requests_mock.post(ANY, json={"foo": "bar"})

        client = bk_repo.BkRepoClient(fake_access_token, fake_username)
        resp_data = client.create_chart_repo(fake_project_code)
        assert resp_data == {"foo": "bar"}
        assert requests_mock.request_history[0].method == "POST"

    def test_set_auth(self, requests_mock):
        requests_mock.post(ANY, json={"result": True, "data": {"foo": "bar"}})

        client = bk_repo.BkRepoClient(fake_access_token, fake_username)
        resp_data = client.set_auth(fake_project_code, fake_username, fake_pwd)
        assert resp_data == {"foo": "bar"}
        assert requests_mock.request_history[0].method == "POST"


class TestBkRepoRawClient:
    def test_get_charts(self, requests_mock):
        requests_mock.get(ANY, json={"foo": "bar"})

        client = bk_repo.BkRepoRawClient(fake_username, fake_pwd)
        resp_data = client.get_charts(fake_project_code, fake_project_code)
        assert resp_data == {"foo": "bar"}
        assert requests_mock.called

    def test_get_chart_versions(self, requests_mock):
        requests_mock.get(ANY, json={"foo": "bar"})

        client = bk_repo.BkRepoRawClient(fake_access_token, fake_username)
        resp_data = client.get_chart_versions(fake_project_code, fake_project_code, fake_chart_name)
        assert resp_data == {"foo": "bar"}
        assert requests_mock.called
        assert requests_mock.request_history[0].method == "GET"

    def test_get_chart_version_detail(self, requests_mock):
        requests_mock.get(ANY, json={"foo": "bar"})

        client = bk_repo.BkRepoRawClient(fake_access_token, fake_username)
        resp_data = client.get_chart_version_detail(
            fake_project_code, fake_project_code, fake_chart_name, fake_chart_version
        )
        assert resp_data == {"foo": "bar"}
        assert requests_mock.called
        assert requests_mock.request_history[0].method == "GET"

    def test_delete_chart_version(self, requests_mock):
        requests_mock.delete(ANY, json={"foo": "bar"})

        client = bk_repo.BkRepoRawClient(fake_access_token, fake_username)
        resp_data = client.delete_chart_version(
            fake_project_code, fake_project_code, fake_chart_name, fake_chart_version
        )
        assert resp_data == {"foo": "bar"}
        assert requests_mock.called
        assert requests_mock.request_history[0].method == "DELETE"
