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

from backend.iam.permissions import decorators
from backend.iam.permissions.perm import PermCtx, Permission
from backend.iam.permissions.request import ActionResourcesRequest, ResourceRequest
from backend.iam.permissions.resources.project import related_project_perm
from backend.packages.blue_krill.data_types.enum import EnumField, StructuredEnum

ResourceType = "templateset"


class TemplatesetAction(str, StructuredEnum):
    CREATE = EnumField("templateset_create", label="templateset_create")
    VIEW = EnumField("templateset_view", label="templateset_view")
    UPDATE = EnumField("templateset_update", label="templateset_update")
    DELETE = EnumField("templateset_delete", label="templateset_delete")
    INSTANTIATE = EnumField("templateset_instantiate", label="templateset_instantiate")


@dataclass
class TemplatesetPermCtx(PermCtx):
    project_id: str = ''
    templateset_id: Optional[str] = None


class TemplatesetRequest(ResourceRequest):
    resource_type: str = ResourceType
    attr = {'_bk_iam_path_': f'/templateset,{{templateset_id}}/'}

    def _make_attribute(self, res_id: str) -> Dict:
        self.attr['_bk_iam_path_'] = self.attr['_bk_iam_path_'].format(
            templateset_id=self.attr_kwargs['templateset_id']
        )
        return self.attr


class related_templateset_perm(decorators.RelatedPermission):
    module_name: str = ResourceType

    def _convert_perm_ctx(self, instance, args, kwargs) -> PermCtx:
        """仅支持第一个参数是 PermCtx 子类实例"""
        if len(args) <= 0:
            raise TypeError('missing TemplatesetPermCtx instance argument')
        if isinstance(args[0], PermCtx):
            return TemplatesetPermCtx(
                username=args[0].username, project_id=args[0].project_id, templateset_id=args[0].templateset_id
            )
        else:
            raise TypeError('missing TemplatesetPermCtx instance argument')

    def _action_request_list(self, perm_ctx: TemplatesetPermCtx) -> List[ActionResourcesRequest]:
        """"""
        resources = [perm_ctx.templateset_id] if perm_ctx.templateset_id else None
        return [
            ActionResourcesRequest(
                resource_type=self.perm_obj.resource_type, action_id=self.action_id, resources=resources
            )
        ]


class templateset_perm(decorators.Permission):
    module_name: str = ResourceType


class TemplatesetPermission(Permission):
    """模板集权限"""

    resource_type: str = ResourceType
    resource_request_cls: Type[ResourceRequest] = TemplatesetRequest

    @related_project_perm(method_name="can_view")
    def can_create(self, perm_ctx: TemplatesetPermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, TemplatesetAction.CREATE, raise_exception)

    @related_project_perm(method_name="can_view")
    def can_view(self, perm_ctx: TemplatesetPermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, TemplatesetAction.VIEW, raise_exception, use_cache=True)

    @related_templateset_perm(method_name="can_view")
    def can_update(self, perm_ctx: TemplatesetPermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, TemplatesetAction.UPDATE, raise_exception)

    @related_templateset_perm(method_name="can_view")
    def can_delete(self, perm_ctx: TemplatesetPermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, TemplatesetAction.DELETE, raise_exception)

    @related_templateset_perm(method_name="can_view")
    def can_instantiate(self, perm_ctx: TemplatesetPermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, TemplatesetAction.INSTANTIATE, raise_exception)

    def _make_res_request(self, res_id: str, perm_ctx: TemplatesetPermCtx) -> ResourceRequest:
        return self.resource_request_cls(res_id, templateset_id=perm_ctx.templateset_id)

    def _get_resource_id_from_ctx(self, perm_ctx: TemplatesetPermCtx) -> Optional[str]:
        return perm_ctx.templateset_id
