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
import pytest

from backend.iam.permissions.exceptions import PermissionDeniedError
from backend.iam.permissions.request import ActionResourcesRequest, IAMResource
from backend.iam.permissions.resources.cluster import ClusterAction, ClusterPermission
from backend.iam.permissions.resources.constants import ResourceType
from backend.iam.permissions.resources.namespace import (
    NamespaceAction,
    NamespacePermCtx,
    NamespacePermission,
    calc_iam_ns_id,
    namespace_perm,
)
from backend.iam.permissions.resources.project import ProjectAction, ProjectPermission
from backend.tests.iam.conftest import generate_apply_url

from . import roles


class TestNamespacePermission:
    """
    命名空间资源权限
    note: 仅测试 namespace_use 这一代表性的权限，其他操作权限逻辑重复
    """

    def test_can_not_create_cluster_project(self, namespace_permission_obj, project_id, cluster_id):
        username = roles.NAMESPACE_NO_CLUSTER_PROJECT_USER
        perm_ctx = NamespacePermCtx(username=username, project_id=project_id, cluster_id=cluster_id)
        with pytest.raises(PermissionDeniedError) as exec:
            namespace_permission_obj.can_create(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=ClusterPermission.resource_type,
                    action_id=ClusterAction.VIEW,
                    resources=[cluster_id],
                    parent_chain=[IAMResource(ResourceType.Project, project_id)],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def test_can_not_use(self, namespace_permission_obj, project_id, cluster_id, namespace_name):
        username = roles.ANONYMOUS_USER
        perm_ctx = NamespacePermCtx(
            username=username, project_id=project_id, cluster_id=cluster_id, name=namespace_name
        )
        with pytest.raises(PermissionDeniedError) as exec:
            namespace_permission_obj.can_use(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=NamespacePermission.resource_type,
                    action_id=NamespaceAction.USE,
                    resources=[perm_ctx.iam_ns_id],
                    parent_chain=[
                        IAMResource(ResourceType.Project, project_id),
                        IAMResource(ResourceType.Cluster, cluster_id),
                    ],
                ),
                ActionResourcesRequest(
                    resource_type=NamespacePermission.resource_type,
                    action_id=NamespaceAction.VIEW,
                    resources=[perm_ctx.iam_ns_id],
                    parent_chain=[
                        IAMResource(ResourceType.Project, project_id),
                        IAMResource(ResourceType.Cluster, cluster_id),
                    ],
                ),
                ActionResourcesRequest(
                    resource_type=ClusterPermission.resource_type,
                    action_id=ClusterAction.VIEW,
                    resources=[cluster_id],
                    parent_chain=[IAMResource(ResourceType.Project, project_id)],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def test_can_not_use_cluster_project(self, namespace_permission_obj, project_id, cluster_id, namespace_name):
        """测试场景: 有命名空间使用权限，但是无集群和项目权限"""
        username = roles.NAMESPACE_NO_CLUSTER_PROJECT_USER
        perm_ctx = NamespacePermCtx(
            username=username, project_id=project_id, cluster_id=cluster_id, name=namespace_name
        )

        # 不抛出异常
        assert not namespace_permission_obj.can_use(perm_ctx, raise_exception=False)

        # 抛出异常
        with pytest.raises(PermissionDeniedError) as exec:
            namespace_permission_obj.can_use(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=ClusterPermission.resource_type,
                    action_id=ClusterAction.VIEW,
                    resources=[cluster_id],
                    parent_chain=[IAMResource(ResourceType.Project, project_id)],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )


@namespace_perm(method_name='can_use')
def helm_install(perm_ctx: NamespacePermCtx):
    """helm install 到某个命名空间"""


class TestNamespacePermDecorator:
    def test_can_not_create(self, namespace_permission_obj, project_id, cluster_id):
        username = roles.ANONYMOUS_USER
        perm_ctx = NamespacePermCtx(username=username, project_id=project_id, cluster_id=cluster_id)
        with pytest.raises(PermissionDeniedError) as exec:
            namespace_permission_obj.can_create(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=ClusterPermission.resource_type,
                    action_id=NamespaceAction.CREATE,
                    resources=[cluster_id],
                    parent_chain=[IAMResource(ResourceType.Project, project_id)],
                ),
                ActionResourcesRequest(
                    resource_type=ClusterPermission.resource_type,
                    action_id=ClusterAction.VIEW,
                    resources=[cluster_id],
                    parent_chain=[IAMResource(ResourceType.Project, project_id)],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )

    def test_can_use(self, namespace_permission_obj, project_id, cluster_id, namespace_name):
        perm_ctx = NamespacePermCtx(
            username=roles.ADMIN_USER, project_id=project_id, cluster_id=cluster_id, name=namespace_name
        )
        helm_install(perm_ctx)

    def test_can_not_manage(self, namespace_permission_obj, project_id, cluster_id, namespace_name):
        username = roles.ANONYMOUS_USER
        perm_ctx = NamespacePermCtx(
            username=username, project_id=project_id, cluster_id=cluster_id, name=namespace_name
        )
        with pytest.raises(PermissionDeniedError) as exec:
            helm_install(perm_ctx)
        assert exec.value.data['apply_url'] == generate_apply_url(
            username,
            [
                ActionResourcesRequest(
                    resource_type=NamespacePermission.resource_type,
                    action_id=NamespaceAction.USE,
                    resources=[perm_ctx.iam_ns_id],
                    parent_chain=[
                        IAMResource(ResourceType.Project, project_id),
                        IAMResource(ResourceType.Cluster, cluster_id),
                    ],
                ),
                ActionResourcesRequest(
                    resource_type=NamespacePermission.resource_type,
                    action_id=NamespaceAction.VIEW,
                    resources=[perm_ctx.iam_ns_id],
                    parent_chain=[
                        IAMResource(ResourceType.Project, project_id),
                        IAMResource(ResourceType.Cluster, cluster_id),
                    ],
                ),
                ActionResourcesRequest(
                    resource_type=ClusterPermission.resource_type,
                    action_id=ClusterAction.VIEW,
                    resources=[cluster_id],
                    parent_chain=[IAMResource(ResourceType.Project, project_id)],
                ),
                ActionResourcesRequest(
                    resource_type=ProjectPermission.resource_type, action_id=ProjectAction.VIEW, resources=[project_id]
                ),
            ],
        )


@pytest.mark.parametrize(
    'cluster_id, namespace_name, expected',
    [
        ('BCS-K8S-40000', 'test-default', 'BCS-K8S-40000:test-default'),
        ('BCS-K8S-40000', 'abc' * 30, 'BCS-K8S-40000:daa54284568d250dde'),
        ('BCS-K8S-40000', None, None),
    ],
)
def test_calc_cluster_ns_id(cluster_id, namespace_name, expected):
    assert calc_iam_ns_id(cluster_id, namespace_name) == expected
