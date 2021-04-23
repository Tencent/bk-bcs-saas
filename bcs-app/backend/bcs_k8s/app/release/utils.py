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

from backend.resources import secret
from backend.resources.cluster.models import CtxCluster


def list_release(access_token: str, project_id: str, cluster_id_list: List[str], namespace: str = None) -> List[Dict]:
    """查询 release 列表"""
    ctx_cluster_list = [
        CtxCluster.create(token=access_token, project_id=project_id, id=cluster_id) for cluster_id in cluster_id_list
    ]
    release_list = []
    for ctx_cluster in ctx_cluster_list:
        client = secret.Secret(ctx_cluster)
        client.list(formatter=secret.ReleaseSecretFormatter())
