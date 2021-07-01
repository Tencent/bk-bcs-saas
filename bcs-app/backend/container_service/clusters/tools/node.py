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
from dataclasses import dataclass
from typing import Dict, List

from backend.components.base import ComponentAuth
from backend.components.paas_cc import PaaSCCClient
from backend.container_service.clusters import constants as node_constants
from backend.container_service.clusters.base.models import CtxCluster
from backend.container_service.clusters.models import NodeStatus
from backend.resources.node.client import Node
from backend.resources.utils.format import ResourceDefaultFormatter
from backend.utils.basic import getitems


def get_node_status(conditions: List) -> str:
    """获取节点状态
    ref: https://github.com/kubernetes/dashboard/blob/0de61860f8d24e5a268268b1fbadf327a9bb6013/src/app/backend/resource/node/list.go#L106  # noqa
    """
    for condition in conditions:
        if condition["type"] != node_constants.NodeConditionType.Ready:
            continue
        # 正常可用状态
        if condition["status"] == "True":
            return node_constants.NodeConditionStatus.Ready
        # 节点不健康而且不能接收 Pod
        return node_constants.NodeConditionStatus.NotReady
    # 节点控制器在最近 node-monitor-grace-period 期间（默认 40 秒）没有收到节点的消息
    return node_constants.NodeConditionStatus.Unknown


def query_cluster_nodes(ctx_cluster: CtxCluster) -> Dict[str, Dict]:
    # 查询集群下node信息
    client = Node(ctx_cluster)
    nodes = client.list()
    # 根据传入的inner_ip过滤节点信息
    data = {}
    for node in nodes:
        node_data = node.data
        # 解析数据用于前端展示
        metadata = node_data.get("metadata", {})
        labels = metadata.get("labels", {})

        # 过滤掉master
        if labels.get("node-role.kubernetes.io/master") == "true":
            continue

        taints = getitems(node_data, ["spec", "taints"], [])

        # 组装数据，用于展示
        data[node.inner_ip] = {
            "inner_ip": node.inner_ip,
            "name": node.name,
            "labels": labels,
            "taints": taints,
            "status": get_node_status(getitems(node_data, ["status", "conditions"], [])),
            "unschedulable": getitems(node_data, ["spec", "unschedulable"], False),
        }

    return data


def query_bcs_cc_nodes(ctx_cluster: CtxCluster) -> List:
    """查询bcs cc中的节点数据"""
    client = PaaSCCClient(ComponentAuth(access_token=ctx_cluster.context.auth.access_token))
    node_data = client.get_node_list(ctx_cluster.project_id, ctx_cluster.id)
    return {
        node["inner_ip"]: node
        for node in (node_data.get("results") or [])
        if node["status"] not in [NodeStatus.Removed]
    }


def transform_status(cluster_node_status: str, unschedulable: bool, bcs_cc_node_status: str = None) -> str:
    """转换节点状态"""
    # 如果集群中节点为非正常状态，则返回not_ready
    if cluster_node_status == node_constants.NodeConditionStatus.NotReady:
        return node_constants.BcsCCNodeStatus.NotReady

    # 如果集群中节点为正常状态，根据是否允许调度，转换状态
    if cluster_node_status == node_constants.NodeConditionStatus.Ready:
        if unschedulable:
            if bcs_cc_node_status == node_constants.BcsCCNodeStatus.ToRemoved:
                return node_constants.BcsCCNodeStatus.ToRemoved
            return node_constants.BcsCCNodeStatus.Removable
        else:
            return node_constants.BcsCCNodeStatus.Normal

    return node_constants.BcsCCNodeStatus.Unknown


@dataclass
class NodesData:
    bcs_cc_nodes: Dict  # bcs cc中存储的节点数据
    cluster_nodes: Dict  # 集群中实际存在的节点数据
    cluster_id: str
    cluster_name: str

    @property
    def _normal_status(self) -> List:
        return [
            node_constants.BcsCCNodeStatus.Normal,
            node_constants.BcsCCNodeStatus.ToRemoved,
            node_constants.BcsCCNodeStatus.Removable,
        ]

    def nodes(self) -> List:
        """组装节点数据"""
        # 1. 集群中不存在的节点，并且bcs cc中状态处于初始化中、初始化失败、移除中、移除失败状态时，需要展示bcs cc中数据
        # 2. 集群中存在的节点，则以集群中为准，注意状态的转换
        # 把bcs cc中非正常状态节点放到数组的前面，方便用户查看
        node_list = self._compose_data_by_bcs_cc_nodes()
        node_list.extend(self._compose_data_by_cluster_nodes())
        return node_list

    def _compose_data_by_bcs_cc_nodes(self) -> List:
        # 处理在bcs cc中的节点，但是状态为非正常状态数据
        node_list = []
        for inner_ip in self.bcs_cc_nodes:
            node = self.bcs_cc_nodes[inner_ip]
            if (inner_ip in self.cluster_nodes) or (node["status"] in self._normal_status):
                continue
            node_list.append(node)
        return node_list

    def _compose_data_by_cluster_nodes(self) -> List:
        node_list = []
        # 以集群中数据为准
        for inner_ip, node in self.cluster_nodes.items():
            # 如果bcs cc中存在节点信息，则从bcs cc获取节点的额外数据
            if inner_ip in self.bcs_cc_nodes:
                item = self.bcs_cc_nodes[inner_ip].copy()
                item.update(
                    node,
                    **{
                        "status": transform_status(
                            node["status"], node["unschedulable"], self.bcs_cc_nodes[inner_ip]["status"]
                        ),
                        "cluster_name": self.cluster_name,
                    }
                )
                node_list.append(item)
            else:
                # TODO: 这里先不添加集群名称，以ID展示是否合适
                node["cluster_id"] = self.cluster_id
                node["cluster_name"] = self.cluster_name
                node["status"] = transform_status(node["status"], node["unschedulable"])
                node_list.append(node)
        return node_list
