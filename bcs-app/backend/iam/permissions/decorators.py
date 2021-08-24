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
import importlib
import logging
from abc import ABCMeta, abstractmethod
from typing import List, Type

import wrapt

from backend.utils.basic import str2bool
from backend.utils.response import PermsResponse

from .client import IAMClient
from .exceptions import PermissionDeniedError
from .perm import PermCtx
from .perm import Permission as PermPermission
from .request import ResourceRequest

logger = logging.getLogger(__name__)


class RelatedPermission(metaclass=ABCMeta):
    """
    用于资源 Permission 类的方法装饰, 目的是支持 related_actions.

    如 related_project_perm 和 related_cluster_perm 装饰器的用法:

    class ClusterPermission(Permission):

        resource_type: str = 'cluster'
        resource_request_cls: Type[ResourceRequest] = ClusterRequest

        @related_project_perm(method_name='can_view')
        def can_view(self, perm_ctx: ClusterPermCtx, raise_exception: bool = True, just_raise: bool = False) -> bool:
            return self.can_action(perm_ctx, ClusterAction.VIEW, raise_exception, just_raise)

        @related_cluster_perm(method_name='can_view')
        def can_manage(self, perm_ctx: ClusterPermCtx, raise_exception: bool = True, just_raise: bool = False) -> bool:
            return self.can_action(perm_ctx, ClusterAction.MANAGE, raise_exception, just_raise)

    """

    module_name: str  # 资源模块名 如 cluster, project

    def __init__(self, method_name: str):
        """
        :param method_name: 权限类的 can_{action} 方法名，用于校验用户是否具有对应的操作权限
        """
        self.method_name = method_name

    def _gen_perm_obj(self) -> PermPermission:
        """获取权限类实例，如 project.ProjectPermission"""
        p_module_name = __name__[: __name__.rfind(".")]
        try:
            return getattr(
                importlib.import_module(f'{p_module_name}.resources.{self.module_name}'),
                f'{self.module_name.capitalize()}Permission',
            )()
        except (ModuleNotFoundError, AttributeError) as e:
            logger.error('_gen_perm_obj error: %s', e)

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        self.perm_obj = self._gen_perm_obj()

        perm_ctx = self._convert_perm_ctx(instance, args, kwargs)

        try:
            is_allowed = wrapped(*args, **kwargs)
        except PermissionDeniedError as e:
            # 按照权限中心的建议，无论关联资源操作是否有权限，统一按照无权限返回，目的是生成最终的 apply_url
            perm_ctx.force_raise = True
            try:
                getattr(self.perm_obj, self.method_name)(perm_ctx)
            except PermissionDeniedError as err:
                raise PermissionDeniedError(
                    f'{e.message}; {err.message}',
                    username=perm_ctx.username,
                    action_request_list=e.action_request_list + err.action_request_list,
                )
        else:
            # 无权限，并且没有抛出 PermissionDeniedError, 说明 raise_exception = False
            if not is_allowed:
                return is_allowed

            logger.debug(f'continue to verify {self.method_name} {self.module_name} permission...')

            # 有权限时，继续校验关联操作的权限
            raise_exception = kwargs.get('raise_exception', True)
            return getattr(self.perm_obj, self.method_name)(perm_ctx, raise_exception=raise_exception)

    @abstractmethod
    def _convert_perm_ctx(self, instance, args, kwargs) -> PermCtx:
        """将被装饰的方法中的 perm_ctx 转换成 perm_obj.method_name 需要的 perm_ctx"""

    @property
    def action_id(self) -> str:
        return f'{self.perm_obj.resource_type}_{self.method_name[4:]}'


class Permission:
    """鉴权装饰器基类，用于装饰函数或者方法"""

    module_name: str  # 资源模块名 如 cluster, project

    def __init__(self, method_name: str):
        """
        :param method_name: 权限类的 can_{action} 方法名，用于校验用户是否具有对应的操作权限
        """
        self.method_name = method_name

    def _gen_perm_obj(self) -> PermPermission:
        """获取权限类实例，如 project.ProjectPermission"""
        p_module_name = __name__[: __name__.rfind(".")]
        try:
            return getattr(
                importlib.import_module(f'{p_module_name}.resources.{self.module_name}'),
                f'{self.module_name.capitalize()}Permission',
            )()
        except (ModuleNotFoundError, AttributeError) as e:
            logger.error('_gen_perm_obj error: %s', e)

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):

        self.perm_obj = self._gen_perm_obj()

        if len(args) <= 0:
            raise TypeError('missing PermCtx instance argument')
        if not isinstance(args[0], PermCtx):
            raise TypeError('missing ProjectPermCtx instance argument')

        getattr(self.perm_obj, self.method_name)(args[0])

        return wrapped(*args, **kwargs)


class response_perms:
    def __init__(
        self,
        action_id_list: List[str],
        res_request_cls: Type[ResourceRequest],
        resource_id_key: str = 'id',
        auto_add: bool = True,
    ):
        self.action_id_list = action_id_list
        self.res_request_cls = res_request_cls
        self.resource_id_key = resource_id_key
        self.auto_add = auto_add

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        resp = wrapped(*args, **kwargs)
        if not isinstance(resp, PermsResponse):
            raise ValueError('response_perms decorator only support PermsResponse')

        if not resp.resource_data:
            return resp

        with_perms = self.auto_add
        request = args[0]
        if not self.auto_add:
            with_perms = str2bool(request.query_params.get('with_perms') or True)

        if not with_perms:
            return resp

        client = IAMClient()
        if isinstance(resp.resource_data, list):
            res = [item.get(self.resource_id_key) for item in resp.resource_data]
        else:
            res = resp.resource_data.get(self.resource_id_key)

        iam_path_attrs = {}
        try:
            iam_path_attrs = {'project_id': request.project.project_id}
        except Exception:
            pass

        iam_path_attrs.update(resp.iam_path_attrs)
        perms = client.batch_resource_multi_actions_allowed(
            request.user.username,
            self.action_id_list,
            self.res_request_cls(res, **iam_path_attrs),
        )

        if hasattr(resp, "web_annotations"):
            resp.web_annotations = resp.web_annotations or {}
            resp.web_annotations.update({"perms": perms})
        else:
            resp.web_annotations = {"perms": perms}
        return resp
