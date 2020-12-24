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
from unittest.mock import patch

from backend.components.paas_cc import get_cluster
from backend.components.bcs.mesos import MesosClient
from backend.apps.cluster.views.node_views.utils import MesosNodeLabelsQuerier


@patch("backend.components.paas_cc.get_cluster")
@patch("backend.components.bcs.mesos.MesosClient.get_agent_attrs")
@pytest.mark.parametrize("access_token, project_id, cluster_id", [("access_token", "project_id", "cluster_id")])
def test_get_mesos_labels(mock_get_agent_attrs, mock_get_cluster, access_token, project_id, cluster_id):
    mock_get_cluster.return_value = {"code": 0, "data": {"environment": "stag"}}
    attrs = [
        {"strings": {"test": {"value": "val"}}},
        {"strings": {"test1": {"value": "val1"}}},
        {"strings": {"test": {"value": "val1"}}},
        {"strings": {"test1": {"value": "val1"}}},
    ]
    mock_get_agent_attrs.return_value = attrs

    key_vals = MesosNodeLabelsQuerier(access_token, project_id).query_labels([cluster_id])
    expect_result = {"test": set(["val", "val1"]), "test1": set(["val1"])}
    assert key_vals == expect_result
