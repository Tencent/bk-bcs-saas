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

from rest_framework import permissions

from backend.utils import FancyDict

from .constants import ACCESS_TOKEN_KEY_NAME

logger = logging.getLogger(__name__)


class RemoteAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return True


class AccessTokenPermission(RemoteAccessPermission):
    message = "no valid access_token"

    def has_permission(self, request, view):
        has_perm = super().has_permission(request, view)
        if not has_perm:
            return False

        access_token = request.META.get(ACCESS_TOKEN_KEY_NAME, "")

        if access_token:
            request.user.token = FancyDict(access_token=access_token)
            return True

        return False
