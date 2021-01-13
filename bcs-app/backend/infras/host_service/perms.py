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
import re
from typing import List

from backend.components.cc import get_cc_hosts

from .exceptions import IPPermissionDenied


def check_use_hosts(bk_biz_id: int, username: str, host_ip_list: List):
    resp = get_cc_hosts(bk_biz_id, username)
    ip_list = []
    for info in resp.get("data") or []:
        inner_ip = info.get('bk_host_innerip', '')
        inner_ip_list = re.findall(r'[^;,]+', inner_ip)
        ip_list.extend(inner_ip_list)

    diff_ip_list = set(host_ip_list) - set(ip_list)
    if diff_ip_list:
        raise IPPermissionDenied("can not use ip")
