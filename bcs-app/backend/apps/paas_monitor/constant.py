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
from backend.utils.basic import ChoicesEnum


class ExpressionLogic(ChoicesEnum):
    AND = 'and'
    OR = 'or'
    REPLACE = 'replace'
    REMOVE = 'remove'
    ADD_ROOT = 'add_root'


# 指标分组
class MetricCategoryEnum(ChoicesEnum):
    BCS_PERFORMANCE = 'bcs_performance'
    PERFORMANCE = 'performance'
    CUSTOM = 'custom'
    PROMETHEUS = 'prometheus'

    _choices_labels = (
        (BCS_PERFORMANCE, "容器服务"),
        (PERFORMANCE, "主机服务"),
        (CUSTOM, "自定义"),
        (PROMETHEUS, "Prometheus"),
    )


# 维度
class DimensionEnum(ChoicesEnum):
    CLUSTER = 'cluster'
    POD = 'pod'
    TASKGROUP = 'taskgroup'
    NODE = 'node'
    ACROSS_ALL_CLUSTER = 'across_all_cluster'
    ACROSS_ALL_CONTAINER = 'across_all_container'
    ACROSS_ALL_NODE = 'across_all_node'
    CUSTOM_MONITOR = 'custom_monitor'

    _choices_labels = (
        (CLUSTER, "按集群"),  # 容器服务
        (POD, '按Pod'),  # 容器服务(k8s)
        (TASKGROUP, '按Taskgroup'),  # 容器服务(mesos)
        (NODE, "按节点"),  # 主机服务(节点)
        (ACROSS_ALL_CLUSTER, "跨所有集群"),
        (ACROSS_ALL_CONTAINER, "跨所有容器"),  # 容器服务
        (ACROSS_ALL_NODE, "跨所有节点"),  # 主机服务
        (CUSTOM_MONITOR, "自定义Metric"),  # 自定义监控
    )


# 基础性能指标类型
class MetricTypeEnum(ChoicesEnum):
    CPU = 'cpu'
    NET = 'net'
    MEM = 'mem'
    DISK = 'disk'
    IO = 'io'
    PROCESS = 'process'
    SYSTEM_ENV = 'system_env'
    CUSTOM = 'custom'

    _choices_labels = (
        (CPU, "CPU"),
        (NET, "网络"),
        (MEM, "内存"),
        (DISK, "磁盘"),
        (IO, "输入输出"),
        (PROCESS, "进程"),
        (SYSTEM_ENV, "系统环境"),
        (CUSTOM, "自定义"),
    )


# 指标所属的项目类型
class MetricBelongProjectKindEnum(ChoicesEnum):
    K8S = 'k8s'
    MESOS = 'mesos'
    ALL = 'all'

    _choices_labels = (
        (K8S, 'Kubernetes'),
        (MESOS, 'Mesos'),
        (ALL, 'All')
    )

    _choices_project_kind = (
        (K8S, 1),
        (MESOS, 2)
    )

    @classmethod
    def get_choice_by_project_kind(cls, project_kind):
        return dict([(i[1], i[0]) for i in cls._choices_project_kind.value]).get(project_kind, project_kind)

    @classmethod
    def get_project_kind_list(cls):
        return dict(cls._choices_project_kind.value).values()


# 数据来源
class MonitorDataSrcEnum(ChoicesEnum):
    BKDATA = 'bkdata'
    KAFKA = 'kafka'
    ES = 'es'
    PROMETHEUS = 'prometheus'

    _choices_labels = (
        (BKDATA, "数据平台"),
        (KAFKA, "Kafka"),
        (ES, "Elasticsearch"),
        (PROMETHEUS, 'Prometheus'),
    )


class LogStreamTypeEnum(ChoicesEnum):
    STANDARD = 'standard'
    NON_STANDARD = 'non_standard'
    CUSTOM = 'custom'

    _choices_labels = (
        (STANDARD, '标准日志'),
        (NON_STANDARD, '非标准日志'),
        (CUSTOM, '自定义日志'),
    )


# 警报状态
ALARM_SHOW_STATUS = (
    ('alarm', u"告警中"),
    ('ok', u"正常"),
    ('insufficient', u"数据不足"),
)
ALARM_STATUS_CHOICE = (
    ('created', '新创建'),
    ('no_result_table', '无数据表'),
) + ALARM_SHOW_STATUS


# 告警策略
STRATEGY_CHOICES = (
    ("1000", u"静态阈值"),
    ("1001", u"同比策略"),
    ("1002", u"环比策略"),
    # (1003, u"同比策略（高级）"),
    # (1004, u"环比策略（高级）"),
    # (1005, u"同比振幅"),
    # (1006, u"同比区间"),
    # (1007, u"环比振幅"),
    # (4000, u"关键字匹配"),
    # (5000, u"进程端口监控检测策略"),
    # (5001, u"系统重新启动监控策略"),
    # (6000, u"自定义字符型告警"),
)

# 缺失数据处理
MISS_DATA_ACTION_CHOICE = (
    ('good', u"好（未超出阈值）"),
    ('bad', u"不良（超出阈值）"),
    ('ignore', u"忽略（保持警报状态）"),
    ('missing', u"缺失"),
)


# 聚合函数
AGGREGATOR_CHOICES = (
    ("avg", "平均值"),
    ("min", "最小值"),
    ("max", "最大值"),
    ("sum", "总计"),
    ("count", "计数"),
)

# 事件demo
BCS_STATE_CHANGE_EVENT = {
    "事件时间": "2018-06-13 20:19:23",
    "所属项目": "K8S容器服务测试(k8stest)",
    "所属集群": "bcs-test[BCS-K8S-10000]",
    "命名空间": "default",
    "IP": "ip-10-0-0-1-n-bcs-k8s-10000",
    "告警详情": "[Pod monocular-monocular-ui-5654489c97-l8qf8]FailedSync:Error syncing pod",
    "告警原因": "podEventWarnning"
}

# 事件的服务名称&事件类型
EVENT_SERVICE = [
    {
        "name": "容器服务",
        "service_name": "BCS_EVENT",
        "events": [
            {
                "name": u"状态改变",
                "event_type": "state_change",
                "event_demo": BCS_STATE_CHANGE_EVENT,
                "condition": [
                    {
                        "field": "app_alarm_level",
                        "name": u"级别",
                        "value_type": "select",
                        "specific_method": "in",
                        "specific_placeholder": u"请选择级别",
                    },
                    {
                        "field": "cluster_id",
                        "name": u"集群",
                        "value_type": "select",
                        "specific_method": "in",
                        "specific_placeholder": u"请选择集群",
                    },
                    {
                        "field": "namespace",
                        "name": u"命名空间",
                        "value_type": "select",
                        "specific_method": "in",
                        "specific_placeholder": u"请选择命名空间",
                    },
                    {
                        "field": "messages",
                        "name": u"关键字",
                        "value_type": "input",
                        "specific_method": "include_any",
                        "specific_placeholder": u"多个关键字以英文逗号分隔(,)，如：关键字1,关键字2",
                    }
                ]
            },
        ]
    }
]

# 事件维度
EVENT_DEMISSION = [
    {"name": "cluster_id - 集群ID", "value": "cluster_id"},
    {"name": "namespace - 命名空间", "value": "namespace"},
    {"name": "messages - 告警详情", "value": "messages"},
    {"name": "app_alarm_level - 告警级别", "value": "app_alarm_level"},
    {"name": "module_name - 模块名称", "value": "module_name"},
    {"name": "label - 标签", "value": "label"},
    {"name": "version - 版本", "value": "version"},
    {"name": "host - 主机IP", "value": "host"},
    {"name": "reason - 告警原因", "value": "reason"},
    {"name": "affiliation - 隶属关系", "value": "affiliation"},
]

# 事件方法
EVENT_METHORD = [
    {"name": "eq - 等于", "method": "eq", "type": "string", "tips": ""},
    {"name": "neq - 不等于", "method": "neq", "type": "string", "tips": ""},
    {"name": "in - 在列表中", "method": "in", "type": "array", "tips": "多个关键字以英文逗号分隔"},
    {"name": "include - 包含关键字", "method": "include", "type": "string", "tips": ""},
    {"name": "exclude - 不包含关键字", "method": "exclude", "type": "string", "tips": ""},
    {"name": "include_all - 包含列表中所有关键字", "method": "include_all", "type": "array", "tips": "多个关键字以英文逗号分隔"},
    {"name": "include_any - 包含列表中任意关键字", "method": "include_any", "type": "array", "tips": "多个关键字以英文逗号分隔"},
    {"name": "startswith - 以字符串开头", "method": "startswith", "type": "string", "tips": ""},
    {"name": "nstartswith - 不以字符串开头", "method": "nstartswith", "type": "string", "tips": ""},
    {"name": "reg - 正则表达式", "method": "reg", "type": "string", "tips": ""},
    {"name": "gte - 大于等于", "method": "gte", "type": "string", "tips": ""},
    {"name": "lte - 小于等于", "method": "lte", "type": "string", "tips": ""},
]

# 事件级别列表: 重要/一般/不重要 （important / general / unimportant）
EVENT_LEVEL_LIST = [
    {"value": "important", "name": u"重要"},
    {"value": "general", "name": u"一般"},
    {"value": "unimportant", "name": u"不重要"},
]


# 告警状态（与监控后台 kernel/constants.py INSTANCE_USER_STATUS 保持一致）
INSTANCE_STATUS_SHOW = {
    "shield": "已屏蔽",
    "converged": "已收敛",
    "notified": "已通知",
    "unnotified": "通知失败"
}
INSTANCE_STATUS_DESC = INSTANCE_STATUS_SHOW.copy()
INSTANCE_STATUS_DESC.update({"skipped": "已收敛"})

# 告警类型
INSTANCE_CATE = {
    "alarm": "告警",
    "event": "事件",
    "log": "日志"
}
# 告警类型对应的Source_type
SOURCE_TYPE_BY_CATE = {
    "alarm": "BCS_ALERT",
    "event": "BCS_EVENT",
    "log": "BCS_LOG"
}
# Source_type 对应的告警类型
ALARM_CATE_BY_SOURCE = {v: k for k, v in SOURCE_TYPE_BY_CATE.items()}

# 空值显示
NO_VALUE_DISPLAY = "无"

# 屏蔽类型: 告警类型 + 全屏蔽
SHIELD_TYPES = INSTANCE_CATE.copy()
SHIELD_TYPES.update({"all": "全屏蔽"})

#  屏蔽对象
SHIELD_OBJECTS = {
    "cluster_id": "按集群",
    "monitor_id": "按告警名称"
}

SHIELD_OBJECTS_SHOW = {
    "cluster_id": "集群",
    "monitor_id": "告警名称"
}

# 屏蔽状态
SHIELD_STATUS = {
    'deactivated': "已停用",
    'unshielded': "待屏蔽",
    'shielding': "屏蔽中",
    "expired": "已过期"
}


METHOD_CONSTANT = {
    'neq': '!=',
    'eq': '=',
    'gt': '>',
    'gte': '>=',
    'lt': '<',
    'lte': '<='
}
