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
from dataclasses import dataclass
from typing import Dict, List, Optional, Type

from backend.iam.permissions.perm import PermCtx
from backend.packages.blue_krill.data_types.enum import EnumField, StructuredEnum

from .. import decorators
from ..perm import Permission
from ..request import ActionResourcesRequest, ResourceRequest
from .cluster import related_cluster_perm

ResourceType = 'namespace'


class NamespaceAction(str, StructuredEnum):
    CREATE = EnumField('namespace_create', label='namespace_create')
    VIEW = EnumField('namespace_view', label='namespace_view')
    UPDATE = EnumField('namespace_update', label='namespace_update')
    DELETE = EnumField('namespace_delete', label='namespace_delete')
    USE = EnumField('namespace_use', label='namespace_use')


@dataclass
class NamespacePermCtx(PermCtx):
    project_id: str = ''
    cluster_id: str = ''
    namespace_id: Optional[str] = None


class NamespaceRequest(ResourceRequest):
    resource_type: str = ResourceType
    attr = {'_bk_iam_path_': f'/project,{{project_id}}/cluster,{{cluster_id}}/'}

    def _make_attribute(self, res_id: str) -> Dict:
        self.attr['_bk_iam_path_'] = self.attr['_bk_iam_path_'].format(
            project_id=self.attr_kwargs['project_id'], cluster_id=self.attr_kwargs['cluster_id']
        )
        return self.attr


class related_namespace_perm(decorators.RelatedPermission):

    module_name: str = ResourceType

    def _convert_perm_ctx(self, instance, args, kwargs) -> PermCtx:
        """仅支持第一个参数是 PermCtx 子类实例"""
        if len(args) <= 0:
            raise TypeError('missing NamespacePermCtx instance argument')
        if isinstance(args[0], PermCtx):
            return NamespacePermCtx(
                username=args[0].username,
                project_id=args[0].project_id,
                cluster_id=args[0].cluster_id,
                namespace_id=args[0].namespace_id,
            )
        else:
            raise TypeError('missing NamespacePermCtx instance argument')

    def _action_request_list(self, perm_ctx: NamespacePermCtx) -> List[ActionResourcesRequest]:
        """"""
        resources = [perm_ctx.namespace_id] if perm_ctx.namespace_id else None
        return [
            ActionResourcesRequest(
                resource_type=self.perm_obj.resource_type, action_id=self.action_id, resources=resources
            )
        ]


class namespace_perm(decorators.Permission):
    module_name: str = ResourceType


class NamespacePermission(Permission):
    """命名空间权限"""

    resource_type: str = ResourceType
    resource_request_cls: Type[ResourceRequest] = NamespaceRequest

    @related_cluster_perm(method_name='can_view')
    def can_create(self, perm_ctx: NamespacePermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, NamespaceAction.CREATE, raise_exception)

    @related_cluster_perm(method_name='can_view')
    def can_view(self, perm_ctx: NamespacePermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, NamespaceAction.VIEW, raise_exception, use_cache=True)

    @related_namespace_perm(method_name='can_view')
    def can_update(self, perm_ctx: NamespacePermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, NamespaceAction.UPDATE, raise_exception)

    @related_namespace_perm(method_name='can_view')
    def can_delete(self, perm_ctx: NamespacePermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, NamespaceAction.DELETE, raise_exception)

    @related_namespace_perm(method_name='can_view')
    def can_use(self, perm_ctx: NamespacePermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, NamespaceAction.USE, raise_exception)

    def _make_res_request(self, res_id: str, perm_ctx: NamespacePermCtx) -> ResourceRequest:
        return self.resource_request_cls(res_id, project_id=perm_ctx.project_id, cluster_id=perm_ctx.cluster_id)

    def _get_resource_id_from_ctx(self, perm_ctx: NamespacePermCtx) -> Optional[str]:
        return perm_ctx.namespace_id
