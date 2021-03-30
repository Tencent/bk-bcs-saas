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
from typing import Optional

from django.conf import settings
from rest_framework.permissions import BasePermission

from backend.accounts import bcs_perm
from backend.apps.constants import ClusterType
from backend.components import paas_cc
from backend.components.iam import permissions
from backend.utils import FancyDict
from backend.utils.cache import region
from backend.utils.errcodes import ErrorCode

EXPIRATION_TIME = 3600 * 24 * 30


class ProjectPermission(BasePermission):
    message = "no project permissions"

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        access_token = request.user.token.access_token
        user_id = request.user.username

        project_id_or_code = view.kwargs.get('project_id') or view.kwargs.get('project_id_or_code')
        project_id = self._get_cached_project_id(access_token, project_id_or_code)
        if not project_id:
            return False

        if settings.REGION == 'ce':
            perm = permissions.ProjectPermission()
            return perm.can_view(user_id, project_id)
        else:
            # 实际调用paas_auth.verify_project
            return bcs_perm.verify_project_by_user(
                access_token=access_token, project_id=project_id, project_code="", user_id=user_id
            )

    def _get_cached_project_id(self, access_token, project_id_or_code: str) -> str:
        cache_key = f'BK_DEVOPS_BCS:PROJECT_ID:{project_id_or_code}'
        project_id = region.get(cache_key, expiration_time=EXPIRATION_TIME)

        if not project_id:
            resp = paas_cc.get_project(access_token, project_id_or_code)
            if resp.get('code') != ErrorCode.NoError:
                return ''

            project_id = resp['data']['project_id']
            region.set(cache_key, project_id)

        return project_id


class IsEnabledBCS(BasePermission):
    message = "project does not enable bcs"

    def has_permission(self, request, view):
        project_id_or_code = view.kwargs.get('project_id') or view.kwargs.get('project_id_or_code')
        project = self._get_cached_enabled_project(request.user.token.access_token, project_id_or_code)
        if project:
            # 将project设置为request的属性，在view中使用
            request.project = project
            return True

        return False

    def _get_cached_enabled_project(self, access_token, project_id_or_code: str) -> Optional[FancyDict]:
        cache_key = f"BK_DEVOPS_BCS:ENABLED_BCS_PROJECT:{project_id_or_code}"
        project = region.get(cache_key, expiration_time=EXPIRATION_TIME)
        if project and isinstance(project, FancyDict):
            return project

        resp = paas_cc.get_project(access_token, project_id_or_code)
        if resp.get('code') != ErrorCode.NoError:
            return None

        project = FancyDict(**resp['data'])
        project.coes = project.kind

        try:
            from backend.apps.projects.utils import get_project_kind

            # k8s类型包含kind为1(bcs k8s)或其它属于k8s的编排引擎
            project.kind = get_project_kind(project.kind)
        except ImportError:
            pass

        # 用户绑定了项目, 并且选择了编排类型
        if project.cc_app_id != 0 and project.kind in ClusterType:
            region.set(cache_key, project)
            return project

        return None
