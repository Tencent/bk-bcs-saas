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
from typing import Dict, List

from backend.resources.utils.filters import filter_by_owners
from backend.resources.utils.format import ResourceDefaultFormatter
from backend.resources.utils.kube_client import get_dynamic_client, make_labels_string


class Pod:
    """INFO：这个类下的所有查询方法，返回的结果都是通过 ResourceDefaultFormatter 转换过的数据格式"""

    def __init__(self, access_token: str, project_id: str, cluster_id: str, namespace: str):
        self.namespace = namespace
        self.dynamic_client = get_dynamic_client(access_token, project_id, cluster_id)
        self.api = self.dynamic_client.get_preferred_resource('Pod')

    def get_pod(self, pod_name: str) -> List[Dict]:
        """通过名称获取 Pod"""
        pod = self.api.get_or_none(namespace=self.namespace, name=pod_name)
        if not pod:
            return []
        # TODO: 格式化为 Response 格式的逻辑应该从此处往外移动
        return [ResourceDefaultFormatter().format(pod)]

    def get_pod_by_labels(self, selector_labels: Dict) -> List[Dict]:
        """通过 labels 字典过滤 Pods"""
        pods = self.api.get(namespace=self.namespace, label_selector=make_labels_string(selector_labels))
        return ResourceDefaultFormatter().format_list(pods)

    def get_pods_by_rs(self, rs_name: str) -> List[Dict]:
        """根据 ReplicaSet 名称查询 Pod 列表"""
        pods = self.api.get(namespace=self.namespace)
        results = filter_by_owners(pods.items, 'ReplicaSet', [rs_name])
        return ResourceDefaultFormatter().format_list(results)
