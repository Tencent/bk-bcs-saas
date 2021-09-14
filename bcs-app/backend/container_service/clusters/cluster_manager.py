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
import logging
from typing import Dict, List

from django.conf import settings

from backend.components import base as comp_base
from backend.components import paas_cc
from backend.components.bcs_api import cluster
from backend.container_service.clusters.models import CommonStatus

from . import constants

logger = logging.getLogger(__name__)


def create_cluster(access_token: str, project_id: str, cc_app_id: int, data: Dict) -> Dict:
    """创建集群信息"""
    bcs_cc_client = paas_cc.PaaSCCClient(comp_base.ComponentAuth(access_token))
    cluster_env = settings.CLUSTER_ENV.get(data["environment"])
    data["environment"] = cluster_env
    cluster_data = bcs_cc_client.create_cluster(project_id, data)

    # 写入数据到clustermanager
    bcs_basic_config = cluster.BcsBasicConfig(
        projectID=project_id,
        businessID=str(cc_app_id),
        clusterID=cluster_data["cluster_id"],
        clusterName=data["name"],
        provider="bcs",
        environment=cluster_env,
        engineType=data["coes"],
        onlyCreateInfo=True,
    )
    # NOTE: 切换流程后需要适配集群的配置
    cloud_cluster_config = cluster.CloudClusterConfig(
        region=data.get("area_id"),
        master=data.get("master_ips") or [],
        vpcID=data.get("vpc_id"),
        clusterBasicSettings={"version": data.get("version", "")},
        clusterAdvanceSettings={
            "containerRuntime": constants.ContainerRuntime.Docker,
            "IPVS": True if data.get("kube_proxy_mode") == constants.KubeProxy.IPVS else False,
        },
    )
    try:
        cluster_config = cluster.ClusterConfig(
            creator=data["creator"], bcs_basic_config=bcs_basic_config, cloud_cluster_config=cloud_cluster_config
        )
        client = cluster.BcsClusterApiClient(comp_base.ComponentAuth(access_token))
        client.add_cluster(cluster_config)
    except Exception as e:
        logger.error("add clustermanager cluster failed, %s", e)
    return cluster_data


def update_cluster(access_token: str, project_id: str, cluster_id: str, data: Dict) -> Dict:
    """更新集群"""
    bcs_cc_client = paas_cc.PaaSCCClient(comp_base.ComponentAuth(access_token))
    cluster_data = bcs_cc_client.update_cluster(project_id, cluster_id, data)
    cluster_config = cluster.UpdatedClusterConfig(
        projectID=project_id,
        clusterID=cluster_id,
        updater=data.get("updater"),
        clusterName=data.get("name"),
        status=constants.ClusterStatus.RUNNING,
    )
    try:
        client = cluster.BcsClusterApiClient(comp_base.ComponentAuth(access_token))
        client.update_cluster(cluster_config)
    except Exception as e:
        logger.error("update clustermanager cluster failed, %s", e)

    return cluster_data


def delete_cluster(access_token: str, project_id: str, cluster_id: str) -> Dict:
    """删除集群"""
    bcs_cc_client = paas_cc.PaaSCCClient(comp_base.ComponentAuth(access_token))
    cluster_data = bcs_cc_client.update_cluster(project_id, cluster_id, {"status": CommonStatus.Removing})
    try:
        client = cluster.BcsClusterApiClient(comp_base.ComponentAuth(access_token))
        client.delete_cluster(cluster_id=cluster_id, only_delete_info=True)
    except Exception as e:
        logger.error("delete clustermanager cluster failed, %s", e)
    return cluster_data


def add_nodes(access_token: str, project_id: str, cluster_id: str, data: Dict):
    """添加节点"""
    bcs_cc_client = paas_cc.PaaSCCClient(comp_base.ComponentAuth(access_token))
    bcs_cc_client.add_nodes(project_id, cluster_id, data)
    try:
        client = cluster.BcsClusterApiClient(comp_base.ComponentAuth(access_token))
        node_config = cluster.NodeConfig(nodes=[node["inner_ip"] for node in data["objects"]], onlyCreateInfo=True)
        client.add_nodes(cluster_id, node_config)
    except Exception as e:
        logger.error("add clustermanager nodes failed, %s", e)


def delete_nodes(access_token: str, project_id: str, cluster_id: str, node_ips: List[str]):
    """删除节点"""
    bcs_cc_client = paas_cc.PaaSCCClient(comp_base.ComponentAuth(access_token))
    data = [paas_cc.UpdateNodesData(inner_ip=ip, status=CommonStatus.Removing) for ip in node_ips]
    bcs_cc_client.update_node_list(project_id, cluster_id, data)
    try:
        client = cluster.BcsClusterApiClient(comp_base.ComponentAuth(access_token))
        client.delete_nodes(cluster_id, node_ips)
    except Exception as e:
        logger.error("update clustermanager nodes failed, %s", e)
