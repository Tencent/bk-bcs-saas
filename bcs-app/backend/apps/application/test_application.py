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

from backend.utils.test import APITestCase
from backend.apps.application.utils import CustomThreadHandler


class TestApplication(APITestCase):

    def setUp(self):
        pass

    def test_thread(self):
        kwargs = {
            "access_token": "A59JMgYn6Dbkryv2LLpsTJhTgbofBT",
            "cluster_id": "BCS-TESTBCSTEST01-10001",
            "namespace": ["test1", "test2", "test3", "test4"],
            "data": ""
        }
        client = CustomThreadHandler(kwargs, num=5)
        client.create_thread(self)
        print(client.ret_success_data)
        print(client.ret_fail_data)
