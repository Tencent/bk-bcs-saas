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
from typing import Dict, List, Optional, Type

from django.conf import settings
from iam import IAM, Action, MultiActionRequest, Request, Resource, Subject

from .exceptions import PermissionDeniedError
from .request import ActionResourcesRequest, ResourceRequest

logger = logging.getLogger(__name__)


class IAMClient:
    """提供基础的 iam client 方法封装"""

    iam = IAM(settings.APP_ID, settings.APP_TOKEN, settings.BK_IAM_HOST, settings.BK_PAAS_INNER_HOST)

    def resource_type_allowed(self, username: str, action_id: str, use_cache: bool = False) -> bool:
        """
        判断用户是否具备某个操作的权限
        note: 权限判断与资源实例无关，如创建某资源
        """
        request = self._make_request(username, action_id)
        if not use_cache:
            return self.iam.is_allowed(request)
        return self.iam.is_allowed_with_cache(request)

    def resource_inst_allowed(
        self, username: str, action_id: str, res_request: ResourceRequest, use_cache: bool = False
    ) -> bool:
        """
        判断用户对某个资源实例是否具有指定操作的权限
        note: 权限判断与资源实例有关，如更新某个具体资源
        """
        request = self._make_request(username, action_id, resources=res_request.make_resources())
        if not use_cache:
            return self.iam.is_allowed(request)
        return self.iam.is_allowed_with_cache(request)

    def resource_type_multi_actions_allowed(self, username: str, action_ids: List[str]) -> Dict[str, bool]:
        """
        判断用户是否具备多个操作的权限
        note: 权限判断与资源实例无关，如创建某资源

        :returns 示例 {'project_create': True}
        """
        return {action_id: self.resource_type_allowed(username, action_id) for action_id in action_ids}

    def resource_inst_multi_actions_allowed(
        self, username: str, action_ids: List[str], res_request: ResourceRequest
    ) -> Dict[str, bool]:
        """
        判断用户对某个资源实例是否具有多个操作的权限.
        note: 权限判断与资源实例有关，如更新某个具体资源

        :returns 示例 {'project_view': True, 'project_edit': False}
        """
        actions = [Action(action_id) for action_id in action_ids]
        request = MultiActionRequest(
            settings.APP_ID, Subject("user", username), actions, res_request.make_resources(), None
        )
        return self.iam.resource_multi_actions_allowed(request)

    def batch_resource_multi_actions_allowed(
        self, username: str, action_ids: List[str], res_request: ResourceRequest
    ) -> Dict[str, Dict[str, bool]]:
        """
        判断用户对某些资源是否具有多个指定操作的权限
        note: 当前sdk仅支持同类型的资源

        :returns 示例 {'0ad86c25363f4ef8adcb7ac67a483837': {'project_view': True, 'project_edit': False}}
        """
        actions = [Action(action_id) for action_id in action_ids]
        request = MultiActionRequest(settings.APP_ID, Subject("user", username), actions, [], None)
        return self.iam.batch_resource_multi_actions_allowed(request, res_request.make_resources())

    def _make_request(self, username: str, action_id: str, resources: Optional[List[Resource]] = None) -> Request:
        return Request(
            settings.APP_ID,
            Subject("user", username),
            Action(action_id),
            resources,
            None,
        )

    def _grant_resource_creator_actions(self, username: str, resource_type: str, resource_id: str, resource_name: str):
        """
        用于创建资源时，注册用户对该资源的关联操作权限.
        note: 具体的关联操作见权限模型的 resource_creator_actions 字段
        """
        data = {
            "type": resource_type,
            "id": resource_id,
            "name": resource_name,
            "system": settings.APP_ID,
            "creator": username,
        }
        return self.iam._client.grant_resource_creator_actions(None, username, data)


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
    parent_perm_obj: Optional['Permission'] = None

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

    def has_parent(self) -> bool:
        return self.parent_perm_obj is not None

    def _can_action(self, perm_ctx: PermCtx, action_id: str, use_cache: bool = False) -> bool:
        res_id = self._get_resource_id(perm_ctx)

        if res_id:  # 与当前资源实例相关
            res_request = self.make_res_request(res_id, perm_ctx)
            return self.resource_inst_allowed(perm_ctx.username, action_id, res_request, use_cache)

        # 与当前资源实例无关, 并且无关联上级资源, 按资源实例无关处理
        if not self.has_parent():
            return self.resource_type_allowed(perm_ctx.username, action_id, use_cache)

        # 有关联上级资源
        request_method = getattr(self.parent_perm_obj, 'make_res_request')
        res_request = request_method(res_id=self._get_parent_resource_id(perm_ctx), perm_ctx=perm_ctx)
        return self.resource_inst_allowed(perm_ctx.username, action_id, res_request, use_cache)

    def _raise_permission_denied_error(self, perm_ctx: PermCtx, action_id: str):
        res_id = self._get_resource_id(perm_ctx)

        resources = None
        resource_type = self.resource_type

        if res_id:
            resources = [res_id]
        elif self.has_parent():
            resource_type = self.parent_perm_obj.resource_type
            resources = [self._get_parent_resource_id(perm_ctx)]

        raise PermissionDeniedError(
            f"no {action_id} permission",
            username=perm_ctx.username,
            action_request_list=[
                ActionResourcesRequest(resource_type=resource_type, action_id=action_id, resources=resources)
            ],
        )

    @abstractmethod
    def _get_resource_id(self, perm_ctx: PermCtx) -> Optional[str]:
        """从 ctx 中获取当前资源对应的 id"""

    @abstractmethod
    def _get_parent_resource_id(self, perm_ctx: PermCtx) -> Optional[str]:
        """从 ctx 中获取当前资源关联的父级资源的 id"""