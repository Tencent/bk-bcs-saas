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
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ProjectDataInfo(models.Model):
    """项目与数据平台相关的数据
    @note: 可以将数据存放到配置中心

    @note: 此Model数据需采用 save 方法保存，因需要触发signals处理关联数据
    """

    cc_biz_id = models.IntegerField(_("业务ID"), blank=True, default=0)
    project_id = models.CharField(_("项目ID"), max_length=32, unique=True)
    data_project_id = models.IntegerField(_("数据平台上申请的项目ID"), null=True, blank=True)
    # 标准日志
    standard_data_id = models.IntegerField(_("标准日志采集的dataid"), null=True, blank=True)
    standard_data_name = models.CharField(_("标准日志采集源数据"), max_length=255, null=True, blank=True)
    standard_table_name = models.CharField(_("标准日志表名"), max_length=255, null=True, blank=True)
    standard_storage_success = models.BooleanField(default=False)

    non_standard_data_id = models.IntegerField(_("非标准日志采集的dataid"), null=True, blank=True)
    non_standard_data_name = models.CharField(_("非标准日志采集源数据"), max_length=255, null=True, blank=True)
    non_standard_table_name = models.CharField(_("非标准日志表名"), max_length=255, null=True, blank=True)
    non_standard_storage_success = models.BooleanField(default=False)
