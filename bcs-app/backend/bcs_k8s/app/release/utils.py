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
from typing import Dict, List, Tuple

from backend.resources import secret
from backend.resources.cluster.models import CtxCluster
from backend.utils.basic import getitems, normalize_time

from .constants import ReleaseOperations, ReleaseStatuses


def list_release(access_token: str, project_id: str, cluster_id_list: List[str], namespace: str = None) -> List[Dict]:
    """查询 release 列表"""
    ctx_cluster_list = [
        CtxCluster.create(token=access_token, project_id=project_id, id=cluster_id) for cluster_id in cluster_id_list
    ]
    release_list = []
    for ctx_cluster in ctx_cluster_list:
        client = secret.Secret(ctx_cluster)
        releases = client.list(formatter=secret.ReleaseSecretFormatter())
        # 需要处理release
        # 处理同一集群，同一命名空间下 release 多版本，针对list，仅展示最新的版本
        release_list.extend(get_latest_version_releases(releases))

    # 转换为前端可以展示的字段

    # 按照`last_deployed`字段逆序排列
    release_list.sort(key=lambda x: x["info"]["last_deployed"], reverse=True)


def tranform_transition_status(release_status: str) -> Tuple[bool, bool]:
    """获取 release 任务信息，包含 是否执行中，是否成功"""
    # transitioning_on: True表示执行中， False表示结束
    # transitioning_result: True表示成功， False表示失败
    transitioning_on, transitioning_result = True, True
    if release_status in [ReleaseStatuses.FAILED.value, ReleaseStatuses.UNKNOWN.value]:
        transitioning_on, transitioning_result = False, False
    elif release_status in [
        ReleaseStatuses.DEPLOYED.value,
        ReleaseStatuses.SUPERSEDED.value,
        ReleaseStatuses.UNINSTALLED.value,
    ]:
        transitioning_on = False
    return transitioning_on, transitioning_result


def get_transition_operation(description: str, revision: int) -> str:
    """通过描述和revision获取对应的操作类型"""
    # 如果revision为1，则标识为初创建，操作为create
    if revision == 1:
        return ReleaseOperations.CREATE.value
    if revision > 1:
        if "Upgrade" in description:
            return ReleaseOperations.UPDATE.value
        elif "Rollback" in description:
            return ReleaseOperations.ROLLBACK.value

    return ReleaseOperations.ROLLBACK.value


def tranform_release(release: Dict) -> Dict:
    """转换release字段"""
    chart_info, release_metadata = release["chart"], release["info"]
    transitioning_on, transitioning_result = tranform_transition_status(release_metadata["status"])
    return {
        "name": release["name"],
        "namespace": release["namespace"],
        "revision": release["version"],
        "chart_name": chart_info["metadata"]["name"],
        "chart_version": chart_info["metadata"]["version"],
        "transitioning_message": release_metadata["description"],
        "notes": release_metadata["notes"],
        "created": normalize_time(release_metadata["first_deployed"]),
        "updated": normalize_time(release_metadata["last_deployed"]),
        "transitioning_action": get_transition_operation(release_metadata["description"], release["version"]),
    }


def get_latest_version_releases(releases: Dict) -> List[Dict]:
    """获取最新的release，用于类似 helm list 的展示

    注意: 这里已经限制了同一个集群
    """
    release_by_name_and_namespace = {}
    for release in releases:
        name, namespace = release["name"], release["namespace"]
        # 同一集群下的 release 唯一标识
        release_unique_key = (name, namespace)
        if release_unique_key in release_by_name_and_namespace:
            # release 的 version 大于已经 release_by_name_and_namespace 已存的 version 时，替换对应的内容
            if release_by_name_and_namespace[release_unique_key]["version"] < release["version"]:
                release_by_name_and_namespace[release_unique_key] = release
        else:
            release_by_name_and_namespace[release_unique_key] = release

    return release_by_name_and_namespace.values()
