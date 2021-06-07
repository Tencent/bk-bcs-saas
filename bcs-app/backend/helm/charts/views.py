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
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.helm.repository.utils import auth, repo

from .utils.chart import ChartData, get_chart_versions


class HelmChartViewSet(SystemViewSet):
    def list_versions(self, request, project_id, chart_name):
        """查询chart的版本列表"""
        is_public = request.query_params.get("is_public", False)
        project_code = request.project.project_code
        repo_obj = repo.get_repo(project_id, project_code, is_public=is_public)
        username, password = repo_obj.username_password
        project_name, repo_name = repo.get_project_and_repo_name(project_code, is_public)
        versions = get_chart_versions(
            repo.RepoData(project_name=project_name, repo_name=repo_name),
            auth.RepoAuthData(username=username, password=password),
            ChartData(chart_name=chart_name),
        )
        return Response(versions)
