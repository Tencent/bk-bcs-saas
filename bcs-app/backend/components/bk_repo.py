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
import json
import logging
from typing import Dict, List

from django.conf import settings
from requests import PreparedRequest
from requests.auth import AuthBase

from backend.components.base import (
    BaseHttpClient,
    BkApiClient,
    response_hander,
    update_request_body,
    update_url_parameters,
)

logger = logging.getLogger(__name__)


class BkRepoConfig:
    """BK Repo注册到apigw的地址"""

    def __init__(self, host: str):
        # 请求域名
        self.host = host

        # 请求地址
        self.create_project = f"{host}/repository/api/project"
        self.create_chart_repo = f"{host}/repository/api/repo"
        self.set_user_auth = f"{host}/auth/api/user/create/project"


class BkRepoRawConfig:
    """Bk Repo原生API地址"""

    def __init__(self, host: str):
        # 请求域名
        self.host = host

        self.get_charts = f"{host}/api/{{project_name}}/{{repo_name}}/charts"
        self.get_chart_versions = f"{host}/api/{{project_name}}/{{repo_name}}/charts/{{chart_name}}"
        self.get_chart_version_detail = f"{host}/api/{{project_name}}/{{repo_name}}/charts/{{chart_name}}/{{version}}"
        self.delete_chart_version = f"{host}/api/{{project_name}}/{{repo_name}}/charts/{{chart_name}}/{{version}}"


class BkRepoAuth(AuthBase):
    """用于调用注册到APIGW的BK Repo 系统接口的鉴权"""

    def __init__(self, access_token: str, username: str):
        self.access_token = access_token
        self.username = username

    def __call__(self, r: PreparedRequest):
        # 添加auth参数到headers中
        r.headers.update(
            {
                "X-BKREPO-UID": self.username,
                "authorization": getattr(settings, "HELM_REPO_PLATFORM_AUTHORIZATION", ""),
                "Content-Type": "application/json",
                "X-BKAPI-AUTHORIZATION": json.dumps({"access_token": self.access_token}),
            }
        )
        return r


class BkRepoRawAuth(AuthBase):
    """用于调用注册到APIGW的BK Repo 系统接口的鉴权"""

    def __init__(self, repo_user: str, repo_pwd: str):
        self.repo_user = repo_user
        self.repo_pwd = repo_pwd

    def __call__(self, r: PreparedRequest):
        # 添加auth
        r.prepare_auth((self.repo_user, self.repo_pwd))
        return r


class BkRepoClient(BkApiClient):
    def __init__(self, access_token: str, username: str):
        self._config = BkRepoConfig(host=getattr(settings, "BK_REPO_URL_PREFIX", ""))
        self._client = BaseHttpClient(
            BkRepoAuth(access_token, username),
        )

    def create_project(self, project_code: str, project_name: str, description: str) -> Dict:
        """创建仓库所属项目

        :param project_code: BCS项目code
        :param project_name: BCS项目名称
        :param description: BCS项目描述
        :returns: 返回项目
        """
        data = {"name": project_code, "displayName": project_name, "description": description}
        return self._common_request("POST", self._config.create_project, json=data, raise_for_status=False)

    def create_chart_repo(self, project_code: str) -> Dict:
        """创建chart 仓库

        :param project_code: BCS项目code
        :returns: 返回仓库
        """
        data = {
            "projectId": project_code,
            "name": project_code,
            "type": "HELM",
            "category": "LOCAL",
            "public": False,  # 容器服务项目自己的仓库
            "configuration": {"type": "local"},
        }
        return self._common_request("POST", self._config.create_chart_repo, json=data, raise_for_status=False)

    @response_hander()
    def set_auth(self, project_code: str, repo_admin_user: str, repo_admin_pwd: str) -> Dict:
        """设置权限

        :param project_code: BCS项目code
        :param repo_admin_user: 仓库admin用户
        :param repo_admin_pwd: 仓库admin密码
        :returns: 返回auth信息
        """
        data = {
            "admin": True,
            "name": repo_admin_user,
            "pwd": repo_admin_pwd,
            "userId": repo_admin_user,
            "asstUsers": [repo_admin_user],
            "group": True,
            "projectId": project_code,
        }
        return self._common_request("POST", self._config.set_user_auth, json=data, raise_for_status=False)

    def _common_request(self, method: str, url: str, **kwargs) -> Dict:
        """请求BK repo接口
        :param method: 请求接口的方法，如GET、POST等
        :param url: 请求接口的URL
        :param kwargs: 支持更多的参数、如params、data、headers等
        :returns: 返回Response
        """
        return self._client.request_json(method, url, **kwargs)


class BkRepoRawClient(BkApiClient):
    def __init__(self, repo_user: str, repo_pwd: str):
        self._config = BkRepoRawConfig(host=getattr(settings, "HELM_MERELY_REPO_URL", ""))
        self._client = BaseHttpClient(
            BkRepoRawAuth(repo_user, repo_pwd),
        )

    def get_charts(self, project_name: str, repo_name: str, start_time: str = None) -> Dict:
        """获取项目下的chart

        :param project_name: 项目名称
        :param repo_name: 仓库名称
        :param start_time: 增量查询的起始时间
        :returns: 返回项目下的chart列表
        """
        url = self._config.get_charts.format(project_name=project_name, repo_name=repo_name)
        return self._client.request_json("GET", url, params={"startTime": start_time})

    def get_chart_versions(self, project_name: str, repo_name: str, chart_name: str) -> List:
        """获取项目下指定chart的版本列表

        :param project_name: 项目名称
        :param repo_name: 仓库名称
        :param chart_name: chart 名称
        :returns: 返回chart版本列表
        """
        url = self._config.get_chart_versions.format(
            project_name=project_name, repo_name=repo_name, chart_name=chart_name
        )
        return self._client.request_json("GET", url)

    def get_chart_version_detail(self, project_name: str, repo_name: str, chart_name: str, version: str) -> Dict:
        """获取指定chart版本的详情

        :param project_name: 项目名称
        :param repo_name: 仓库名称
        :param chart_name: chart 名称
        :param version: chart 版本
        :returns: 返回chart版本详情，包含名称、创建时间、版本、url等
        """
        url = self._config.get_chart_version_detail.format(
            project_name=project_name, repo_name=repo_name, chart_name=chart_name, version=version
        )
        return self._client.request_json("GET", url)

    def delete_chart_version(self, project_name: str, repo_name: str, chart_name: str, version: str) -> Dict:
        """删除chart版本

        :param project_name: 项目名称
        :param repo_name: 仓库名称
        :param chart_name: chart 名称
        :param version: chart 版本
        :returns: 返回删除信息，格式: {"deleted": True}
        """
        url = self._config.delete_chart_version.format(
            project_name=project_name, repo_name=repo_name, chart_name=chart_name, version=version
        )
        return self._client.request_json("DELETE", url)


try:
    from .bk_repo_ext import BkRepoRawConfig  # noqa
except ImportError as e:
    logger.debug("Load extension failed: %s", e)
