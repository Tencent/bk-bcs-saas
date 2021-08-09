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
try:
    from iam.resource.utils import get_filter_obj, get_page_obj
except Exception:
    pass

from ..exceptions import ResNotFoundError
from .project import ProjectProvider

PROVIDER_CLS_MAP = {"project": ProjectProvider}


class BCSResourceProvider:
    def __init__(self, resource_type):
        try:
            self.resource_provider = PROVIDER_CLS_MAP.get(resource_type)()
        except Exception:
            raise ResNotFoundError(f"unsupported resource type: {resource_type}")

    def _parse_filter_and_page(self, data):
        filter_obj = get_filter_obj(data["filter"], ["ids", "parent", "search", "resource_type_chain"])
        page_obj = get_page_obj(data.get("page"))
        return filter_obj, page_obj

    def provide(self, data, **options):
        handler = getattr(self, data["method"])
        return handler(data, **options)

    def list_attr(self, data, **options):
        result = self.resource_provider.list_attr(**options)
        return result.to_list()

    def list_attr_value(self, data, **options):
        filter, page = self._parse_filter_and_page(data)
        result = self.resource_provider.list_attr_value(filter, page, **options)
        return result.to_dict()

    def list_instance(self, data, **options):
        filter, page = self._parse_filter_and_page(data)
        result = self.resource_provider.list_instance(filter, page, **options)
        return result.to_dict()

    def fetch_instance_info(self, data, **options):
        filter, _ = self._parse_filter_and_page(data)
        result = self.resource_provider.fetch_instance_info(filter, **options)
        return result.to_list()

    def list_instance_by_policy(self, data, **options):
        filter, page = self._parse_filter_and_page(data)
        result = self.resource_provider.list_instance_by_policy(filter, page, **options)
        return result.to_list()
