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
"""
import json
from urllib.parse import urlparse

import arrow
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.container_service.observability.metric import constants
from backend.container_service.observability.metric.models import Metric


class BaseMetricSLZ(serializers.Serializer):
    start_at = serializers.DateTimeField(required=False)
    end_at = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        now = arrow.now().timestamp

        attrs['start_at'] = (
            arrow.get(attrs['start_at']).timestamp
            if 'start_at' in attrs
            else now - constants.METRICS_DEFAULT_TIMEDELTA
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


# --------- Service Monitor 相关 -----------


class ServiceMonitorInfoSLZ(serializers.Serializer):
    """ ServiceMonitor 基础信息 """

    name = serializers.CharField(label='名称')
    namespace = serializers.CharField(label='命名空间')

    def validate_name(self, name):
        if not constants.SM_NAME_PATTERN.match(name):
            raise ValidationError(_('名称由小写英文字母、中划线或数字组成，且需以小写字母开头'))
        return name


class ServiceMonitorUpdateSLZ(serializers.Serializer):
    """ 更新 ServiceMonitor """

    port = serializers.CharField(label='端口')
    path = serializers.CharField(label='绝对路径')
    interval = serializers.IntegerField(label='时间间隔')
    sample_limit = serializers.IntegerField(
        label='样本数限制', min_value=constants.SM_SAMPLE_LIMIT_MIN, max_value=constants.SM_SAMPLE_LIMIT_MAX
    )
    selector = serializers.JSONField(label='选择器参数')
    params = serializers.JSONField(label='额外参数', required=False)

    def validate_selector(self, selector):
        if not selector or not isinstance(selector, dict):
            raise ValidationError(_('选择器参数不能为空 且 需为字典类型'))
        return selector

    def validate_interval(self, interval):
        if interval not in constants.ALLOW_SM_INTERVAL:
            raise ValidationError(_('参数不合法，只允许 {}').format(constants.ALLOW_SM_INTERVAL))
        return f'{interval}s'

    def validate_path(self, path):
        if not path.startswith('/'):
            raise ValidationError(_('参数不合法，必须是绝对路径'))
        return path

    def validate_params(self, params):
        if not isinstance(params, dict):
            raise ValidationError(_('额外参数必须是字典类型'))
        return params


class ServiceMonitorCreateSLZ(ServiceMonitorInfoSLZ, ServiceMonitorUpdateSLZ):
    """ 创建 ServiceMonitor """

    service_name = serializers.CharField(label='Service 名称')


class ServiceMonitorBatchDeleteSLZ(serializers.Serializer):
    """ 批量删除 ServiceMonitor """

    service_monitors = serializers.ListField(
        label='待删除 ServiceMonitor 列表', child=ServiceMonitorInfoSLZ(), allow_empty=False
    )


# ----------- Metric(model) 相关 -----------


def validate_http_body(body):
    """验证http_body"""
    try:
        body = json.loads(body)
    except Exception:
        raise ValidationError(_("GET方式，http_body必须是json数据"))

    if not isinstance(body, dict):
        raise ValidationError(_("GET方式，http_body必须是字典类型"))

    for k, v in body.items():
        if isinstance(k, (tuple, list, dict)) or isinstance(v, (tuple, list, dict)):
            raise ValidationError(_("GET方式，http_body键和值必须是数字或者字符串类型"))

        if not k or not v:
            raise ValidationError(_("GET方式，http_body键和值不能为空"))


class UpdateMetricSLZ(serializers.Serializer):
    port = serializers.IntegerField()
    uri = serializers.CharField(min_length=2)
    frequency = serializers.IntegerField()
    http_method = serializers.ChoiceField(choices=Metric.method_choice, default="GET")
    http_headers = serializers.JSONField(required=False, allow_null=True)
    http_body = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    # 新增兼容 prometheus 采集的字段
    metric_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    const_labels = serializers.JSONField(required=False, allow_null=True)
    timeout = serializers.IntegerField(required=True)

    def validate_name(self, name):
        count = Metric.objects.filter(project_id=self.context["project_id"], name=name).count()
        if count > 0:
            raise ValidationError(_("name已经存在"))

        if not constants.METRIC_NAME_PATTERN.match(name):
            raise ValidationError(constants.METRIC_NAME_PATTERN_MSG)
        return name

    def validate_uri(self, uri):
        parse = urlparse(uri)
        if parse.scheme or parse.netloc:
            raise ValidationError(_("uri不需要填写协议和域名"))
        if uri[0] != "/":
            raise ValidationError(_("uri必须是绝对路径"))
        return uri

    def validate_port(self, port):
        if port < 1 or port > 65535:
            raise ValidationError(_("port必须在1-65535之间"))
        return port

    def validate_http_headers(self, http_headers):
        if not http_headers:
            http_headers = {}
        return json.dumps(http_headers)

    def validate_http_body(self, http_body):
        if not http_body:
            return ""
        else:
            return http_body

    def validate_metric_type(self, metric_type):
        """只能为空或者为'prometheus'"""
        if not metric_type:
            return ""
        if metric_type in ["prometheus"]:
            return metric_type
        raise ValidationError(_("metric_type 只能为空或者为'prometheus'"))

    def validate_const_labels(self, const_labels):
        if not const_labels:
            const_labels = {}
        return json.dumps(const_labels)

    def validate(self, data):
        if not data:
            raise ValidationError(_("参数不能为空"))

        if data.get("http_body") and data["http_method"] == "GET":
            validate_http_body(data["http_body"])
        return data


class CreateMetricSLZ(UpdateMetricSLZ):
    name = serializers.CharField(max_length=253, min_length=3)

    def validate_name(self, name):
        count = Metric.objects.filter(project_id=self.context["project_id"], name=name).count()
        if count > 0:
            raise ValidationError(_("name已经存在"))

        if not constants.METRIC_NAME_PATTERN.match(name):
            raise ValidationError(constants.METRIC_NAME_PATTERN_MSG)
        return name
