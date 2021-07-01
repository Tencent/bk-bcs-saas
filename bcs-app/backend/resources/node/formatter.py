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
from typing import Dict

from backend.resources.utils.format import BCSResourceData, ResourceDefaultFormatter
from backend.utils.basic import getitems


@dataclass
class NodeResourceData(BCSResourceData):
    name: str
    inner_ip: str


class NodeFormatter(ResourceDefaultFormatter):
    """Node 格式化"""

    def format_dict(self, resource_dict: Dict) -> NodeResourceData:
        addresses = getitems(resource_dict, ["status", "addresses"], [])
        # 获取IP
        inner_ip = ""
        for addr in addresses:
            if addr["type"] == "InternalIP":
                inner_ip = addr["address"]
                break
        name = getitems(resource_dict, ["metadata", "name"], "")

        return NodeResourceData(data=resource_dict, name=name, inner_ip=inner_ip)
