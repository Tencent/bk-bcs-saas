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
from typing import Any, List, Dict


from kubernetes import client
from kubernetes.dynamic import DynamicClient

from backend.utils.basic import getitems
from backend.resources.client import BcsKubeConfigurationService
from backend.resources.utils.kube_client import (
    get_or_none,
    get_preferred_resource,
)


class Deployment:
    def __init__(self, access_token: str, project_id: str, cluster_id: str, namespace: str):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        # TODO: 去掉初始化方法里的 namespace 参数，与其他类保持统一
        self.namespace = namespace

        config = BcsKubeConfigurationService(self.access_token, self.project_id, self.cluster_id).make_configuration()
        self.dynamic_client = DynamicClient(client.ApiClient(config))
        self.api = get_preferred_resource(self.dynamic_client, 'Deployment')

    def create(self, body: Any):
        """创建一个 Deployment 资源

        :param body: Deployment 字典数据，或 OpenAPI Model 对象
        """
        # 使用 sanitize 方法剔除 OpenAPI 对象里的 None 值
        body = self.dynamic_client.client.sanitize_for_serialization(body)
        return self.api.create(namespace=self.namespace, body=body)

    def get_deployments_by_namespace(self) -> List[Dict]:
        """查询当前 namespace 下的所有 Deployment"""
        results = self.api.get(namespace=self.namespace).to_dict()
        return results['items']

    def get_deployment(self, deploy_name: str) -> List[Dict]:
        """根据名称获取 Deployment，为了向前兼容，该方法将返回列表"""
        result = get_or_none(self.api, namespace=self.namespace, name=deploy_name)
        return [result.to_dict()] if result else []

    def update_deployment(self, deploy_name: str, manifest: Dict) -> Dict:
        """修改 Deployment"""
        # 使用 sanitize 方法剔除 OpenAPI 对象里的 None 值
        body = self.dynamic_client.client.sanitize_for_serialization(manifest)
        result = self.api.replace(namespace=self.namespace, name=deploy_name, body=body)
        return result.to_dict()

    def get_selector_labels(self, deploy_name: str) -> Dict:
        """获取 deployment 所匹配的 labels"""
        item = self.get_deployment(deploy_name)
        if item:
            return getitems(item[0], 'spec.selector.matchLabels', {})
        return {}

    def get_rs_name_list(self, deploy_name: str) -> List[str]:
        """根据 Deployment 名称查询所有的 ReplicaSet 名称

        :param: Deployment 名称
        """
        rs_api = get_preferred_resource(self.dynamic_client, 'ReplicaSet')
        rs_results = rs_api.get(namespace=self.namespace).to_dict()

        results = []
        for rs_data in rs_results['items']:
            owner_names = [owner['name'] for owner in getitems(rs_data, 'metadata.ownerReferences', [])]
            # NOTE: 是否应该校验 owner 的 Kind 是否严格为 Deployment？
            if deploy_name in owner_names:
                rs_name = getitems(rs_data, 'metadata.name')
                results.append(rs_name)
        return results

    def get_pods_by_deployment(self, deploy_name):
        selector_labels = self.get_selector_labels(deploy_name)
        pods = self.pod.get_pod_by_labels(selector_labels)

        rs_name_list = self.get_rs_name_list(deploy_name)
        pods_in_deployment = []
        for pod in pods:
            owner_references = getitems(pod, ['data', 'metadata', 'ownerReferences'], [''])[0]
            if owner_references['name'] in rs_name_list:
                pods_in_deployment.append(pod)

        return pods_in_deployment
