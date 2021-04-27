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
from unittest import mock

from backend.tests.contents.fake_viewsets import FakeSystemViewSet
from backend.tests.contents.fake_k8s_client import get_dynamic_client

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def common_patch():
    with mock.patch('backend.dashboard.workload.views.job.SystemViewSet', new=FakeSystemViewSet), \
            mock.patch('backend.resources.resource.get_dynamic_client', new=get_dynamic_client):
        yield


class TestJob:

    def test_list(self, api_client, project_id, cluster_id):
        """ 测试获取资源列表接口 """
        response = api_client.get(
            f'/api/dashboard/projects/{project_id}/clusters/{cluster_id}/workloads/jobs/'
        )
        assert response.json()['code'] == 0
