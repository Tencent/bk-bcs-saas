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
import json
import logging
from typing import Dict, List

from backend.container_service.clusters.base.models import CtxCluster
from backend.resources.node.client import Node
from backend.resources.utils.format import ResourceDefaultFormatter
from backend.utils.basic import getitems

logger = logging.getLogger(__name__)


class NodeFormatter(ResourceDefaultFormatter):
    def format_dict(self, resource_dict: Dict) -> Dict[str, Dict]:
        addresses = getitems(resource_dict, ["status", "addresses"], [])
        # 获取IP
        inner_ip = ""
        for addr in addresses:
            if addr["type"] == "InternalIP":
                inner_ip = addr["address"]
        # 如果不存在ip，返回数据为空
        if not inner_ip:
            logger.warning("节点InnerIP字段为空，resource数据: %s", json.dumps(resource_dict))
            return {}

        # 解析数据
        metadata = resource_dict.get("metadata", {})
        labels = metadata.get("labels", {})
        annotations = metadata.get("annotations", {})
        host_name = metadata.get("name", "")
        taints = getitems(resource_dict, ["spec", "taints"], [])

        return {inner_ip: {"host_name": host_name, "taints": taints, "labels": labels, "annotations": annotations}}


def query_nodes(ctx_cluster: CtxCluster, inner_ip_list=None) -> Dict[str, Dict]:
    client = Node(ctx_cluster)
    # 查询node列表
    nodes = client.list(formatter=NodeFormatter())
    # 分为两种场景处理
    if inner_ip_list:
        return {inner_ip: node[inner_ip] for node in nodes for inner_ip in node if inner_ip in inner_ip_list}
    return {inner_ip: node[inner_ip] for node in nodes for inner_ip in node}
