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
from typing import List, Optional, Type

from .auditors import Auditor
from .context import AuditContext


class BaseLogAudit(metaclass=ABCMeta):
    """
    带参数的审计装饰器(抽象基类)。参数说明
    - auditor_cls: 执行审计记录的类, 默认为 Auditor
    - activity_type: 操作类型，默认为''。可在 audit_ctx 中覆盖
    - auto_audit: 是否记录审计，默认为记录
    - ignore_exception_classes: 忽略审计的异常类列表
    """

    def __init__(
        self,
        auditor_cls: Type[Auditor] = type(Auditor),
        activity_type: str = '',
        auto_audit: bool = True,
        ignore_exception_classes: Optional[List[Type[Exception]]] = None,
    ):
        self.auditor_cls = auditor_cls
        self.activity_type = activity_type
        self.auto_audit = auto_audit
        self.ignore_exception_classes = ignore_exception_classes

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            audit_ctx = self._pre_audit_ctx(*args, **kwargs)
            err_msg = ''

            try:
                ret = func(*args, **kwargs)
                return ret
            except Exception as e:
                # 如果是 ignore_exception_classes 中的异常，不做审计记录
                if self.ignore_exception_classes and type(e) in self.ignore_exception_classes:
                    self.auto_audit = False
                else:
                    err_msg = str(e)
                raise

            finally:
                if self.auto_audit:
                    audit_ctx = self._post_audit_ctx(audit_ctx, *args, **kwargs)
                    self._save_audit(audit_ctx, err_msg)

        return wrapper

    @abstractmethod
    def _pre_audit_ctx(self, *args, **kwargs) -> AuditContext:
        """前置获取初始 audit_ctx"""
        pass

    def _post_audit_ctx(self, audit_ctx: AuditContext, *args, **kwargs) -> AuditContext:
        """后置更新 audit_ctx"""
        return audit_ctx

    def _save_audit(self, audit_ctx: AuditContext, err_msg: str):
        """审计内容入库: 如果 err_msg 有错误信息，则审计状态标记为 failed; 否则 succeed"""
        auditor = self.auditor_cls(audit_ctx)
        if err_msg:
            auditor.log_failed(err_msg)
        else:
            auditor.log_succeed()


class log_audit_on_view(BaseLogAudit):
    """
    用于 view 的操作审计装饰器

    使用示例:
    class TemplatesetsViewSet(SystemViewSet):

        @log_audit_on_view(TemplatesetsAuditor, activity_type='create')
        def create(self, request, project_id):
            request.audit_ctx.update_fields(resource='nginx')
            return Response()
    """

    def _pre_audit_ctx(self, *args, **kwargs) -> AuditContext:
        request = args[1]
        if hasattr(request, 'audit_ctx'):
            request.audit_ctx.update_fields(activity_type=self.activity_type)
        else:
            request.audit_ctx = AuditContext(
                user=request.user.username,
                project_id=self._get_project_id(request, **kwargs),
                activity_type=self.activity_type,
            )
        return request.audit_ctx

    def _post_audit_ctx(self, audit_ctx: AuditContext, *args, **kwargs) -> AuditContext:
        """根据请求参数，生成默认的extra"""
        if audit_ctx.extra:
            return audit_ctx

        # TODO 优化默认 extra 的构成
        request = args[1]
        extra = dict(**kwargs)
        if hasattr(request, 'data'):
            if isinstance(request.data, dict):
                extra.update(request.data)
            elif isinstance(request.data, str):
                extra['body'] = request.data

        audit_ctx.extra = extra
        return audit_ctx

    def _get_project_id(self, request, **kwargs) -> str:
        if hasattr(request, 'project'):
            return request.project.project_id
        return kwargs.get('project_id', '')


class log_audit(BaseLogAudit):
    """
    用于一般类实例方法或函数的操作审计装饰器。使用规则:
    - 对于类实例方法，第二个位置参数必须是 AuditContext 实例
    - 对于普通方法，通常需要第一个位置参数是 AuditContext 实例

    使用示例:

    @log_audit(HelmAuditor, activity_type='install')
    def install_chart(audit_ctx: AuditContext):
        audit_ctx.update_fields(
            description='test install helm', extra={'chart': 'http://example.chart.com/nginx/nginx1.12.tgz'}
        )
    """

    def _pre_audit_ctx(self, *args, **kwargs) -> AuditContext:
        if len(args) <= 0:
            raise TypeError('missing AuditContext instance argument')

        if isinstance(args[0], AuditContext):
            audit_ctx = args[0]

        elif len(args) >= 2 and isinstance(args[1], AuditContext):
            audit_ctx = args[1]
        else:
            raise TypeError('missing AuditContext instance argument')

        if not audit_ctx.activity_type:
            audit_ctx.activity_type = self.activity_type
        return audit_ctx
