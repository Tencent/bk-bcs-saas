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
from typing import Sequence, Iterator, Dict, Collection

from kubernetes.dynamic.resource import ResourceField
from backend.resources.utils.format import serialize_resource
from backend.utils.basic import getitems


def filter_by_owners(
    resources: Iterator[ResourceField], owner_kind: str, owner_names: Collection[str]
) -> Sequence[Dict]:
    """按照资源所有者过滤资源列表

    :param resources: 资源列表，通过 DynamicClient.get() 查询返回的结果
    :param owner_kind: 所有者资源类型
    :param owner_names: 所有者资源名称，接收多个
    """
    resources = serialize_resource(resources)
    results = []
    for data in resources:
        for owner in getitems(data, 'metadata.ownerReferences', []):
            if owner['name'] in owner_names and owner['kind'] == owner_kind:
                results.append(data)
                break
    return results
