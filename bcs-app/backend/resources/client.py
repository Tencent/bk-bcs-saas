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
import logging
from typing import Any, Dict

from django.conf import settings
from kubernetes import client
from kubernetes.client.configuration import Configuration

from backend.components.bcs import k8s
from backend.container_service.clusters.base import CtxCluster
from backend.utils import exceptions
from backend.utils.errcodes import ErrorCode

logger = logging.getLogger(__name__)


class K8SClient:
    def __init__(self, access_token, project_id, cluster_id):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.client = k8s.K8SClient(access_token, project_id, cluster_id, None)


class BcsAPIEnvironmentQuerier:
    """查询 BCS 集群的 API 网关环境名称"""

    def __init__(self, cluster: CtxCluster):
        self.cluster = cluster

    def do(self) -> str:
        """通过 PaaS-CC 服务查询查询集群环境名称，然后找到其对应的 API 网关环境名称

        :raises ComponentError: 从 PaaS-CC 返回了错误响应
        """
        # Cache
        if hasattr(self, '_api_env_name'):
            return self._api_env_name

        cluster_resp = self.cluster.comps.paas_cc.get_cluster(self.cluster.project_id, self.cluster.id)
        # TODO: 封装异常，不使用模糊的 ComponentError
        if cluster_resp.get('code') != ErrorCode.NoError:
            raise exceptions.ComponentError(cluster_resp.get('message'))

        environment = cluster_resp['data']['environment']
        self._api_env_name = settings.BCS_API_ENV[environment]
        return self._api_env_name


class BcsKubeConfigurationService:
    """生成用于连接 Kubernetes 集群的配置对象 Configuration
    根据规则组装 集群访问 URL，由 环境变量 获取 集群管理 TOKEN

    :param cluster: 集群对象
    """

    def __init__(self, cluster: CtxCluster):
        self.cluster = cluster
        self.bcs_api = self.cluster.comps.bcs_api
        self.env_querier = BcsAPIEnvironmentQuerier(cluster)

    def make_configuration(self) -> Configuration:
        """生成 Kubernetes SDK 所需的 Configuration 对象"""
        env_name = self.env_querier.do()

        config = client.Configuration()
        config.verify_ssl = False
        config.host = '{host}/v4/clusters/{cluster_id}'.format(
            host=self._get_apiservers_host(env_name), cluster_id=self.cluster.id
        )
        config.api_key = {"authorization": f"Bearer {settings.BCS_CLUSTER_ADMIN_TOKEN}"}
        return config

    @staticmethod
    def _get_apiservers_host(api_env_name: str) -> str:
        """获取 Kubernetes 集群 apiserver 基础地址"""
        return settings.BCS_SERVER_HOST[api_env_name]
