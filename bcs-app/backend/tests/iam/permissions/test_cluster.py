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
from unittest import mock

import pytest

from backend.iam.permissions.resources.cluster import ClusterPermCtx, ClusterPermission
from backend.iam.permissions.resources.project import ProjectPermission, project_perm

from ..fake_iam import FakeClusterPermission, FakeProjectPermission
from . import roles


@pytest.fixture
def cluster_permission_obj():
    patcher = mock.patch.object(ClusterPermission, '__bases__', (FakeClusterPermission,))
    project_patcher = mock.patch.object(ProjectPermission, '__bases__', (FakeProjectPermission,))
    with patcher, project_patcher, mock.patch.object(project_perm, 'perm_type', new=ProjectPermission):
        patcher.is_local = True  # 标注为本地属性，__exit__ 的时候恢复成 patcher.temp_original
        project_patcher.is_local = True
        yield ClusterPermission()


class TestClusterPermission:
    def test_can_view(self, cluster_permission_obj, project_id, cluster_id):
        perm_ctx = ClusterPermCtx(username=roles.ADMIN_USER, project_id=project_id, cluster_id=cluster_id)
        assert cluster_permission_obj.can_view(perm_ctx)
