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


def query_labels(ctx_cluster: CtxCluster, node_name_list: List = None) -> Dict[str, List]:
    nodes = query_cluster_nodes(ctx_cluster)
    # 获取labels
    labels = {}
    for inner_ip, node in nodes.items():
        if node_name_list and node["name"] not in node_name_list:
            continue
        labels[inner_ip] = node["labels"]
    return labels


def set_labels(ctx_cluster: CtxCluster, label_list: List):
    """节点设置标签

    ctx_cluster: 集群模型数据
    taint_list: 节点的污点内容，格式: [{"node_name": "demo", "labels": {"key1": "value1", "key2": "value2"}]
    """
    client = Node(ctx_cluster)
    # 下发的body格式: {"metadata": {"labels": {"demo": "demo"}}}
    tasks = [
        functools.partial(client.patch, {"metadata": {"labels": l["labels"]}}, l["node_name"]) for l in label_list
    ]
    # 当有操作失败的，抛出异常
    async_run(tasks)
