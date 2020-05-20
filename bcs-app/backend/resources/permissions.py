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

from backend.components import paas_perm
from backend.utils import FancyDict
from backend.utils.error_codes import error_codes
from backend.utils.errcodes import ErrorCode

logger = logging.getLogger(__name__)

SERVICE_CODE = 'bcs'
POLICY_CODE_MAP = FancyDict({
    'CREATE': 'create',
    'DELETE': 'delete',
    'VIEW': 'view',
    'EDIT': 'edit',
    'USE': 'use',
    'DEPLOY': 'deploy',
    'DOWNLOAD': 'download'
})
# 操作列表
POLICY_CODE_LIST = POLICY_CODE_MAP.values()


def get_resource_policy_list(res_type_list, policy_list):
    p_res_list = []
    for p_code in policy_list:
        for res_type in res_type_list:
            p_res_list.append({'policy_code': p_code, 'resource_type': res_type})
    return p_res_list


def has_permission(user, project_id, resource_type, resource_code, policy_code):
    resp = paas_perm.verify_user_perm(
        user.user_access_token, project_id, SERVICE_CODE, policy_code,
        resource_type, resource_code, user.username
    )
    return resp.get('code') == ErrorCode.NoError


def get_multi_perm_resource(user, project_id, policy_list, is_exact_resource=1):
    resp = paas_perm.get_multi_perm_resource(user.user_access_token, project_id, SERVICE_CODE, user.username,
                                             policy_list, is_exact_resource)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.IAMCheckFailed(resp.get('message'))

    return resp.get('data') or []


def get_res_policy_data(user, project_id, policy_list):
    res_with_permissions = get_multi_perm_resource(
        user, project_id, policy_list
    )
    return {(item['resource_type'], item['policy_code']): item['resource_code_list']
            for item in res_with_permissions}
