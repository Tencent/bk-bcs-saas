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

from backend.tests.bcs_mocks.misc import FakePaaSCCMod, FakeProjectPermissionAllowAll
from backend.utils.cache import region

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def patch_permissions():
    """Patch permission checks to allow API requests, includes:

    - paas_cc module: return faked project infos
    - ProjectPermission: allow all permission checks
    - get_api_public_key: return None
    """
    with mock.patch('backend.utils.base.permissions.paas_cc', new=FakePaaSCCMod()), mock.patch(
        'backend.utils.permissions.permissions.ProjectPermission', new=FakeProjectPermissionAllowAll
    ), mock.patch('backend.components.apigw.get_api_public_key', return_value=None):
        yield


class TestViewSets:
    def test_userviewset(self, api_client, project_id):
        resp = api_client.get(f'/apis/projects/{project_id}/status/')
        data = resp.json()['data']

        assert data[project_id] == 'ok'
        assert region.get(f'BK_DEVOPS_BCS:PROJECT_ID:{project_id}') == project_id
        assert region.get(f'BK_DEVOPS_BCS:ENABLED_BCS_PROJECT:{project_id}').project_id == project_id
