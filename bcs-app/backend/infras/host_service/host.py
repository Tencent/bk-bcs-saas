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

from backend.components import cc, gse


def get_cc_hosts(cc_app_id: str, username: str, request_data: Dict = None) -> List:
    """获取主机信息
    :param cc_app_id: 业务 ID
    :param username: 当前请求的用户名
    :param request_data: 包含资源池信息，集群信息、access_token，可以为空
    """
    resp = cc.get_app_hosts(username, cc_app_id)
    if not resp.get("result"):
        return []
    return resp.get("data") or []


def get_agent_status(username: str, ip_list: List) -> List:
    """查询主机 agent 状态
    :param username: 当前请求的用户名
    :param ip_list: IP 列表，用于查询主机的 agent 状态
    """
    hosts = []
    for info in ip_list:
        # 查询所属区域云区域
        plat_info = info.get("bk_cloud_id") or []
        plat_id = plat_info[0]["id"] if plat_info else 0
        hosts.extend(
            [{"plat_id": plat_id, "bk_cloud_id": plat_id, "ip": ip} for ip in info.get("inner_ip", "").split(",")]
        )
    return gse.get_agent_status(username, hosts)
