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
"""
一次性任务，初始化 ProjectDataInfo 中数据的 cc_biz_id 信息

Usage:
```
workon xxx
python manage.py init_project_biz -n IAnlbGg31xLXHdfEYOjpYiT4toebWH
```
"""
from django.core.management.base import BaseCommand

from backend.accounts import bcs_perm
from backend.apps.datalog.models import ProjectDataInfo
from backend.components import paas_cc


class Command(BaseCommand):
    def handle(self, *args, **options):
        access_token = bcs_perm.get_access_token().get('access_token')
        if not access_token:
            print('get access_token by paas_auth fail')
            return

        for project in ProjectDataInfo.objects.all():
            result = paas_cc.get_project(access_token, project.project_id)
            if result['result']:
                project.cc_biz_id = result['data']['cc_app_id']
                project.save(update_fields=['cc_biz_id'])
            else:
                print(project.project_id, result)
