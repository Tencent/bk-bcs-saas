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
"""
数据平台 标准日志、非标准日志、Metric接入相关方法
"""
from enum import Enum
import time
import logging
from django.conf import settings

from backend.components.utils import http_post

from .constant import DATA_API_V3_PREFIX, DATA_TOKEN

logger = logging.getLogger(__name__)


class DataType(Enum):
    # 标准日志
    SLOG = 'slog'
    # 非标准日志
    CLOG = 'clog'
    # Metric
    METRIC = 'metric'


# 标准日志的清洗规则
SLOG_CLEAN_FIELDS = [
    {
        "field_name": "log",
        "field_alias": "log",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 1
    },
    {
        "field_name": "stream",
        "field_alias": "stream",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 2
    },
    {
        "field_name": "logfile",
        "field_alias": "logfile",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 3
    },
    {
        "field_name": "gseindex",
        "field_alias": "gseindex",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 4
    },
    {
        "field_name": "bcs_appid",
        "field_alias": "bcs_appid",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 5
    },
    {
        "field_name": "bcs_cluster",
        "field_alias": "bcs_cluster",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 6
    },
    {
        "field_name": "container_id",
        "field_alias": "container_id",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 7
    },
    {
        "field_name": "bcs_namespace",
        "field_alias": "bcs_namespace",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 8
    },
    {
        "field_name": "timestamp_orig",
        "field_alias": "timestamp_orig",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 9
    },
    {
        "field_name": "bcs_custom_labels",
        "field_alias": "bcs_custom_labels",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 10
    }
]
SLOG_JSON_CONDIF = '{"extract": {"args": [], "type": "fun", "method": "from_json", "next": {"type": "branch", "name": "", "next": [{"subtype": "assign_obj", "type": "assign", "assign": [{"type": "string", "assign_to": "logfile", "key": "logfile"}, {"type": "string", "assign_to": "gseindex", "key": "gseindex"}], "next": null}, {"subtype": "access_obj", "type": "access", "key": "container", "next": {"type": "branch", "name": "", "next": [{"subtype": "assign_obj", "type": "assign", "assign": [{"type": "string", "assign_to": "container_id", "key": "id"}], "next": null}, {"subtype": "access_obj", "type": "access", "key": "labels", "next": {"type": "branch", "name": "", "next": [{"subtype": "assign_obj", "type": "assign", "assign": [{"type": "int", "assign_to": "bcs_appid", "key": "io.tencent.bcs.app.appid"}, {"type": "string", "assign_to": "bcs_cluster", "key": "io.tencent.bcs.cluster"}, {"type": "string", "assign_to": "bcs_namespace", "key": "io.tencent.bcs.namespace"}], "next": null}, {"subtype": "access_obj", "next": {"next": {"subtype": "assign_json", "next": null, "type": "assign", "assign": [{"type": "string", "assign_to": "bcs_custom_labels", "key": "__all_keys__"}], "label": null}, "args": [], "type": "fun", "method": "from_json", "label": null}, "type": "access", "key": "io.tencent.bcs.custom.labels", "label": null}]}}]}}, {"subtype": "access_obj", "type": "access", "key": "log", "next": {"args": [], "type": "fun", "method": "iterate", "next": {"type": "branch", "name": "", "next": [{"subtype": "assign_obj", "type": "assign", "assign": [{"type": "string", "assign_to": "stream", "key": "stream"}, {"type": "string", "assign_to": "log", "key": "log"}, {"type": "string", "assign_to": "timestamp_orig", "key": "timestamp_orig"}], "next": null}, {"subtype": "access_obj", "type": "access", "key": "time", "next": {"args": ["+"], "type": "fun", "method": "split", "next": {"index": "0", "subtype": "access_pos", "type": "access", "next": {"args": ["."], "type": "fun", "method": "split", "next": {"index": "0", "subtype": "access_pos", "type": "access", "next": {"args": ["T", "", ":", "", "-", ""], "type": "fun", "method": "replace", "next": {"subtype": "assign_pos", "type": "assign", "assign": [{"index": "0", "assign_to": "timestamp", "type": "string"}], "next": null}}}}}}}]}}}]}}, "conf": {"timestamp_len": 0, "encoding": "UTF8", "time_format": "yyyyMMddHHmmss", "timezone": 0, "output_field_name": "timestamp", "time_field_name": "timestamp"}}'  # noqa
SLOG_STORAGE_CONFIG = '{"analyzed_fields": ["log"], "doc_values_fields": [], "json_fields": ["bcs_custom_labels"]}'  # noqa

# 非标准日志清洗规则
CLOG_CLEAN_FIELDS = [
    {
        "field_name": "log",
        "field_alias": "log",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 1
    },
    {
        "field_name": "stream",
        "field_alias": "stream",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 2
    },
    {
        "field_name": "logfile",
        "field_alias": "logfile",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 3
    },
    {
        "field_name": "gseindex",
        "field_alias": "gseindex",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 4
    },
    {
        "field_name": "bcs_appid",
        "field_alias": "bcs_appid",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 5
    },
    {
        "field_name": "bcs_cluster",
        "field_alias": "bcs_cluster",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 6
    },
    {
        "field_name": "container_id",
        "field_alias": "container_id",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 7
    },
    {
        "field_name": "bcs_namespace",
        "field_alias": "bcs_namespace",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 8
    },
    {
        "field_name": "timestamp_orig",
        "field_alias": "timestamp_orig",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 9
    },
    {
        "field_name": "bcs_custom_labels",
        "field_alias": "bcs_custom_labels",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 10
    }
]
CLOG_JSON_CONDIF = '{"extract": {"next": {"next": [{"subtype": "assign_obj", "next": null, "type": "assign", "assign": [{"type": "string", "assign_to": "logfile", "key": "logfile"}, {"type": "string", "assign_to": "gseindex", "key": "gseindex"}], "label": null}, {"subtype": "access_obj", "next": {"next": [{"subtype": "assign_obj", "next": null, "type": "assign", "assign": [{"type": "string", "assign_to": "container_id", "key": "id"}], "label": null}, {"subtype": "access_obj", "next": {"next": [{"subtype": "assign_obj", "next": null, "type": "assign", "assign": [{"type": "string", "assign_to": "bcs_appid", "key": "io.tencent.bcs.app.appid"}, {"type": "string", "assign_to": "bcs_cluster", "key": "io.tencent.bcs.cluster"}, {"type": "string", "assign_to": "bcs_namespace", "key": "io.tencent.bcs.namespace"}], "label": null}, {"subtype": "access_obj", "next": {"next": {"subtype": "assign_json", "next": null, "type": "assign", "assign": [{"type": "string", "assign_to": "bcs_custom_labels", "key": "__all_keys__"}], "label": null}, "args": [], "type": "fun", "method": "from_json", "label": null}, "type": "access", "key": "io.tencent.bcs.custom.labels", "label": null}], "type": "branch", "name": "", "label": null}, "type": "access", "key": "labels", "label": null}], "type": "branch", "name": "", "label": null}, "type": "access", "key": "container", "label": null}, {"subtype": "access_obj", "next": {"next": {"subtype": "assign_pos", "next": null, "type": "assign", "assign": [{"index": "0", "assign_to": "log", "type": "string"}], "label": null}, "args": [], "type": "fun", "method": "iterate", "label": null}, "type": "access", "key": "log", "label": null}, {"subtype": "access_obj", "next": {"next": {"index": "0", "next": {"next": {"index": "0", "next": {"next": {"subtype": "assign_pos", "next": null, "type": "assign", "assign": [{"index": "0", "assign_to": "timestamp", "type": "string"}], "label": null}, "args": ["T", "", ":", "", "-", ""], "type": "fun", "method": "replace", "label": null}, "type": "access", "subtype": "access_pos", "label": null}, "args": ["."], "type": "fun", "method": "split", "label": null}, "type": "access", "subtype": "access_pos", "label": null}, "args": ["+"], "type": "fun", "method": "split", "label": null}, "type": "access", "key": "timestamp", "label": null}], "type": "branch", "name": "", "label": null}, "args": [], "type": "fun", "method": "from_json", "label": null}, "conf": {"timestamp_len": 0, "encoding": "UTF8", "time_format": "yyyyMMddHHmmss", "timezone": 8, "output_field_name": "timestamp", "time_field_name": "timestamp"}}'  # noqa
CLOG_STORAGE_CONFIG = '{"analyzed_fields": ["log"], "doc_values_fields": [],  "json_fields": ["bcs_custom_labels"]}'  # noqa

# Metric 清洗规则
METRIC_CLEAN_FIELDS = [
    {
        "field_name": "labels",
        "field_alias": "labels",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 1
    },
    {
        "field_name": "metric_name",
        "field_alias": "metric_name",
        "field_type": "string",
        "is_dimension": False,
        "field_index": 2
    },
    {
        "field_name": "metric_value",
        "field_alias": "metric_value",
        "field_type": "double",
        "is_dimension": False,
        "field_index": 3
    }
]
METRIC_JSON_CONDIF = '{"extract": {"next": {"next": [{"subtype": "access_obj", "next": {"next": {"index": "0", "next": {"next": {"subtype": "assign_pos", "next": null, "type": "assign", "assign": [{"index": "0", "assign_to": "time", "type": "string"}], "label": null}, "args": [":", "", "T", "", "-", ""], "type": "fun", "method": "replace", "label": null}, "type": "access", "subtype": "access_pos", "label": null}, "args": ["."], "type": "fun", "method": "split", "label": null}, "type": "access", "key": "@timestamp", "label": null}, {"subtype": "access_obj", "next": {"subtype": "access_obj", "next": {"subtype": "access_obj", "next": {"next": {"next": [{"subtype": "assign_obj", "next": null, "type": "assign", "assign": [{"type": "string", "assign_to": "metric_name", "key": "key"}, {"type": "double", "assign_to": "metric_value", "key": "value"}], "label": null}, {"subtype": "assign_json", "next": null, "type": "assign", "assign": [{"type": "string", "assign_to": "labels", "key": "labels"}], "label": null}], "type": "branch", "name": "", "label": null}, "args": [], "type": "fun", "method": "iterate", "label": null}, "type": "access", "key": "metrics", "label": null}, "type": "access", "key": "collector", "label": null}, "type": "access", "key": "prometheus", "label": null}], "type": "branch", "name": "", "label": null}, "args": [], "type": "fun", "method": "from_json", "label": null}, "conf": {"timestamp_len": 0, "encoding": "UTF8", "time_format": "yyyyMMddHHmmss", "timezone": 0, "output_field_name": "timestamp", "time_field_name": "time"}}'  # noqa
METRIC_STORAGE_CONFIG = '{"analyzed_fields": [], "doc_values_fields": [], "json_fields": ["labels"]}'  # noqa


def deploy_plan(bk_username, bk_biz_id, data_name, data_type):
    """
    提交接入部署计划,获取dataid
    data_type: slog/clog/metric
    data_name: data_name/dataset(create_metric_data_id)
               '^[a-zA-Z][a-zA-Z0-9_]*$'，业务下唯一，长度限制了 15 个字符
    """
    description = ''
    if data_type == DataType.SLOG.value:
        description = "标准日志采集"
    elif data_type == DataType.CLOG.value:
        description = "非标准日志采集"
    elif data_type == DataType.METRIC.value:
        description = 'BCS metric'
    data = {
        'bk_app_code': settings.APP_ID,
        'bk_app_secret': settings.APP_TOKEN,
        'bk_username': bk_username,
        'bkdata_authentication_method': 'user',
        'data_scenario': 'log',
        'bk_biz_id': bk_biz_id,
        'description': description,
        'data_token': DATA_TOKEN,
        "access_raw_data": {
            'raw_data_alias': data_name,
            'raw_data_name': data_name,
            'maintainer': bk_username,
            'description': description,
            'data_category': 'online',
            'data_source': 'svr',
            'data_encoding': 'UTF-8',
            'sensitivity': 'private'
        },
    }
    resp = http_post(f'{DATA_API_V3_PREFIX}/access/deploy_plan/', json=data)
    if resp.get('result'):
        return True, resp.get('data', {}).get('raw_data_id')

    return False, resp.get('message')


def setup_clean(bk_username, bk_biz_id, raw_data_id, data_type):
    """
    创建清洗配置,并启动清洗任务
    """
    url = f'{DATA_API_V3_PREFIX}/databus/scenarios/setup_clean/'

    # result_table_name: 清洗配置英文标识。英文标识在业务下唯一，重复创建会报错
    # 唯一,小于15字符,符合正则'^[a-zA-Z][a-zA-Z0-9_]*$'
    result_table_name = '%s_%s' % (data_type[:4], int(time.time()))

    if data_type == DataType.SLOG.value:
        fields = SLOG_CLEAN_FIELDS
        json_config = SLOG_JSON_CONDIF
        description = "标准日志采集清洗任务"
    elif data_type == DataType.CLOG.value:
        fields = CLOG_CLEAN_FIELDS
        json_config = CLOG_JSON_CONDIF
        description = "非标准日志采集清洗任务"
    elif data_type == DataType.METRIC.value:
        fields = METRIC_CLEAN_FIELDS
        json_config = METRIC_JSON_CONDIF
        description = "BCS metric清洗任务"

    data = {
        "data_token": DATA_TOKEN,
        "raw_data_id": raw_data_id,
        "result_table_name": result_table_name,
        "result_table_name_alias": result_table_name,
        "bk_biz_id": bk_biz_id,
        "bk_username": bk_username,
        "description": description,
        "fields": fields,
        "json_config": json_config,
        "pe_config": "",
    }
    resp = http_post(url, json=data)
    if resp.get('result'):
        return True, resp.get('data', {}).get('result_table_id')

    return False, resp.get('message')


def setup_shipper(raw_data_id, result_table_id, data_type):
    """
    创建分发存储，并启动对应的分发任务
    dtEventTime、dtEventTimeStamp、localTime、timestamp
    """
    url = f'{DATA_API_V3_PREFIX}/databus/scenarios/setup_shipper/'

    if data_type == DataType.SLOG.value:
        storage_config = SLOG_STORAGE_CONFIG
    elif data_type == DataType.CLOG.value:
        storage_config = CLOG_STORAGE_CONFIG
    elif data_type == DataType.METRIC.value:
        storage_config = METRIC_STORAGE_CONFIG

    data = {
        "cluster_name": "es-test",  # ? 需要变更, 数据平台提供默认的
        "cluster_type": "eslog",  # eslog，这种是直接读取源数据写入es，支持json类型字段的
        "create_storage": True,
        "expire_days": 7,
        "raw_data_id": raw_data_id,
        "result_table_id": result_table_id,
        "storage_config": storage_config
    }
    resp = http_post(url, json=data)

    if resp.get('result'):
        return True, resp.get('data', {}).get('result_table_id')

    return False, resp.get('message')
