# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from unittest import TestCase

from .utils import render_helm_values


class TestRenderHelmValue(TestCase):
    def test_http_protocol(self):
        protocol_type = "http"
        print(render_helm_values(protocol_type, 1))

    def test_https_protocol(self):
        protocol_type = "https"
        print(render_helm_values(protocol_type, 1))

    def test_http_https_protocol(self):
        protocol_type = "http;https"
        print(render_helm_values(protocol_type, 1))

    def test_replica(self):
        replica_count = 2
        print(render_helm_values("https;http", replica_count))
