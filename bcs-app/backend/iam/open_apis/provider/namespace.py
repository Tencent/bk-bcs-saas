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

from .utils import get_system_token


class NamespaceProvider(ResourceProvider):
    """命名空间 Provider"""

    def list_instance(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        cluster_id = filter_obj.parent['id']
        namespace_list = self._list_namespaces(cluster_id)

        namespace_slice = namespace_list[page_obj.slice_from : page_obj.slice_to]
        results = [{'id': f"{cluster_id}:{ns['name']}", 'display_name': ns['name']} for ns in namespace_slice]

        return ListResult(results=results, count=len(namespace_list))

    def fetch_instance_info(self, filter_obj: FancyDict, **options) -> ListResult:
        cluster_id = filter_obj.parent['id']
        namespace_list = self._list_namespaces(cluster_id)

        if filter_obj.ids:
            # cluster_ns_id 结构如 BCS-K8S-40000:test
            filter_ns_list = [cluster_ns_id.split(':')[1] for cluster_ns_id in filter_obj.ids]
            results = [
                {'id': f"{cluster_id}:{ns['name']}", 'display_name': ns['name']}
                for ns in namespace_list
                if ns['name'] in filter_ns_list
            ]
        else:
            results = [{'id': f"{cluster_id}:{ns['name']}", 'display_name': ns['name']} for ns in namespace_list]

        return ListResult(results=results, count=len(results))

    def list_instance_by_policy(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        # TODO 确认基于实例的查询是不是就是id的过滤查询
        return ListResult(results=[], count=0)

    def list_attr(self, **options) -> ListResult:
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        return ListResult(results=[], count=0)

    def _list_namespaces(self, cluster_id: str) -> List[Dict]:
        paas_cc = PaaSCCClient(auth=ComponentAuth(get_system_token()))
        cluster = paas_cc.get_cluster_by_id(cluster_id=cluster_id)
        ns_data = paas_cc.get_cluster_namespace_list(project_id=cluster['project_id'], cluster_id=cluster_id)
        return ns_data['results']
