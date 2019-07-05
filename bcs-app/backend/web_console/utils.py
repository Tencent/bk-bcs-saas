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
import copy
import logging
import time

from django.conf import settings
from logstash.formatter import LogstashFormatterBase

from backend.utils.log import LogstashRedisHandler
from backend.web_console import constants
from backend.components.utils import http_post

logger = logging.getLogger(__name__)


class WebConsoleFormatter(LogstashFormatterBase):
    def format(self, record):
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(time.time()),
            '@version': '1',
            'host': self.host,
            'tags': self.tags,
            'type': self.message_type,
        }

        message.update(record)

        return self.serialize(message)


def len_char(string):
    length = 0
    for i in string:
        if '\u4e00' <= i <= '\u9fff':
            length += 2
        else:
            length += 1
    return length


def hello_message(message=constants.HELLO_MESSAGE, width=81):
    """连接是显示的字符串
    """
    messages = []
    messages.append('#' * width)
    console = '#' + ((width - 2 - len(message)) // 2) * ' ' + message + ((width - 2 - len(message)) // 2) * ' ' + ' #'
    messages.append(console)
    messages.append('#' * width)
    for guide in constants.GUIDE_MESSAGE:
        messages.append('#' + guide + (width - len_char(guide) - 2) * ' ' + '#')
    messages.append('#' * width)
    return '\r\n'.join(messages) + '\r\n'


def clean_bash_escape(text):
    """删除bash转义字符
    """
    # 删除转移字符
    text = constants.ANSI_ESCAPE.sub('', text)
    # 再删除\x01字符
    text = text.replace(chr(constants.STDOUT_CHANNEL), '')
    return text


def get_auditor():
    """操作审计记录
    """
    try:
        # 复用redis的配置
        auditor_handler = copy.deepcopy(settings.RDS_HANDER_SETTINGS)
        auditor_handler['queue_name'] = 'bcs_web_console_record'
        auditor_handler['tags'].append('bcs-web-console')

        # 初始化logger
        auditor = LogstashRedisHandler(
            auditor_handler['redis_url'],
            auditor_handler['queue_name'],
            auditor_handler['tags'])
        auditor.formatter = WebConsoleFormatter(
            auditor_handler['message_type'],
            auditor_handler['tags'], fqdn=False)
    except Exception:
        # fallbck to normal logger
        auditor = logging.getLogger('auditor')

    return auditor


def _setup_logging(verbose=None, filename=None):
    """设置日志级别
    """
    LOG_FORMAT = '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(format=LOG_FORMAT, level=level, filename=filename)


def get_kubectld_version(cluster_version):
    if not cluster_version:
        return constants.DEFAULT_KUBECTLD_VERSION

    for kubectld, patterns in constants.KUBECTLD_VERSION.items():
        for pattern in patterns:
            if pattern.match(cluster_version):
                return kubectld

    return constants.DEFAULT_KUBECTLD_VERSION


def format_term_size(size: str, default_size: int) -> int:
    """格式term大小参数
    """
    if not size:
        return default_size

    try:
        return int(size)
    except Exception:
        return default_size
