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

logger = logging.getLogger(__name__)


def get_auth_url(perms=None):
    return f'{settings.BK_IAM_APP_URL}/perm-apply/'


# 通过 extension 模块替换现有 get_auth_url 函数
try:
    from .exceptions_ext import get_auth_url  # noqa # type: ignore
except ImportError:
    logger.debug('Replacement for "get_auth_url" not found, skip')
