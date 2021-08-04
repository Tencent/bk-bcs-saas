# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from unittest.mock import patch

import pytest

from backend.components.bcs.mesos import MesosClient
from backend.components.paas_cc import get_cluster
from backend.container_service.clusters.views.node_views.utils import MesosNodeLabelsQuerier

fake_cc_get_cluster_result = {"code": 0, "data": {"environment": "stag"}}
fake_mesos_agent_attrs_result = [
    {"strings": {"test": {"value": "val"}}},
    {"strings": {"test1": {"value": "val1"}}},
    {"strings": {"test": {"value": "val1"}}},
    {"strings": {"test1": {"value": "val1"}}},
]
fake_mesos_agent_attrs_null_result = [{"strings": None}]


@patch("backend.components.paas_cc.get_cluster", return_value=fake_cc_get_cluster_result)
@patch("backend.components.bcs.mesos.MesosClient.get_agent_attrs", return_value=fake_mesos_agent_attrs_result)
def test_get_mesos_labels(mock_get_agent_attrs, mock_get_cluster):
    key_vals = MesosNodeLabelsQuerier("access_token", "project_id").query_labels(["cluster_id"])
    expect_result = {"test": set(["val", "val1"]), "test1": set(["val1"])}
    assert key_vals == expect_result


@patch("backend.components.paas_cc.get_cluster", return_value=fake_mesos_agent_attrs_null_result)
@patch("backend.components.bcs.mesos.MesosClient.get_agent_attrs", return_value=fake_mesos_agent_attrs_null_result)
def test_get_mesos_null_labels(mock_get_agent_attrs, mock_get_cluster):
    key_vals = MesosNodeLabelsQuerier("access_token", "project_id").query_labels(["cluster_id"])
    assert key_vals == {}
