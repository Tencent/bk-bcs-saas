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


def convert_mappings(mappings, data, reversed=False, default=NotImplemented):
    result = {}
    for k1, k2 in mappings.items():
        if reversed:
            key, target = k2, k1
        else:
            key, target = k1, k2
        if target not in data and default is NotImplemented:
            continue
        result[key] = data[target]
    return result


def num_transform(num, format='to_zore'):
    """数字转换
    to_zore: 标识负值转换为0
    """
    return {
        'to_zore': lambda x: x if x > 0 else 0
    }.get(format)(num)


def str2bool(source):
    """str转换为bool
    True: "true", "True", "1"
    False: "false", "False", "0"
    """
    if not isinstance(source, str):
        raise TypeError(f"{source} not string type")

    mapping = {"true": True, "1": True, "false": False, "0": False}
    source = source.lower()
    if source in mapping:
        return mapping[source]

    raise ValueError(f"{source} can not convert to bool")
