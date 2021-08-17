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
from typing import Optional

from iam.collection import FancyDict
from iam.resource.provider import ListResult, ResourceProvider
from iam.resource.utils import Page

from backend.templatesets.legacy_apps.configuration.utils import filter_templatesets


class TemplatesetProvider(ResourceProvider):
    """模板集 资源拉取接口具体实现"""

    def list_instance(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        """
        获取模板集实例列表
        :param filter_obj: 查询参数。 以下为必传如: {"parent": {"id": 1}}
        :param page_obj: 分页对象
        """
        return self._filter_templateset(filter_obj, page_obj)

    def fetch_instance_info(self, filter_obj: FancyDict, **options) -> ListResult:
        """
        批量获取模板集实例属性详情
        :param filter_obj: 查询参数。 以下为必传如: {"parent": {"id": 1}}
        """
        return self._filter_templateset(filter_obj)

    def _filter_templateset(self, filter_obj: FancyDict, page_obj: Optional[Page] = None) -> ListResult:
        """获取模板集且根据分页需求分页,转换数据后返回"""
        project_id = filter_obj.parent["id"]
        templateset_list = filter_templatesets(project_id, filter_obj.ids, ["id", "project_id", "name"])
        count = len(templateset_list)

        if page_obj:
            templateset_list = templateset_list[page_obj.slice_from : page_obj.slice_to]

        results = [{'id': templateset['id'], 'display_name': templateset['name']} for templateset in templateset_list]

        return ListResult(results=results, count=count)

    def list_instance_by_policy(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        # TODO 确认基于实例的查询是不是就是id的过滤查询
        return ListResult(results=[], count=0)

    def list_attr(self, **options) -> ListResult:
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter_obj: FancyDict, page_obj: Page, **options) -> ListResult:
        return ListResult(results=[], count=0)
