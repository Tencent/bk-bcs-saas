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
import mock
import pytest

from backend.bcs_web.viewsets import SystemViewSet

# @pytest.fixture(autouse=True)
# def patch_permissions():
#     """Patch permission checks to allow API requests, includes:
#
#     - paas_cc module: return faked project infos
#     - ProjectPermission: allow all permission checks
#     - get_api_public_key: return None
#     """
#     with mock.patch('backend.bcs_web.permissions.PaaSCCClient', new=FakePaaSCCClient), mock.patch(
#         'backend.bcs_web.permissions.permissions.ProjectPermission', new=FakeProjectPermission
#     ), mock.patch('backend.components.apigw.get_api_public_key', return_value=None):
#         yield


class TemplatesetsViewSet(SystemViewSet):
    def list(self, request, project):
        pass

    def create(self, request, project):
        pass


def install_chart():
    pass


class HelmViewSet(SystemViewSet):
    def create(self, request, project):
        pass


class TestAuditDecorator:

    pass
