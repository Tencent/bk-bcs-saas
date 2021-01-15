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
import logging
from typing import Dict, Any

from django.conf import settings
from kubernetes.client.configuration import Configuration
from kubernetes import client

from backend.utils.errcodes import ErrorCode
from backend.components.utils import http_get
from backend.components.bcs import k8s
from backend.components import paas_cc
from backend.utils import exceptions


logger = logging.getLogger(__name__)


class K8SClient:
    def __init__(self, access_token, project_id, cluster_id):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.client = k8s.K8SClient(access_token, project_id, cluster_id, None)


class BcsKubeAddressesProvider:
    """提供访问集群的各 API 访问地址，包括：

    - 查询集群信息的 BCS API 地址
    - 连接集群 apiserver 的基础地址
    """

    def __init__(self, access_token: str, project_id: str, cluster_id: str):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id

    def _query_api_env_name(self) -> str:
        """通过 PaaS-CC 服务查询查询集群环境名称，然后找到其对应的 API 网关环境名称

        :raises ComponentError: 从 PaaS-CC 返回了错误响应
        """
        # Cache
        if hasattr(self, '_api_env_name'):
            return self._api_env_name

        cluster = paas_cc.get_cluster(self.access_token, self.project_id, self.cluster_id)
        # TODO: 封装异常，不使用模糊的 ComponentError
        if cluster.get('code') != ErrorCode.NoError:
            raise exceptions.ComponentError(cluster.get('message'))

        environment = cluster['data']['environment']
        self._api_env_name = settings.BCS_API_ENV[environment]
        return self._api_env_name

    def get_api_base_url(self) -> str:
        """获取 BCS API 服务基础 URL 地址"""
        api_env_name = self._query_api_env_name()
        return f"{settings.BCS_API_PRE_URL}/{api_env_name}"

    def get_clusters_base_url(self) -> str:
        """获取通过 BCS API 查询集群信息的基础 URL 地址"""
        api_base_url = self.get_api_base_url()
        return f"{api_base_url}/rest/clusters"

    def get_kube_apiservers_host(self) -> str:
        """获取 Kubernetes 集群 apiserver 基础地址"""
        api_env_name = self._query_api_env_name()
        return settings.BCS_SERVER_HOST[api_env_name]


class BcsKubeConfigurationService:
    """生成用于连接 Kubernetes 集群的配置对象 Configuration
    通过查询 BCS 服务，获取集群 apiserver 地址与 token 等信息

    :param access_token: 用户 token，请求 API 时使用
    :param project_id: 项目 ID
    :param cluster_id: 集群 ID
    """

    def __init__(self, access_token: str, project_id: str, cluster_id: str):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.addresses = BcsKubeAddressesProvider(access_token, project_id, cluster_id)

    def make_configuration(self) -> Configuration:
        """生成 Kubernetes SDK 所需的 Configuration 对象"""
        config = client.Configuration()
        config.verify_ssl = False

        # Get credentials
        credentials = self.get_client_credentials()
        config.host = '{}{}'.format(
            self.addresses.get_kube_apiservers_host(), credentials['server_address_path']
        ).rstrip("/")
        config.api_key = {"authorization": f"Bearer {credentials['user_token']}"}
        return config

    def get_client_credentials(self) -> Dict[str, Any]:
        """获取访问集群 apiserver 所需的鉴权信息，比如证书、user_token、server_address_path 等"""
        bke_cluster_id = self._get_bke_cluster_id()
        _query_credentials_url = f"{self.addresses.get_clusters_base_url()}/{bke_cluster_id}/client_credentials"

        result = http_get(
            _query_credentials_url,
            params={"access_token": self.access_token},
            raise_for_status=False,
            headers=self.bcs_request_headers,
        )
        return result

    def _get_bke_cluster_id(self) -> str:
        """查询集群在 BKE 服务的 ID"""
        _query_cluster_url = f"{self.addresses.get_clusters_base_url()}/bcs/query_by_id/"
        result = http_get(
            _query_cluster_url,
            params={"access_token": self.access_token, "project_id": self.project_id, "cluster_id": self.cluster_id},
            raise_for_status=False,
            headers=self.bcs_request_headers,
        )
        return result['id']

    @property
    def bcs_request_headers(self):
        """用户请求 BCS 接口的 headers"""
        auth_token = getattr(settings, "BCS_AUTH_TOKEN", "")
        return {"Authorization": auth_token, "Content-Type": "application/json"}
