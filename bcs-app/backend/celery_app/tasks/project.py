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
from celery import shared_task
from django.conf import settings
from django.utils.translation import ugettext as _

from backend.components.op import notify_project_to_op
from backend.utils.send_msg import send_message

DEFAULT_OP_SUCCESS_CODE = 200
DEFAULT_OP_MAINTAINERS = settings.OP_MAINTAINERS


@shared_task
def notify_project_to_op_task(access_token, data):
    # set retry
    resp = notify_project_to_op(access_token, data)
    if resp.get("code") == DEFAULT_OP_SUCCESS_CODE:
        return
    title = f"[{settings.PLAT_SHOW_NAME}]{_('项目信息变更通知失败')}"
    message = f"{_('异常信息')}: {resp.get('message')}"

    send_message(DEFAULT_OP_MAINTAINERS, title + message, title=None, send_way='wx')
    send_message(DEFAULT_OP_MAINTAINERS, message, title=title, send_way='rtx')
