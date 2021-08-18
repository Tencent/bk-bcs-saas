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
import logging
import re
import time
from collections import OrderedDict
from urllib.parse import urlparse

import arrow
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.apps import constants
from backend.container_service.observability.metric_mesos.models import Metric

logger = logging.getLogger(__name__)

NAME_PATTERN = re.compile(r"^[a-z][-a-z0-9]*$")
NAME_PATTERN_MSG = _("名称由小写英文字母、中划线或数字组成，且不可以数字开头")


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

        if not NAME_PATTERN.match(name):
            raise ValidationError(NAME_PATTERN_MSG)
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

        if not NAME_PATTERN.match(name):
            raise ValidationError(NAME_PATTERN_MSG)
        return name


class PromMetricSLZBase(serializers.Serializer):
    start_at = serializers.DateTimeField(required=False)
    end_at = serializers.DateTimeField(required=False)

    def validate(self, data):
        now = int(time.time())
        # handle the start_at
        if "start_at" in data:
            data["start_at"] = arrow.get(data["start_at"]).timestamp
        else:
            # default one hour
            data["start_at"] = now - constants.METRICS_DEFAULT_TIMEDELTA
        # handle the end_at
        if "end_at" in data:
            data["end_at"] = arrow.get(data["end_at"]).timestamp
        else:
            data["end_at"] = now
        # start_at must be less than end_at
        if data["end_at"] <= data["start_at"]:
            raise ValidationError(_("param[start_at] must be less than [end_at]"))
        return data


class PromMetricSLZ(PromMetricSLZBase):
    res_id = serializers.CharField(required=True)


class PromPodMetricSLZ(PromMetricSLZBase):
    """Pod数据查询"""

    res_id_list = serializers.CharField(required=True)

    def validate_res_id_list(self, res_id_list):
        res_id_list = res_id_list.split(",")
        return res_id_list


class PromContainerMetricSLZ(PromMetricSLZBase):
    """容器数据查询"""

    res_id_list = serializers.CharField(required=False)
    pod_name = serializers.CharField(required=False)

    def _get_mesos_pod_name(self, pod_id):
        """
        转换示例 2.application-1.bellketest4.10039.1586934929583467102 -> applications-1-2
        """
        if "." not in pod_id:
            return pod_id

        try:
            return "{1}-{0}".format(*pod_id.split("."))
        except Exception as error:
            logger.error("extract mesos pod_name error: %s, %s", pod_id, error)
        return pod_id

    def _get_mesos_namespace(self, res_id_list):
        """
        转换示例 2.application-1.bellketest4.10039.1586934929583467102 -> bellketest4
        """
        ns_list = set()
        try:
            for pod_id in res_id_list:
                if "." not in pod_id:
                    continue
                ns_list.add(pod_id.split(".")[2])
        except Exception as error:
            logger.error("extract mesos namespace error: %s, %s", res_id_list, error)

        if len(ns_list) > 0:
            return "|".join(ns_list)
        return ".*"

    def _get_mesos_res_id_map(self, res_id_list):
        res_id_map = {}

        for res_id in res_id_list:
            pod_name = self._get_mesos_pod_name(res_id)
            res_id_map[pod_name] = res_id

        return res_id_map

    def validate_res_id_list(self, res_id_list):
        res_id_list = res_id_list.split(",")
        return res_id_list

    def validate_pod_name(self, pod_name):
        # mesos 做一次转换
        if self.context["request"].project.kind == constants.ProjectKind.MESOS.value:
            return self._get_mesos_pod_name(pod_name)

        return pod_name

    def validate(self, data: OrderedDict):
        data = super().validate(data)

        if not (data.get("res_id_list") or data.get("pod_name")):
            raise ValidationError(_("res_id_list, pod_name不能同时为空"))

        # mesos做一次转换
        if self.context["request"].project.kind == constants.ProjectKind.MESOS.value:
            if data.get("res_id_list"):
                data["namespace"] = self._get_mesos_namespace(data["res_id_list"])
                data["res_id_map"] = self._get_mesos_res_id_map(data["res_id_list"])
                data["res_id_list"] = data["res_id_map"].keys()
            else:
                data["namespace"] = self._get_mesos_namespace([self.initial_data["pod_name"]])

        data.setdefault("pod_name", ".*")
        data.setdefault("namespace", ".*")
        data.setdefault("res_id_map", {})
        data.setdefault("res_id_list", [".*"])

        return data


class ServiceMonitorUpdateSLZ(serializers.Serializer):
    """ServiceMonitor更新"""

    port = serializers.CharField()
    path = serializers.CharField()
    interval = serializers.IntegerField()
    # scrape_timeout = serializers.IntegerField()
    sample_limit = serializers.IntegerField(min_value=1, max_value=100000)
    selector = serializers.JSONField()
    params = serializers.JSONField(required=False)

    def validate_selector(self, selector):
        if not selector or not isinstance(selector, dict):
            raise ValidationError(_("参数不能为空且为字典类型"))
        return selector

    def validate_interval(self, interval):
        if interval not in [30, 60, 120]:
            raise ValidationError(_("参数不合法，只允许【30, 60, 120】"))
        return f"{interval}s"

    def validate_path(self, path):
        if not path.startswith("/"):
            raise ValidationError(_("参数不合法，必须是绝对路径"))
        return path

    def validate_params(self, params):
        if not isinstance(params, dict):
            raise ValidationError(_("参数必须是字典类型"))
        return params


class ServiceMonitorCreateSLZ(ServiceMonitorUpdateSLZ):
    """ServiceMonitor创建"""

    name = serializers.CharField()
    cluster_id = serializers.CharField()
    namespace = serializers.CharField()
    service_name = serializers.CharField()

    def validate_name(self, name):
        if not NAME_PATTERN.match(name):
            raise ValidationError(NAME_PATTERN_MSG)
        return name


class ServiceMonitorDeleteSLZ(serializers.Serializer):
    """ServiceMonitor删除"""

    name = serializers.CharField()
    namespace = serializers.CharField()

    def validate_name(self, name):
        if not NAME_PATTERN.match(name):
            raise ValidationError(NAME_PATTERN_MSG)
        return name


class ServiceMonitorBatchDeleteSLZ(serializers.Serializer):
    """ServiceMonitor批量删除"""

    servicemonitors = serializers.ListField(child=ServiceMonitorDeleteSLZ(), min_length=1)
