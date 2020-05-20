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
from . import utils
from .permissions import get_namespace_policy_list, POLICY_CODE_LIST
from backend.resources.permissions import get_res_policy_data
from backend.utils.error_codes import error_codes


def _add_permissions_fields(namespaces, ns_policy_data, policy_code_list):
    for ns in namespaces:
        permissions = {p_code: False for p_code in policy_code_list}
        # ns_policy_data like {('namespace', 'view'): ['namespaceA', 'namespaceB']}
        for res_policy_key in ns_policy_data:
            if str(ns['id']) in ns_policy_data[res_policy_key]:
                p_code = res_policy_key[1]
                permissions[p_code] = True
        ns['permissions'] = permissions


def get_namespaces_by_cluster_id(user, project_id, cluster_id, policy_code_list=None):
    namespaces = utils.get_namespaces_by_cluster_id(user.access_token, project_id, cluster_id)
    if not namespaces:
        return []

    policy_code_list = policy_code_list or POLICY_CODE_LIST
    ns_policy_data = get_res_policy_data(user, project_id, get_namespace_policy_list(policy_code_list))
    if not ns_policy_data:
        raise error_codes.IAMCheckFailed(
            f'{user.username} have no permissions for namespaces in cluster_id {cluster_id}')

    _add_permissions_fields(namespaces, ns_policy_data, policy_code_list)
    return namespaces
