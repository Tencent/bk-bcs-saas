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
from typing import Dict, List

from iam.collection import FancyDict
from iam.resource.provider import ListResult, ResourceProvider
from iam.resource.utils import Page

from backend.components.base import ComponentAuth
from backend.components.paas_cc import PaaSCCClient
from backend.iam.permissions.resources.namespace import calc_iam_ns_id

from .utils import get_system_token


class NamespaceProvider(ResourceProvider):
    """命名空间 Provider"""

    def list_instance(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        cluster_id = filter_obj.parent['id']
        namespace_list = self._list_namespaces(cluster_id)

        namespace_slice = namespace_list[page_obj.slice_from : page_obj.slice_to]
        results = [
            {'id': calc_iam_ns_id(cluster_id, ns['name']), 'display_name': ns['name']} for ns in namespace_slice
        ]

        return ListResult(results=results, count=len(namespace_list))

    def fetch_instance_info(self, filter_obj: FancyDict, **options) -> ListResult:
        iam_cluster_ns = self._calc_iam_cluster_ns(filter_obj.ids)

        results = []
        for iam_ns_id in filter_obj.ids:
            name = iam_cluster_ns.get(iam_ns_id)
            if name:
                results.append({'id': iam_ns_id, 'display_name': name})

        return ListResult(results=results, count=len(results))

    def list_instance_by_policy(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        # TODO 确认基于实例的查询是不是就是id的过滤查询
        return ListResult(results=[], count=0)

    def list_attr(self, **options) -> ListResult:
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        return ListResult(results=[], count=0)

    def _calc_iam_cluster_ns(self, iam_ns_id_list: List[str]) -> Dict[str, str]:
        """
        计算出iam_ns_id和命名空间名称的映射表
        :param iam_ns_id_list: iam_ns_id 列表
        :return 映射表 如 {'BCS-K8S-40000:test-default': 'test-default'}
        """
        cluster_namespaces = {}
        iam_cluster_ns = {}
        for iam_ns_id in iam_ns_id_list:
            cluster_id = iam_ns_id.split(':')[0]
            if cluster_id not in cluster_namespaces:
                cluster_namespaces[cluster_id] = self._list_namespaces(cluster_id)
                for ns in cluster_namespaces[cluster_id]:
                    iam_cluster_ns[calc_iam_ns_id(cluster_id, ns['name'])] = ns['name']
        return iam_cluster_ns

    def _list_namespaces(self, cluster_id: str) -> List[Dict]:
        paas_cc = PaaSCCClient(auth=ComponentAuth(get_system_token()))
        cluster = paas_cc.get_cluster_by_id(cluster_id=cluster_id)
        ns_data = paas_cc.get_cluster_namespace_list(project_id=cluster['project_id'], cluster_id=cluster_id)
        return ns_data['results']
