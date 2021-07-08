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
from typing import Any, Optional

from backend.container_service.clusters.base.models import CtxCluster
from backend.resources.node.client import Node


class NodeClient:
    def __init__(self, ctx_cluster: CtxCluster):
        self.client = Node(ctx_cluster)

    def do(self, func_name: str, *args, **kwargs) -> Any:
        func = getattr(self.client, func_name, None)
        if not func:
            raise NotImplementedError(f"unsupported function: {func_name}")
        return func(*args, **kwargs)
