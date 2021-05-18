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
from typing import Dict

from backend.resources.cluster.models import CtxCluster
from backend.resources.workloads.pod import Pod
from backend.utils.error_codes import error_codes


def fetch_pod_config(ctx_cluster: CtxCluster, namespace: str, pod_name: str) -> Dict:
    """
    获取指定 Pod 配置信息

    :param ctx_cluster: 集群 Context
    :param namespace: 命名空间
    :param pod_name: Pod 名称
    :return: Pod 配置信息
    """
    pod = Pod(ctx_cluster).get(namespace=namespace, name=pod_name, is_format=False)
    if not pod:
        raise error_codes.ResNotFoundError.f(f'Type: Pod, Namespace: {namespace}, Name: {pod_name}')
    return pod.to_dict()
