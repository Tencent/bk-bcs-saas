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
from django.conf import settings
from backend.apps.configuration.constants import K8sResourceName

ActivityTypes = dict(
    add='创建',
    modify='更新',
    rollback='回滚',
    delete='删除',
    begin='开始',
    end='结束',
    start='启动',
    pause='暂停',
    carryon='继续',
    stop='停止',
    restart='重启',
)
ActivityTypeChoices = {v: k for k, v in ActivityTypes.items()}

ActivityStatus = dict(
    completed='完成',
    error='错误',
    succeed='成功',
    failed='失败',
)
ActivityStatusChoices = {v: k for k, v in ActivityStatus.items()}


ResourceTypes = dict(
    project='项目',
    cluster='集群',
    node='节点',
    template='模板集',
    instance='应用',

    service='Service',
    ingress='Ingress',
    lb='LoadBalance',
    configmap='Configmap',
    secret='Secret',

    metric='Metric',
    web_console='WebConsole',
    helm_app='Helm',
    hpa='HPA',
)

ResourceTypeChoices = {v: k for k, v in ResourceTypes.items()}

MetaMap = {
    'activity_type': ActivityTypes,
    'activity_status': ActivityStatus,
    'resource_type': ResourceTypes
}
