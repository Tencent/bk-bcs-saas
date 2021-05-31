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

from backend.container_service.observability.metric.constants import MetricDimension
from backend.tests.testing_utils.mocks.viewsets import FakeSystemViewSet


@pytest.fixture
def metric_api_common_patch():
    """ 指标类 API 通用 mock patch """
    with mock.patch('backend.bcs_web.viewsets.SystemViewSet', new=FakeSystemViewSet):
        yield


@pytest.fixture
def pod_metric_api_patch():
    with mock.patch(
        'backend.container_service.observability.metric.views.pod.PodMetricViewSet._common_query_handler',
        new=lambda *args, **kwargs: None,
    ):
        yield


@pytest.fixture
def container_metric_api_patch():
    with mock.patch(
        'backend.container_service.observability.metric.views.container.ContainerMetricViewSet._common_query_handler',
        new=lambda *args, **kwargs: None,
    ):
        yield


@pytest.fixture
def node_metric_api_patch():
    with mock.patch(
        'backend.container_service.observability.metric.views.node.NodeMetricViewSet._common_query_handler',
        new=lambda *args, **kwargs: None,
    ):
        yield


@pytest.fixture
def node_info_api_patch():
    with mock.patch(
        'backend.container_service.observability.metric.views.node.get_cluster_node_list',
        new=lambda *args, **kwargs: [{'inner_ip': '127.0.0.1', 'id': 1}],
    ), mock.patch(
        'backend.container_service.observability.metric.views.node.get_node_info',
        new=lambda *args, **kwargs: {
            'result': [
                {
                    'metric': {
                        'dockerVersion': 'v1',
                    },
                },
                {
                    'metric': {
                        'osVersion': 'v2',
                    }
                },
                {'metric': {'metric_name': 'cpu_count'}, 'value': [None, '8']},
            ]
        },
    ):
        yield


@pytest.fixture
def node_overview_api_patch():
    MOCK_NODE_DIMENSIONS_FUNC = {
        MetricDimension.CpuUsage: lambda *args, **kwargs: None,
        MetricDimension.MemoryUsage: lambda *args, **kwargs: None,
        MetricDimension.DiskUsage: lambda *args, **kwargs: None,
        MetricDimension.DiskIOUsage: lambda *args, **kwargs: None,
    }
    with mock.patch(
        'backend.container_service.observability.metric.views.node.get_container_pod_count',
        new=lambda *args, **kwargs: {'result': [{'metric': {'metric_name': 'pod_count'}, 'value': [None, '8']}]},
    ), mock.patch(
        'backend.container_service.observability.metric.views.node.NODE_DIMENSIONS_FUNC', new=MOCK_NODE_DIMENSIONS_FUNC
    ):
        yield


@pytest.fixture
def cluster_metric_api_patch():
    MOCK_CLUSTER_DIMENSIONS_FUNC = {
        MetricDimension.CpuUsage: lambda *args, **kwargs: None,
        MetricDimension.MemoryUsage: lambda *args, **kwargs: None,
        MetricDimension.DiskUsage: lambda *args, **kwargs: None,
    }
    with mock.patch(
        'backend.container_service.observability.metric.views.cluster.ClusterMetricViewSet._get_cluster_node_ip_list',
        new=lambda *args, **kwargs: ['127.0.0.1'],
    ), mock.patch(
        'backend.container_service.observability.metric.views.cluster.CLUSTER_DIMENSIONS_FUNC',
        new=MOCK_CLUSTER_DIMENSIONS_FUNC,
    ):
        yield
