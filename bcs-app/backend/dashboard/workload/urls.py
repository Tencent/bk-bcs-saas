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
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=True)

router.register(r'cron_job', views.CronJobViewSet, base_name='cron_job')
router.register(r'daemon_set', views.DaemonSetViewSet, base_name='daemon_set')
router.register(r'deployment', views.DeploymentViewSet, base_name='deployment')
router.register(r'job', views.JobViewSet, base_name='job')
router.register(r'pod', views.PodViewSet, base_name='pod')
router.register(r'stateful_set', views.StatefulSetViewSet, base_name='stateful_set')
