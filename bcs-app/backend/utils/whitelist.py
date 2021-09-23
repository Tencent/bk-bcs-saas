# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
# TODO: apps/whitelist是否可以统一
from backend.utils.func_controller import get_func_controller


def check_bcs_api_gateway_enabled(cluster_id: str) -> bool:
    """校验是否通过 bcs-api-gateway 链路访问集群 apiserver"""
    func_code = "BCS_API_GATEWAY_FOR_CLUSTER"
    enabled, wlist = get_func_controller(func_code)
    return enabled or cluster_id in wlist
