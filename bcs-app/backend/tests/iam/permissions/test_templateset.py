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

from ..fake_iam import FakeProjectPermission, FakeTemplatesetPermission
from . import roles
from .conftest import generate_apply_url


@pytest.fixture
def templateset_permission_obj():
    templateset_patcher = mock.patch.object(TemplatesetPermission, '__bases__', (FakeTemplatesetPermission,))
    project_patcher = mock.patch.object(ProjectPermission, '__bases__', (FakeProjectPermission,))
    with templateset_patcher, project_patcher:
        templateset_patcher.is_local = True  # 标注为本地属性，__exit__ 的时候恢复成 patcher.temp_original
        project_patcher.is_local = True
        yield TemplatesetPermission()


class TestTemplatesetPermission:
    """
    模板集资源权限
    note: 仅测试 templateset_create 和 templateset_view 两种代表性的权限，其他操作权限逻辑重复
    """

    def test_can_create(self, templateset_permission_obj, project_id, template_id):
        perm_ctx = TemplatesetPermCtx(username=roles.ADMIN_USER, project_id=project_id)
        assert templateset_permission_obj.can_create(perm_ctx)

    def test_can_not_create(self, templateset_permission_obj, project_id, template_id):
        perm_ctx = TemplatesetPermCtx(username=roles.ANONYMOUS_USER, project_id=project_id)
        assert not templateset_permission_obj.can_create(perm_ctx, raise_exception=False)

    def test_can_view(self, templateset_permission_obj, project_id, template_id):
        perm_ctx = TemplatesetPermCtx(username=roles.ADMIN_USER, project_id=project_id, template_id=template_id)
        assert templateset_permission_obj.can_view(perm_ctx)

    def test_can_not_view(self, templateset_permission_obj, project_id, template_id):
        """测试场景: 无权限不抛出异常"""
        perm_ctx = TemplatesetPermCtx(username=roles.ANONYMOUS_USER, project_id=project_id, template_id=template_id)
        assert not templateset_permission_obj.can_view(perm_ctx, raise_exception=False)

    def test_can_not_view_templateset(self, templateset_permission_obj, project_id, template_id):
        """测试场景：有项目权限但无模板集权限"""
        self._test_can_not_view(
            roles.PROJECT_NO_TEMPLATESET_USER,
            templateset_permission_obj,
            project_id,
            template_id,
            expected_action_list=[
                ActionResourcesRequest(
                    resource_type=templateset_permission_obj.resource_type,
                    action_id=TemplatesetAction.VIEW,
                    resources=[template_id],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def test_can_not_view_project(self, templateset_permission_obj, project_id, template_id):
        """测试场景：有模板集权限但无项目权限"""
        self._test_can_not_view(
            roles.TEMPLATESET_NO_PROJECT_USER,
            templateset_permission_obj,
            project_id,
            template_id,
            expected_action_list=[
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                )
            ],
        )

    def test_can_not_view_project_and_templateset(self, templateset_permission_obj, project_id, template_id):
        """测试场景：模板集和项目均无权限"""
        self._test_can_not_view(
            roles.ANONYMOUS_USER,
            templateset_permission_obj,
            project_id,
            template_id,
            expected_action_list=[
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.VIEW,
                    resources=[template_id],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def _test_can_not_view(self, username, templateset_permission_obj, project_id, template_id, expected_action_list):
        perm_ctx = TemplatesetPermCtx(username=username, project_id=project_id, template_id=template_id)
        with pytest.raises(PermissionDeniedError) as exec:
            templateset_permission_obj.can_view(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(username, expected_action_list)

    def test_can_not_instantiate_templateset_and_project(self, templateset_permission_obj, project_id, template_id):
        """测试场景：模板集和项目均无权限"""
        username = roles.ANONYMOUS_USER
        perm_ctx = TemplatesetPermCtx(username=username, project_id=project_id, template_id=template_id)
        with pytest.raises(PermissionDeniedError) as exec:
            templateset_permission_obj.can_instantiate(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.INSTANTIATE,
                    resources=[template_id],
                ),
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.VIEW,
                    resources=[template_id],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def test_can_not_instantiate_project(self, templateset_permission_obj, project_id, template_id):
        """测试场景：有模板集权限，无项目权限"""
        username = roles.TEMPLATESET_NO_PROJECT_USER
        perm_ctx = TemplatesetPermCtx(username=username, project_id=project_id, template_id=template_id)
        with pytest.raises(PermissionDeniedError) as exec:
            templateset_permission_obj.can_instantiate(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                )
            ],
        )


@templateset_perm(method_name='can_instantiate')
def instantiate_templateset(perm_ctx: TemplatesetPermCtx):
    """"""


class TestTemplatesetPermDecorator:
    def test_can_instantiate(self, templateset_permission_obj, project_id, template_id):
        perm_ctx = TemplatesetPermCtx(username=roles.ADMIN_USER, project_id=project_id, template_id=template_id)
        instantiate_templateset(perm_ctx)

    def test_can_not_instantiate(self, templateset_permission_obj, project_id, template_id):
        username = roles.ANONYMOUS_USER
        perm_ctx = TemplatesetPermCtx(username=username, project_id=project_id, template_id=template_id)
        with pytest.raises(PermissionDeniedError) as exec:
            instantiate_templateset(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.INSTANTIATE,
                    resources=[template_id],
                ),
                ActionResourcesRequest(
                    resource_type=TemplatesetPermission.resource_type,
                    action_id=TemplatesetAction.VIEW,
                    resources=[template_id],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )
