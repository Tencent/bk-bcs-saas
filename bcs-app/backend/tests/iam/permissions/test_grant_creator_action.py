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
from unittest import mock

import pytest

from backend.iam.permissions.resources import NamespacePermission, ProjectPermission, TemplatesetPermission
from backend.iam.permissions.resources.namespace import NamespaceCreatorActionCtx
from backend.iam.permissions.resources.project import ProjectCreatorActionCtx
from backend.iam.permissions.resources.templateset import TemplatesetCreatorActionCtx

from ..fake_iam import FakeIAMClient
from . import roles


@pytest.fixture(autouse=True)
def patch_iam_client():
    with mock.patch(
        'backend.iam.permissions.client.IAMClient._grant_resource_creator_actions',
        FakeIAMClient().grant_resource_creator_actions,
    ):
        yield


class TestIamGrantCreatorAction:
    def test_templateset_grant_creator_action(self, template_id, template_name, project_id):
        """模板集，单层ancestors"""
        perm = TemplatesetPermission()
        result, data = perm.grant_resource_creator_actions(
            username=roles.ADMIN_USER,
            res_create_action_ctx=TemplatesetCreatorActionCtx(
                resource_id=template_id, resource_name=template_name, project_id=project_id, username=roles.ADMIN_USER
            ),
        )
        assert result is True
        assert data["id"] == template_id
        assert data["ancestors"][0]["id"] == project_id

    def test_namespace_grant_creator_action(self, namespace, namespace_name, project_id, cluster_id):
        """命名空间，多层ancestors，先porject后cluster"""
        perm = NamespacePermission()
        result, data = perm.grant_resource_creator_actions(
            roles.ADMIN_USER,
            NamespaceCreatorActionCtx(
                resource_id=namespace,
                resource_name=namespace_name,
                project_id=project_id,
                cluster_id=cluster_id,
                username=roles.ADMIN_USER,
            ),
        )
        assert result is True
        assert data["id"] == namespace
        assert data["ancestors"][1]["id"] == cluster_id

    def test_project_grant_creator_action(self, random_name, project_id):
        """项目 无上层则无ancestors"""
        result, data = ProjectPermission().grant_resource_creator_actions(
            roles.ADMIN_USER,
            ProjectCreatorActionCtx(
                resource_id=project_id,
                resource_name=random_name,
                username=roles.ADMIN_USER,
            ),
        )
        assert result is True
        assert data["id"] == project_id
        assert "ancestors" not in data
