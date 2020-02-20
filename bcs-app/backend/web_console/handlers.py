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
import json
import logging

import arrow
import tornado.web
import tornado.websocket
from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation.trans_real import get_supported_language_variant
from tornado import locale
from tornado.ioloop import IOLoop, PeriodicCallback

from backend.web_console import bcs_client, constants, utils
from backend.web_console.auth import authenticated
from backend.web_console.pod_life_cycle import PodLifeCycle
from backend.web_console.utils import clean_bash_escape, get_auditor

logger = logging.getLogger(__name__)


class LocaleHandlerMixin:
    """国际化Mixin
    """

    def get_user_locale(self):
        bk_lang = self.get_cookie(settings.LANGUAGE_COOKIE_NAME)
        try:
            lang_code = get_supported_language_variant(bk_lang)
        except LookupError:
            lang_code = settings.LANGUAGE_CODE
        translation.activate(lang_code)
        return locale.get(lang_code)


class IndexPageHandler(LocaleHandlerMixin, tornado.web.RequestHandler):
    """首页处理
    """

    def get(self, project_id, cluster_id):
        session_url = f"{settings.DEVOPS_BCS_API_URL}/api/projects/{project_id}/clusters/{cluster_id}/web_console/session/"  # noqa

        # mesos集群会带具体信息
        query = self.request.query
        if query:
            session_url += f"?{query}"

        data = {"settings": settings, "session_url": session_url, "cluster_id": cluster_id}
        self.render("templates/index.html", **data)


class MgrHandler(LocaleHandlerMixin, tornado.web.RequestHandler):
    """管理页
    """

    def get(self, project_id):
        data = {"settings": settings, "project_id": project_id}
        self.render("templates/mgr.html", **data)


class BCSWebSocketHandler(LocaleHandlerMixin, tornado.websocket.WebSocketHandler):
    """WebSocket处理
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_record = []
        self.input_buffer = ""
        self.last_input_ts = IOLoop.current().time()
        self.login_ts = IOLoop.current().time()

        self.record_callback = None
        self.tick_callback = None
        self.record_interval = 10
        self.heartbeat_callback = None
        self.auditor = get_auditor()
        self.pod_life_cycle = PodLifeCycle()
        self.exit_buffer = ""
        self.exit_command = "exit"
        self.user_pod_name = None
        self.source = None

    def check_origin(self, origin):
        return True

    @authenticated
    def get(self, *args, **kwargs):
        """只鉴权使用
        """
        return super().get(*args, **kwargs)

    def open(self, project_id, cluster_id, context):
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.context = context
        self.user_pod_name = context["user_pod_name"]
        self.source = self.get_argument("source")

        rows = self.get_argument("rows")
        rows = utils.format_term_size(rows, constants.DEFAULT_ROWS)

        cols = self.get_argument("cols")
        cols = utils.format_term_size(cols, constants.DEFAULT_COLS)

        mode = context.get("mode")
        self.bcs_client = bcs_client.factory.create(mode, self, context, rows, cols)

    def on_message(self, message):
        self.last_input_ts = IOLoop.current().time()
        channel = int(message[0])
        message = message[1:]
        if channel == constants.RESIZE_CHANNEL:
            rows, cols = message.split(",")
            rows = int(rows)
            cols = int(rows)
            self.bcs_client.set_pty_size(rows, cols)
        else:
            if message == "\r":
                if self.exit_buffer.lstrip().startswith(self.exit_command):
                    self.write_message({"data": _("BCS Console 主动退出"), "type": "exit_message"})
                self.exit_buffer == ""
            else:
                self.exit_buffer += message

            self.send_message(message)

    def on_close(self):
        self.send_exit()

        if self.tick_callback:
            logger.info("stop tick callback, %s", self.user_pod_name)
            self.tick_callback.stop()

        if self.record_callback:
            logger.info("stop record_callback, %s", self.user_pod_name)
            self.record_callback.stop()

        if self.heartbeat_callback:
            logger.info("stop heartbeat_callback, %s", self.user_pod_name)
            self.heartbeat_callback.stop()

        logger.info("on_close")

    def send_exit(self):
        exit_msg = "\nexit\n"
        self.send_message(exit_msg)

    def flush_input_record(self):
        """获取输出记录
        """
        record = self.input_record[:]
        self.input_record = []
        return record

    def tick_timeout(self):
        """主动停止掉session
        """
        self.tick_callback = PeriodicCallback(self.periodic_tick, self.record_interval * 1000)
        self.tick_callback.start()

    def tick_timeout2client(self, message):
        """客户端退出
        """
        # 下发提示消息
        self.write_message({"data": message, "type": "exit_message"})
        # 服务端退出bash, exit
        self.send_exit()

    def periodic_tick(self):

        now = IOLoop.current().time()
        idle_time = now - max(self.bcs_client.last_output_ts, self.last_input_ts)
        if idle_time > constants.TICK_TIMEOUT:
            tick_timeout_min = constants.TICK_TIMEOUT // 60
            message = _("BCS Console 已经{}分钟无操作").format(tick_timeout_min)
            self.tick_timeout2client(message)
            logger.info("tick timeout, close session %s, idle time, %.2f", self.user_pod_name, idle_time)
        logger.info("tick active %s, idle time, %.2f", self.user_pod_name, idle_time)

        login_time = now - self.login_ts
        if login_time > constants.LOGIN_TIMEOUT:
            login_timeout = constants.LOGIN_TIMEOUT // (60 * 60)
            message = _("BCS Console 使用已经超过{}小时，请重新登录").format(login_timeout)
            self.tick_timeout2client(message)
            logger.info("tick timeout, close session %s, login time, %.2f", self.user_pod_name, login_time)
        logger.info("tick active %s, login time, %.2f", self.user_pod_name, login_time)

    def heartbeat(self):
        """每秒钟上报心跳
        """
        self.heartbeat_callback = PeriodicCallback(lambda: self.pod_life_cycle.heartbeat(self.user_pod_name), 1000)
        self.heartbeat_callback.start()

    def start_record(self):
        """操作审计"""
        self.record_callback = PeriodicCallback(self.periodic_record, self.record_interval * 1000)
        self.record_callback.start()

    def periodic_record(self):
        """周期上报操作记录
        """
        input_record = self.flush_input_record()
        output_record = self.bcs_client.flush_output_record()

        if not input_record and not output_record:
            return

        # 上报的数据
        data = {
            "input_record": "\r\n".join(input_record),
            "output_record": "\r\n".join(output_record),
            "session_id": self.context["session_id"],
            "context": self.context,
            "project_id": self.project_id,
            "cluster_id": self.cluster_id,
            "user_pod_name": self.user_pod_name,
            "username": self.context["username"],
        }
        self.auditor.emit(data)
        logger.info(data)

    def send_message(self, message):
        if not self.bcs_client.ws or self.bcs_client.ws.stream.closed():
            logger.info("session %s, close, message just ignore", self)
            return

        self.input_buffer += message

        if self.input_buffer.endswith(constants.INPUT_LINE_BREAKER):
            # line_msg = ['command', '']
            line_msg = self.input_buffer.split(constants.INPUT_LINE_BREAKER)
            for i in line_msg[:-1]:
                record = "%s: %s" % (arrow.now().strftime("%Y-%m-%d %H:%M:%S.%f"), clean_bash_escape(i))
                logger.debug(record)
                self.input_record.append(record)
            # empty input_buffer
            self.input_buffer = line_msg[-1]

        try:
            self.bcs_client.write_message(message)
        except Exception as e:
            logger.exception(e)
