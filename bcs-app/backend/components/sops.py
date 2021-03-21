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
from dataclasses import asdict, dataclass, field
from typing import Dict

from django.conf import settings

from backend.components.base import BaseHttpClient, BkApiClient


class SopsConfig:
    """标准运维系统配置信息，提供后续使用的host， url等"""

    def __init__(self, host: str):
        # 请求域名
        self.host = host

        # 请求地址
        self.create_task_url = f"{host}/prod/create_task/{{template_id}}/{{bk_biz_id}}/"
        self.start_task_url = f"{host}/prod/start_task/{{task_id}}/{{bk_biz_id}}/"
        self.get_task_status_url = f"{host}/prod/get_task_status/{{task_id}}/{{bk_biz_id}}/"
        self.get_task_node_data_url = f"{host}/prod/get_task_node_data/{{bk_biz_id}}/{{task_id}}/"


@dataclass
class CommonParams:
    bk_username: str = settings.ADMIN_USERNAME  # 模板所属业务的运维
    app_code: str = settings.APP_ID
    app_secret: str = settings.APP_TOKEN


@dataclass
class CreateTaskParams(CommonParams):
    name: str = ""
    constants: Dict = field(default_factory=dict)


@dataclass
class StartTaskParams(CommonParams):
    """启动任务参数"""

    pass


@dataclass
class TaskStatusParams(CommonParams):
    """查询任务状态参数"""

    pass


@dataclass
class TaskNodeDataParmas(CommonParams):
    node_id: str = ""


class SopsClient(BkApiClient):
    def __init__(self):
        self._config = SopsConfig(host=settings.SOPS_API_HOST)
        self._client = BaseHttpClient()

    def create_task(self, bk_biz_id: str, template_id: str, data: CreateTaskParams) -> Dict:
        """通过业务流程创建任务"""
        url = self._config.create_task_url.format(template_id=template_id, bk_biz_id=bk_biz_id)
        return self._request_json("POST", url, json=asdict(data))

    def start_task(self, bk_biz_id: str, task_id: str, data: StartTaskParams) -> Dict:
        """启动任务"""
        url = self._config.start_task_url.format(task_id=task_id, bk_biz_id=bk_biz_id)
        return self._request_json("POST", url, json=asdict(data))

    def get_task_status(self, bk_biz_id: str, task_id: str) -> Dict:
        """获取任务状态"""
        url = self._config.get_task_status_url.format(task_id=task_id, bk_biz_id=bk_biz_id)
        return self._request_json("GET", url)

    def get_task_node_data(self, bk_biz_id: str, task_id: str, params: TaskNodeDataParmas) -> Dict:
        url = self._config.get_task_node_data_url.format(task_id=task_id, bk_biz_id=bk_biz_id)
        return self._request_json("GET", url, params=params)

    def _request_json(self, method: str, url: str, **kwargs) -> Dict:
        return self._client.request_json(method, url, **kwargs)
