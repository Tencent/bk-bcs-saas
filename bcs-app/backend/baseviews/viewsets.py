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
from rest_framework import permissions, viewsets
from rest_framework.renderers import BrowsableAPIRenderer

from backend.utils.renderers import BKAPIRenderer

from .authentication import JWTAndTokenAuthentication
from .permissions import AccessProjectPermission, ProjectEnableBCS


class SystemViewSet(viewsets.ViewSet):
    """容器服务SaaS app使用的API view"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    # authentication_classes配置在REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]中
    permission_classes = (permissions.IsAuthenticated, AccessProjectPermission, ProjectEnableBCS)


class UserViewSet(viewsets.ViewSet):
    """提供给流水线等第三方服务的API view"""

    renderer_classes = (BKAPIRenderer,)
    authentication_classes = (JWTAndTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, AccessProjectPermission, ProjectEnableBCS)
