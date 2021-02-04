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
from django.utils.translation import ugettext as _

from backend.utils.basic import ChoicesEnum

# default node count
DEFAULT_NODE_LIMIT = 10000

# filter removed node
FILTER_NODE_STATUS = ['removed']

# cluster status
COMMON_FAILED_STATUS = [
    "initial_failed",
    "failed",
    "check_failed",
    "remove_failed",
    "so_init_failed",
    "upgrade_failed",
]  # noqa
COMMON_RUNNING_STATUS = ["initializing", "running", "initial_checking", "removing", "so_initializing", "upgrading"]
CLUSTER_FAILED_STATUS = COMMON_FAILED_STATUS
CLUSTER_RUNNING_STATUS = COMMON_RUNNING_STATUS
NODE_FAILED_STATUS = ['ScheduleFailed', 'bke_failed']
NODE_FAILED_STATUS.extend(COMMON_FAILED_STATUS)
NODE_RUNNING_STATUS = ['Scheduling', None, 'bke_installing']
NODE_RUNNING_STATUS.extend(COMMON_RUNNING_STATUS)
DEFAULT_PAGE_LIMIT = 5
DEFAULT_MIX_VALUE = "*****-----$$$$$"

# no specific resource flag
NO_RES = '**'

# project all cluster flag
PROJECT_ALL_CLUSTER = 'all'

# 主机key的映射，便于前端进行展示
CCHostKeyMappings = {
    'bak_operator': 'bk_bak_operator',
    'classify_level_name': 'classify_level_name',
    'device_class': 'svr_device_class',
    'device_type_id': 'bk_svr_type_id',
    'device_type_name': 'svr_type_name',
    'hard_memo': 'hard_memo',
    'host_id': 'bk_host_id',
    'host_name': 'bk_host_name',
    'idc': 'idc_name',
    'idc_area': 'bk_idc_area',
    'idc_area_id': 'bk_idc_area_id',
    'idc_id': 'idc_id',
    'idcunit': 'idc_unit_name',
    'idcunit_id': 'idc_unit_id',
    'inner_ip': 'bk_host_innerip',
    'memo': 'bk_comment',
    'module_name': 'module_name',
    'operator': 'operator',
    'osname': 'bk_os_name',
    'osversion': 'bk_os_version',
    'outer_ip': 'bk_host_outerip',
    'server_rack': 'rack',
    'project_name': 'project_name',
    'cluster_name': 'cluster_name',
    'cluster_id': 'cluster_id',
    'is_used': 'is_used',
    'bk_cloud_id': 'bk_cloud_id',
    "is_valid": "is_valid",
}

# 节点默认标签
DEFAULT_SYSTEM_LABEL_KEYS = [
    "beta.kubernetes.io/arch",
    "beta.kubernetes.io/os",
    "kubernetes.io/hostname",
    "node-role.kubernetes.io/node",
]


class ProjectKindName(ChoicesEnum):
    _choices_labels = ((1, 'k8s'), (2, 'mesos'))


ClusterType = dict(ProjectKindName._choices_labels.get_choices())


# TODO: 第一版只创建两个module: master和node
CC_MODULE_INFO = {
    "mesos": {
        "stag": "test",
        "prod": "pro",
        "debug": "debug",
        "module_suffix_name": [
            "master",
            "node",
            # "zk"
        ],
    },
    "k8s": {
        "stag": "test",
        "prod": "pro",
        "debug": "debug",
        "module_suffix_name": [
            "master",
            "node",
            # "etcd",
            # "bcs",
        ],
    },
}


class OpType(ChoicesEnum):
    ADD_NODE = 'add_node'
    DELETE_NODE = 'delete_node'


# skip namespace
K8S_SKIP_NS_LIST = ['kube-system', 'thanos', 'web-console']

# 调用接口异常的消息，记录到db中，可以直接转换
BCS_OPS_ERROR_INFO = {"state": "FAILURE", "node_tasks": [{"state": "FAILURE", "name": _("- 调用初始化接口失败")}]}

# 状态映射
class ClusterStatusName(ChoicesEnum):
    normal = _("正常")
    initial_checking = _("前置检查中")
    check_failed = _("前置检查失败")
    so_initializing = _("SO初始化中")
    so_init_failed = _("SO初始化失败")
    initializing = _("初始化中")
    initial_failed = _("初始化失败")
    removing = _("删除中")
    remove_failed = _("删除失败")
    removed = _("已删除")


class ClusterState(ChoicesEnum):
    BCSNew = "bcs_new"
    Existing = "existing"

    _choices_labels = ((BCSNew, "bcs_new"), (Existing, "existing"))
