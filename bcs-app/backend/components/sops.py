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

from django.conf import settings

from backend.components.base import BaseHttpClient, BkApiClient, ComponentAuth


class SopsConfig:
    """标准运维系统配置信息，提供后续使用的host， url等"""

    def __init__(self, host: str, bk_biz_id: str):
        # 请求域名
        self.host = host
        self.bk_biz_id = bk_biz_id

        # 请求地址
        self.create_task_url = f"{host}/prod/create_task/{{template_id}}/{bk_biz_id}/"
        self.start_task_url = f"{host}/prod/start_task/{{task_id}}/{bk_biz_id}/"
        self.get_task_status_url = f"{host}/prod/get_task_status/{{task_id}}/{bk_biz_id}/"
        self.get_task_node_data_url = f"{host}/get_task_node_data/{bk_biz_id}/{{task_id}}/"


class SopsClient(BkApiClient):
    def __init__(self, bk_biz_id: str):
        self._config = SopsConfig(host=settings.SOPS_API_HOST, bk_biz_id=bk_biz_id)
        self._client = BaseHttpClient()

    def create_task(self, template_id: str, data: Dict) -> Dict:
        """通过业务流程创建任务"""
        pass

    def start_task(self, task_id: str) -> Dict:
        """启动任务"""
        pass

    def get_task_status(self):
        """获取任务状态"""
        pass

    def get_task_node_data(self):
        pass
