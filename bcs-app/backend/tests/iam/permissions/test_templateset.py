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

from backend.iam.permissions.exceptions import PermissionDeniedError
from backend.iam.permissions.request import ActionResourcesRequest
from backend.iam.permissions.resources.project import ProjectAction, ProjectPermission
from backend.iam.permissions.resources.templateset import (
    TemplatesetAction,
    TemplatesetPermCtx,
    TemplatesetPermission,
    templateset_perm,
)

from ..fake_iam import FakeProjectPermission, FakeTemplateSetPermission
from . import roles
from .conftest import generate_apply_url


@pytest.fixture
def template_set_permission_obj():
    template_set_patcher = mock.patch.object(TemplatesetPermission, '__bases__', (FakeTemplateSetPermission,))
    project_patcher = mock.patch.object(ProjectPermission, '__bases__', (FakeProjectPermission,))
    with template_set_patcher, project_patcher:
        template_set_patcher.is_local = True  # 标注为本地属性，__exit__ 的时候恢复成 patcher.temp_original
        project_patcher.is_local = True
        yield TemplatesetPermission()


class TestTemplateSetPermission:
    """
    模板集资源权限
    note: 仅测试 templateset_create 和 templateset_view 两种代表性的权限，其他操作权限逻辑重复
    """

    def test_can_create(self, template_set_permission_obj, project_id, template_set_id):
        perm_ctx = TemplatesetPermCtx(username=roles.ADMIN_USER, project_id=project_id)
        assert template_set_permission_obj.can_create(perm_ctx)

    def test_can_not_create(self, template_set_permission_obj, project_id, template_set_id):
        perm_ctx = TemplatesetPermCtx(username=roles.ANONYMOUS_USER, project_id=project_id)
        assert not template_set_permission_obj.can_create(perm_ctx, raise_exception=False)

    def test_can_view(self, template_set_permission_obj, project_id, template_set_id):
        perm_ctx = TemplatesetPermCtx(username=roles.ADMIN_USER, project_id=project_id, templateset_id=template_set_id)
        assert template_set_permission_obj.can_view(perm_ctx)

    def test_can_not_view(self, template_set_permission_obj, project_id, template_set_id):
        """测试场景: 无权限不抛出异常"""
        perm_ctx = TemplatesetPermCtx(
            username=roles.ANONYMOUS_USER, project_id=project_id, templateset_id=template_set_id
        )
        assert not template_set_permission_obj.can_view(perm_ctx, raise_exception=False)

    def test_can_not_view_template_set(self, template_set_permission_obj, project_id, template_set_id):
        """测试场景：有项目权限但无模板集权限"""
        self._test_can_not_view(
            roles.PROJECT_NO_TEMPLATE_SET_USER,
            template_set_permission_obj,
            project_id,
            template_set_id,
            expected_action_list=[
                ActionResourcesRequest(
                    resource_type=template_set_permission_obj.resource_type,
                    action_id=TemplatesetAction.VIEW,
                    resources=[template_set_id],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def test_can_not_view_project(self, template_set_permission_obj, project_id, template_set_id):
        """测试场景：有模板集权限但无项目权限"""
        self._test_can_not_view(
            roles.TEMPLATE_SET_NO_PROJECT_USER,
            template_set_permission_obj,
            project_id,
            template_set_id,
            expected_action_list=[
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                )
            ],
        )

    def test_can_not_view_project_and_template_set(self, template_set_permission_obj, project_id, template_set_id):
        """测试场景：模板集和项目均无权限"""
        self._test_can_not_view(
            roles.ANONYMOUS_USER,
            template_set_permission_obj,
            project_id,
            template_set_id,
            expected_action_list=[
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.VIEW,
                    resources=[template_set_id],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def _test_can_not_view(
        self, username, template_set_permission_obj, project_id, template_set_id, expected_action_list
    ):
        perm_ctx = TemplatesetPermCtx(username=username, project_id=project_id, templateset_id=template_set_id)
        with pytest.raises(PermissionDeniedError) as exec:
            template_set_permission_obj.can_view(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(username, expected_action_list)

    def test_can_not_instantiate_template_set_and_project(
        self, template_set_permission_obj, project_id, template_set_id
    ):
        """测试场景：模板集和项目均无权限"""
        username = roles.ANONYMOUS_USER
        perm_ctx = TemplatesetPermCtx(username=username, project_id=project_id, templateset_id=template_set_id)
        with pytest.raises(PermissionDeniedError) as exec:
            template_set_permission_obj.can_instantiate(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.INSTANTIATE,
                    resources=[template_set_id],
                ),
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.VIEW,
                    resources=[template_set_id],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def test_can_not_instantiate_project(self, template_set_permission_obj, project_id, template_set_id):
        """测试场景：有模板集权限，无项目权限"""
        username = roles.TEMPLATE_SET_NO_PROJECT_USER
        perm_ctx = TemplatesetPermCtx(username=username, project_id=project_id, templateset_id=template_set_id)
        with pytest.raises(PermissionDeniedError) as exec:
            template_set_permission_obj.can_instantiate(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                )
            ],
        )


@templateset_perm(method_name='can_instantiate')
def instantiate_template_set(perm_ctx: TemplatesetPermCtx):
    """"""


class TestTemplateSetPermDecorator:
    def test_can_instantiate(self, template_set_permission_obj, project_id, template_set_id):
        perm_ctx = TemplatesetPermCtx(username=roles.ADMIN_USER, project_id=project_id, templateset_id=template_set_id)
        instantiate_template_set(perm_ctx)

    def test_can_not_instantiate(self, template_set_permission_obj, project_id, template_set_id):
        username = roles.ANONYMOUS_USER
        perm_ctx = TemplatesetPermCtx(username=username, project_id=project_id, templateset_id=template_set_id)
        with pytest.raises(PermissionDeniedError) as exec:
            instantiate_template_set(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.INSTANTIATE,
                    resources=[template_set_id],
                ),
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.VIEW,
                    resources=[template_set_id],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )
