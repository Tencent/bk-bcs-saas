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
"""
权限中心API
"""

import logging

from django.conf import settings

from backend.components.utils import http_delete, http_post, http_put, http_get
from backend.utils import cache

logger = logging.getLogger(__name__)


class BKIAMClient(object):
    def __init__(self, project_code):
        self.project_code = project_code

        self.system_id = 'bcs'
        self.system_prefix = 'bkiam/api/v1/perm/systems'

        self.bk_app_code = settings.APP_ID
        self.bk_app_secret = settings.APP_TOKEN
        # 头部添加X-BK-APP-CODE和X-BK-APP-SECRET 作为服务间认证鉴权
        self.headers = {
            'X-BK-APP-CODE': self.bk_app_code,
            'X-BK-APP-SECRET': self.bk_app_secret
        }
        self.kwargs = {"headers": self.headers, "timeout": 10}

    def verify_user_perm(self, user_id, action_id, resource_type, resource_id):
        """
        查询用户是否有某个资源某个的权限
        """
        url = f'{settings.BK_IAM_HOST}/{self.system_prefix}/{self.system_id}/resources-perms/verify'
        data = {
            "scope_type": "project",
            "scope_id": self.project_code,
            "principal_type": "user",
            "principal_id": user_id,
            "action_id": action_id,
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return http_post(url, json=data, **self.kwargs)

    def get_multi_perm_resource(self, user_id, res_list):
        """
        批量查询用户有某个权限的资源
        res_list:[
                {
                    "action_id": "read",
                    "resource_type": "namespace",
                },
                {
                    "action_id": "manage",
                    "resource_type": "namespace"
                }
            ]
        """
        url = f'{settings.BK_IAM_HOST}/{self.system_prefix}/{self.system_id}/authorized-resources/search'
        data = {
            "scope_type": "project",
            "scope_id": self.project_code,
            "principal_type": "user",
            "principal_id": user_id,
            "resource_types_actions": res_list
        }
        return http_post(url, json=data, **self.kwargs)

    def register_res(self, user_id, resource_type, resource_id, resource_name):
        """
        注册资源到权限中心
        """
        url = f'{settings.BK_IAM_HOST}/{self.system_prefix}/{self.system_id}/resources'
        data = {
            "scope_type": "project",
            "scope_id": self.project_code,
            "creator_type": "user",
            "creator_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "resource_name": resource_name
        }
        return http_post(url, json=data, **self.kwargs)

    def delete_res(self, resource_type, resource_id):
        """
        删除资源
        """
        url = f'{settings.BK_IAM_HOST}/{self.system_prefix}/{self.system_id}/resources'
        data = {
            "scope_type": "project",
            "scope_id": self.project_code,
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return http_delete(url, json=data, **self.kwargs)

    def update_res(self, resource_type, resource_id, resource_name):
        """
        更新资源
        """
        url = f'{settings.BK_IAM_HOST}/{self.system_prefix}/{self.system_id}/resources'
        data = {
            "scope_type": "project",
            "scope_id": self.project_code,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "resource_name": resource_name
        }
        return http_put(url, json=data, **self.kwargs)

    def get_authorized_projects(self, user_id):
        """
        获取用户有权限的项目列表
        """
        url = f'{settings.BK_IAM_HOST}/bkiam/api/v1/perm/scope_type/project/authorized-scopes'
        data = {
            "principal_type": "user",
            "principal_id": user_id
        }
        res = http_post(url, json=data, **self.kwargs)
        data = res.get('data') or {}
        return data

    def verify_project(self, user_id, project_code):
        """
        验证用户是否有项目权限
        """
        url = f'{settings.BK_IAM_HOST}/bkiam/api/v1/perm/scope_type/project/scopes/{self.project_code}/scopes-perms/verify'  # noqa
        data = {
            "principal_type": "user",
            "principal_id": user_id
        }
        res = http_post(url, json=data, **self.kwargs)
        data = res.get('data') or {}
        return data.get('is_pass') or False

    def get_access_token_by_credentials(self, bk_token):
        """获取access_token
        """
        url = f'{settings.BK_IAM_HOST}/bkiam/api/v1/auth/access-tokens'
        data = {
            'env_name': 'prod',
            'grant_type': 'authorization_code',
            'id_provider': 'bk_login',
        }
        credentials = {
            'bk_token': bk_token,
        }
        data.update(credentials)
        return http_post(url, json=data, **self.kwargs)

    def get_client_access_token(self):
        """获取非用户态access_token
        """
        url = f'{settings.BK_IAM_HOST}/bkiam/api/v1/auth/access-tokens'
        data = {
            'grant_type': 'client_credentials',
            'id_provider': 'client'
        }
        return http_post(url, json=data, **self.kwargs)

    def get_project_users(self):
        """获取项目的所有用户
        """
        url = f'{settings.BK_IAM_HOST}/bkiam/api/v1/perm/scope_type/project/scopes/{self.project_code}/principal_type/user/principals'  # noqa
        return http_get(url, **self.kwargs)


# ################# 权限中心 Auth 模块API #################
def get_access_token():
    """获取没有登录态的 access_token，用于执行后台任务
    """
    # 注意: 调用生成access_token接口不需要项目
    client = BKIAMClient('')
    result = client.get_client_access_token()
    token_dict = result.get('data') or {}
    logger.debug('New access token exchanged by credentials, token=%s', token_dict.get('access_token'))
    return token_dict


@cache.region.cache_on_arguments(expiration_time=240)
def get_access_token_by_credentials(bk_token):
    """Request a new request token by credentials
    """
    client = BKIAMClient('fake_project_id')
    result = client.get_access_token_by_credentials(bk_token)
    token_dict = result['data']
    logger.debug('New access token exchanged by credentials, token=%s', token_dict['access_token'])
    return token_dict
