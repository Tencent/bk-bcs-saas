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
from unittest.mock import MagicMock

import pytest

from backend.helm.toolkit.kubehelm.client import HelmClient, HelmError


@pytest.fixture
def helm_client():
    return HelmClient()


class TestHelmClient:
    def test_run(self, helm_client, random_name, namespace):
        helm_client.run = MagicMock(return_value=(b"success", b""))
        params = ("install", random_name, namespace, "/demo.tar.gz", ["--skip-crds", "--wait"])
        helm_client.run(*params)
        helm_client.run.assert_called_with(*params)

    def test_run_command_with_retry(self, helm_client):
        with pytest.raises(HelmError):
            helm_client._run_command_with_retry(cmd_args=["test"])
