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

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

from backend.components.utils import http_get
from backend.components.enterprise import iam
from backend.utils.authentication import NoAuthError

logger = logging.getLogger(__name__)


class IAMAccessToken(object):
    def __init__(self, credentials):
        self.credentials = credentials
        self.bk_token = credentials['bk_token']

    @property
    def access_token(self):
        data = iam.get_access_token_by_credentials(self.bk_token)
        return data['access_token']


class BKTokenAuthentication(BaseAuthentication):
    """企业版bk_token校验
    """

    def verify_bk_token(self, bk_token):
        """校验是否
        """
        url = f'{settings.BK_PAAS_HOST}/login/accounts/is_login/'
        params = {'bk_token': bk_token}
        resp = http_get(url, params=params)
        if resp.get('result') is not True:
            raise NoAuthError(resp.get('message', ''))

        return resp['data']['username']

    def get_credentials(self, request):
        return {
            'bk_token': request.COOKIES.get('bk_token'),
        }

    def get_user(self, username):
        user_model = get_user_model()
        defaults = {'is_active': True, 'is_staff': False, 'is_superuser': False}
        user, _ = user_model.objects.get_or_create(username=username, defaults=defaults)
        return user

    def authenticate(self, request):
        auth_credentials = self.get_credentials(request)
        if not auth_credentials['bk_token']:
            return None

        credentials = request.session.get('auth_credentials')
        if not credentials or credentials != auth_credentials:
            try:
                username = self.verify_bk_token(**auth_credentials)
            except NoAuthError as error:
                logger.info('%s authentication error: %s', auth_credentials['bk_token'], error)
                return None
            except Exception as error:
                logger.exception('ticket authentication error: %s', error)
                return None

            # 缓存auth_credentials
            auth_credentials['username'] = username
            request.session['auth_credentials'] = auth_credentials
        else:
            username = credentials['username']

        user = self.get_user(username)
        user.token = IAMAccessToken(auth_credentials)
        return (user, None)
