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
from celery import Celery
from celery.schedules import crontab
from django.apps import AppConfig
from django.conf import settings  # noqa

app = Celery('backend')
app.config_from_object('django.conf:settings')


# 周期任务配置
app.conf.beat_schedule = {
    'bcs_perm_tasks': {
        # 调用task全路径
        'task': 'backend.accounts.bcs_perm.tasks.sync_bcs_perm',
        'schedule': crontab(hour=2),
    },
    # 每天三点进行一次强制同步
    'helm_force_sync_repo_tasks': {
        'task': 'backend.bcs_k8s.helm.tasks.force_sync_all_repo',
        'schedule': crontab(hour=3),
    },
}


class CeleryConfig(AppConfig):
    name = "backend.celery_app"
    verbose_name = "celery_app"

    def ready(self):
        from backend.accounts.bcs_perm import tasks as bcs_tasks  # noqa
        from backend.apps.cluster import node_tasks  # noqa
        from backend.apps.cluster.views_bk import tasks as cluster_node_tasks
        from backend.apps.configuration import tasks as backend_instance_status  # noqa
        from backend.apps.metric import tasks as metric_tasks  # noqa
        from backend.bcs_k8s.app import tasks as helm_app_tasks  # noqa
        from backend.bcs_k8s.helm import tasks as helm_chart_tasks  # noqa
        from backend.utils import notify  # noqa

        from . import periodic_tasks  # noqa
