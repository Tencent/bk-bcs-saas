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
from backend.components.bcs_api import cluster

SUCCESS_CODE = 0


class TestBcsApiClient:
    def test_add_cluster(self, project_id, cluster_id, request_user, random_name, requests_mock):
        expected_data = {"cluster_id": cluster_id}
        expected_task = {"taskID": random_name}
        requests_mock.post(ANY, json={"code": SUCCESS_CODE, "data": expected_data, "task": expected_task})

        client = cluster.BcsClusterApiClient(ComponentAuth(request_user.token.access_token))
        cloud_cluster_config = cluster.CloudClusterConfig(
            region=random_name, manageType="INDEPENDENT_CLUSTER", master=["fake_ip"], vpcID=random_name, cloudID=1
        )
        bcs_basic_config = cluster.BcsBasicConfig(
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
        cluster_config = cluster.ClusterConfig(
            creator=request_user.username,
            cloud_cluster_config=cloud_cluster_config,
            bcs_basic_config=bcs_basic_config,
        )
        resp = client.add_cluster(cluster_config)
        assert resp["task"] == expected_task
        assert resp["data"] == expected_data

    def test_update_cluster(self, project_id, cluster_id, request_user, random_name, requests_mock):
        expected_data = {"cluster_id": cluster_id}
        requests_mock.put(ANY, json={"code": SUCCESS_CODE, "data": expected_data})

        client = cluster.BcsClusterApiClient(ComponentAuth(request_user.token.access_token))
        cluster_config = cluster.UpdatedClusterConfig(
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
        requests_mock.delete(ANY, json={"code": SUCCESS_CODE, "data": {}, "task": expected_task})

        client = cluster.BcsClusterApiClient(ComponentAuth(request_user.token.access_token))
        resp = client.delete_cluster(cluster_id)
        assert resp["task"] == expected_task

    def test_query_task(self, random_name, request_user, requests_mock):
        expected_data = {"taskID": random_name}
        requests_mock.get(ANY, json={"code": SUCCESS_CODE, "data": expected_data})

        client = cluster.BcsClusterApiClient(ComponentAuth(request_user.token.access_token))
        resp = client.query_task(random_name)
        assert resp["data"] == expected_data
