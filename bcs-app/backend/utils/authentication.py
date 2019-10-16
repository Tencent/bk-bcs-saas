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

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import exceptions as jwt_exceptions
from rest_framework.authentication import BaseAuthentication, SessionAuthentication

from backend.utils import FancyDict

logger = logging.getLogger(__name__)

User = get_user_model()


class JWTUser(User):

    @property
    def is_authenticated(self):
        return True

    class Meta(object):
        app_label = 'bkpaas_auth'


class JWTClient(object):

    def __init__(self, content):
        self.content = content
        self.payload = {}
        self.headers = {}

    @property
    def project(self):
        return FancyDict(self.payload.get('project') or {})

    @property
    def user(self):
        return FancyDict(self.payload.get('user') or {})

    @property
    def app(self):
        return FancyDict(self.payload.get('app') or {})

    def is_valid(self, apigw_public_key=None):
        if not self.content:
            return False

        try:
            if apigw_public_key is None:
                apigw_public_key = settings.APIGW_PUBLIC_KEY

            self.headers = jwt.get_unverified_header(self.content)
            self.payload = jwt.decode(self.content, apigw_public_key, issuer='APIGW')
            return True
        except jwt_exceptions.InvalidTokenError as error:
            logger.error("check jwt error, %s", error)
            return False
        except Exception:
            logger.exception("check jwt exception")
            return False

    def __str__(self):
        return '<%s, %s>' % (self.headers, self.payload)


class JWTAuthentication(BaseAuthentication):
    JWT_KEY_NAME = 'HTTP_X_BKAPI_JWT'

    def authenticate(self, request):
        client = JWTClient(request.META.get(self.JWT_KEY_NAME, ''))
        if not client.is_valid():
            return None

        user = JWTUser(username=client.user.username)
        return (user, None)


class CsrfExceptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class NoAuthError(Exception):
    pass
