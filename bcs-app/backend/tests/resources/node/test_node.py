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
#
import copy
from unittest import mock

import pytest
from kubernetes.dynamic.exceptions import ResourceNotFoundError

from backend.resources.node.client import Node

from ..conftest import FakeBcsKubeConfigurationService

fake_inner_ip = "127.0.0.1"
fake_node_name = "bcs-test-node"
fake_labels = {"bcs-test": "test"}
fake_taints = {"key": "test", "value": "tet", "effect": "NoSchedule"}


class TestNode:
    @pytest.fixture(autouse=True)
    def use_faked_configuration(self):
        with mock.patch(
            'backend.resources.utils.kube_client.BcsKubeConfigurationService',
            new=FakeBcsKubeConfigurationService,
        ):
            yield

    @pytest.fixture
    def client(self, ctx_cluster):
        return Node(ctx_cluster)

    @pytest.fixture
    def create_and_delete_node(self, client):
        client.update_or_create(
            body={
                "apiVersion": "v1",
                "kind": "Node",
                "metadata": {"name": fake_node_name, "labels": fake_labels},
                "spec": {"taints": [fake_taints]},
                "status": {
                    "addresses": [
                        {"address": fake_inner_ip, "type": "InternalIP"},
                    ],
                    "conditions": [
                        {
                            "lastHeartbeatTime": "2021-07-07T04:13:48Z",
                            "lastTransitionTime": "2020-09-16T05:24:53Z",
                            "message": "kubelet is posting ready status",
                            "reason": "KubeletReady",
                            "status": "True",
                            "type": "Ready",
                        }
                    ],
                },
            },
            name=fake_node_name,
        )
        yield
        client.delete_wait_finished(fake_node_name)

    def test_query_node(self, client, create_and_delete_node):
        nodes = client.list()
        assert len(nodes) > 0
        assert fake_inner_ip in [node["inner_ip"] for node in nodes]

    def test_query_labels(self, client, create_and_delete_node):
        labels = client.query_labels(node_name_list=[fake_node_name])
        assert fake_inner_ip in labels
        assert labels[fake_inner_ip] == fake_labels

    def test_query_taints(self, client, create_and_delete_node):
        taints = client.query_taints(node_name_list=[fake_node_name])
        assert fake_inner_ip in taints
        assert fake_taints in taints[fake_inner_ip]

    @pytest.mark.parametrize(
        "field, node_id_name, expected_data",
        [
            (["kind"], "inner_ip", "Node"),
            (["metadata", "labels"], "name", fake_labels),
            (["apiVersion"], "name", "v1"),
        ],
    )
    def test_query_field_data(self, field, node_id_name, expected_data, client, create_and_delete_node):
        data = client.query_field_data(field, [fake_node_name], node_id_name=node_id_name)
        node_id = fake_inner_ip if node_id_name == "inner_ip" else fake_node_name
        assert data[node_id] == expected_data

    @pytest.mark.parametrize(
        "labels, expected",
        [
            ({"bcs-test": "v1"}, {"bcs-test": "v1"}),
            ({"bcs-test": "v1", "bcs-test1": "v2"}, {"bcs-test": "v1", "bcs-test1": "v2"}),
            ({"bcs-test1": "v2"}, {"bcs-test1": "v2"}),
            ({}, {}),
        ],
    )
    def test_set_labels(self, labels, expected, client, create_and_delete_node):
        client.set_labels([{"node_name": fake_node_name, "labels": labels}])
        # 查询label
        node_labels = client.query_labels(node_name_list=[fake_node_name])
        assert node_labels[fake_inner_ip] == expected

    @pytest.mark.parametrize(
        "taints, expected",
        [
            ([{"key": "test", "value": "", "effect": "NoSchedule"}], [{"key": "test", "effect": "NoSchedule"}]),
            ([], []),
        ],
    )
    def test_set_taints(self, taints, expected, client, create_and_delete_node):
        client.set_taints([{"node_name": fake_node_name, "taints": taints}])
        node_taints = client.query_taints(node_name_list=[fake_node_name])
        assert expected == node_taints[fake_inner_ip]
