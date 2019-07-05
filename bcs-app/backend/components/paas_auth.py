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
from backend.components import paas_cc
from backend.components.enterprise.iam import BKIAMClient
from backend.components.enterprise.iam import get_access_token as get_access_token_by_iam


def get_project_code_by_id(access_token, project_id):
    result = paas_cc.get_project(access_token, project_id)
    project = result.get('data') or {}
    project_code = project.get('english_name', '')
    return project_code


def get_access_token():
    """获取非用户态access_toke
    """
    return get_access_token_by_iam()


def verify_project(access_token, project_id, user_id):
    """@note：项目标识为 project_code 而不是 project_id
    """
    project_code = get_project_code_by_id(access_token, project_id)
    iam_client = BKIAMClient(project_code)
    return iam_client.verify_project(user_id, project_code)


def get_role_list(access_token, project_id, need_user=False):
    """获取角色列表(权限中心暂时没有角色的概念，先获取所有用户)
    """
    # 根据 project_id 获取 project_code
    project_code = get_project_code_by_id(access_token, project_id)
    iam_client = BKIAMClient(project_code)
    user_res = iam_client.get_project_users()
    user_data = user_res.get('data') or []
    role_list = []
    for _u in user_data:
        # 所有用户都设置为项目成员
        role_list.append({
            "display_name": "项目成员",
            "role_id": 0,
            "role_name": "manager",
            "user_id": _u,
            "user_type": "user"
        })
    return role_list


def get_project_user(access_token, project_id, group_code=''):
    """获取项目用户列表
    """
    # 根据 project_id 获取 project_code
    project_code = get_project_code_by_id(access_token, project_id)
    iam_client = BKIAMClient(project_code)
    return iam_client.get_project_users()


def verify_project_by_user(access_token, project_id, project_code, user_id):
    """
    验证用户是否有项目权限
    """
    iam_client = BKIAMClient(project_code)
    return iam_client.verify_project(user_id, project_code)
