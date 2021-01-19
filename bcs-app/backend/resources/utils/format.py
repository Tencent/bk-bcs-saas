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
import copy
from typing import Any, Dict, List, Optional, Union

import arrow
from django.utils import timezone
from kubernetes.dynamic.resource import ResourceField, ResourceInstance

from backend.utils.basic import normalize_datetime


def serialize_resource(field: Union[ResourceInstance, ResourceField, List[ResourceField]]) -> Any:
    """将 dynamic client 返回的 ResourceField / ResourceInstance 等对象转换为普通数据结构"""
    if isinstance(field, ResourceField):
        return {k: serialize_resource(v) for k, v in field.__dict__.items()}
    elif isinstance(field, (list, tuple)):
        return [serialize_resource(item) for item in field]
    elif isinstance(field, ResourceInstance):
        return field.to_dict()
    else:
        return field


class InstanceAccessor:
    """方便读取 Kubernetes 资源的工具类，只提供常见方法，不提供完整建模"""

    def __init__(self, data: Dict):
        self.data = data

    @property
    def name(self) -> str:
        return self.data['metadata']['name']


class ResourceDefaultFormatter:
    """格式化 Kubernetes 资源为通用资源格式"""

    def format_list(self, resources: Union[ResourceInstance, List[Dict], None]) -> List[Dict]:
        if isinstance(resources, (list, tuple)):
            return [self.format_dict(res) for res in resources]
        if resources is None:
            return []
        # Type: ResourceInstance with multiple results returned by DynamicClient
        return [self.format_dict(res) for res in resources.to_dict()['items']]

    def format(self, resource: Optional[ResourceInstance]) -> Dict:
        if resource is None:
            return {}
        return self.format_dict(resource.to_dict())

    def format_dict(self, resource_dict: Dict) -> Dict:
        resource_copy = copy.deepcopy(resource_dict)
        metadata = resource_copy['metadata']
        self.set_metadata_null_values(metadata)

        # Get create_time and update_time
        create_time = self.parse_create_time(metadata)
        update_time = metadata['annotations'].get("io.tencent.paas.updateTime") or create_time
        if update_time:
            update_time = normalize_datetime(update_time)
        return {
            "data": resource_copy,
            "clusterId": self.get_cluster_id(metadata),
            "resourceType": resource_copy['kind'],
            "resourceName": metadata['name'],
            "namespace": metadata.get('namespace', ''),
            "createTime": create_time,
            "updateTime": update_time,
        }

    def set_metadata_null_values(self, metadata: Dict):
        """设置 metadata 字段里的空值"""
        metadata['annotations'] = metadata.get('annotations') or {}
        metadata['labels'] = metadata.get('labels') or {}

    def parse_create_time(self, metadata: Dict) -> str:
        """获取 metadata 中的 create_time"""
        create_time = metadata.get("creationTimestamp", "")
        if create_time:
            # create_time format: '2019-12-16T09:10:59Z'
            d_time = arrow.get(create_time).datetime
            create_time = timezone.localtime(d_time).strftime("%Y-%m-%d %H:%M:%S")
        return create_time

    def get_cluster_id(self, metadata: Dict) -> str:
        """获取集群 ID"""
        labels = metadata.get("labels", {})
        return labels.get("io.tencent.bcs.clusterid") or ""
