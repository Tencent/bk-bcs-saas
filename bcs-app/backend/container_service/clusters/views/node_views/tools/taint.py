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

from .node import query_nodes


def query_taints(ctx_cluster: CtxCluster, host_name_list=None) -> Dict[str, List]:
    nodes = query_nodes(ctx_cluster)
    # 获取taints
    if host_name_list:
        return {
            inner_ip: node_info["taints"]
            for inner_ip, node_info in nodes.items()
            if node_info["host_name"] in host_name_list
        }
    else:
        return {inner_ip: node_info["taints"] for inner_ip, node_info in nodes.items()}


def set_taints(ctx_cluster: CtxCluster, taint_list: List):
    """节点设置污点"""
    client = Node(ctx_cluster)
    # 下发的body格式: {"spec": {"taints": [{"key": xxx, "value": xxx, "effect": xxx}]}}
    tasks = [functools.partial(client.patch, {"spec": {"taints": t["taints"]}}, t["host_name"]) for t in taint_list]
    # 当有操作失败的，抛出异常
    async_run(tasks)
