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
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from django.conf import settings
from iam import Resource


class ResourceRequest:
    resource_type: str = ''
    attr: Optional[Dict] = None

    def __init__(self, res: Union[List[str], str], attr: Optional[Dict] = None, **attr_kwargs):
        """
        :param res: 单个资源 ID 或资源 ID 列表
        :param attr: 属性字典。如 {'_bk_iam_path_': f'/project,{{project_id}}/'}
        :param attr_kwargs: 用于替换 attr 中可能需要 format 的值
        """
        self.res = res
        if attr:
            self.attr = attr
        self.attr_kwargs = dict(**attr_kwargs)

    def make_resources(self) -> List[Resource]:
        if isinstance(self.res, str):
            return [Resource(settings.APP_ID, self.resource_type, self.res, self._make_attribute(self.res))]

        return [
            Resource(settings.APP_ID, self.resource_type, res_id, self._make_attribute(res_id)) for res_id in self.res
        ]

    def _make_attribute(self, res_id: str) -> Dict:
        return {}


@dataclass
class ActionResourcesRequest:
    """
    操作资源请求
    note: resources 是由资源 ID 构成的列表. 为 None 时，表示资源无关.
    """

    resource_type: str
    action_id: str
    resources: Optional[List[str]] = None
