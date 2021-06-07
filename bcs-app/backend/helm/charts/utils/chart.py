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
import io
import logging
import tarfile
from dataclasses import dataclass, field
from typing import Dict, List

from backend.components.bk_repo import BkRepoClient
from backend.helm.repository.utils import auth, repo

from .tools import is_binary_file

logger = logging.getLogger(__name__)


@dataclass
class ChartData:
    chart_name: str
    version: str = None
    urls: List = field(default_factory=list)  # chart 的地址


def get_chart_versions(repo_data: repo.RepoData, repo_auth: auth.RepoAuthData, chart_data: ChartData):
    """获取chart的版本
    NOTE: 考虑后续支持用户创建自己的仓库，后续允许输入仓库地址，接口遵循bkrepo的接口协议
    """
    client = BkRepoClient(repo_auth.username, password=repo_auth.password)
    return client.get_chart_versions(repo_data.project_name, repo_data.repo_name, chart_data.chart_name)


def get_chart_version_info(repo_data: repo.RepoData, repo_auth: auth.RepoAuthData, chart_data: ChartData):
    """获取chart版本详情"""
    client = BkRepoClient(repo_auth.username, password=repo_auth.password)
    return client.get_chart_version_detail(
        repo_data.project_name, repo_data.repo_name, chart_data.chart_name, chart_data.version
    )


def get_chart_files(repo_data: repo.RepoData, repo_auth: auth.RepoAuthData, chart_data: ChartData) -> Dict[str, str]:
    """解析chart的文件"""
    client = BkRepoClient(repo_auth.username, password=repo_auth.password)
    chart_content = client.download_chart(chart_data.urls[0])
    tar = tarfile.open(mode="r:*", fileobj=io.BytesIO(chart_content))

    files = {}
    for member in tar.getnames().members:
        if member.isdir():
            continue
        file_path = member.path
        # 提取文件内容
        file_content = tar.extractfile(file_path).read()
        # 忽略二进制文件
        if is_binary_file(file_content[:1024]):
            logger.warning("file %s is a binary file, content: %s", file_path, file_content[:1024])
            continue
        try:
            decode_content = file_content.decode()
        except Exception as e:
            logger.exception(
                "download_template_data failed %s, file_path=%s, file_content: %s", e, file_path, file_content
            )
            decode_content = ""
        # 文件格式: {"bk-redis/templates/ingress.yaml": "xxx"}
        files[file_path] = decode_content

    return files


def get_chart_value_files(
    repo_data: repo.RepoData, repo_auth: auth.RepoAuthData, chart_data: ChartData
) -> Dict[str, str]:
    """下载chart，然后解析获取到对应的value文件内容"""
    files = get_chart_files(repo_data, repo_auth, chart_data)
    values_files = {}
    # 现阶段BCS允许的values中文件路径
    # 1. 以values.yaml结尾的文件
    # 2. bcs-values文件夹下的文件
    for file_path in files:
        if file_path.endswith("values.yaml") or "bcs-values" in file_path:
            values_files[file_path] = files[file_path]
    return values_files
