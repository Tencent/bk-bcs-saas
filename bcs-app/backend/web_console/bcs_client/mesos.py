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
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import arrow
import tornado.gen
from django.utils.encoding import smart_text
from tornado.concurrent import run_on_executor
from tornado.httpclient import HTTPRequest
from tornado.ioloop import IOLoop

from backend.components.bcs.mesos import MesosClient
from backend.web_console import constants, utils
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

    def write_message(self, message):
        """写入消息
        """
        self.ws.write_message(message)

    @run_on_executor
    def set_pty_size(self, rows: int, cols: int):
        """设置长宽高
        """
        try:
            self.api_client.resize_container_exec(self.host_ip, self.exec_id, rows, cols)
        except Exception as error:
            logger.error('mesos set_pty_size error, %s', error)

    @tornado.gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                logger.info("mesos client connection closed")
                self.msg_handler.close()
                break

            if self.msg_handler.stream.closed():
                logger.info("mesos msg_handler connection closed")
                self.ws.close()
                break

            try:
                self.last_output_ts = IOLoop.current().time()

                try:
                    msg = smart_text(msg)
                except Exception:
                    msg = smart_text(msg, 'latin1')

                self.output_buffer += msg

                if constants.OUTPUT_LINE_BREAKER in self.output_buffer:
                    line_msg = self.output_buffer.split(constants.OUTPUT_LINE_BREAKER)
                    for i in line_msg[:-1]:
                        record = '%s: %s' % (arrow.now().strftime("%Y-%m-%d %H:%M:%S.%f"), utils.clean_bash_escape(i))
                        self.output_record.append(record)
                    # 前面多行已经赋值到record, 最后一行可能剩余未换行的数据
                    self.output_buffer = line_msg[-1]

                self.msg_handler.write_message({'data': msg})
            except Exception as e:
                logger.exception(e)
                self.ws.close()


class ContainerDirectClient(MesosClientBase):
    MODE = 'mesos_container_direct'

    @classmethod
    def create_client(cls, msg_handler, context, rows, cols):
        """获取mesos client
        """
        host = urlparse(context['server_address'])
        if host.scheme == 'https':
            scheme = 'wss'
        else:
            scheme = 'ws'

        bcs_address = host._replace(scheme=scheme).geturl()

        ws_url = f'{bcs_address}/bcsapi/v1/webconsole/start_exec?host_ip={context["host_ip"]}&exec_id={context["exec_id"]}'  # noqa
        api_client = MesosClient(**context['client_context'])
        client = cls(ws_url, rows, cols, msg_handler, context["host_ip"], context["exec_id"], api_client)
        return client
