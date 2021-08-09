# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from dataclasses import dataclass
from typing import Dict, List

from backend.components.bcs import mesos
from backend.container_service.projects.base.constants import ProjectKind


class NodeLabelsQuerier:
    def __init__(self, access_token: str, project_id: str):
        self.access_token = access_token
        self.project_id = project_id

    def query_labels(self, cluster_id_list: List[str]) -> Dict:
        return {}


class MesosNodeLabelsQuerier(NodeLabelsQuerier):
    def _refine_labels_key_val(self, labels: List) -> Dict:
        """组装格式: {key: [val1, val2]}，便于前端通过key，展示不同节点的value"""
        key_val = {}
        for label in labels:
            # NOTE: 当节点label为空时，返回格式为{"string": None}
            label_strings = label.get("strings") or {}
            for key, vals in label_strings.items():
                val = vals.get("value", "")
                if key in key_val:
                    key_val[key].add(val)
                else:
                    key_val[key] = set([val])
        return key_val

    def query_labels(self, cluster_id_list: List[str]) -> Dict:
        labels = []
        for cluster_id in cluster_id_list:
            client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, None)
            # data 格式: [{"innerIP": xxx, "strings": {key: {"value": val}}}]
            data = client.get_agent_attrs()
            labels.extend(data)
        # 提取labels中的key和value
        return self._refine_labels_key_val(labels)


class K8sNodeLabelsQuerier(NodeLabelsQuerier):
    def query_labels(self, cluster_id_list: List[str]) -> Dict:
        raise NotImplementedError


def get_label_querier(project_kind: int, access_token: str, project_id: str):
    if project_kind == ProjectKind.MESOS.value:
        return MesosNodeLabelsQuerier(access_token=access_token, project_id=project_id)
    return K8sNodeLabelsQuerier(access_token=access_token, project_id=project_id)
