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
from typing import Dict, List

from attr import asdict, dataclass
from django.conf import settings

from ..base import BaseHttpClient, BkApiClient, ComponentAuth, response_handler
from . import BcsApiAuth
from .constants import BCS_API_VERSION, ClusterManageType, ManageType


class BcsApiGatewayConfig:
    def __init__(self, host: str, env: str):
        self.host = host

        _cluster_api_url_prefix = f"{host}/{env}/{BCS_API_VERSION}/clustermanager/v1"
        # cluster manager中集群相关接口url
        self.add_cluster_url = f"{_cluster_api_url_prefix}/cluster/{{cluster_id}}"
        self.delete_cluster_url = f"{_cluster_api_url_prefix}/cluster/{{cluster_id}}"
        self.update_cluster_url = f"{_cluster_api_url_prefix}/cluster/{{cluster_id}}"
        self.add_nodes_url = f"{_cluster_api_url_prefix}/cluster/{{cluster_id}}/node"
        self.delete_nodes_url = f"{_cluster_api_url_prefix}/cluster/{{cluster_id}}/node"
        self.query_task_url = f"{_cluster_api_url_prefix}/task/{{task_id}}"


@dataclass
class CloudClusterConfig:
    """集群初始化需要的基本配置
    region: 区域
    manageType: 集群管理类型，公有云时生效，MANAGED_CLUSTER(云上托管集群)，INDEPENDENT_CLUSTER(独立集群，自行维护)
    master: 集群master
    vpcID: vpc ID
    cloudID: 所属云ID
    nodes: 集群的节点
    networkSettings: 网络配置
    clusterBasicSettings: 集群的基本配置
    clusterAdvanceSettings: 集群的高级配置
    nodeSettings: 节点配置信息
    systemReinstall: 是否重装master节点的系统，机器被托管情况下有效
    initLoginPassword: 重装master节点的系统时，初始化password，机器被托管情况下有效
    status: 状态
    """

    region: str
    master: List
    manageType: str = ManageType.MANAGED_CLUSTER
    vpcID: str = ""
    cloudID: str = ""
    nodes: List = []
    networkSettings: Dict = {}
    clusterBasicSettings: Dict = {}
    clusterAdvanceSettings: Dict = {}
    nodeSettings: Dict = {}
    systemReinstall: bool = False
    initLoginPassword: str = ""
    status: str = ""


@dataclass
class BcsBasicConfig:
    """集群初始化时，BCS需要的基本配置"""

    projectID: str
    businessID: str
    clusterID: str
    clusterName: str
    provider: str
    environment: str  # 集群环境，如prod、debug、test
    engineType: str  # 引擎类型，如k8s
    clusterType: str = ClusterManageType.SINGLE
    isExclusive: bool = False  # 是否为独占集群
    federationClusterID: str = ""  # 联邦集群ID
    labels: Dict = {}
    onlyCreateInfo: bool = False
    bcsAddons: Dict = {}
    extraAddons: Dict = {}


@dataclass
class ClusterConfig:
    """集群配置"""

    creator: str
    bcs_basic_config: BcsBasicConfig
    cloud_cluster_config: CloudClusterConfig


@dataclass
class UpdatedClusterConfig:
    """更新的集群配置选项"""

    projectID: str
    clusterID: str
    updater: str
    status: str
    clusterName: str = ""
    labels: Dict = {}


@dataclass
class NodeConfig:
    nodes: List[str]
    nodeGroupID: str = ""
    onlyCreateInfo: bool = False
    initLoginPassword: str = ""


class BcsClusterApiClient(BkApiClient):
    """访问 BCS 集群 API 服务的 Client 对象
    :param auth: 包含校验信息的对象
    """

    def __init__(self, auth: ComponentAuth):
        self._config = BcsApiGatewayConfig(host=settings.BCS_API_GW_DOMAIN, env=settings.BCS_API_GW_ENV)
        self._client = BaseHttpClient(BcsApiAuth(auth.access_token))

    def add_cluster(self, cluster_config: ClusterConfig) -> Dict:
        """添加集群
        :param creator: 创建者
        :param cluster_config: 集群初始化的配置，包含bcs平台需要的信息和集群初始化需要的信息
        :return: 返回初始化的集群的信息，任务信息，格式: {"data": {}, "task": {}}
        """
        # 组装参数
        cluster_config_data = asdict(cluster_config.cloud_cluster_config)
        cluster_config_data.update(asdict(cluster_config.bcs_basic_config), creator=cluster_config.creator)
        # 下发初始化配置
        url = self._config.add_cluster_url.format(cluster_id=cluster_config_data["clusterID"])
        return self._client.request_json("POST", url, json=cluster_config_data)

    @response_handler()
    def update_cluster(self, cluster_config: UpdatedClusterConfig) -> Dict:
        """更新集群
        :param cluster_config: 更新集群的配置
        :return: 返回集群的配置
        """
        # 组装参数，并去掉为None的属性
        cluster_config_data = {k: v for k, v in asdict(cluster_config).items() if v is not None}
        # 下发更新的配置
        url = self._config.update_cluster_url.format(cluster_id=cluster_config_data["clusterID"])
        return self._client.request_json("PUT", url, json=cluster_config_data)

    def delete_cluster(
        self,
        cluster_id: str,
        is_force: bool = False,
        is_clean_resource: bool = True,
        only_delete_info: bool = False,
    ) -> Dict:
        """删除集群
        :param cluster_id: 集群ID
        :param is_force: 是否强制删除，默认为False
        :param is_clean_resource: 强制删除有效时，是否清理机器上部署的资源
        :param only_delete_info: 是否仅删除记录的信息，默认为False
        :return: 返回删除的集群信息，任务信息
        """
        url = self._config.delete_cluster_url.format(cluster_id=cluster_id)
        params = {"isForced": is_force, "resourceClean": is_clean_resource, "onlyDeleteInfo": only_delete_info}
        return self._client.request_json("DELETE", url, params=params)

    @response_handler()
    def add_nodes(self, cluster_id: str, node_config: NodeConfig) -> Dict:
        """添加节点
        :param cluster_id: 集群ID
        :param node_config: 节点配置
        :return: 返回节点的数据，包含任务ID
        """
        url = self._config.add_nodes_url.format(cluster_id=cluster_id)
        data = asdict(node_config)
        data["clusterID"] = cluster_id
        return self._client.request_json("POST", url, json=data)

    @response_handler()
    def delete_nodes(
        self, cluster_id: str, nodes: List[str], delete_mode: str = "RETAIN", is_force: bool = False
    ) -> Dict:
        """删除节点
        :param cluster_id: 集群ID
        :param nodes: 节点列表
        :param delete_mode: 删除模式，RETAIN(移除集群，但是保留主机)，TERMINATE(只支持按量计费的机器)
        :param is_force: 是否强制删除
        :return: 返回删除的节点信息，包含任务ID
        """
        url = self._config.delete_nodes_url.format(cluster_id=cluster_id)
        data = {"clusterID": cluster_id, "nodes": nodes, "deleteMode": delete_mode, "isForce": is_force}
        return self._client.request_json("DELETE", url, json=data)

    def query_task(self, task_id: str) -> Dict:
        """查询任务状态
        :param task_id: 任务ID
        :return: 返回任务的执行详情
        """
        url = self._config.query_task_url.format(task_id=task_id)
        return self._client.request_json("GET", url)
