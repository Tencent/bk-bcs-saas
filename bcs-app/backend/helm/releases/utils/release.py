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
import logging
from typing import Dict, List

from backend.container_service.clusters.base.models import CtxCluster
from backend.resources.configs import secret
from backend.utils.basic import getitems

from .formatter import ReleaseSecretFormatter
from .parser import ReleaseParser
from .tools import get_updater_by_resource_annotations

logger = logging.getLogger(__name__)


def list_namespaced_releases(ctx_cluster: CtxCluster, namespace: str) -> List[Dict]:
    """查询namespace下的release
    NOTE: 为防止后续helm release对应的secret名称规则(sh.helm.release.v1.名称.v版本)变动，不直接根据secret名称进行过滤
    """
    client = secret.Secret(ctx_cluster)
    # 查询指定命名空间下的secrets
    return client.list(formatter=ReleaseSecretFormatter(), label_selector="owner=helm", namespace=namespace)


def get_release_detail(ctx_cluster: CtxCluster, namespace: str, release_name: str) -> Dict:
    """获取release详情"""
    release_list = list_namespaced_releases(ctx_cluster, namespace)
    release_list = [release for release in release_list if release.get("name") == release_name]
    if not release_list:
        logger.error(
            "not found release: [cluster_id: %s, namespace: %s, name: %s]", ctx_cluster.id, namespace, release_name
        )
        return {}
    # 通过release中的version对比，过滤到最新的 release data
    # NOTE: helm存储到secret中的release数据，每变动一次，增加一个secret，对应的revision就会增加一个，也就是最大的revision为当前release的存储数据
    return max(release_list, key=lambda item: item["version"])


def get_release_notes(ctx_cluster: CtxCluster, namespace: str, release_name: str) -> str:
    """查询release的notes"""
    release_detail = get_release_detail(ctx_cluster, namespace, release_name)
    return ReleaseParser(release_detail).notes


def refine_namespace_releases(namespace_release_map: Dict, release_info: Dict) -> Dict:
    """根据namespace和release名称，处理release"""
    namespace_release = (release_info["namespace"], release_info["name"])
    if namespace_release in namespace_release_map:
        # 比较version大小，当version大于已经存在的release中的version时，替换release信息
        if namespace_release_map[namespace_release]["version"] < release_info["version"]:
            namespace_release_map[namespace_release] = release_info
    else:
        namespace_release_map[namespace_release] = release_info

    return namespace_release_map


def list_releases(ctx_cluster: CtxCluster, namespace: str = None) -> List[Dict]:
    """查询release, 如果namespace不为None，则过滤namespace下的release"""
    releases = list_namespaced_releases(ctx_cluster, namespace)
    # 因为列表查出来的同一个release会因为升级或者回滚生成多个secret
    # 所以根据命名空间名称+release名称过滤
    namespace_release_map = {}
    for release in releases:
        parser = ReleaseParser(release)
        release_info = parser.metadata
        release_info["updater"] = parser.release_updater
        release_info["chart_metadata"] = parser.chart_metadata
        namespace_release_map = refine_namespace_releases(namespace_release_map, release_info)

    # 根据最后部署时间排序逆序
    release_list = list(namespace_release_map.values())
    release_list.sort(key=lambda item: item["last_deployed"], reverse=False)

    return release_list
