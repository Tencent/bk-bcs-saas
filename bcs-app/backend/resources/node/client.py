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
from typing import Any, Dict, List, Union

from backend.resources.constants import K8sResourceKind
from backend.resources.resource import ResourceClient
from backend.utils.async_run import async_run
from backend.utils.basic import getitems

from .formatter import NodeFormatter


class Node(ResourceClient):
    """节点 client
    针对节点的查询、操作等
    """

    kind = K8sResourceKind.Node.value
    formatter = NodeFormatter()

    def set_labels(self, label_list: List):
        """设置标签

        :param label_list: 要设置的标签信息，格式: [{"node_name": "", "labels": {"key": "val"}}]
        NOTE: 如果要删除某个label时，不建议使用replace，可以把要删除的label的值设置为None
        """
        node_label_list = self.query_field_data(
            ["metadata", "labels"], [label["node_name"] for label in label_list], node_id="name", default_data={}
        )
        # 比对数据，当label在集群节点中存在，而变更的数据中不存在，则需要在变更的数据中设置为None
        for node in label_list:
            labels = node_label_list.get(node["node_name"]) or {}
            # 设置要删除key的值为None
            for key in set(labels) - set(node["labels"]):
                node["labels"][key] = None

        # 下发的body格式: {"metadata": {"labels": {"demo": "demo"}}}
        tasks = [
            functools.partial(self.patch, {"metadata": {"labels": l["labels"]}}, l["node_name"]) for l in label_list
        ]
        # 当有操作失败的，抛出异常
        async_run(tasks)

    def set_taints(self, taint_list: List):
        """设置污点

        :param taint_list: 要设置的污点信息，格式: [{"node_name": "", "taints": [{"key": "", "value": "", "effect": ""}]}]
        """
        # 下发的body格式: {"spec": {"taints": [{"key": xxx, "value": xxx, "effect": xxx}]}}
        tasks = [functools.partial(self.patch, {"spec": {"taints": t["taints"]}}, t["node_name"]) for t in taint_list]
        # 当有操作失败的，抛出异常
        async_run(tasks)

    def query_labels(self, node_name_list: List[str] = None) -> Dict:
        """查询标签"""
        return self.query_field_data(["metadata", "labels"], node_name_list, default_data={})

    def query_taints(self, node_name_list: List[str] = None) -> Dict:
        """查询污点"""
        return self.query_field_data(["spec", "taints"], node_name_list, default_data=[])

    def query_field_data(
        self,
        field: Union[List, str],
        node_name_list: List[str] = None,
        node_id: str = "inner_ip",
        default_data: Any = None,
    ) -> Dict:
        """查询节点属性

        :param field: 查询的属性
        :param node_name_list: 节点name列表
        :param node_id: 节点的标识，支持name和inner_ip，默认是inner_ip
        :returns: 返回节点的属性数据
        """
        nodes = self.list()
        data = {}
        for node in nodes:
            if node_name_list and node["name"] not in node_name_list:
                continue
            data[node[node_id]] = getitems(node["data"], field, default=default_data)
        return data
