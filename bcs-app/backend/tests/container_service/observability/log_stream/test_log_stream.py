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


class TestLogStream:
    def test_fetch(self, api_client, project_id, cluster_id, namespace, pod_name, container_name):
        """ 测试获取日志 """
        response = api_client.get(
            f'/api/logstream/projects/{project_id}/clusters/{cluster_id}/namespaces/{namespace}/pods/{pod_name}/'
        )
        assert response.json()['code'] == 0
