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
from typing import List

from backend.components import paas_cc


def get_cluster_node_list(access_token: str, project_id: str, cluster_id: str) -> List:
    """
    获取指定集群节点信息列表

    :param access_token: 用户 AccessToken
    :param project_id: 项目 ID
    :param cluster_id: 集群 ID
    :return: 集群下属节点列表
    """
    ret = paas_cc.get_node_list(access_token, project_id, cluster_id)
    node_list = ret.get('data', {}).get('results') or []
    return node_list
