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
"""容器管理使用常量
"""
from django.conf import settings

from enum import Enum
from backend.utils.basic import ChoicesEnum
from backend.apps.constants_bk import *  # noqa


class NodeStatus(Enum):
    # 未初始化
    UNINITIALIZED = 'uninitialized'
    # 初始化中
    INITIALIZING = 'initializing'
    # 正常状态
    NORMAL = 'normal'
    # 初始化失败
    INITIAL_FAILED = 'initial_failed'
    # 待移除
    TO_REMOVED = 'to_removed'
    # 可移除
    REMOVABLE = 'removable'
    # 移除中
    REMOVING = 'removing'
    # 移除失败 remove_failed
    REMOVE_FAILED = 'remove_failed'
    # 已移除
    REMOVED = 'removed'


# 节点使用中状态
NodeActiveStatus = [NodeStatus.UNINITIALIZED,
                    NodeStatus.INITIALIZING, NodeStatus.NORMAL]


# docker状态排序
# default will be 100
DockerStatusDefaultOrder = 100
DockerStatusOrdering = {
    'running': 0,
    'waiting': 1,
    'lost': 8,  # mesos
    'terminated': 9
}


# 模板实例化时需要传递给BCS的KEY
TEMPLATE_ID = "io.tencent.paas.templateId"
VERSION_ID = "io.tencent.paas.versionId"
VERSION = "io.tencent.paas.version"
PROJECT_ID = "projectId"


# env 环境, 现在是给namespace使用
class EnvType(Enum):
    DEV = 'dev'
    TEST = 'test'
    PROD = 'prod'


ClusterType = dict(ProjectKind._choices_labels.get_choices())


class MetricProjectKind(ChoicesEnum):
    _choices_labels = (
        (1, 'k8s'),
        (2, 'Mesos')
    )


# 限制project kind
PROJECT_KIND_LIST = [kind for kind, _ in ProjectKind.get_choices()]

# paas_cc 获取全部使用的limit值
ALL_LIMIT = 10000

# 针对k8s的节点移除，过滤掉下面namespace上的容器
# 因为kube-system为系统自己的容器
K8S_SKIP_NS = "kube-system"

# metrics 默认时间 1小时
METRICS_DEFAULT_TIMEDELTA = 3600

# 功能开关
BIND_BIZ_ID_FUNC_CODE = 'bind_biz_id_enabled'
NOTIFY_MANAGER_FUNC_CODE = 'notify_manager'
NOTIFY_PROJECT_APPROVAL_FUNC_CODE = 'notify_project_approval'

# k8s 中系统的命名空间，不允许用户创建，也不能操作上面的资源 kube-system, kube-public
K8S_SYS_NAMESPACE = ['kube-system', 'kube-public']

# k8s 组件命名空间, 页面上所有集群下都不可以操作这些命名空间的资源
K8S_COMPONENT_NAMESPACE = ['thanos']

# k8s 平台服务用的命名空间
K8S_PLAT_NAMESPACE = ['web-console', 'gitlab-ci', 'thanos']

SKIP_REQUEST_NAMESPACE = ["projects", "projects_pub"]

# all cluster flag
ALL_CLUSTER_FLAG = 'ALL'
