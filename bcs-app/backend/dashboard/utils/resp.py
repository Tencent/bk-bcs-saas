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
from typing import Dict

from django.utils.translation import ugettext_lazy as _

from backend.dashboard.exceptions import ResourceNotExist
from backend.resources.resource import ResourceClient


class ListApiRespBuilder:
    """ 构造 Dashboard 资源列表 Api 响应内容逻辑 """

    def __init__(self, client: ResourceClient, **kwargs):
        """
        构造器初始化

        :param client: 资源客户端
        """
        self.client = client
        self.resources = self.client.list(is_format=False, **kwargs).to_dict()

    def build(self) -> Dict:
        """ 组装 Dashboard Api 响应内容 """
        result = {
            'manifest': self.resources,
            'manifest_ext': {
                item['metadata']['uid']: self.client.formatter.format_dict(item) for item in self.resources['items']
            },
        }
        return result


class RetrieveApiRespBuilder:
    """ 构造 Dashboard 资源详情 Api 响应内容逻辑 """

    def __init__(self, client: ResourceClient, namespace: str, name: str, **kwargs):
        """
        构造器初始化

        :param client: 资源客户端
        :param namespace: 资源命名空间
        :param name: 资源名称
        """
        self.client = client
        raw_resource = self.client.get(namespace=namespace, name=name, is_format=False, **kwargs)
        if not raw_resource:
            raise ResourceNotExist(_('资源(Namespace: {}, Name: {})不存在').format(namespace, name))
        self.resource = raw_resource.to_dict()

    def build(self) -> Dict:
        """ 组装 Dashboard Api 响应内容 """
        return {
            'manifest': self.resource,
            'manifest_ext': self.client.formatter.format_dict(self.resource),
        }
