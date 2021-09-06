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
import pytest
from requests_mock import ANY

from backend.components import bcs_api
from backend.components.base import ComponentAuth
from backend.components.bcs_api import BcsApiClient

BCS_AUTH_TOKEN = 'example-auth-token'

fake_ip = "127.0.0.1"
success_code = 0


@pytest.fixture(autouse=True)
def setup_token(settings):
    settings.BCS_AUTH_TOKEN = BCS_AUTH_TOKEN


class TestBcsApiClient:
    def test_get_cluster_simple(self, project_id, cluster_id, requests_mock):
        requests_mock.get(ANY, json={'id': 'foo-id'})

        client = BcsApiClient(ComponentAuth('fake_token'))
        result = client.query_cluster_id('stag', project_id, cluster_id)
        assert result == 'foo-id'

        req_history = requests_mock.request_history[0]
        # Assert token was in request headers and access_token was in query string
        assert req_history.headers.get('Authorization') == BCS_AUTH_TOKEN
        assert 'access_token=fake_token' in req_history.url

    def test_get_cluster_credentials(self, requests_mock):
        requests_mock.get(ANY, json={'name': 'foo'})

        client = BcsApiClient(ComponentAuth('fake_token'))
        resp = client.get_cluster_credentials('stag', 'fake-bcs-cluster-foo')
        assert resp == {'name': 'foo'}

    def test_query_project(self, project_id, request_user, requests_mock):
        expected_data = {"project_id": project_id}
        requests_mock.get(ANY, json={"code": success_code, "data": expected_data})

        client = BcsApiClient(ComponentAuth(request_user.token.access_token))
        resp = client.query_project(project_id)
        assert resp == expected_data

    def test_create_project(self, project_id, request_user, random_name, requests_mock):
        requests_mock.post(ANY, json={"code": success_code, "message": "success"})

        client = BcsApiClient(ComponentAuth(request_user.token.access_token))
        basic_config = bcs_api.ProjectBasicConfig(
            projectID=project_id,
            name=random_name,
            englishName=random_name,
            kind="k8s",
            businessID=1,
            description="",
            credentials={},
        )
        reserved_config = bcs_api.ProjectReservedConfig(
            bgID="",
            bgName="",
            deptID="",
            deptName="",
            centerID="",
            centerName="",
            isSecret=False,
            deployType=2,
            isOffline=False,
            useBKRes=False,
            projectType=1,
        )
        project_config = bcs_api.ProjectConfig(
            creator=request_user.username, basic_config=basic_config, reserved_config=reserved_config
        )
        resp = client.create_project(project_config)
        assert resp["code"] == success_code

    def test_update_project(self, project_id, request_user, random_name, requests_mock):
        expected_data = {"project_id": project_id}
        requests_mock.put(ANY, json={"code": success_code, "data": expected_data})

        client = BcsApiClient(ComponentAuth(request_user.token.access_token))
        project_config = bcs_api.UpdatedProjectConfig(
            projectID=project_id,
            updater=request_user.username,
            name=random_name,
            kind="k8s",
            businessID=1,
        )
        resp = client.update_project(project_config)
        assert resp["code"] == success_code

    def test_add_cluster(self, project_id, cluster_id, request_user, random_name, requests_mock):
        expected_data = {"cluster_id": cluster_id}
        expected_task = {"taskID": random_name}
        requests_mock.post(ANY, json={"code": 0, "data": expected_data, "task": expected_task})

        client = BcsApiClient(ComponentAuth(request_user.token.access_token))
        cloud_cluster_config = bcs_api.CloudClusterConfig(
            region=random_name,
            manageType="INDEPENDENT_CLUSTER",
            master=["fake_ip"],
            vpcID=random_name,
            cloudID=1,
            nodes=[],
            networkSettings={},
            clusterBasicSettings={},
            clusterAdvanceSettings={},
            nodeSettings={},
            systemReinstall=False,
            initLoginPassword="",
            status="",
        )
        bcs_cluster_config = bcs_api.BcsClusterConfig(
            projectID=project_id,
            businessID=1,
            clusterID=cluster_id,
            clusterName=random_name,
            provider="",
            environment="test",
            engineType="k8s",
            isExclusive=False,
            clusterType="k8s",
            federationClusterID="",
            labels={},
            onlyCreateInfo=True,
            bcsAddons={},
            extraAddons={},
        )
        cluster_config = bcs_api.ClusterConfig(
            creator=request_user.username,
            cloud_cluster_config=cloud_cluster_config,
            bcs_cluster_config=bcs_cluster_config,
        )
        resp = client.add_cluster(cluster_config)
        assert resp["task"] == expected_task
        assert resp["data"] == expected_data

    def test_update_cluster(self, project_id, cluster_id, request_user, random_name, requests_mock):
        expected_data = {"cluster_id": cluster_id}
        requests_mock.put(ANY, json={"code": 0, "data": expected_data})

        client = BcsApiClient(ComponentAuth(request_user.token.access_token))
        cluster_config = bcs_api.UpdatedClusterConfig(
            projectID=project_id,
            clusterID=cluster_id,
            updater=request_user.username,
            clusterName="test",
            status="RUNNING",
        )
        resp = client.update_cluster(cluster_config)
        assert resp == expected_data

    def test_delete_cluster(self, cluster_id, random_name, request_user, requests_mock):
        expected_task = {"taskID": random_name}
        requests_mock.delete(ANY, json={"code": 0, "data": {}, "task": expected_task})

        client = BcsApiClient(ComponentAuth(request_user.token.access_token))
        resp = client.delete_cluster(cluster_id)
        assert resp["task"] == expected_task

    def test_query_task(self, random_name, request_user, requests_mock):
        expected_data = {"taskID": random_name}
        requests_mock.get(ANY, json={"code": 0, "data": expected_data})

        client = BcsApiClient(ComponentAuth(request_user.token.access_token))
        resp = client.query_task(random_name)
        assert resp["data"] == expected_data
