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


@pytest.fixture
def bcs_cc_nodes():
    return {
        "127.0.0.1": {"inner_ip": "127.0.0.1", "status": "initializing"},
        "127.0.0.2": {"inner_ip": "127.0.0.2", "status": "normal"},
        "127.0.0.3": {"inner_ip": "127.0.0.3", "status": "initial_failed"},
    }


@pytest.fixture
def cluster_nodes():
    return {
        "127.0.0.2": {"inner_ip": "127.0.0.2", "status": "Ready", "unschedulable": False, "node_name": "127.0.0.2"},
        "127.0.0.4": {"inner_ip": "127.0.0.3", "status": "Ready", "unschedulable": False, "node_name": "127.0.0.4"},
    }
