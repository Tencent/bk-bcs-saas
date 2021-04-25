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
from typing import Dict, List, Union

from backend.resources.constants import K8sResourceKind


def calc_max_resource_version(resources: List[Dict]) -> Union[str, None]:
    """ 计算资源列表中最大的 resource_version """
    if not resources:
        return None
    return str(max(int(r['resourceVersion']) for r in resources))


def gen_list_resource_response_data(resources: List, kind: K8sResourceKind) -> Dict:
    """ 通用的生成 list resource 接口返回结果逻辑 """
    return {
        'total': len(resources),
        'list': resources,
        'kind': kind.value,
        'max_rv': calc_max_resource_version(resources),
    }
