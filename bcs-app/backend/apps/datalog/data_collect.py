# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by
# making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
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
import logging

from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from backend.utils.error_codes import error_codes
from backend.apps.datalog.models import ProjectDataInfo
from backend.utils.notify import notify_manager
from backend.components.data import deploy_plan, create_data_bus, DataType, IS_DATA_OPEN, get_data_id_by_name

logger = logging.getLogger(__name__)


def deploy_log_plan(username, cc_biz_id, project_code, data_log_type):
    data_log_name = f"{data_log_type}_{project_code}_{cc_biz_id}"
    data_id = get_data_id_by_name(data_log_name)
    if data_id:
        return data_id, data_log_name

    result, data = deploy_plan(username, cc_biz_id, data_log_name, data_log_type)
    if not result:
        notify_manager(
            _("申请{data_log_type}采集dataid[业务ID:{cc_biz_id},项目名:{project_code}]失败,原因:{data},请关注").format(
                data_log_type=data_log_type, cc_biz_id=cc_biz_id, project_code=project_code, data=data
            )
        )
        raise error_codes.APIError(_("申请{}采集dataid失败:{}").format(data_log_type, data))

    return data, data_log_name


def create_data_project(username, project_id, cc_biz_id, project_code):
    """
    @summary: 在数据平台上创建项目信息
    @note: 创建项目时调用，关联了蓝鲸业务的项目才需要创建
    """
    # 数据平台功能没有开启，则直接返回
    if not IS_DATA_OPEN:
        return True

    project_data, created = ProjectDataInfo.objects.get_or_create(
        project_id=project_id, defaults={"cc_biz_id": cc_biz_id}
    )

    if not created and project_data.cc_biz_id != cc_biz_id:
        project_data.cc_biz_id = cc_biz_id
        project_data.save(update_fields=["cc_biz_id"])
        created = True

    if created:
        # 数据平台 V3 API 没有project_id的概念，给一个默认的值
        project_data.data_project_id = 1
        project_data.save(update_fields=["data_project_id"])

    if created or not project_data.standard_data_id:
        # 申请标准日志采集 dataid, standard_data_name 修改 db 中的字段信息
        std_data_id, std_data_name = deploy_log_plan(username, cc_biz_id, project_code, DataType.SLOG.value)
        project_data.__dict__.update(
            {
                "standard_data_id": std_data_id,
                "standard_data_name": std_data_name,
                "standard_table_name": "",
                "standard_storage_success": False,
            }
        )
        project_data.save()

    if created or not project_data.non_standard_data_id:
        # 申请非标准日志采集 dataid
        non_std_data_id, non_std_data_name = deploy_log_plan(username, cc_biz_id, project_code, DataType.CLOG.value)
        project_data.__dict__.update(
            {
                "non_standard_data_id": non_std_data_id,
                "non_standard_data_name": non_std_data_name,
                "non_standard_table_name": "",
                "non_standard_storage_success": False,
            }
        )
        project_data.save()

    return True


def create_and_start_standard_data_flow(username, project_id, cc_biz_id):
    return _create_and_start_data_flow(username, project_id, cc_biz_id, DataType.SLOG.value)


def create_and_start_non_standard_data_flow(username, project_id, cc_biz_id):
    return _create_and_start_data_flow(username, project_id, cc_biz_id, DataType.CLOG.value)


def _create_and_start_data_flow(username, project_id, cc_biz_id, data_type):
    if not IS_DATA_OPEN:
        return True, _("数据平台功能暂未开启")

    try:
        project_data = ProjectDataInfo.objects.get(project_id=project_id, cc_biz_id=cc_biz_id)
    except ProjectDataInfo.DoesNotExist:
        return False, _("请先在数据平台创建项目信息")

    if not project_data.standard_data_id and data_type == DataType.SLOG.value:
        logger.error("no standard_data_id")
        return True, ""

    if not project_data.non_standard_data_id and data_type == DataType.CLOG.value:
        logger.error("no non_standard_data_id")
        return True, ""

    data_bus_cls = create_data_bus(data_type)
    data_bus = data_bus_cls(project_data)
    result, message = data_bus.clean_and_storage_data(username)
    if not result:
        message = _("启动{}日志采集清洗和入库任务失败[{}],原因:{},请关注").format(data_type, project_id, message)
        notify_manager(message)
        return False, message

    return True, message


def create_prometheus_data_flow(username, project_id, cc_app_id, english_name, dataset):
    """prometheus 类型的Metric申请数据平台的dataid，并配置默认的清洗入库规则
    """
    return True, _("数据平台功能暂未开启")


def apply_dataid_by_metric(biz_id, dataset, operator):
    # 数据平台功能没有开启，则直接返回
    return True, 0


def get_metric_data_name(metric_name, project_id):
    """
    数据平台(raw_data_name)长度限制为 30 个字符
    metric_name 最大长度为 28 个字符
    """
    metric_name_len = len(metric_name)
    rand = get_random_string(30 - metric_name_len - 1)
    raw_data_name = f"{metric_name}_{rand}"
    return raw_data_name
