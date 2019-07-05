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

import json
from unittest import TestCase

import mock

from backend.apps.cluster import models

from . import cluster


class TestPollingOnce(TestCase):
    def setUp(self):
        self.project_id = "000"
        self.cluster_id = "111"
        self.node_id = "222"

    def test_clusterinstalllog_polling_once(self):
        log = models.ClusterInstallLog.objects.create(  # noqa
            project_id=self.project_id,
            cluster_id=self.cluster_id,
        )
        self.polling_once_test(models.ClusterInstallLog, log)

    def test_polling_once(self):
        log = models.NodeUpdateLog.objects.create(  # noqa
            project_id=self.project_id,
            cluster_id=self.cluster_id,
            node_id=self.node_id,
        )
        self.polling_once_test(models.NodeUpdateLog, log)

    @mock.patch("backend.components.bcs_api.get_task_result")
    def polling_once_test(self, model, log, get_task_result):
        log.is_finished = False
        log.save()

        get_task_result.return_value = {
            "code": -1,
            "result": False,
            "message": "Query task status fail: gcloudTaskStatusHTTPGet do GET fail",
            "data": None
        }

        log = cluster._polling_once(model, log)
        self.assertFalse(log.is_finished)

        data = {
            "log": "",
            "status": "RUNNING",
            "steps": {},
        }
        get_task_result.return_value = {
            "code": 0,
            "result": True,
            "message": "",
            "data": data,
        }

        log = cluster._polling_once(model, log)
        self.assertFalse(log.is_finished)

        data["steps"] = {
            "2.step": {
                "id": 81497656,
                "is_stop_after": False,
                "is_timer_run": False,
                "node_tasks": [
                    {
                        "auto_ignore": False,
                        "id": 81497666,
                        "is_chg_renovate_node": False,
                        "is_sleep_node": False,
                        "is_text_node": False,
                        "node_num": 0,
                        "retry_times": 0,
                        "sleep_time": "",
                        "state": "SUCCESS"
                    }
                ],
                "stage_name": "2.step",
                "state": "SUCCESS"
            },
            "1.step": {
                "id": 81497656,
                "is_stop_after": False,
                "is_timer_run": False,
                "node_tasks": [
                    {
                        "auto_ignore": False,
                        "id": 81497666,
                        "is_chg_renovate_node": False,
                        "is_sleep_node": False,
                        "is_text_node": False,
                        "node_num": 0,
                        "retry_times": 0,
                        "sleep_time": "",
                        "state": "SUCCESS"
                    }
                ],
                "stage_name": "1.step",
                "state": "SUCCESS"
            }
        }

        log = cluster._polling_once(model, log)
        self.assertFalse(log.is_finished)

        data["status"] = "SUCCESS"
        log = cluster._polling_once(model, log)
        self.assertTrue(log.is_finished)
        self.assertEqual(log.status, "normal")
        data = json.loads(log.log)
        node_tasks = data["node_tasks"]
        self.assertEqual(data["state"], "SUCCESS")
        self.assertEqual(node_tasks[0]["state"], "SUCCESS")
        self.assertEqual(node_tasks[0]["name"], "1.step")
        self.assertEqual(node_tasks[1]["state"], "SUCCESS")
        self.assertEqual(node_tasks[1]["name"], "2.step")
