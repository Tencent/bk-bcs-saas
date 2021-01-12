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

from backend.resources import resource_quota

logger = logging.getLogger(__name__)


@dataclass
class NamespaceQuota:
    """命名空间下资源配额相关功能"""

    access_token: str
    project_id: str
    cluster_id: str

    def __post_init__(self):
        self.client = resource_quota.ResourceQuota(
            access_token=self.access_token, project_id=self.project_id, cluster_id=self.cluster_id
        )

    def _ns_quota_conf(self, name: str, quota: dict) -> Dict:
        return {"apiVersion": "v1", "kind": "ResourceQuota", "metadata": {"name": name}, "spec": {"hard": quota}}

    def create_namespace_quota(self, name: str, quota: dict) -> None:
        """创建命名空间下资源配额"""
        # 资源配额名称和命名空间名称设置为相同
        data = self._ns_quota_conf(name, quota)
        self.client.create_resource_quota(name, data)

    def get_namespace_quota(self, name: str) -> Dict:
        try:
            # 命名空间配额，配额名称和命名空间名称一样
            quota = self.client.get_namespaced_resource_quota(name, name)
            return {"hard": quota.status.hard, "used": quota.status.used}
        except Exception as e:
            logger.error("query namespace quota error, namespace: %s, name: %s, error: %s", name, name, e)
            return {}

    def list_namespace_quota(self, name: str) -> List:
        """获取命名空间下的资源配额"""
        resource_quota_list = self.client.list_resource_quota(name)
        # 解析获取基本数据
        if resource_quota_list:
            return [
                {
                    "name": i.metadata.name,
                    "namespace": i.metadata.namespace,
                    "quota": {"hard": i.status.hard, "used": i.status.used},
                }
                for i in resource_quota_list
            ]
        return []

    def delete_namespace_quota(self, name: str) -> None:
        """通过名称和命名空间删除资源配额"""
        self.client.delete_resource_quota(name, name)

    def update_or_create_namespace_quota(self, name: str, quota: dict) -> None:
        """更新或创建资源配额"""
        data = self._ns_quota_conf(name, quota)
        self.client.update_or_create_resource_quota(name, name, data)
