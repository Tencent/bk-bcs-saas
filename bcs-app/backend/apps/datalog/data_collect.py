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
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from backend.utils.error_codes import error_codes
from backend.apps.datalog.models import ProjectDataInfo
from backend.utils.notify import notify_manager
from backend.components.data import deploy_plan, setup_clean, setup_shipper, DataType, IS_DATA_OPEN


def create_data_project(username, project_id, cc_app_id, english_name):
    """
    @summary: 在数据平台上创建项目信息
    @note: 创建项目时调用，关联了蓝鲸业务的项目才需要创建
    """
    # 数据平台功能没有开启，则直接返回
    if not IS_DATA_OPEN:
        return True

    project, _c = ProjectDataInfo.objects.get_or_create(project_id=project_id, defaults={'cc_biz_id': cc_app_id})
    # 判断项目是否已经创建，已经创建则不再重复创建
    if all([project.data_project_id, project.standard_data_id, project.non_standard_data_id]):
        return True

    # 申请标准日志采集 dataid, standard_data_name 修改 db 中的字段信息
    standard_data_name = f'{DataType.SLOG.value}_{english_name}'
    res1, standard_data_id = deploy_plan(username, cc_app_id, standard_data_name, DataType.SLOG.value)
    if not res1:
        message = _('申请标准日志采集 dataid, 业务ID:{cc_app_id},项目名:{english_name}失败,原因:{standard_data_id},失败').format(
            cc_app_id=cc_app_id,
            english_name=english_name,
            standard_data_id=standard_data_id,
        )
        notify_manager(message)
        raise error_codes.APIError(_('申请标准日志采集 dataid 失败:{}').format(standard_data_id))

    # 申请非标准日志采集 dataid
    non_standard_data_name = f'{DataType.CLOG.value}_{english_name}'
    res2, non_standard_data_id = deploy_plan(username, cc_app_id, non_standard_data_name, DataType.CLOG.value)
    if not res2:
        message = _('申请非标准日志采集 dataid, 业务ID:{cc_app_id},项目名:{english_name}失败,原因:{standard_data_id},请关注').format(
            cc_app_id=cc_app_id,
            english_name=english_name,
            standard_data_id=standard_data_id,
        )
        notify_manager(message)
        raise error_codes.APIError(_('申请非标准日志采集dataid失败:{}').format(standard_data_id))

    # 数据平台 V3 API 没有project_id的概念，给一个默认的值
    project.data_project_id = 1

    project.standard_data_id = standard_data_id
    project.standard_data_name = standard_data_name
    project.non_standard_data_id = non_standard_data_id
    project.non_standard_data_name = non_standard_data_name
    project.save()
    return True


def create_and_start_standard_data_flow(username, project_id, cc_app_id):
    """
    @summary: 标准日志：创建清洗配置,并启动清洗任务;创建分发存储，并启动对应的分发任务
    @note: 初始化集群时调用
    @return: True/data_project_id, False/error_msg
    """
    # 数据平台功能没有开启，则直接返回
    if not IS_DATA_OPEN:
        return True, _("数据平台功能暂未开启")

    try:
        project = ProjectDataInfo.objects.get(project_id=project_id)
    except Exception:
        return False, _("请先在数据平台创建项目信息")
    # db 中已经有任务信息，则说明已经创建/启动了任务，不需要再重复启动
    if project.standard_flow_id and project.standard_flow_task_id:
        return project.standard_flow_id

    # 已经创建清洗配置则不再重新创建，只分发任务
    if not project.standard_flow_id:
        # 创建清洗配置
        res, flow_id = setup_clean(username, cc_app_id, project.standard_data_id, DataType.SLOG.value)
        if not res:
            message = _('启动标准日志采集清洗任务失败[{}],原因:{},请关注').format(project_id, flow_id)
            notify_manager(message)
            return False, _('启动标准日志采集清洗任务失败:{}').format(flow_id)
    else:
        flow_id = project.standard_flow_id

    # 启动分发任务
    res2, flow_task_id = setup_shipper(project.standard_data_id, flow_id, DataType.SLOG.value)
    if not res2:
        message = _('启动标准日志采集分发任务失败[{}],原因:{},请关注').format(project_id, flow_task_id)
        notify_manager(message)
        return False, _('启动标准日志采集清洗任务失败:{}').format(flow_task_id)
    # 将任务相关的id保存到db中，下次初始化集群则可以直接查询状态
    project.standard_flow_id = flow_id
    project.standard_flow_task_id = flow_task_id
    project.save()
    return True, _("启动标准日志采集任务成功")


def create_and_start_non_standard_data_flow(username, project_id, cc_app_id):
    """
    @summary: 非标准日志：创建清洗配置,并启动清洗任务;创建分发存储，并启动对应的分发任务
    @note: 初始化集群时调用
    @return: True/data_project_id, False/error_msg
    """
    # 数据平台功能没有开启，则直接返回
    if not IS_DATA_OPEN:
        return True, _("数据平台功能暂未开启")

    try:
        project = ProjectDataInfo.objects.get(project_id=project_id)
    except Exception:
        return False, _("请先在数据平台创建项目信息")
    # db 中已经有任务信息，则说明已经创建/启动了任务，不需要再重复启动
    if project.non_standard_flow_id and project.non_standard_flow_task_id:
        return project.non_standard_flow_id

    # 已经创建清洗配置则不再重新创建，只分发任务
    if not project.non_standard_flow_id:
        # 创建清洗配置
        res, flow_id = setup_clean(username, cc_app_id, project.non_standard_data_id, DataType.CLOG.value)
        if not res:
            message = _('创建非标准日志采集清洗任务失败[{}],原因:{},请关注').format(project_id, flow_id)
            notify_manager(message)
            return False, '{}:{}'.format(_("创建非标准日志采集清洗任务失败"), flow_id)
    else:
        flow_id = project.non_standard_flow_id

    # 启动任务
    res2, flow_task_id = setup_shipper(project.non_standard_data_id, flow_id, DataType.CLOG.value)
    if not res2:
        message = _('启动非标准日志采集分发任务失败[{}],原因:{},请关注').format(project_id, flow_task_id)
        notify_manager(message)
        return False, _('创建非标准日志采集清洗任务失败:{}').format(flow_task_id)
    # 将任务相关的id保存到db中，下次初始化集群则可以直接查询状态
    project.non_standard_flow_id = flow_id
    project.non_standard_flow_task_id = flow_task_id
    project.save()
    return True, _("启动非标准日志采集任务成功")


def create_prometheus_data_flow(username, project_id, cc_app_id, english_name, dataset):
    """prometheus 类型的Metric申请数据平台的dataid，并配置默认的清洗入库规则
    """
    # 数据平台功能没有开启，则直接返回
    if not IS_DATA_OPEN:
        return True, _("数据平台功能暂未开启")

    # 1. 提交接入部署计划,获取dataid
    is_ok, data_id = deploy_plan(username, cc_app_id, dataset, DataType.METRIC.value)
    if not is_ok:
        message = _('申请标准日志采集Prometheus Metric dataid[业务ID:{cc_app_id},项目名:{english_name}]失败,原因:{data_id},失败').format(
            cc_app_id=cc_app_id,
            english_name=english_name,
            data_id=data_id,
        )
        notify_manager(message)
        return False, _('申请Prometheus Metric dataid:{}').format(data_id)

    # 2. 创建清洗配置,并启动清洗任务
    res, result_table_id = setup_clean(username, cc_app_id, data_id, DataType.METRIC.value)
    if not res:
        notify_manager(_('创建Prometheus Metric清洗任务失败[{english_name}],原因:{table_id}请关注').format(
            english_name=english_name,
            table_id=result_table_id,
        ))

        return False, _('创建Prometheus Metric清洗任务失败:{}').format(result_table_id)

    # 3. 创建分发存储，并启动对应的分发任务
    res2, msg = setup_shipper(data_id, result_table_id, DataType.METRIC.value)
    if not res2:
        message = _('启动非标准日志采集分发任务失败[{}],原因:{},请关注').format(project_id, msg=msg)
        notify_manager(message)
        return False, _('启动非标准日志采集分发任务失败:{}').format(msg)
    return True, data_id


def apply_dataid_by_metric(biz_id, dataset, operator):
    # 数据平台功能没有开启，则直接返回
    if not IS_DATA_OPEN:
        return True, 0

    is_ok, data_id = deploy_plan(operator, biz_id, dataset, DataType.METRIC.value)
    return is_ok, data_id


def get_metric_data_name(metric_name, project_id):
    """
    数据平台(raw_data_name)长度限制为 30 个字符
    metric_name 最大长度为 28 个字符
    """
    metric_name_len = len(metric_name)
    rand = get_random_string(30 - metric_name_len - 1)
    raw_data_name = f'{metric_name}_{rand}'
    return raw_data_name
