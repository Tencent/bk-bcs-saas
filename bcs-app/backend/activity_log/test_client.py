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
from rest_framework import test

from backend.activity_log import client


class TestUserActivityLogClient(test.APITransactionTestCase):
    def setUp(self):
        self.project_id = "000"
        self.user = "testuser"
        self.client = client.UserActivityLogClient(
            project_id=self.project_id,
            user=self.user,
            resource_type="testcase",
        )

    def test_context_log1(self):
        with self.client.context_log():
            self.client.log_note(
                resource="test1",
            )
            self.assertEqual(self.client.activity_log.activity_type, "note")
        self.assertIsNotNone(self.client.activity_log)
        self.assertEqual(self.client.activity_log.activity_status, "completed")

    def test_context_log2(self):
        with self.assertRaises(ZeroDivisionError):
            with self.client.context_log():
                self.client.log_note(
                    resource="test2",
                )
                self.assertEqual(self.client.activity_log.activity_type, "note")
                raise ZeroDivisionError()
        self.assertIsNotNone(self.client.activity_log)
        self.assertEqual(self.client.activity_log.activity_status, "error")


class TestContextActivityLogClient(test.APITransactionTestCase):
    def setUp(self):
        self.project_id = "000"
        self.user = "testuser"
        self.client = client.ContextActivityLogClient(
            project_id=self.project_id,
            user=self.user,
            resource_type="testcase",
        )

    def test_log(self):
        self.client.log_note(resource="test")
        self.assertEqual(self.client.activity_log.activity_status, "completed")

    def test_with_log(self):
        with self.client.log_note(resource="test"):
            pass
        self.assertEqual(self.client.activity_log.activity_status, "completed")

    def test_log_note(self):
        with self.assertRaises(ZeroDivisionError):
            with self.client.log_note(resource="test1"):
                self.assertEqual(
                    self.client.activity_log.activity_status, "completed")
                self.assertEqual(self.client.activity_log.activity_type, "note")
                raise ZeroDivisionError()

        self.assertEqual(self.client.activity_log.activity_status, "error")
