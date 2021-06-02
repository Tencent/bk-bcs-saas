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
from django.utils.translation import ugettext_lazy as _

from backend.packages.blue_krill.data_types.enum import EnumField, StructuredEnum

ActivityTypes = dict(
    add=_('创建'),
    modify=_('更新'),
    rollback=_('回滚'),
    delete=_('删除'),
    begin=_('开始'),
    end=_('结束'),
    start=_('启动'),
    pause=_('暂停'),
    carryon=_('继续'),
    stop=_('停止'),
    restart=_('重启'),
)
ActivityTypeChoices = {v: k for k, v in ActivityTypes.items()}


ActivityStatus = dict(
    completed=_('完成'),
    error=_('错误'),
    succeed=_('成功'),
    failed=_('失败'),
)
ActivityStatusChoices = {v: k for k, v in ActivityStatus.items()}


ResourceTypes = dict(
    project=_('项目'),
    cluster=_('集群'),
    node=_('节点'),
    namespace=_('命名空间'),
    template=_('模板集'),
    instance=_('应用'),
    service=_('Service'),
    ingress=_('Ingress'),
    lb=_('LoadBalancer'),
    configmap=_('Configmap'),
    secret=_('Secret'),
    metric=_('Metric'),
    web_console=_('WebConsole'),
    helm_app=_('Helm'),
    hpa=_('HPA'),
)
ResourceTypeChoices = {v: k for k, v in ResourceTypes.items()}

MetaMap = {'activity_type': ActivityTypes, 'activity_status': ActivityStatus, 'resource_type': ResourceTypes}


# ---- 避免与已定义结构冲突，需要使用枚举类型使用以下枚举类 ----


class BaseActivityType(str, StructuredEnum):
    """ 操作类型 """

    Add = EnumField('add', _('创建'))
    Modify = EnumField('modify', _('更新'))
    Rollback = EnumField('rollback', _('回滚'))
    Delete = EnumField('delete', _('删除'))
    Begin = EnumField('begin', _('开始'))
    End = EnumField('end', _('结束'))
    Start = EnumField('start', _('启动'))
    Pause = EnumField('pause', _('暂停'))
    CarryOn = EnumField('carryon', _('继续'))
    Stop = EnumField('stop', _('停止'))
    Restart = EnumField('restart', _('重启'))
    Retrieve = EnumField('retrieve', _('查询'))


class BaseActivityStatus(str, StructuredEnum):
    """ 操作状态 """

    Add = EnumField('completed', _('完成'))
    Error = EnumField('error', _('错误'))
    Succeed = EnumField('succeed', _('成功'))
    Failed = EnumField('failed', _('失败'))


class BaseResourceType(str, StructuredEnum):
    """ 资源类型 """

    Project = EnumField('project', _('项目'))
    Cluster = EnumField('cluster', _('集群'))
    Node = EnumField('node', _('节点'))
    Namespace = EnumField('namespace', _('命名空间'))
    Template = EnumField('template', _('模板集'))
    Instance = EnumField('instance', _('应用'))
    Service = EnumField('service', _('Service'))
    Ingress = EnumField('ingress', _('Ingress'))
    LB = EnumField('lb', _('LoadBalancer'))
    ConfigMap = EnumField('configmap', _('Configmap'))
    Secret = EnumField('secret', _('Secret'))
    Metric = EnumField('metric', _('Metric'))
    WebConsole = EnumField('web_console', _('WebConsole'))
    HelmApp = EnumField('helm_app', _('Helm'))
    HPA = EnumField('hpa', _('HPA'))
