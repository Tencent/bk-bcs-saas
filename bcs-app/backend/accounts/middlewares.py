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

from django.utils.deprecation import MiddlewareMixin

from backend.utils.local import local

logger = logging.getLogger(__name__)


class DisableCSRFCheck(MiddlewareMixin):
    """本地开发，去掉django rest framework强制的csrf检查"""

    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)


class RequestProvider(object):
    """request_id中间件
    调用链使用
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        local.request = request
        request.request_id = local.get_http_request_id()

        response = self.get_response(request)
        response['X-Request-Id'] = request.request_id

        local.release()

        return response

    # Compatibility methods for Django <1.10
    def process_request(self, request):
        local.request = request
        request.request_id = local.get_http_request_id()

    def process_response(self, request, response):
        response['X-Request-Id'] = request.request_id
        local.release()
        return response


try:
    from .middlewares_ext import *  # noqa
except ImportError as e:
    logger.debug('Load extension failed: %s', e)
