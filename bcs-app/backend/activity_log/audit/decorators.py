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
from functools import wraps
from typing import Type, List, Optional

from .auditors import Auditor
from .context import AuditContext


def log_audit_on_view(
    auditor_cls: Type[Auditor], activity_type: str, ignore_exception_classes: Optional[List[Exception]] = None
):
    """
    用于 view 的操作审计装饰器
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, request, *args, **kwargs):
            request.audit_ctx = AuditContext(
                user=request.user.username, project_id=request.project.project_id, activity_type=activity_type
            )

            ignore = False
            err_msg = ''
            try:
                resp = view_func(view, request, *args, **kwargs)
            except Exception as e:
                if ignore_exception_classes and type(e) in ignore_exception_classes:
                    ignore = True

                err_msg = str(e)
                raise
            else:
                return resp
            finally:
                if not ignore:
                    if not request.audit_ctx.extra:
                        request.audit_ctx.extra = _wrapped_view(request, **kwargs)
                    save_audit(auditor_cls, request.audit_ctx, err_msg)

        return _wrapped_view

    return decorator


def log_audit(auditor_cls: Type[Auditor], activity_type: str):
    """
    用于一般类实例方法或函数的操作审计装饰器，使用规则:
    - 类实例方法第二个位置参数必须是 AuditContext 实例
    - 普通方法，通常需要第一个位置参数是 AuditContext 实例
    """

    def decorator(func):
        @wraps(func)
        def _wrapped_view(*args, **kwargs):
            if len(args) <= 0:
                raise TypeError('missing AuditContext instance argument')

            if isinstance(args[0], AuditContext):
                audit_ctx = args[0]
            elif len(args) >= 2 and isinstance(args[1], AuditContext):
                audit_ctx = args[1]
            else:
                raise TypeError('missing AuditContext instance argument')

            err_msg = ''
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                err_msg = str(e)
                raise
            else:
                return ret
            finally:
                audit_ctx.activity_type = activity_type
                save_audit(auditor_cls, audit_ctx, err_msg)

        return _wrapped_view

    return decorator


def save_audit(auditor_cls, audit_ctx, err_msg):
    auditor = auditor_cls(audit_ctx)
    if err_msg:
        auditor.log_failed(err_msg)
    else:
        auditor.log_succeed()


def _gen_default_extra(request, **kwargs):
    extra = dict(**kwargs)
    if hasattr(request, 'data'):
        extra.update(request.data)
