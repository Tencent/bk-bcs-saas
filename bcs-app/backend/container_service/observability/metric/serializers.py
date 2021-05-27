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
import arrow
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.container_service.observability.metric.constants import METRICS_DEFAULT_TIMEDELTA


class BaseMetricSLZ(serializers.Serializer):
    start_at = serializers.DateTimeField(required=False)
    end_at = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        now = arrow.now().timestamp

        attrs['start_at'] = (
            arrow.get(attrs['start_at']).timestamp if 'start_at' in attrs else now - METRICS_DEFAULT_TIMEDELTA
        )

        attrs['end_at'] = arrow.get(attrs['end_at']).timestamp if 'end_at' in attrs else now

        if attrs['end_at'] <= attrs['start_at']:
            raise ValidationError(_('查询的 起始时间 需小于 结束时间'))
        return attrs


class FetchPodMetricSLZ(BaseMetricSLZ):
    """ 获取多个 Pod 指标信息 """

    pod_name_list = serializers.ListField(
        label='Pod 名称列表', child=serializers.CharField(max_length=64), allow_empty=False
    )


class FetchContainerMetricSLZ(BaseMetricSLZ):
    """ 获取容器指标信息 """

    container_ids = serializers.ListField(
        label='容器 ID 列表', child=serializers.CharField(max_length=64), allow_empty=False, required=False
    )


class FetchMetricOverviewSLZ(serializers.Serializer):
    """ 获取指标总览 """

    dimensions = serializers.ListField(
        label='指标维度', child=serializers.CharField(max_length=16), allow_empty=True, required=False
    )


class FetchTargetsSLZ(serializers.Serializer):
    """ 获取 Target 列表 """

    show_discovered = serializers.BooleanField(label='是否展示 Discovered', default=False, required=False)
