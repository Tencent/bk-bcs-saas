# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import importlib
import logging

from .permissions.exceptions import AttrValidationError
from .permissions.perm import PermCtx, Permission

logger = logging.getLogger(__name__)


def make_perm_ctx(username: str, res_type: str, **ctx_kwargs) -> PermCtx:
    """根据资源类型，生成对应的perm ctx"""
    p_module_name = __name__[: __name__.rfind(".")]
    try:
        perm_ctx_cls = getattr(
            importlib.import_module(f'{p_module_name}.permissions.resources'), f'{res_type.capitalize()}PermCtx'
        )
    except (ModuleNotFoundError, AttributeError) as e:
        logger.error('make_res_permission error: %s', e)
        raise

    try:
        perm_ctx = perm_ctx_cls(username=username, **ctx_kwargs)
    except TypeError as e:
        logger.exception(e)
        raise AttrValidationError("perm ctx got an unexpected init argument")

    perm_ctx.validate()
    return perm_ctx


def make_res_permission(res_type: str) -> Permission:
    """根据资源类型，生成对应的permission"""
    p_module_name = __name__[: __name__.rfind(".")]
    try:
        perm_cls = getattr(
            importlib.import_module(f'{p_module_name}.permissions.resources'), f'{res_type.capitalize()}Permission'
        )
        return perm_cls()
    except (ModuleNotFoundError, AttributeError) as e:
        logger.error('make_res_permission error: %s', e)
        raise
