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
from typing import List

from backend.bcs_k8s.helm.models.chart import Chart, ChartVersion, ChartVersionSnapshot
from backend.bcs_k8s.helm.models.repo import Repository


def update_bcs_chart_records(project_id: str, project_code: str, chart: Chart, versions: List[str]):
    """更新bcs记录的chart的相关记录"""
    chart_versions = ChartVersion.objects.filter(chart=chart, version__in=versions)
    version_digests = [info.digest for info in chart_versions]
    # 处理digest不变动的情况
    ChartVersionSnapshot.objects.filter(digest__in=version_digests).delete()
    chart_versions.delete()
    # 如果chart下没有版本了，需要删除当前chart；否则，更新默认版本为剩余版本中最新版本
    chart_all_versions = ChartVersion.objects.filter(chart=chart)
    if not chart_all_versions:
        chart.delete()
    else:
        chart.defaultChartVersion = chart_all_versions.order_by("-created")[0]
        chart.save(update_fields=["defaultChartVersion"])

    # 设置commit id为空，以防出现强制推送版本后，相同版本digest不变动的情况
    Repository.objects.filter(project_id=project_id, name=project_code).update(commit=None)
