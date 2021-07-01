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
import functools
from typing import Dict, List

from backend.container_service.clusters.base.models import CtxCluster
from backend.resources.node.client import Node
from backend.utils.async_run import async_run
from backend.utils.basic import getitems

from .node import query_cluster_nodes


def query_taints(ctx_cluster: CtxCluster, node_name_list=None) -> Dict[str, List]:
    nodes = query_cluster_nodes(ctx_cluster)
    # 获取taints
    taints = {}
    for inner_ip, node in nodes.items():
        if node_name_list and node["name"] not in node_name_list:
            continue
        taints[inner_ip] = node["taints"]
    return taints


def set_taints(ctx_cluster: CtxCluster, taint_list: List):
    """节点设置污点，因为可能有多个节点分别调用接口完成打污点，使用asyncio处理，减少耗时

    ctx_cluster: 集群模型数据
    taint_list: 节点的污点内容，格式: [{"node_name": "demo", "taints": [{"key": xxx, "value": xxx, "effect": xxx}]]
    """
    client = Node(ctx_cluster)
    # 下发的body格式: {"spec": {"taints": [{"key": xxx, "value": xxx, "effect": xxx}]}}
    tasks = [functools.partial(client.patch, {"spec": {"taints": t["taints"]}}, t["node_name"]) for t in taint_list]
    # 当有操作失败的，抛出异常
    async_run(tasks)
