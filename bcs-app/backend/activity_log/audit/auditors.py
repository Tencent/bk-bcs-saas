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
from dataclasses import asdict

from ..models import UserActivityLog
from .context import AuditContext


class Auditor:
    """提供操作审计日志记录功能"""

    def __init__(self, audit_context: AuditContext):
        self.audit_context = audit_context

    def log_succeed(self):
        self._log('succeed')

    def log_failed(self, err_msg: str = ''):
        self._log('failed', err_msg)

    def _log(self, activity_status: str, err_msg: str = ''):
        if not self.audit_context.description:
            self.audit_context.description = self._gen_default_description(activity_status, err_msg)
        self.audit_context.activity_status = activity_status
        UserActivityLog.objects.create(**asdict(self.audit_context))

    def _gen_default_description(self, activity_status: str, err_msg: str):
        audit_context = self.audit_context
        description_prefix = f'{audit_context.activity_type} {audit_context.resource_type}'
        if audit_context.resource:
            description_prefix = f'{description_prefix} {audit_context.resource}'

        if err_msg:
            return f'{description_prefix} {activity_status}: {err_msg}'
        return f'{description_prefix} {activity_status}'


class TemplatesetAuditor(Auditor):
    def __init__(self, audit_context: AuditContext):
        super().__init__(audit_context)
        self.audit_context.resource_type = 'templateset'


class HelmAuditor(Auditor):
    def __init__(self, audit_context: AuditContext):
        super().__init__(audit_context)
        self.audit_context.resource_type = 'helm'
