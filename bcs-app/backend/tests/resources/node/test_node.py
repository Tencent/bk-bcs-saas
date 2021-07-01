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
import pytest

from backend.resources.node.formatter import NodeFormatter, NodeResourceData

fake_inner_ip = "127.0.0.1"
fake_node_name = "ip-127-0-0-1-n-bcs-k8s-15091"
fake_resource_data = {
    "metadata": {"labels": {"key": "value"}, "name": fake_node_name},
    "spec": {"taints": [{"key": "key", "value": "value", "effect": "NoSchedule"}]},
    "status": {
        "addresses": [
            {"address": fake_inner_ip, "type": "InternalIP"},
            {"address": fake_node_name, "type": "Hostname"},
        ]
    },
}


class TestNodeFormatter:
    @pytest.mark.parametrize(
        "resource_dict,expected_data",
        [(fake_resource_data, NodeResourceData(name=fake_node_name, inner_ip=fake_inner_ip, data=fake_resource_data))],
    )
    def test_from_dict(self, resource_dict, expected_data):
        format = NodeFormatter()
        node_data = format.format_dict(resource_dict)
        assert node_data.name == expected_data.name
        assert node_data.inner_ip == expected_data.inner_ip
