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
import logging

from django.db import models
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)


class ProjectDataInfo(models.Model):
    """项目与数据平台相关的数据
    @note: 可以将数据存放到配置中心

    @note: 此Model数据需采用 save 方法保存，因需要触发signals处理关联数据
    """
    cc_biz_id = models.IntegerField(_('业务ID'), blank=True, default=0)
    project_id = models.CharField(_("项目ID"), max_length=32, unique=True)
    data_project_id = models.IntegerField(_("数据平台上申请的项目ID"), null=True, blank=True)
    # 标准日志采集
    standard_data_id = models.IntegerField(_("标准日志采集的dataid"), null=True, blank=True)
    standard_data_name = models.CharField(_("标准日志采集源数据"), max_length=255, null=True, blank=True,
                                          help_text=_('变更后，会同步更新paas_monitor/log中ES-Index配置'))
    standard_flow_id = models.IntegerField(_("标准日志采集DataFlow ID"), null=True, blank=True)
    standard_flow_task_id = models.IntegerField(_("标准日志采集DataFlow 任务ID"), null=True, blank=True)

    non_standard_data_id = models.IntegerField(_("非标准日志采集的dataid"), null=True, blank=True)
    non_standard_data_name = models.CharField(_("非标准日志采集源数据"), max_length=255, null=True, blank=True,
                                              help_text=_('变更后，会同步更新paas_monitor/log中ES-Index配置'))
    non_standard_flow_id = models.IntegerField(_("非标准日志采集DataFlow ID"), null=True, blank=True)
    non_standard_flow_task_id = models.IntegerField(_("非标准日志采集DataFlow 任务ID"), null=True, blank=True)

    def _get_result_table_id(self, data_name, flow_task_id):
        # 如果 DataFlow 任务ID 为空，后端存储实际不可用，不需要创建日志流
        if data_name and data_name.strip() and flow_task_id:
            return '%s_etl_%s' % (self.cc_biz_id, data_name.strip())
        return ''

    @property
    def standard_result_table_id(self):
        return self._get_result_table_id(self.standard_data_name, self.standard_flow_task_id)

    @property
    def non_standard_result_table_id(self):
        return self._get_result_table_id(self.non_standard_data_name, self.non_standard_flow_task_id)
