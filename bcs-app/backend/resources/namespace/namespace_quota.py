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
from typing import Dict, List
from dataclasses import dataclass

from kubernetes import client
from kubernetes.client.exceptions import ApiException
from kubernetes.dynamic import DynamicClient

from backend.resources.client import BcsKubeConfigurationService
from backend.resources.utils.kube_client import update_or_create, delete_ignore_nonexistent

logger = logging.getLogger(__name__)


@dataclass
class NamespaceQuota:
    """命名空间下资源配额相关功能"""

    access_token: str
    project_id: str
    cluster_id: str

    def __post_init__(self):
        config = BcsKubeConfigurationService(self.access_token, self.project_id, self.cluster_id).make_configuration()
        self.dynamic_client = DynamicClient(client.ApiClient(config))
        self.api = self.dynamic_client.resources.get(kind='ResourceQuota')

    def _ns_quota_conf(self, name: str, quota: Dict) -> Dict:
        return {"apiVersion": "v1", "kind": "ResourceQuota", "metadata": {"name": name}, "spec": {"hard": quota}}

    def create_namespace_quota(self, name: str, quota: Dict) -> None:
        """创建命名空间下资源配额

        :param name: 资源配额名称，也会用做 namespace
        :param quota: 资源配额内容
        """
        body = self._ns_quota_conf(name, quota)
        update_or_create(self.api, body=body, name=name, namespace=name)

    def get_namespace_quota(self, name: str) -> Dict:
        """获取命名空间资源配额，当请求出错时，返回空字典

        :param name: 资源名称，也会用做 namespace
        """
        try:
            quota = self.api.get(name=name, namespace=name)
            return {"hard": quota.status.hard, "used": quota.status.used}
        except ApiException as e:
            logger.error("query namespace quota error, namespace: %s, name: %s, error: %s", name, name, e)
            return {}

    def list_namespace_quota(self, namespace: str) -> List:
        """获取命名空间下的所有资源配额"""
        items = self.api.get(namespace=namespace).items
        return [
            {
                "name": i.metadata.name,
                "namespace": i.metadata.namespace,
                "quota": {"hard": i.status.hard, "used": i.status.used},
            }
            for i in items
        ]

    def delete_namespace_quota(self, name: str) -> None:
        """通过名称和命名空间删除资源配额，当资源不存在时忽略"""
        delete_ignore_nonexistent(self.api, name=name, namespace=name)

    def update_or_create_namespace_quota(self, name: str, quota: Dict) -> None:
        """更新或创建资源配额"""
        body = self._ns_quota_conf(name, quota)
        update_or_create(self.api, body=body, name=name, namespace=name)
