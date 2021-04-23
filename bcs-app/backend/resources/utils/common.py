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
import arrow


def calculate_age(create_at: str) -> str:
    """
    DashBoard 用，计算当前对象存活时间

    :param create_at: 对象创建时间
    :return: 对象存活时间
    """
    return calculate_duration(create_at)


def calculate_duration(start: str, end: str = None) -> str:
    """
    计算 起始 至 终止时间 间时间长度（带单位）

    :param start: 起始时间
    :param end: 终止时间
    :return: 持续时间（带单位）
    """
    if not start:
        return '--'

    start = arrow.get(start)
    end = arrow.get(end) if end else arrow.utcnow()

    duration = end - start
    d_days = duration.days
    d_seconds = duration.seconds
    d_minute = (d_seconds % 3600) // 60
    d_hour = d_seconds // 3600

    if d_days > 0:
        return f"{d_days}d{d_hour}h"

    if d_hour > 0:
        return f"{d_hour}h{d_minute}m"

    if d_minute > 0:
        return f"{d_seconds // 60}m{d_seconds % 60}s"

    return f"{d_seconds % 60}s"
