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
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from django.conf import settings
from requests import PreparedRequest
from requests.auth import AuthBase

from .base import BaseHttpClient, BkApiClient, ComponentAuth, response_handler, update_url_parameters

# bcs api的版本
bcs_version = "v4"

record_not_exist_code = 1405420
record_exist_code = 1405405


class BcsApiConfig:
    """BcsApi 系统配置对象，为 Client 提供地址等信息"""

    def __init__(self, host: str):
        self.host = host

        # BCS API 系统接口地址
        self.query_cluster_id_url = f"{host}/{{env_name}}/rest/clusters/bcs/query_by_id/"
        self.get_cluster_credentials_url = f"{host}/{{env_name}}/rest/clusters/{{bcs_cluster_id}}/client_credentials"


class BcsApiGatewayConfig:
    def __init__(self, host: str, env: str):
        self.host = host

        # cluster manager相关接口url
        self.query_project_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/project/{{project_id}}"
        self.create_project_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/project/{{project_id}}"
        self.update_project_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/project/{{project_id}}"
        self.add_cluster_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/cluster/{{cluster_id}}"
        self.delete_cluster_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/cluster/{{cluster_id}}"
        self.update_cluster_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/cluster/{{cluster_id}}"
        self.add_nodes_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/cluster/{{cluster_id}}/node"
        self.delete_nodes_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/cluster/{{cluster_id}}/node"
        self.query_task_url = f"{host}/{env}/{bcs_version}/clustermanager/v1/task/{{task_id}}"


class BcsApiAuth(AuthBase):
    """用于调用 bcs-api 系统的鉴权对象"""

    def __init__(self, access_token: str):
        self.access_token = access_token

    def __call__(self, r: PreparedRequest):
        # 从配置文件读取访问系统的通用 Token，置入请求头中
        auth_token = getattr(settings, "BCS_AUTH_TOKEN", "")
        r.headers['Authorization'] = auth_token
        r.headers['Content-Type'] = 'application/json'

        # 在 GET 请求参数中追加 access_token
        r.url = update_url_parameters(r.url, {'access_token': self.access_token})
        return r


@dataclass
class ProjectReservedConfig:
    bgID: str = ""
    bgName: str = ""
    deptID: str = ""
    deptName: str = ""
    centerID: str = ""
    centerName: str = ""
    isSecret: bool = False
    deployType: int = 2  # 业务部署类型，1:物理机部署，2:容器部署
    isOffline: bool = False  # 项目是否已经离线，默认False
    useBKRes: bool = False  # 是否使用蓝鲸提供的资源池，主要用于资源计费，默认False
    projectType: int = 1  # 1:platform，2:business


@dataclass
class ProjectBasicConfig:
    """项目的基本配置
    projectID: 项目ID，长度为32位字符串
    name: 项目名称
    englishName: 项目英文缩写，长度不能超过32字符
    kind: 项目中集群类型，支持k8s/mesos
    businessID: 项目绑定的BK CC的业务ID
    credentials: 记录的账户信息
    description: 项目的描述信息，默认为空
    """

    projectID: str
    name: str
    englishName: str
    kind: str
    businessID: str
    description: str
    credentials: Dict = field(default_factory=dict)


@dataclass
class ProjectConfig:
    """项目配置信息"""

    creator: str
    basic_config: ProjectBasicConfig
    reserved_config: ProjectReservedConfig


@dataclass
class UpdatedProjectConfig:
    """更新项目配置信息"""

    projectID: str
    updater: str
    name: str
    kind: str
    businessID: str


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
    manageType: str = "INDEPENDENT_CLUSTER"
    vpcID: str = ""
    cloudID: str = ""
    nodes: List = field(default_factory=list)
    networkSettings: Dict = field(default_factory=dict)
    clusterBasicSettings: Dict = field(default_factory=dict)
    clusterAdvanceSettings: Dict = field(default_factory=dict)
    nodeSettings: Dict = field(default_factory=dict)
    systemReinstall: bool = False
    initLoginPassword: str = ""
    status: str = ""


@dataclass
class BcsClusterConfig:
    """集群初始化时，BCS需要的基本配置"""

    projectID: str
    businessID: str
    clusterID: str
    clusterName: str
    provider: str
    environment: str  # 集群环境，如prod、debug、test
    engineType: str  # 引擎类型，如k8s、mesos
    clusterType: str = "single"  # 集群类型, 例如[federation, single], federation表示为联邦集群，single表示独立集群，默认为single
    isExclusive: bool = False  # 是否为独占集群
    federationClusterID: str = ""  # 联邦集群ID
    labels: Dict = field(default_factory=dict)
    onlyCreateInfo: bool = False
    bcsAddons: Dict = field(default_factory=dict)
    extraAddons: Dict = field(default_factory=dict)


@dataclass
class ClusterConfig:
    """集群配置"""

    creator: str
    bcs_cluster_config: BcsClusterConfig
    cloud_cluster_config: CloudClusterConfig


@dataclass
class UpdatedClusterConfig:
    """更新的集群配置选项"""

    projectID: str
    clusterID: str
    updater: str
    status: str
    clusterName: str = ""
    labels: Dict = field(default_factory=dict)


@dataclass
class NodeConfig:
    nodes: List[str]
    nodeGroupID: str = ""
    onlyCreateInfo: bool = False
    initLoginPassword: str = ""


class BcsApiClient(BkApiClient):
    """访问 BCS API 服务的 Client 对象
    :param auth: 包含校验信息的对象
    API 方法常用请求参数说明
    ===
    :param env_name: 集群环境，比如 stag/prod
    :param project_id: 项目 ID
    :param cluster_id: 集群 ID
    :param bcs_cluster_id: 集群在 BCS 系统中的唯一 ID
    """

    def __init__(self, auth: ComponentAuth):
        self._config = BcsApiConfig(host=settings.BCS_API_PRE_URL)
        self._client = BaseHttpClient(BcsApiAuth(auth.access_token))
        self._apigw_config = BcsApiGatewayConfig(host=settings.BCS_API_GW_PRE_URL, env=settings.BCS_API_GW_ENV)
        self._apigw_client = BaseHttpClient(BcsApiAuth(auth.access_token))

    def query_cluster_id(self, env_name: str, project_id: str, cluster_id: str) -> str:
        """查询集群在 BCS-Api 中的 ID
        :returns: 集群 ID 字符串
        """
        url = self._config.query_cluster_id_url.format(env_name=env_name)
        resp = self._client.request_json(
            'GET', url, params={'project_id': project_id, 'cluster_id': cluster_id}, raise_for_status=False
        )
        return resp['id']

    def get_cluster_credentials(self, env_name: str, bcs_cluster_id: str) -> Dict:
        """
        获取访问集群 apiserver 所需的鉴权信息，比如证书、user_token、server_address_path 等
        :returns: 包含集群鉴权信息的字典
        """
        url = self._config.get_cluster_credentials_url.format(env_name=env_name, bcs_cluster_id=bcs_cluster_id)
        return self._client.request_json('GET', url, raise_for_status=False)

    @response_handler()
    def query_project(self, project_id: str) -> Dict:
        """查询项目信息
        :param project_id: 项目ID
        :returns: 返回项目信息
        """
        url = self._apigw_config.query_project_url.format(project_id=project_id)
        return self._apigw_client.request_json("GET", url)

    def create_project(self, project_config: ProjectConfig) -> Dict:
        """创建项目
        :param project_config: 项目信息，包含项目的基本信息和项目的保留字段信息
        :returns: 返回项目信息
        """
        # 组装参数
        project_config_data = asdict(project_config.basic_config)
        project_config_data.update(asdict(project_config.reserved_config), creator=project_config.creator)
        # 下发配置
        url = self._apigw_config.create_project_url.format(project_id=project_config_data["projectID"])
        return self._apigw_client.request_json("POST", url, json=project_config_data)

    def update_project(self, project_config: UpdatedProjectConfig) -> Dict:
        """更新项目
        :param project_config: 更新的项目信息
        :returns: 返回更新的项目信息
        """
        # 组装参数
        project_config_data = asdict(project_config)
        # 下发配置
        url = self._apigw_config.create_project_url.format(project_id=project_config_data["projectID"])
        return self._apigw_client.request_json("PUT", url, json=project_config_data)

    def add_cluster(self, cluster_config: ClusterConfig) -> Dict:
        """添加集群
        :param creator: 创建者
        :param cluster_config: 集群初始化的配置，包含bcs平台需要的信息和集群初始化需要的信息
        :returns: 返回初始化的集群的信息，任务信息，格式: {"data": {}, "task": {}}
        """
        # 组装参数
        cluster_config_data = asdict(cluster_config.cloud_cluster_config)
        cluster_config_data.update(asdict(cluster_config.bcs_cluster_config), creator=cluster_config.creator)
        # 下发初始化配置
        url = self._apigw_config.add_cluster_url.format(cluster_id=cluster_config_data["clusterID"])
        return self._apigw_client.request_json("POST", url, json=cluster_config_data)

    @response_handler()
    def update_cluster(self, cluster_config: UpdatedClusterConfig) -> Dict:
        """更新集群
        :param cluster_config: 更新集群的配置
        :returns: 返回集群的配置
        """
        # 组装参数，并去掉为None的属性
        cluster_config_data = {k: v for k, v in asdict(cluster_config).items() if v is not None}
        # 下发更新的配置
        url = self._apigw_config.update_cluster_url.format(cluster_id=cluster_config_data["clusterID"])
        return self._apigw_client.request_json("PUT", url, json=cluster_config_data)

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
        :returns: 返回删除的集群信息，任务信息
        """
        url = self._apigw_config.delete_cluster_url.format(cluster_id=cluster_id)
        params = {"isForced": is_force, "resourceClean": is_clean_resource, "onlyDeleteInfo": only_delete_info}
        return self._apigw_client.request_json("DELETE", url, params=params)

    @response_handler()
    def add_nodes(self, cluster_id: str, node_config: NodeConfig) -> Dict:
        """添加节点
        :param cluster_id: 集群ID
        :param node_config: 节点配置
        :returns: 返回节点的数据，包含任务ID
        """
        url = self._apigw_config.add_nodes_url.format(cluster_id=cluster_id)
        data = asdict(node_config)
        data["clusterID"] = cluster_id
        return self._apigw_client.request_json("POST", url, json=data)

    @response_handler()
    def delete_nodes(
        self, cluster_id: str, nodes: List[str], delete_mode: str = "RETAIN", is_force: bool = False
    ) -> Dict:
        """删除节点
        :param cluster_id: 集群ID
        :param nodes: 节点列表
        :param delete_mode: 删除模式，RETAIN(移除集群，但是保留主机)，TERMINATE(只支持按量计费的机器)
        :param is_force: 是否强制删除
        :returns: 返回删除的节点信息，包含任务ID
        """
        url = self._apigw_config.delete_nodes_url.format(cluster_id=cluster_id)
        data = {"clusterID": cluster_id, "nodes": nodes, "deleteMode": delete_mode, "isForce": is_force}
        return self._apigw_client.request_json("DELETE", url, json=data)

    def query_task(self, task_id: str) -> Dict:
        """查询任务状态
        :param task_id: 任务ID
        :returns: 返回任务的执行详情
        """
        url = self._apigw_config.query_task_url.format(task_id=task_id)
        return self._apigw_client.request_json("GET", url)
