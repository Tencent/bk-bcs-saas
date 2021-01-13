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
from typing import Dict, List

import arrow

from backend.utils.basic import getitems

creation_timestamp_path = ".metadata.creationTimestamp"


def calculate_age(create_at):
    s = arrow.get(create_at).datetime
    e = arrow.utcnow().datetime

    delta = e - s
    d_days = delta.days
    d_seconds = delta.seconds
    d_hour = d_seconds // 3600

    if d_days > 0:
        return f"{d_days}d{d_hour}h"

    if d_hour > 0:
        d_minute = (d_seconds % 3600) // 60
        return f"{d_hour}h{d_minute}m"

    return f"{d_seconds // 60}m{d_seconds % 60}s"


def parse_column_data(co_item, columns: List[Dict]) -> Dict:
    column_data = {}
    for col in columns:
        col_name = col["col_name"]
        json_path = col["json_path"]
        value = getitems(co_item, json_path)
        if json_path == creation_timestamp_path:
            column_data[col_name] = calculate_age(value)
        else:
            column_data[col_name] = value
    return column_data


def parse_columns(crd_dict: Dict) -> List[Dict]:
    """
    解析出crd中col名以及其值在spec中的位置(json_path)
    """
    columns = [
        {"col_name": "name", "json_path": ".metadata.name"},
        {"col_name": "namespace", "json_path": ".metadata.namespace"},
    ]

    additional_printer_columns = getitems(crd_dict, "spec.additional_printer_columns")

    if not additional_printer_columns:
        columns.append({"col_name": "AGE", "json_path": creation_timestamp_path})
        return columns

    creation_timestamp_exist = False

    for add_col in additional_printer_columns:
        if add_col.json_path == creation_timestamp_path:
            creation_timestamp_exist = True
        columns.append({"col_name": add_col.name, "json_path": add_col.json_path})

    if not creation_timestamp_exist:
        columns.append({"col_name": "AGE", "json_path": creation_timestamp_path})
    return columns


def to_table_format(crd_dict: Dict, cobjs_list: List) -> Dict:
    """
    :return: 返回给前端约定的表格结构，th_list是表头内容，td_list是对应的表格内容
    """
    columns = parse_columns(crd_dict)
    column_data_list = [parse_column_data(co_item, columns) for co_item in cobjs_list]
    if column_data_list:
        return {"th_list": [col["col_name"] for col in columns], "td_list": column_data_list}
    return {"th_list": [], "td_list": []}
