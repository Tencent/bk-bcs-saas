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
from urllib import parse

import arrow

from backend.resources.pod.constants import Log


def calc_previous_page(logs: List[Log], slz_data: Dict, url_prefix: str):
    """计算上一页的请求链接"""
    if len(logs) < 2:
        return None

    previous_params = {
        "container_name": slz_data["container_name"],
        'previous': slz_data['previous'],
        "started_at": logs[0].time,
        "finished_at": logs[-1].time,
    }
    previous = url_prefix + "?" + parse.urlencode(previous_params)
    return previous


def calc_since_time(started_at: str, finished_at: str):
    """计算下一次的开始时间
    简单场景, 认为日志打印量是均衡的，通过计算时间差获取
    """
    _started_at = arrow.get(started_at)
    _finished_at = arrow.get(finished_at)
    span = _finished_at - _started_at
    offset = _started_at - span
    # 返回纳秒级别时间
    new_since_time = offset.format("YYYY-MM-DDTHH:mm:ss.SSSSSSSSS") + "Z"
    return new_since_time
