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
from backend.apps.datalog.models import ProjectDataInfo
from backend.apps.datalog.data_collect import (create_data_project, create_and_start_standard_data_flow,  # noqa
                                               create_and_start_non_standard_data_flow)  # noqa


def get_data_id_by_project_id(project_id):
    """获取项目标准日志采集的dataid
    """
    try:
        project = ProjectDataInfo.objects.get(project_id=project_id)
    except Exception:
        standard_data_id = None
        non_standard_data_id = None
    else:
        standard_data_id = project.standard_data_id
        non_standard_data_id = project.non_standard_data_id

    return {
        'standard_data_id': standard_data_id if standard_data_id else 0,
        'non_standard_data_id': non_standard_data_id if non_standard_data_id else 0
    }


def get_std_log_index(project_id):
    try:
        data_info = ProjectDataInfo.objects.get(project_id=project_id)
    except ProjectDataInfo.DoesNotExist:
        return ''
    else:
        return f'{data_info.cc_biz_id}_etl_{data_info.standard_data_name}_*'
