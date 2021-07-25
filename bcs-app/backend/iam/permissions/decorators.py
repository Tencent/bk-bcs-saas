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
from typing import List, Type

import wrapt

from .exceptions import PermissionDeniedError
from .perm import ActionResourcesRequest, ApplyURLGenerator, PermCtx, Permission


class PermissionDecorator(metaclass=ABCMeta):

    perm_type: Type[Permission]

    def __init__(self, method_name: str):
        """
        :param method_name: 权限类的 can_{action} 方法名，用于校验用户是否具有对应的操作权限
        """
        self.method_name = method_name

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        perm_ctx = self._convert_perm_ctx(instance, args, kwargs)

        try:
            is_allowed = wrapped(*args, **kwargs)
        except PermissionDeniedError as e:
            # 按照权限中心的建议，直接把关联的操作资源统一生成 apply_url，让用户都申请一次
            action_request_list = e.action_request_list + self._action_request_list(perm_ctx)
            raise PermissionDeniedError(
                f'no {self.action_id} permission; {e.message}',
                apply_url=ApplyURLGenerator.generate_apply_url(perm_ctx.username, action_request_list),
                action_request_list=action_request_list,
            )

        # 无权限，并且没有抛出 PermissionDeniedError, 说明 raise_exception = False
        if not is_allowed:
            return is_allowed

        # 有权限时，继续校验关联操作的权限
        raise_exception = kwargs.get('raise_exception', True)
        return getattr(self.perm_type(), self.method_name)(perm_ctx, raise_exception=raise_exception)

    @abstractmethod
    def _convert_perm_ctx(self, instance, args, kwargs) -> PermCtx:
        """"""

    @abstractmethod
    def _action_request_list(self, perm_ctx: PermCtx) -> List[ActionResourcesRequest]:
        """"""

    @property
    def action_id(self) -> str:
        action = self.method_name.split('can_')[1]
        return f'{self.perm_type.resource_type}_{action}'
