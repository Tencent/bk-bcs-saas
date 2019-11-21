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
import json
import re
from urllib.parse import urlparse

from rest_framework import serializers
from backend.apps.metric.models import Metric
from rest_framework.exceptions import ValidationError

NAME_PATTERN = re.compile(r'^[a-z0-9]([-_a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$')


def validate_http_body(body):
    """验证http_body
    """
    try:
        body = json.loads(body)
    except Exception:
        raise ValidationError("GET方式，http_body必须是json数据")

    if not isinstance(body, dict):
        raise ValidationError("GET方式，http_body必须是字典类型")

    for k, v in body.items():
        if isinstance(k, (tuple, list, dict)) or isinstance(v, (tuple, list, dict)):
            raise ValidationError("GET方式，http_body键和值必须是数字或者字符串类型")

        if not k or not v:
            raise ValidationError("GET方式，http_body键和值不能为空")


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
        count = Metric.objects.filter(project_id=self.context['project_id'], name=name).count()
        if count > 0:
            raise ValidationError("name已经存在")

        if not NAME_PATTERN.match(name):
            raise ValidationError("名称由英文字母、下划线或数字组成，且不可以数字开头")
        return name

    def validate_uri(self, uri):
        parse = urlparse(uri)
        if parse.scheme or parse.netloc:
            raise ValidationError("uri不需要填写协议和域名")
        if uri[0] != '/':
            raise ValidationError("uri必须是绝对路径")
        return uri

    def validate_port(self, port):
        if port < 1 or port > 65535:
            raise ValidationError("port必须在1-65535之间")
        return port

    def validate_http_headers(self, http_headers):
        if not http_headers:
            http_headers = {}
        return json.dumps(http_headers)

    def validate_http_body(self, http_body):
        if not http_body:
            return ''
        else:
            return http_body

    def validate_metric_type(self, metric_type):
        """只能为空或者为'prometheus'
        """
        if not metric_type:
            return ''
        if metric_type in ['prometheus']:
            return metric_type
        raise ValidationError("metric_type 只能为空或者为'prometheus'")

    def validate_const_labels(self, const_labels):
        if not const_labels:
            const_labels = {}
        return json.dumps(const_labels)

    def validate(self, data):
        if not data:
            raise ValidationError("参数不能为空")

        if data.get('http_body') and data['http_method'] == 'GET':
            validate_http_body(data['http_body'])
        return data


class CreateMetricSLZ(UpdateMetricSLZ):
    name = serializers.CharField(max_length=253, min_length=3)

    def validate_name(self, name):
        count = Metric.objects.filter(project_id=self.context['project_id'], name=name).count()
        if count > 0:
            raise ValidationError("name已经存在")

        if not NAME_PATTERN.match(name):
            raise ValidationError("名称由英文字母、下划线、中划线或数字组成，且不可以数字开头")
        return name
