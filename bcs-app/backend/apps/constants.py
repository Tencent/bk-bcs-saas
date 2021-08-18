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

容器管理使用常量
"""
import logging
import re
from collections import OrderedDict
from enum import Enum

from backend.utils.basic import ChoicesEnum

logger = logging.getLogger(__name__)

# 不检查IP是否重复的业务
SKIP_BIZ_INFO = {}

# 白名单接入的业务
BIND_BIZ_ID = []
BIND_BIZ_ID_USER = {}

# CC MODULE INFO
CC_MODULE_INFO = {}

# k8s 平台服务用的集群
K8S_PLAT_CLUSTER_ID = []

# master in binded biz
BCS_APP_ID = ""

# verify resource code for perm
verify_resource_exist = False

# nginx ingress controller path
CONTROLLER_IMAGE_PATH = "public/bcs/k8s/nginx-ingress-controller"
BACKEND_IMAGE_PATH = "public/bcs/k8s/defaultbackend"


# 项目类型
class ProjectKind(ChoicesEnum):
    K8S = 1
    MESOS = 2

    _choices_labels = ((1, 'Kubernetes'), (2, 'Mesos'))


class NodeStatus(Enum):
    # 未初始化
    UNINITIALIZED = "uninitialized"
    # 初始化中
    INITIALIZING = "initializing"
    # 正常状态
    NORMAL = "normal"
    # 初始化失败
    INITIAL_FAILED = "initial_failed"
    # 待移除
    TO_REMOVED = "to_removed"
    # 可移除
    REMOVABLE = "removable"
    # 移除中
    REMOVING = "removing"
    # 移除失败 remove_failed
    REMOVE_FAILED = "remove_failed"
    # 已移除
    REMOVED = "removed"


# 节点使用中状态
NodeActiveStatus = [NodeStatus.UNINITIALIZED, NodeStatus.INITIALIZING, NodeStatus.NORMAL]


# docker状态排序
# default will be 100
DockerStatusDefaultOrder = 100
DockerStatusOrdering = {"running": 0, "waiting": 1, "lost": 8, "terminated": 9}  # mesos


# 模板实例化时需要传递给BCS的KEY
TEMPLATE_ID = "io.tencent.paas.templateId"
VERSION_ID = "io.tencent.paas.versionId"
VERSION = "io.tencent.paas.version"
PROJECT_ID = "projectId"


# env 环境, 现在是给namespace使用
class EnvType(Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


ClusterType = dict(ProjectKind._choices_labels.get_choices())


class MetricProjectKind(ChoicesEnum):
    _choices_labels = ((1, "k8s"), (2, "Mesos"))


# 限制project kind
PROJECT_KIND_LIST = [kind for kind, _ in ProjectKind.get_choices()]

# paas_cc 获取全部使用的limit值
ALL_LIMIT = 10000

# metrics 默认时间 1小时
METRICS_DEFAULT_TIMEDELTA = 3600

# 功能开关
BIND_BIZ_ID_FUNC_CODE = "bind_biz_id_enabled"
NOTIFY_MANAGER_FUNC_CODE = "notify_manager"
NOTIFY_PROJECT_APPROVAL_FUNC_CODE = "notify_project_approval"

SKIP_REQUEST_NAMESPACE = ["projects", "projects_pub"]

# all cluster flag
ALL_CLUSTER_FLAG = "ALL"

# 敏感单词
SENSITIVE_KEYWORD = ["access_token", "bk_app_secret", "X-BKAPI-AUTHORIZATION", "X-BK-APP-SECRET"]


CLUSTER_UPGRADE_VERSION = OrderedDict(
    {re.compile(r'^\S+[vV]?1\.8\.\S+$'): ["v1.12.6"], re.compile(r'^\S+[vV]?1\.12\.\S+$'): ["v1.14.3-tk8s-v1.1-1"]}
)


# TODO: 先放到前端传递，后续gcloud版本统一后，支持分支判断再去掉
UPGRADE_TYPE = {"v1.12.6": "update8to12", "v1.14.3-tk8s-v1.1-1": "update12to14"}


try:
    from .constants_ext import *  # noqa
except ImportError as e:
    logger.debug('Load extension failed: %s', e)
