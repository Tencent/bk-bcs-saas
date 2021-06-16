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
from unittest.mock import patch

import pytest

from backend.container_service.clusters.base.models import CtxCluster
from backend.container_service.clusters.constants import BcsCCNodeStatus, NodeConditionStatus
from backend.container_service.clusters.tools import node
from backend.resources.node.formatter import NodeResourceData


@pytest.mark.parametrize(
    "conditions,expected_status",
    [
        (
            [
                {
                    'lastHeartbeatTime': '2021-06-08T01:55:53Z',
                    'lastTransitionTime': '2020-08-20T12:14:43Z',
                    'message': 'kubelet has sufficient PID available',
                    'reason': 'KubeletHasSufficientPID',
                    'status': 'False',
                    'type': 'PIDPressure',
                },
                {
                    'lastHeartbeatTime': '2021-06-08T01:55:53Z',
                    'lastTransitionTime': '2020-08-20T12:14:43Z',
                    'message': 'kubelet is posting ready status',
                    'reason': 'KubeletReady',
                    'status': 'True',
                    'type': 'Ready',
                },
            ],
            NodeConditionStatus.Ready,
        ),
        (
            [
                {
                    'lastHeartbeatTime': '2021-06-08T01:55:53Z',
                    'lastTransitionTime': '2020-08-20T12:14:43Z',
                    'message': 'kubelet has sufficient PID available',
                    'reason': 'KubeletHasSufficientPID',
                    'status': 'False',
                    'type': 'PIDPressure',
                },
                {
                    'lastHeartbeatTime': '2021-06-08T01:55:53Z',
                    'lastTransitionTime': '2020-08-20T12:14:43Z',
                    'message': 'kubelet is posting ready status',
                    'reason': 'KubeletReady',
                    'status': 'False',
                    'type': 'Ready',
                },
            ],
            NodeConditionStatus.NotReady,
        ),
    ],
)
def test_get_node_status(conditions, expected_status):
    assert node.get_node_status(conditions) == expected_status


fake_inner_ip = "127.0.0.1"
fake_node_name = "ip-127-0-0-1-n-bcs-k8s-15091"
fake_resource_data = {
    "metadata": {"labels": {"key": "value"}, "name": fake_node_name},
    "spec": {"taints": [{"key": "key", "value": "value", "effect": "NoSchedule"}]},
    "status": {
        "addresses": [
            {"address": fake_inner_ip, "type": "InternalIP"},
            {"address": fake_node_name, "type": "Hostname"},
        ],
        "conditions": [
            {
                'lastHeartbeatTime': '2021-06-08T01:55:53Z',
                'lastTransitionTime': '2020-08-20T12:14:43Z',
                'message': 'kubelet is posting ready status',
                'reason': 'KubeletReady',
                'status': 'False',
                'type': 'Ready',
            }
        ],
    },
}
fake_ctx_cluster = CtxCluster.create(token="token", id="BCS-K8S-15091", project_id="test")


@patch(
    "backend.container_service.clusters.tools.node.Node.list",
    return_value=[NodeResourceData(name=fake_node_name, inner_ip=fake_inner_ip, data=fake_resource_data)],
)
def query_cluster_nodes(mock_list):
    cluster_nodes = node.query_cluster_nodes(fake_ctx_cluster)
    assert fake_inner_ip in cluster_nodes
    assert cluster_nodes[fake_inner_ip]["node_name"] == fake_node_name
    assert cluster_nodes[fake_inner_ip]["status"] == NodeConditionStatus.Ready
    assert not cluster_nodes[fake_inner_ip]["unschedulable"]


@pytest.mark.parametrize(
    "cluster_node_status,unschedulable,bcs_cc_node_status,expected_status",
    [
        (NodeConditionStatus.Ready, False, BcsCCNodeStatus.Normal, BcsCCNodeStatus.Normal),
        (NodeConditionStatus.Ready, True, BcsCCNodeStatus.Normal, BcsCCNodeStatus.Removable),
        (NodeConditionStatus.Ready, True, BcsCCNodeStatus.ToRemoved, BcsCCNodeStatus.ToRemoved),
        (NodeConditionStatus.NotReady, True, BcsCCNodeStatus.NotReady, BcsCCNodeStatus.NotReady),
        (NodeConditionStatus.NotReady, True, BcsCCNodeStatus.Removable, BcsCCNodeStatus.NotReady),
        (NodeConditionStatus.Unknown, True, BcsCCNodeStatus.Removable, BcsCCNodeStatus.Unknown),
    ],
)
def test_transform_status(cluster_node_status, unschedulable, bcs_cc_node_status, expected_status):
    assert expected_status == node.transform_status(cluster_node_status, unschedulable, bcs_cc_node_status)


class TestNodesData:
    def test_compose_data_by_bcs_cc_nodes(self, bcs_cc_nodes, cluster_nodes, cluster_id):
        client = node.NodesData(bcs_cc_nodes=bcs_cc_nodes, cluster_nodes=cluster_nodes, cluster_id=cluster_id)
        node_data = client._compose_data_by_bcs_cc_nodes()
        assert len(node_data) == len(
            [node for inner_ip, node in bcs_cc_nodes.items() if node["status"] != BcsCCNodeStatus.Normal]
        )

    def test_compose_data_by_cluster_nodes(self, bcs_cc_nodes, cluster_nodes, cluster_id):
        client = node.NodesData(bcs_cc_nodes=bcs_cc_nodes, cluster_nodes=cluster_nodes, cluster_id=cluster_id)
        node_data = client._compose_data_by_cluster_nodes()
        assert len(node_data) == len(cluster_nodes)
        assert node_data[0]["status"] == BcsCCNodeStatus.Normal
