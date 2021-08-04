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
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Type

from django.conf import settings
from iam import IAM, Action, MultiActionRequest, Request, Resource, Subject

from .exceptions import PermissionDeniedError
from .request import ActionResourcesRequest, ResourceRequest


@dataclass
class PermCtx:
    """
    权限参数上下文
    note: 由于 force_raise 默认值的原因，其子类属性必须设置默认值
    """

    username: str
    force_raise: bool = False  # 如果为 True, 表示不做权限校验，直接以无权限方式抛出异常


class Permission(metaclass=ABCMeta):
    """
    对接 IAM 的权限基类
    """

    resource_type: str = ''
    resource_request_cls: Type[ResourceRequest] = ResourceRequest
    iam = IAM(settings.APP_ID, settings.APP_TOKEN, settings.BK_IAM_HOST, settings.BK_PAAS_INNER_HOST)

    def can_action(self, perm_ctx: PermCtx, action_id: str, raise_exception: bool, use_cache: bool = False) -> bool:
        """
        :param perm_ctx: 权限校验的上下文，至少包含用户名
        :param action_id: 资源操作 ID
        :param raise_exception: 无权限时，是否抛出异常
        :param use_cache: 是否使用本地缓存 (缓存时间 1 min) 校验权限。用于非敏感操作鉴权，比如 view 操作
        """
        res_id = self._get_resource_id_from_ctx(perm_ctx)

        if perm_ctx.force_raise:
            self._raise_permission_denied_error(res_id, perm_ctx, action_id)

        if res_id:
            res_request = self._make_res_request(res_id, perm_ctx)
            is_allowed = self.resource_inst_allowed(perm_ctx.username, action_id, res_request, use_cache)
        else:
            is_allowed = self.resource_type_allowed(perm_ctx.username, action_id, use_cache)

        if raise_exception and not is_allowed:
            self._raise_permission_denied_error(res_id, perm_ctx, action_id)

        return is_allowed

    def grant_resource_creator_actions(self, username: str, resource_id: str, resource_name: str):
        """
        用于创建资源时，注册用户对该资源的关联操作权限.
        note: 具体的关联操作见权限模型的 resource_creator_actions 字段
        """
        data = {
            "type": self.resource_type,
            "id": resource_id,
            "name": resource_name,
            "system": settings.APP_ID,
            "creator": username,
        }
        return self.iam._client.grant_resource_creator_actions(None, username, data)

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

        :params res_maker: 单个资源
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

        :params res_maker: 多个资源
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

    def _make_res_request(self, res_id: str, perm_ctx: PermCtx) -> ResourceRequest:
        return self.resource_request_cls(res_id)

    def _raise_permission_denied_error(self, res_id: str, perm_ctx: PermCtx, action_id: str):
        resources = [res_id] if res_id else None
        action_request_list = [
            ActionResourcesRequest(resource_type=self.resource_type, action_id=action_id, resources=resources)
        ]
        raise PermissionDeniedError(
            f"no {action_id} permission",
            username=perm_ctx.username,
            action_request_list=action_request_list,
        )

    @abstractmethod
    def _get_resource_id_from_ctx(self, perm_ctx: PermCtx) -> Optional[str]:
        """"""
