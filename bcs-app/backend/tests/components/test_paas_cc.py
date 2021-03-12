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
from requests_mock import ANY

from backend.components.base import ComponentAuth
from backend.components.paas_cc import PaaSCCClient


class TestPaaSCCClient:
    def test_get_cluster_simple(self, project_id, cluster_id, requests_mock):
        requests_mock.get(ANY, json={'foo': 'bar'})

        client = PaaSCCClient(ComponentAuth('token'))
        resp = client.get_cluster(project_id, cluster_id)
        assert resp == {'foo': 'bar'}
        assert requests_mock.called
