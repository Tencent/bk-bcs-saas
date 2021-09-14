# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import Dict

from attr import asdict, dataclass
from django.conf import settings

from ..base import BaseHttpClient, BkApiClient, ComponentAuth, response_handler
from . import BcsApiAuth
from .constants import BCS_API_VERSION, DeployType, ProjectType


class BcsApiGatewayConfig:
    def __init__(self, host: str, env: str):
        self.host = host

        # cluster manager相关接口url
        _project_api_url_prefix = f"{host}/{env}/{BCS_API_VERSION}/clustermanager/v1/project"
        self.query_project_url = f"{_project_api_url_prefix}/{{project_id}}"
        self.create_project_url = f"{_project_api_url_prefix}/{{project_id}}"
        self.update_project_url = f"{_project_api_url_prefix}/{{project_id}}"


@dataclass
class ProjectReservedConfig:
    bgID: str = ""
    bgName: str = ""
    deptID: str = ""
    deptName: str = ""
    centerID: str = ""
    centerName: str = ""
    isSecret: bool = False  # 标识项目是否有私密项目，默认为False
    deployType: int = DeployType.Physical  # 业务部署类型，1:物理机部署，2:容器部署
    isOffline: bool = False  # 项目是否已经离线，默认False
    useBKRes: bool = False  # 是否使用蓝鲸提供的资源池，主要用于资源计费，默认False
    projectType: int = ProjectType.Platform  # 1:platform，2:business


@dataclass
class ProjectBasicConfig:
    """项目的基本配置
    projectID: 项目ID，长度为32位字符串
    name: 项目名称
    englishName: 项目英文缩写，长度不能超过32字符
    kind: 项目中集群类型，支持k8s
    businessID: 项目绑定的BK CC的业务ID
    credentials: 记录的账户信息
    description: 项目的描述信息，默认为空
    """

    projectID: str
    name: str
    englishName: str
    kind: str
    businessID: str
    description: str
    credentials: Dict = {}


@dataclass
class ProjectConfig:
    """项目配置信息"""

    creator: str
    basic_config: ProjectBasicConfig
    reserved_config: ProjectReservedConfig


@dataclass
class UpdatedProjectConfig:
    """更新项目配置信息"""

    projectID: str
    updater: str
    name: str
    kind: str
    businessID: str


class BcsProjectApiClient(BkApiClient):
    """访问 BCS 项目 API 服务的 Client 对象
    :param auth: 包含校验信息的对象
    """

    def __init__(self, auth: ComponentAuth):
        self._config = BcsApiGatewayConfig(host=settings.BCS_API_GW_DOMAIN, env=settings.BCS_API_GW_ENV)
        self._client = BaseHttpClient(BcsApiAuth(auth.access_token))

    @response_handler()
    def query_project(self, project_id: str) -> Dict:
        """查询项目信息
        :param project_id: 项目ID
        :return: 项目信息
        """
        url = self._config.query_project_url.format(project_id=project_id)
        return self._client.request_json("GET", url)

    def create_project(self, project_config: ProjectConfig) -> Dict:
        """创建项目
        :param project_config: 项目信息，包含项目的基本信息和项目的保留字段信息
        :return: 项目信息
        """
        # 组装参数
        project_config_data = asdict(project_config.basic_config)
        project_config_data.update(asdict(project_config.reserved_config), creator=project_config.creator)
        # 下发配置
        url = self._config.create_project_url.format(project_id=project_config_data["projectID"])
        return self._client.request_json("POST", url, json=project_config_data)

    def update_project(self, project_config: UpdatedProjectConfig) -> Dict:
        """更新项目
        :param project_config: 更新的项目信息
        :return: 更新的项目信息
        """
        # 组装参数
        project_config_data = asdict(project_config)
        # 下发配置
        url = self._config.create_project_url.format(project_id=project_config_data["projectID"])
        return self._client.request_json("PUT", url, json=project_config_data)
