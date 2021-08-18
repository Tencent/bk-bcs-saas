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
from celery import shared_task
from django.conf import settings

from backend.apps import constants
from backend.components import cc
from backend.utils.func_controller import get_func_controller
from backend.utils.send_msg import send_message


@shared_task
def notify_manager(message):
    """管理员通知"""
    wx_message = '[%s-%s] %s' % (settings.PLAT_SHOW_NAME, settings.PAAS_ENV, message)
    enabled, wlist = get_func_controller(constants.NOTIFY_MANAGER_FUNC_CODE)

    send_message(wlist, wx_message, title=None, send_way='wx')
    send_message(wlist, message, title=None, send_way='rtx')


@shared_task
def create_project_notify(project_name, creator, is_secrecy, biz_id):
    """创建项目通知"""
    message = ['用户【%s】创建新项目【%s】' % (creator, project_name)]
    message.append("保密性：【%s】" % ('保密' if is_secrecy else '非保密'))
    if biz_id:
        app = cc.get_application()
        app = app.get(str(biz_id)) or {}
        biz_name = '%s(%s)' % (app.get('DisplayName') or '-', biz_id)
        message.append('绑定的业务:【%s】' % biz_name)

    link = '%s/admin/configcenter/project/' % settings.PAAS_HOST
    message.append("请及时审批：| %s" % link)
    message = '，'.join(message)

    enabled, wlist = get_func_controller(constants.NOTIFY_PROJECT_APPROVAL_FUNC_CODE)
    send_message(wlist, message, title=None, send_way='rtx')
