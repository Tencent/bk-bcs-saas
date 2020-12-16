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
from typing import Dict, List
from unittest.mock import patch, MagicMock
from dataclasses import make_dataclass

from kubernetes import client

from backend.resources.namespace import namespace


def test_list_namespace_quota():
    Status = make_dataclass("Status", [("hard", Dict), ("used", Dict)])
    Metadata = make_dataclass("Metadata", [("name", str), ("namespace", str)])
    ResourceQuota = make_dataclass("ResourceQuota", [("metadata", Metadata), ("status", Status)])
    Items = make_dataclass("Items", [("items", List)])
    return_value = Items(items=[ResourceQuota(
        metadata=Metadata(name="test", namespace="test"),
        status=Status(
            hard={
                "limits.cpu": "2",
                "limits.memory": "2Gi",
                "requests.cpu": "1",
                "requests.memory": "1Gi"
            },
            used={
                "limits.cpu": "0",
                "limits.memory": "0",
                "requests.cpu": "0",
                "requests.memory": "0"
            }
        )
    )])
    with patch("backend.resources.client.create_api_client") as mock_create_api_client, patch(
        "backend.resources.mixins.CoreAPIClassMixins.get_api_cls_list"
    ) as mock_api_cls_list:
        api_client = client.ApiClient(client.Configuration())
        mock_create_api_client.return_value = api_client
        mock_api_cls_list.return_value = [f"CoreV1Api"]
        quota_client = namespace.NamespaceQuota("access_token", "project_id", "cluster_id")

        quota_client.client.list_namespaced_resource_quota = MagicMock(return_value=return_value)
        quota_list = quota_client.list_namespace_quota("namespace")
        assert len(quota_list) == len(return_value.items)
