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
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from backend.components.paas_auth import get_access_token
from backend.utils import FancyDict
from backend.utils.authentication import JWTClient, JWTUser

from . import constants


class JWTAndTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user = self.authenticate_jwt(request)
        return self.authenticate_token(request, user)

    def authenticate_jwt(self, request):
        client = JWTClient(request.META.get(constants.APIGW_JWT_KEY_NAME, ""))
        if not client.is_valid(constants.BCS_APP_APIGW_PUBLIC_KEY):
            raise exceptions.AuthenticationFailed(f"invalid {constants.APIGW_JWT_KEY_NAME}")

        username = client.user.username
        if not username and client.app.app_code in constants.trusted_app_list:
            username = request.META.get(constants.USERNAME_KEY_NAME, "")

        user = JWTUser(username=username)
        user.client = client
        return user

    def authenticate_token(self, request, user):
        access_token = request.META.get(constants.ACCESS_TOKEN_KEY_NAME, "")
        if access_token:
            try:
                from backend.components.paas_auth import get_user_by_access_token
            except ImportError:
                pass
            else:
                user = get_user_by_access_token(access_token)
                if user.get("user_id") != request.user.username:
                    raise exceptions.AuthenticationFailed(f"invalid {constants.ACCESS_TOKEN_KEY_NAME}")

            user.token = FancyDict(access_token=access_token)
        else:
            user.token = FancyDict(access_token=get_access_token().get("access_token"))

        return (user, None)
