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
import abc
import logging

import tornado.gen
from tornado.httpclient import HTTPRequest
from tornado.ioloop import IOLoop
from tornado.websocket import websocket_connect

from backend.web_console import constants
from backend.web_console.utils import hello_message

logger = logging.getLogger(__name__)


class BCSClientBase(abc.ABC):
    def __init__(self, url, rows, cols, msg_handler):
        self.init_rows = rows
        self.init_cols = cols

        self.url = HTTPRequest(url, validate_cert=False)

        self.msg_handler = msg_handler
        self.ws = None

        self.output_record = []
        self.output_buffer = ""
        self.last_output_ts = IOLoop.current().time()

    @tornado.gen.coroutine
    def connect(self):
        logger.info("trying to connect %s, %s", self.url.url, self.url.headers)
        try:
            self.ws = yield websocket_connect(self.url, ping_interval=constants.WEBSOCKET_PING_INTERVAL)
        except Exception as e:
            logger.exception("connection error, %s" % e)
            self.msg_handler.close()
        else:
            self.post_connected()
            self.run()

    def post_connected(self):
        logger.info("bcs client connected: %s", self.msg_handler.user_pod_name)
        self.msg_handler.write_message({"data": hello_message(self.msg_handler.source)})
        self.msg_handler.start_record()
        self.msg_handler.tick_timeout()
        self.set_pty_size(self.init_rows, self.init_cols)

    def flush_output_record(self):
        """获取输出记录
        """
        record = self.output_record[:]
        self.output_record = []
        return record

    @abc.abstractmethod
    def write_message(self, message):
        """写入消息
        """

    @abc.abstractmethod
    def set_pty_size(self, rows: int, cols: int):
        """自动宽度适应
        """

    @abc.abstractmethod
    def run(self):
        """消息转发实现
        """
