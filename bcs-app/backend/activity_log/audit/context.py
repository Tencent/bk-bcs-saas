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
from dataclasses import dataclass, field, fields
from typing import Dict


@dataclass
class AuditContext:
    user: str
    project_id: str
    description: str = ''
    resource_id: str = ''
    resource: str = ''
    resource_type: str = ''
    activity_type: str = ''
    activity_status: str = ''
    extra: Dict = field(default_factory=dict)

    def update(self, ctx: 'AuditContext'):
        """仅将 ctx 中的非空属性覆盖到当前实例中"""
        for f in fields(AuditContext):
            v = getattr(ctx, f.name)
            if v:
                setattr(self, f.name, v)

    def update_fields(self, **kwargs):
        """仅将 kwargs 中的非空并且合法的属性覆盖到当前实例中"""
        field_name_list = [f.name for f in fields(AuditContext)]
        for k in kwargs:
            if k in field_name_list and kwargs[k]:
                setattr(self, k, kwargs[k])
