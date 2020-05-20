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
from django.conf import settings

from backend.bcs_k8s.helm.models.repo import Repository
from backend.apps.depot.api import get_jfrog_account
from backend.bcs_k8s.helm.providers.repo_provider import add_plain_repo


def add_private_repo_info(user, project):
    # 通过harbor api创建一次项目账号，然后存储在auth中
    project_id = project.project_id
    project_code = project.project_code
    private_repos = Repository.objects.filter(name=project_code, project_id=project_id)
    if private_repos.exists():
        return private_repos[0]
    account = get_jfrog_account(user.token.access_token, project_code, project_id)
    repo_auth = {
        "type": "basic",
        "role": "admin",
        "credentials": {
            "username": account.get("user"),
            "password": account.get("password")
        }
    }
    url = f"{settings.HELM_MERELY_REPO_URL}/chartrepo/{project_code}/"
    private_repo = add_plain_repo(
        target_project_id=project_id,
        name=project_code,
        url=url,
        repo_auth=repo_auth
    )
    return private_repo
