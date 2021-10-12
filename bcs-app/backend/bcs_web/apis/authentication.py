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
from rest_framework.authentication import BaseAuthentication

from backend.utils.authentication import JWTClient, JWTUser

from .constants import APIGW_JWT_KEY_NAME, BCS_APP_APIGW_PUBLIC_KEY, USERNAME_KEY_NAME

# 受信任的app可以从header获取用户名.(私有化版本apigw不支持bk_username传参)
trusted_app_list = ["bk_bcs_monitor", "bk_harbor", "bk_bcs", "workbench"]


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        client = JWTClient(request.META.get(APIGW_JWT_KEY_NAME, ""))
        if not client.is_valid(BCS_APP_APIGW_PUBLIC_KEY):
            return None

        username = client.user.username
        if not username and client.app.app_code in trusted_app_list:
            username = request.META.get(USERNAME_KEY_NAME, "")

        user = JWTUser(username=username)
        user.client = client

        return (user, None)
