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
from typing import Dict

import mock
import pytest
from django.conf import settings

from backend.tests.testing_utils.mocks.k8s_client import get_dynamic_client
from backend.tests.testing_utils.mocks.resp import MockRetrieveApiRespBuilder
from backend.tests.testing_utils.mocks.viewsets import FakeSystemViewSet


@pytest.fixture
def dashboard_api_common_patch():
    with mock.patch('backend.bcs_web.viewsets.SystemViewSet', new=FakeSystemViewSet), mock.patch(
        'backend.resources.resource.get_dynamic_client', new=get_dynamic_client
    ), mock.patch('backend.dashboard.viewsets.RetrieveApiRespBuilder', new=MockRetrieveApiRespBuilder):
        yield


def gen_mock_pod_manifest(*args, **kwargs) -> Dict:
    """ 构造并返回 mock 的 pod 配置信息 """
    with open(f'{settings.BASE_DIR}/backend/tests/resources/formatter/workloads/contents/pod.json') as fr:
        configs = json.load(fr)
    return configs['status_running']


def gen_mock_env_info(*args, **kwargs) -> str:
    """ 构造并返回 mock 的 exec_command 查询到的 env_info """
    return "env1=xxx\nenv2=xxx\nenv3=xxx"


@pytest.fixture
def dashboard_container_api_patch():
    with mock.patch(
        'backend.dashboard.workloads.views.container.Pod.fetch_manifest', new=gen_mock_pod_manifest
    ), mock.patch('backend.dashboard.workloads.views.container.exec_command', new=gen_mock_env_info):
        yield


@pytest.fixture
def dashboard_pod_api_patch():
    with mock.patch('backend.dashboard.workloads.views.pod.Pod.fetch_manifest', new=gen_mock_pod_manifest), mock.patch(
        'backend.dashboard.workloads.views.pod.RetrieveApiRespBuilder', new=MockRetrieveApiRespBuilder
    ):
        yield
