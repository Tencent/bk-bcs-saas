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
from datetime import datetime

import mock
from django.shortcuts import reverse

from backend.activity_log.client import UserActivityLogClient
from backend.activity_log.models import UserActivityLog
from backend.utils.test import APITestCase, get_testing_user


class TestActivityLogView(APITestCase):

    def setUp(self):
        self.project_id = "000"
        self.user = get_testing_user()
        self.log_client = UserActivityLogClient(
            project_id=self.project_id,
            user=self.user.username,
        )
        self.log_client.log_add(
            resource="testing", resource_type="testcase",
        )

    def test_nologin(self):
        url = reverse('activity_log:api.project.activity_logs', kwargs={
            "project_id": self.project_id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("code", response.json())

    def test_get(self):
        url = reverse('activity_log:api.project.activity_logs', kwargs={
            "project_id": self.project_id,
        })
        self.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["code"], 0)
        data = result["data"]
        results = data["results"]
        self.assertEqual(len(results), 1)

    def test_filter(self):
        url = reverse('activity_log:api.project.activity_logs', kwargs={
            "project_id": self.project_id,
        })
        self.log_client.log_note(
            resource="testing", resource_type="testcase",
        )
        self.force_authenticate(self.user)
        response = self.client.get(url, data={
            "activity_type": "note",
            "begin_time": "2017-03-27 09:30:00",
            "end_time": "2117-03-27 09:30:00",
        })
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["code"], 0)
        data = result["data"]
        results = data["results"]
        self.assertEqual(len(results), 1)

    def test_ordering(self):
        url = reverse('activity_log:api.project.activity_logs', kwargs={
            "project_id": self.project_id,
        })
        self.log_client.log_note(
            resource_id="3", resource_type="ordering",
        )
        self.log_client.log_note(
            resource_id="2", resource_type="ordering",
        )
        self.log_client.log_note(
            resource_id="1", resource_type="ordering",
        )
        self.force_authenticate(self.user)
        response = self.client.get(url, data={
            "resource_type": "ordering",
            "limit": 100,
        })
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["code"], 0)
        data = result["data"]
        results = data["results"]
        self.assertEqual(results[0]["resource_id"], "1")
        self.assertEqual(results[1]["resource_id"], "2")
        self.assertEqual(results[2]["resource_id"], "3")


class TestActivityEventView(APITestCase):

    def setUp(self):
        self.project_id = "000"
        self.user = get_testing_user()
        self.log_client = UserActivityLogClient(
            project_id=self.project_id,
            user=self.user.username,
        )
        self.log_client.log_add(
            resource="testing", resource_type="testcase",
        )

    def test_nologin(self):
        url = reverse('activity_log:api.project.activity_events', kwargs={
            "project_id": self.project_id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("code", response.json())

    @mock.patch("backend.activity_log.views.ActivityEventView.query_events")
    @mock.patch("backend.components.paas_cc.get_all_clusters")
    def test_get(self, get_all_clusters, query_events):
        url = reverse('activity_log:api.project.activity_events', kwargs={
            "project_id": self.project_id,
        })
        self.force_authenticate(self.user)
        cluster_id = "BCS-10001"
        cluster_name = "测试集群"
        query_events.return_value = {
            "code": 0,
            "data": [
                {
                    "_id": "59cdf3a98118af1d406d26dc",
                    "clusterId": cluster_id,
                    "component": "kublet",
                    "createTime": "2017-09-29 15:18:01",
                    "data": {
                        "a": "1",
                        "b": "2"
                    },
                    "describe": "wow its killing itself",
                    "env": "mesos",
                    "eventTime": "2017-09-29 12:02:00",
                    "kind": "rc",
                    "level": "warning",
                    "type": "killing"
                }
            ],
            "total": 10,
            "message": "Success",
            "result": True
        }
        get_all_clusters.return_value = {
            "code": 0,
            "data": {
                "count": 3,
                "results": [
                    {
                        "area_id": 1,
                        "artifactory": "",
                        "capacity_updated_at": None,
                        "cluster_id": cluster_id,
                        "cluster_num": 15002,
                        "config_svr_count": 0,
                        "created_at": "2017-10-18T11:11:40+08:00",
                        "creator": "admin",
                        "description": "测试集群",
                        "disabled": False,
                        "environment": "stag",
                        "master_count": 0,
                        "name": cluster_name,
                        "node_count": 0,
                        "project_id": self.project_id,
                        "remain_cpu": 0,
                        "remain_disk": 0,
                        "remain_mem": 0,
                        "status": "",
                        "total_cpu": 0,
                        "total_disk": 0,
                        "total_mem": 0,
                        "type": "k8s",
                        "updated_at": "2017-10-18T14:37:06+08:00"
                    }
                ]
            },
            "message": "获取集群成功",
            "result": True
        }
        response = self.client.get(url)
        result = response.json()
        self.assertEqual(result["code"], 0)
        data = result["data"]
        self.assertEqual(data["count"], 10)
        results = data["results"]
        self.assertTrue(len(results), 1)
        result = results[0]
        self.assertEqual(result["cluster_id"], cluster_id)
        self.assertEqual(result["cluster_name"], cluster_name)


class TestActivityLogResourceTypesView(APITestCase):

    def setUp(self):
        self.project_id = "000"
        self.user = get_testing_user()
        self.log_client = UserActivityLogClient(
            project_id=self.project_id,
            user=self.user.username,
        )
        self.log_client.log_add(
            resource="testing", resource_type="testcase",
        )

    def test_nologin(self):
        url = reverse('activity_log:api.project.activity_log_resource_types')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("code", response.json())

    def test_get(self):
        url = reverse('activity_log:api.project.activity_log_resource_types')
        self.force_authenticate(self.user)
        response = self.client.get(url)
        result = response.json()
        self.assertEqual(result["code"], 0)
        data = result["data"]
        self.assertTrue(bool(data))
