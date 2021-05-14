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
from mock import patch

from backend.apps.cluster.models import NodeStatus
from backend.apps.cluster.serializers import BatchUpdateNodesSLZ
from backend.tests.bcs_mocks.data.paas_cc_json import fake_get_node_list_ok_resp
from backend.tests.bcs_mocks.fake_bcs_cc import FakeBCSCCMod

fake_cluster_node_id_list = [node["id"] for node in fake_get_node_list_ok_resp["results"]]


@pytest.mark.parametrize(
    "request_data,expect_node_id_list",
    [
        ({"status": NodeStatus.ToRemoved, "node_id_list": [1], "is_select_all": False}, [1]),
        ({"status": NodeStatus.ToRemoved, "node_id_list": [1], "is_select_all": True}, [1]),
        ({"status": NodeStatus.ToRemoved, "node_id_list": [], "is_select_all": True}, fake_cluster_node_id_list),
    ],
)
@patch("backend.apps.cluster.serializers.paas_cc.PaaSCCClient", new=FakeBCSCCMod)
def test_batch_node_slz(request_data, expect_node_id_list):
    slz = BatchUpdateNodesSLZ(
        data=request_data,
        context={"access_token": "access_token", "project_id": "projectid", "cluster_id": "clusterid"},
    )
    slz.is_valid(raise_exception=True)
    assert slz.validated_data["node_id_list"] == expect_node_id_list
