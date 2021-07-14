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
from typing import Any, List, Optional

from backend.container_service.clusters.base.models import CtxCluster
from backend.container_service.clusters.constants import K8S_RESERVED_NAMESPACE_LIST
from backend.resources.node.client import Node


class NodeRespBuilder:
    """构造节点 API 返回

    TODO: 现阶段返回先方便前端处理，拆分后，调整返回为{manifest: xxx, manifest_ext: xxx}
          manifest中放置原始node数据, manifest_ext中存放处理的状态等数据
    """

    def __init__(self, ctx_cluster: CtxCluster):
        self.client = Node(ctx_cluster)

    def do(self, func_name: str, *args, **kwargs) -> Any:
        """
        :param func_name: 函数名称
        :returns: 返回请求数据
        """
        func = getattr(self.client, func_name, None)
        if not func:
            raise NotImplementedError(f"unsupported function: {func_name}")
        return func(*args, **kwargs)

    def list_nodes(self, *args, **kwargs) -> Any:
        """查询类 API"""
        nodes = self.do("list", is_format=False)
        return {
            "manifest": nodes.data.to_dict(),
            "manifest_ext": {
                node["metadata"]["uid"]: {
                    "status": node.node_status,
                    "labels": {key: "readonly" for key in filter_label_keys(list(node.labels.keys()))},
                }
                for node in nodes.items
            },
        }


def filter_label_keys(label_keys: List) -> List:
    """过滤满足条件的标签key"""
    return list(filter(lambda key: is_reserved_label_key(key), label_keys))


def is_reserved_label_key(label_key: str) -> bool:
    """判断label是否匹配
    NOTE: 现阶段包含指定字符串的label，认为是预留的label，不允许编辑
    """
    for match_key in K8S_RESERVED_NAMESPACE_LIST:
        if match_key in label_key:
            return True
    return False
