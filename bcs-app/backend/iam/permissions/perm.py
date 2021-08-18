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
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Type

from .client import IAMClient
from .exceptions import PermissionDeniedError
from .request import ActionResourcesRequest, ResourceRequest

logger = logging.getLogger(__name__)


@dataclass
class PermCtx:
    """
    权限参数上下文
    note: 由于 force_raise 默认值的原因，其子类属性必须设置默认值
    """

    username: str
    force_raise: bool = False  # 如果为 True, 表示不做权限校验，直接以无权限方式抛出异常


class Permission(ABC, IAMClient):
    """
    对接 IAM 的权限基类
    """

    resource_type: str = ''
    resource_request_cls: Type[ResourceRequest] = ResourceRequest
    parent_res_perm: Optional['Permission'] = None  # 父级资源的权限类对象

    def can_action(self, perm_ctx: PermCtx, action_id: str, raise_exception: bool, use_cache: bool = False) -> bool:
        """
        :param perm_ctx: 权限校验的上下文
        :param action_id: 资源操作 ID
        :param raise_exception: 无权限时，是否抛出异常
        :param use_cache: 是否使用本地缓存 (缓存时间 1 min) 校验权限。用于非敏感操作鉴权，比如 view 操作
        """
        if perm_ctx.force_raise:
            self._raise_permission_denied_error(perm_ctx, action_id)

        is_allowed = self._can_action(perm_ctx, action_id, use_cache)

        if raise_exception and not is_allowed:
            self._raise_permission_denied_error(perm_ctx, action_id)

        return is_allowed

    def grant_resource_creator_actions(self, username: str, resource_id: str, resource_name: str):
        """
        用于创建资源时，注册用户对该资源的关联操作权限.
        note: 具体的关联操作见权限模型的 resource_creator_actions 字段
        """
        return self._grant_resource_creator_actions(username, self.resource_type, resource_id, resource_name)

    def make_res_request(self, res_id: str, perm_ctx: PermCtx) -> ResourceRequest:
        """创建当前资源 request"""
        return self.resource_request_cls(res_id)

    def has_parent_resource(self) -> bool:
        return self.parent_res_perm is not None

    def _can_action(self, perm_ctx: PermCtx, action_id: str, use_cache: bool = False) -> bool:
        res_id = self._get_resource_id(perm_ctx)

        if res_id:  # 与当前资源实例相关
            res_request = self.make_res_request(res_id, perm_ctx)
            return self.resource_inst_allowed(perm_ctx.username, action_id, res_request, use_cache)

        # 与当前资源实例无关, 并且无关联上级资源, 按资源实例无关处理
        if not self.has_parent_resource():
            return self.resource_type_allowed(perm_ctx.username, action_id, use_cache)

        # 有关联上级资源
        request_method = getattr(self.parent_res_perm, 'make_res_request')
        res_request = request_method(res_id=self._get_parent_resource_id(perm_ctx), perm_ctx=perm_ctx)
        return self.resource_inst_allowed(perm_ctx.username, action_id, res_request, use_cache)

    def _raise_permission_denied_error(self, perm_ctx: PermCtx, action_id: str):
        res_id = self._get_resource_id(perm_ctx)

        resources = None
        resource_type = self.resource_type

        if res_id:
            resources = [res_id]
        elif self.has_parent_resource():
            resource_type = self.parent_res_perm.resource_type
            resources = [self._get_parent_resource_id(perm_ctx)]

        raise PermissionDeniedError(
            f"no {action_id} permission",
            username=perm_ctx.username,
            action_request_list=[
                ActionResourcesRequest(action_id=action_id, resource_type=resource_type, resources=resources)
            ],
        )

    @abstractmethod
    def _get_resource_id(self, perm_ctx: PermCtx) -> Optional[str]:
        """从 ctx 中获取当前资源对应的 id"""

    @abstractmethod
    def _get_parent_resource_id(self, perm_ctx: PermCtx) -> Optional[str]:
        """从 ctx 中获取当前资源关联的父级资源的 id"""