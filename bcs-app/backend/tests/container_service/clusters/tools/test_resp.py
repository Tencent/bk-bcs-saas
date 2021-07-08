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

from backend.container_service.clusters.tools.resp import NodeClient
from backend.tests.testing_utils.mocks.node import StubNodeClient


class TestNodeClient:
    @patch("backend.container_service.clusters.tools.resp.Node", new=StubNodeClient)
    def test_normal(self, ctx_cluster):
        client = NodeClient(ctx_cluster)
        data = client.do("list")
        assert len(data) > 0

    @patch("backend.container_service.clusters.tools.resp.Node", new=StubNodeClient)
    def test_exception(self, ctx_cluster):
        client = NodeClient(ctx_cluster)
        with pytest.raises(NotImplementedError):
            client.do("")
