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
import functools
from dataclasses import asdict, dataclass
from typing import List

from backend.apps.instance import constants as instance_constants
from backend.components.bk_repo import BkRepoClient
from backend.utils.async_run import async_run
from backend.utils.basic import get_bcs_component_version

try:
    from backend.apps.datalog.utils import get_data_id_by_project_id
except ImportError:
    from backend.apps.datalog_ce.utils import get_data_id_by_project_id


def get_kubectl_version(cluster_version, kubectl_version_info, default_kubectl_version):
    return get_bcs_component_version(cluster_version, kubectl_version_info, default_kubectl_version)


@dataclass
class BCSInjectData:
    source_type: str
    creator: str
    updator: str
    version: str
    project_id: str
    app_id: str
    cluster_id: str
    namespace: str
    stdlog_data_id: str
    image_pull_secret: str


def get_stdlog_data_id(project_id):
    data_info = get_data_id_by_project_id(project_id)
    return str(data_info.get('standard_data_id'))


def provide_image_pull_secrets(namespace):
    """
    imagePullSecrets:
    - name: paas.image.registry.namespace_name
    """
    # 固定前缀(backend.apps.instance.constants.K8S_IMAGE_SECRET_PRFIX)+namespace
    return f"{instance_constants.K8S_IMAGE_SECRET_PRFIX}{namespace}"


@dataclass
class ChartData:
    project_name: str
    repo_name: str
    chart_name: str


@dataclass
class RepoAuth:
    username: str
    password: str


def get_chart_version_list(chart_data: ChartData, repo_auth: RepoAuth) -> List[str]:
    """获取 chart 对应的版本列表"""
    client = BkRepoClient(repo_auth.username, password=repo_auth.password)
    chart_versions = client.get_chart_versions(**asdict(chart_data))
    # 如果不为列表，则返回为空
    if isinstance(chart_versions, list):
        return [info["version"] for info in chart_versions]
    return []


def delete_chart_version(chart_data: ChartData, repo_auth: RepoAuth, version: str):
    """删除版本"""
    client = BkRepoClient(repo_auth.username, password=repo_auth.password)
    req_data = asdict(chart_data)
    req_data["version"] = version
    client.delete_chart_version(**req_data)


def batch_delete_chart_versions(chart_data: ChartData, repo_auth: RepoAuth, versions: List[str]):
    """批量删除chart版本"""
    # 组装并发任务
    delete_version = functools.partial(delete_chart_version, chart_data, repo_auth)
    tasks = [functools.partial(delete_version, version) for version in versions]
    async_run(tasks)
