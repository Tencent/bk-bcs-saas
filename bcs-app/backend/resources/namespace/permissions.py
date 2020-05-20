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
from backend.resources import permissions
from backend.utils import FancyDict

POLICY_CODE_MAP = FancyDict({
    'EDIT': 'edit',
    'USE': 'use',
    'VIEW': 'view'
})
# 操作列表
POLICY_CODE_LIST = POLICY_CODE_MAP.values()

RES_TYPE_LIST = ['namespace']


def get_namespace_policy_list(policy_code_list):
    return permissions.get_resource_policy_list(RES_TYPE_LIST, policy_code_list)
