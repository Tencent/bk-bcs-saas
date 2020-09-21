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
from rest_framework import viewsets

from backend.utils.renderers import BKAPIRenderer
from backend.utils.permissions import HasIAMProject, ProjectHasBCS
from backend.utils import FancyDict
from backend.components.ssm import get_client_access_token

from .authentication import JWTAuthentication
from .permissions import AccessTokenPermission, RemoteAccessPermission


class BaseAPIViewSet(viewsets.ViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (AccessTokenPermission, HasIAMProject, ProjectHasBCS)
    renderer_classes = (BKAPIRenderer,)

    def initial(self, request, *args, **kwargs):
        if "project_id" in kwargs:
            return super().initial(request, *args, **kwargs)

        self.kwargs["project_id"] = kwargs.get("project_id_or_code") or kwargs.get("project_code")
        super().initial(request, *args, **kwargs)
        del self.kwargs["project_id"]


class NoAccessTokenBaseAPIViewSet(BaseAPIViewSet):
    permission_classes = (RemoteAccessPermission, HasIAMProject, ProjectHasBCS)

    def initial(self, request, *args, **kwargs):
        request.user.token = FancyDict(access_token=get_client_access_token().get("access_token"))
        super().initial(request, *args, **kwargs)
