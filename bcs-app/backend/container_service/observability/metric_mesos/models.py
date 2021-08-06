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
import datetime
import json
import logging

from django.conf import settings
from django.db import models

from backend.utils.models import BaseModel

logger = logging.getLogger(__name__)


class MetricManager(models.Manager):
    def get_queryset(self):
        """过滤软删除的记录"""
        return super().get_queryset().filter(is_deleted=False)


class Metric(BaseModel):
    method_choice = (('GET', "GET"), ('POST', "POST"))

    STATUS = (('pause', "pause"), ('resume', "resume"))

    project_id = models.CharField(u"项目ID", max_length=32)
    name = models.CharField(u"名称", max_length=128)
    port = models.IntegerField("端口")
    uri = models.TextField("URI")
    frequency = models.IntegerField("采集频率", default=60)

    http_method = models.CharField("Http Method", max_length=16, choices=method_choice, default="GET")
    http_headers = models.TextField("Http Headers")
    http_body = models.TextField("Http 参数")

    version = models.CharField("版本信息", default='v1', max_length=32)
    data_id = models.IntegerField("数据平台DataID")
    # 新增兼容 prometheus 采集的字段
    metric_type = models.CharField("类型", max_length=128, default='', help_text=u"特殊格式如prometheus")
    const_labels = models.TextField("附加数据", default='{}', help_text=u"prometheus格式下，允许附加key-value pair")
    timeout = models.IntegerField("单次采集超时时间（秒）", default=30)
    status = models.CharField("状态", max_length=32, choices=STATUS, default='')

    objects = MetricManager()
    default_objects = models.Manager()

    def __str__(self):
        return '<%s, %s>' % (self.project_id, self.name)

    @property
    def get_const_labels(self):
        try:
            const_labels = json.loads(self.const_labels)
        except Exception:
            const_labels = {}
        return const_labels

    def update_version(self):
        try:
            version = int(self.version[1:])
        except Exception:
            logger.exception("get version error")
            version = 1
        return 'v%s' % (version + 1)

    def soft_delete(self, **kwargs):
        self.is_deleted = True
        self.deleted_time = datetime.datetime.now()
        super(Metric, self).save(**kwargs)

    def update_status(self, status):
        """更新记录状态"""
        self.status = status
        super(Metric, self).save()

    def to_json(self):
        if self.data_id:
            uri_data_clean = settings.URI_DATA_CLEAN.format(data_id=self.data_id)
        else:
            uri_data_clean = ''

        data = {
            'id': self.id,
            'name': self.name,
            'port': self.port,
            'uri': self.uri,
            'frequency': self.frequency,
            'http_method': self.http_method,
            'http_body': self.http_body,
            'version': self.version,
            'uri_data_clean': uri_data_clean,
            'metric_type': self.metric_type,
            'const_labels': self.get_const_labels,
            'timeout': self.timeout,
            'status': self.status,
        }

        if self.http_headers:
            try:
                data['http_headers'] = json.loads(self.http_headers)
            except Exception:
                logger.exception("get json http_header error, %s", self.http_headers)
                data['http_headers'] = {}
        else:
            data['http_headers'] = {}
        if self.http_body and self.http_method == 'GET':
            try:
                data['http_body'] = json.loads(self.http_body)
            except Exception:
                logger.exception("get json http body error, %s", self.http_body)
                data['http_body'] = {}

        return data

    def to_api_json(self):
        """转换为API调用的json"""
        _json = self.to_json()
        if self.http_method == 'GET':
            parameters = _json['http_body']
            if not isinstance(parameters, dict):
                parameters = {}
        else:
            parameters = {'body': self.http_body}
        api_json = {
            "version": self.version,
            "name": self.name,
            "namespace": "",
            "networkMode": "",
            "networkType": "",
            "clusterID": "",
            "dataID": self.data_id,
            "port": self.port,
            "uri": self.uri,
            "method": self.http_method,
            "frequency": self.frequency,
            "head": _json['http_headers'],
            "parameters": parameters,
            "metricType": self.metric_type,
            "constLabels": self.get_const_labels,
            'timeout': self.timeout,
        }
        return api_json
