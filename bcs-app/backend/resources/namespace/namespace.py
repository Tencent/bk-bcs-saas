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
from backend.resources.client import K8SClient

from . import utils
from . import resource_quota


def get_namespaces_by_cluster_id(user, project_id, cluster_id):
    return utils.get_namespaces_by_cluster_id(user.token.access_token, project_id, cluster_id)


class Namespace(K8SClient):
    def get_namespace(self, name):
        # 假定cc中有，集群中也存在
        cc_namespaces = utils.get_namespaces_by_cluster_id(self.access_token, self.project_id, self.cluster_id)
        if not cc_namespaces:
            return {}

        for ns in cc_namespaces:
            if ns["name"] == name:
                return {"name": name, "namespace_id": ns["id"]}
        return {}

    def _create_namespace(self, name):
        return self.client.create_namespace({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": name}})

    def create_namespace(self, creator, name):
        # TODO 补充imagepullsecrets和命名空间变量的创建?
        # TODO 操作审计
        self._create_namespace(name)
        ns = utils.create_cc_namespace(self.access_token, self.project_id, self.cluster_id, name, creator)
        return {"name": name, "namespace_id": ns["id"]}


class ResourceQuota:

    def __init__(self, access_token, project_id, cluster_id):
        self.client = resource_quota.ResourceQuota(
            access_token=access_token, project_id=project_id, cluster_id=cluster_id,
        )

    def _ns_quota_conf(self, name, quota):
        return {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {
                "name": name
            },
            "spec": {
                "hard": quota
            }
        }

    def create_resource_quota(self, namespace, quota):
        """创建命名空间下资源配额
        """
        # 资源配额名称和命名空间名称设置为相同
        data = self._ns_quota_conf(namespace, quota)
        return self.client.create_resource_quota(namespace, data)

    def get_namespace_quota(self, namespace, name):
        try:
            quota = self.client.get_namespaced_resource_quota(namespace, name)
            return {"hard": quota.status.hard, "used": quota.status.used}
        except Exception:
            return {}

    def list_resource_quota(self, namespace):
        """获取命名空间下的资源配额
        """
        resource_quota_list = self.client.list_resource_quota(namespace=namespace)
        # 解析获取基本数据
        if resource_quota_list:
            return [
                {
                    "name": i.metadata.name,
                    "namespace": i.metadata.namespace,
                    "quota": {"hard": i.status.hard, "used": i.status.used}
                }
                for i in resource_quota_list
            ]
        return []

    def delete_resource_quota(self, name, namespace):
        """通过名称和命名空间删除资源配额
        """
        return self.client.delete_resource_quota(name, namespace)

    def update_or_create_resource_quota(self, name, namespace, quota):
        """更新或创建资源配额
        """
        data = self._ns_quota_conf(name, quota)
        return self.client.update_or_create_resource_quota(name, namespace, data)
