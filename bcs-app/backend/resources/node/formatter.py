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
import logging
from typing import Dict, List

from backend.resources.constants import NodeConditionStatus, NodeConditionType
from backend.resources.utils.format import ResourceDefaultFormatter
from backend.utils.basic import getitems

logger = logging.getLogger(__name__)


class NodeFormatter(ResourceDefaultFormatter):
    """Node 格式化"""

    def format_dict(self, resource_dict: Dict) -> Dict:
        """格式化数据
        包含基本的数据，不用调用处再次处理
        """
        addresses = getitems(resource_dict, ["status", "addresses"], [])
        # 获取IP
        inner_ip = self._get_inner_ip(addresses)
        name = getitems(resource_dict, ["metadata", "name"], "")

        return {
            "name": name,
            "inner_ip": inner_ip,
            "status": self._get_node_status(getitems(resource_dict, ["status", "conditions"], [])),
            "data": resource_dict,
        }

    def _get_inner_ip(self, addresses: List[Dict]) -> str:
        """获取inner ip"""
        for addr in addresses:
            if addr["type"] == "InternalIP":
                return addr["address"]
        logger.warning("inner ip of addresses is null, address is %s", addresses)
        return ""

    def _get_node_status(self, conditions: List) -> str:
        """获取节点状态
        ref: https://github.com/kubernetes/dashboard/blob/0de61860f8d24e5a268268b1fbadf327a9bb6013/src/app/backend/resource/node/list.go#L106  # noqa
        """
        for condition in conditions:
            if condition["type"] != NodeConditionType.Ready:
                continue
            # 正常可用状态
            if condition["status"] == "True":
                return NodeConditionStatus.Ready
            # 节点不健康而且不能接收 Pod
            return NodeConditionStatus.NotReady
        # 节点控制器在最近 node-monitor-grace-period 期间（默认 40 秒）没有收到节点的消息
        return NodeConditionStatus.Unknown
