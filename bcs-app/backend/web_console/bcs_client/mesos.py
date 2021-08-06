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
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from tornado.concurrent import run_on_executor

from backend.components.bcs.mesos import MesosClient
from backend.web_console.bcs_client.base import BCSClientBase

logger = logging.getLogger(__name__)


class MesosClientBase(BCSClientBase):
    executor = ThreadPoolExecutor()

    def __init__(self, url, rows, cols, msg_handler, host_ip, exec_id, api_client):
        super().__init__(url, rows, cols, msg_handler)
        self.host_ip = host_ip
        self.exec_id = exec_id
        self.api_client = api_client
        self.connect()

    @run_on_executor
    def set_pty_size(self, rows: int, cols: int):
        """设置长宽高"""
        try:
            self.api_client.resize_container_exec(self.host_ip, self.exec_id, rows, cols)
        except Exception as error:
            logger.error("mesos set_pty_size error, %s", error)


class ContainerDirectClient(MesosClientBase):
    MODE = "mesos_container_direct"

    @classmethod
    def create_client(cls, msg_handler, context, rows, cols):
        """获取mesos client"""
        host = urlparse(context["server_address"])
        if host.scheme == "https":
            scheme = "wss"
        else:
            scheme = "ws"

        bcs_address = host._replace(scheme=scheme).geturl()

        ws_url = f'{bcs_address}/bcsapi/v4/scheduler/mesos/webconsole/start_exec?host_ip={context["host_ip"]}&exec_id={context["exec_id"]}'  # noqa
        api_client = MesosClient(**context["client_context"])
        client = cls(ws_url, rows, cols, msg_handler, context["host_ip"], context["exec_id"], api_client)
        return client
