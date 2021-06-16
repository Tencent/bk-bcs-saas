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
from .. import constants


class BcsRepoProvider:
    def __init__(self, project_code):
        self.project_code = project_code

    @property
    def public_project_name(self):
        """仓库的公共项目名称"""
        return constants.BK_REPO_PUBLIC_PROJECT_NAME

    @property
    def public_repo_name(self):
        """公共仓库的名称"""
        return constants.BK_REPO_PUBLIC_REPO_NAME

    @property
    def project_name(self):
        """仓库的项目名称"""
        return self.project_code

    @property
    def project_repo_name(self):
        """项目仓库的名称"""
        return self.project_code


class HarborRepoProvider(BcsRepoProvider):
    @property
    def project_name(self):
        """harbor的项目名称是固定的"""
        return constants.DEFAULT_PROJECT_NAME


class BkRepoProvider(BcsRepoProvider):
    pass


def get_platform_repo_provider():
    providers = {
        "harbor": HarborRepoProvider,
        "bk_repo": BkRepoProvider,
    }
    return providers[constants.DEFAULT_CHART_REPO_PROVIDER]
