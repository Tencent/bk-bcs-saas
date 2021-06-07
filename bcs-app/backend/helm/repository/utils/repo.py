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
from typing import Tuple

from backend.helm.helm.models.repo import Repository

from .. import constants


@dataclass
class RepoData:
    project_name: str = None
    repo_name: str = None
    repo_prefix_url: str = None


def get_repo(project_id: str, project_code: str, is_public: bool = False, repo_name: str = None) -> Repository:
    if not repo_name:
        repo_name = constants.PUBLIC_CHART_REPO_NAME if is_public else project_code
    return Repository.objects.get(project_id=project_id, name=repo_name)


def get_project_and_repo_name(project_code: str, is_public: bool = False, repo_name: str = None) -> Tuple[str, str]:
    """获取仓库的所属项目名称及仓库名称"""
    if is_public:
        return constants.BK_REPO_PUBLIC_PROJECT_NAME, constants.BK_REPO_PUBLIC_REPO_NAME
    # NOTE: 兼容harbor，harbor项目名称使用的是同一个
    return constants.DEFAULT_PROJECT_NAME or project_code, repo_name or project_code
