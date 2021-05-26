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
import mock
import pytest

from backend.tests.testing_utils.mocks.viewsets import FakeSystemViewSet


@pytest.fixture
def metric_api_common_patch():
    with mock.patch('backend.bcs_web.viewsets.SystemViewSet', new=FakeSystemViewSet), mock.patch(
        'backend.container_service.observability.metric.views.pod.PodMetricViewSet._common_query_handler',
        new=lambda *args, **kwargs: None,
    ), mock.patch(
        'backend.container_service.observability.metric.views.container.ContainerMetricViewSet._common_query_handler',
        new=lambda *args, **kwargs: None,
    ):
        yield
