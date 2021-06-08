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

from backend.container_service.clusters.views.node_views.tools.node import NodeFormatter

fake_inner_ip = "127.0.0.1"
fake_host_name = "ip-127-0-0-1-n-bcs-k8s-15091"


@pytest.mark.parametrize(
    "resource_dict,expected_data",
    [
        (
            {
                "metadata": {"labels": {"key": "value"}, "name": fake_host_name},
                "spec": {"taints": [{"key": "key", "value": "value", "effect": "NoSchedule"}]},
                "status": {
                    "addresses": [
                        {"address": fake_inner_ip, "type": "InternalIP"},
                        {"address": fake_host_name, "type": "Hostname"},
                    ]
                },
            },
            {
                fake_inner_ip: {
                    "host_name": fake_host_name,
                    "labels": {"key": "value"},
                    "taints": [{"key": "key", "value": "value", "effect": "NoSchedule"}],
                    "annotations": {},
                }
            },
        ),
        (
            {
                "metadata": {"labels": {"key": "value"}, "name": fake_host_name},
                "spec": {"taints": [{"key": "key", "value": "value", "effect": "NoSchedule"}]},
                "status": {
                    "addresses": [
                        {"address": "", "type": "InternalIP"},
                        {"address": "", "type": "Hostname"},
                    ]
                },
            },
            {},
        ),
    ],
)
def test_formatter(resource_dict, expected_data):
    formatted_data = NodeFormatter().format_dict(resource_dict)
    assert len(formatted_data) == len(expected_data)
    assert len(formatted_data.values()) == len(expected_data.values())

    if formatted_data:
        assert formatted_data[fake_inner_ip]["taints"] == expected_data[fake_inner_ip]["taints"]
        assert formatted_data[fake_inner_ip]["annotations"] == expected_data[fake_inner_ip]["annotations"]
        assert formatted_data[fake_inner_ip]["labels"] == expected_data[fake_inner_ip]["labels"]
