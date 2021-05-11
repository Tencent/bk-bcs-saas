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
import pytest

pytestmark = pytest.mark.django_db


# 通用的API请求参数
mock_api_params = {
    'pod_name': 'deployment-1',
    'start_at': '2021-01-01 10:00:00',
    'end_at': '2021-01-01 11:00:00'
}


class TestContainerMetric:

    def test_cpu_usage(self, api_client, project_id, cluster_id, metric_api_common_patch):
        """ 测试获取 CPU 使用情况 接口 """
        response = api_client.get(
            f'/api/metrics/projects/{project_id}/clusters/{cluster_id}/container/cpu_usage/', mock_api_params
        )
        assert response.json()['code'] == 0

    def test_memory_usage(self, api_client, project_id, cluster_id, metric_api_common_patch):
        """ 测试获取 内存使用情况 接口 """
        response = api_client.get(
            f'/api/metrics/projects/{project_id}/clusters/{cluster_id}/container/memory_usage/', mock_api_params
        )
        assert response.json()['code'] == 0

    def test_disk_read(self, api_client, project_id, cluster_id, metric_api_common_patch):
        """ 测试获取 磁盘读情况 接口 """
        response = api_client.get(
            f'/api/metrics/projects/{project_id}/clusters/{cluster_id}/container/disk_read/', mock_api_params
        )
        assert response.json()['code'] == 0

    def test_diask_write(self, api_client, project_id, cluster_id, metric_api_common_patch):
        """ 测试获取 磁盘写情况 接口 """
        response = api_client.get(
            f'/api/metrics/projects/{project_id}/clusters/{cluster_id}/container/disk_write/', mock_api_params
        )
        assert response.json()['code'] == 0
