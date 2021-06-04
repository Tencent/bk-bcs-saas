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
from dataclasses import dataclass

from backend.components.bk_repo import BkRepoClient
from backend.helm.repositorys.utils import auth, repo


@dataclass
class ChartData:
    chart_name: str
    version: str = None


def get_chart_versions(repo_data: repo.RepoData, repo_auth: auth.RepoAuthData, chart_data: ChartData):
    """获取chart的版本
    NOTE: 考虑后续支持用户创建自己的仓库，后续允许输入仓库地址，接口遵循bkrepo的接口协议
    """
    client = BkRepoClient(repo_auth.username, password=repo_auth.password)
    return client.get_chart_versions(repo_data.project_name, repo_data.repo_name, chart_data.chart_name)


def get_chart_version_info(repo_data: repo.RepoData, repo_auth: auth.RepoAuthData, chart_data: ChartData):
    """获取chart版本详情"""
    client = BkRepoClient(repo_auth.username, password=repo_auth.password)
    return client.get_chart_version_detail(
        repo_data.project_name, repo_data.repo_name, chart_data.chart_name, chart_data.version
    )
