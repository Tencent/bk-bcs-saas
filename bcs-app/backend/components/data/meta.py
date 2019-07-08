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
数据平台元数据相关API
"""
import logging
import json

from backend.utils import cache
from backend.components.utils import http_get
from .constant import DATA_API_V3_PREFIX, APP_CODE, APP_SECRET


logger = logging.getLogger(__name__)

DATA_API_STAGE = 'prod'


def tsdb_list_fields(cc_app_id, table_name):
    """获取列表
    """
    result_table_id = '{app_id}_{table_name}'.format(app_id=cc_app_id, table_name=table_name)
    return tsdb_list_fields_by_id(result_table_id)


def tsdb_list_fields_by_id(result_table_id):
    """
    字段对应关系
    field (老) - field_name （新）
    type (老) - field_type (新)
    """
    url = f'{DATA_API_V3_PREFIX}/meta/result_tables/{result_table_id}/fields/'
    payload = {
        'bk_app_code': APP_CODE,
        'bk_app_secret': APP_SECRET,
    }
    resp = http_get(url, params=payload)
    # 处理数据，保持兼容老API格式
    data = resp.get('data') or []
    for _d in data:
        _d['field'] = _d.get('field_name')
        _d['type'] = _d.get('field_type')
    return resp


def get_result_table(resutl_table_id, stage=DATA_API_STAGE):
    """查询结果表的详细信息
    该API暂未使用
    """
    url = f'{DATA_API_V3_PREFIX}/meta/result_tables/{resutl_table_id}/'
    params = {
        "bk_app_code": APP_CODE,
        "bk_app_secret": APP_SECRET,
        "includes_children": False
    }
    resp = http_get(url, params=params)
    if resp.get('result'):
        return True, resp.get('data')

    # 记录错误日志
    logger.error(u"data api error: %s\nurl:%s\ndata:%s", resp.get('message'), url, json.dumps(params))
    return False, {}


@cache.region.cache_on_arguments(expiration_time=600)
def get_result_table_detail_by_biz(cc_app_id, stage=DATA_API_STAGE):
    url = f'{DATA_API_V3_PREFIX}/meta/result_tables/'
    params = {
        'bk_app_code': APP_CODE,
        'bk_app_secret': APP_SECRET,
        "bk_biz_id": cc_app_id,
        'related': 'storages',
    }
    resp = http_get(url, params=params)
    # 处理数据，保持兼容老API格式
    data = resp.get('data') or []
    for _d in data:
        _d['id'] = _d.get('result_table_id')
    return resp


def get_es_index(cc_app_id):
    """获取ES索引列表
    """
    url = f'{DATA_API_V3_PREFIX}/meta/result_tables/'

    params = {
        'bk_bk_app_code': APP_CODE,
        'bk_app_secret': APP_SECRET,
        'bk_biz_id': cc_app_id,
        'related': 'storages',
        'related_filter': '{"type": "storages" ,"attr_name": "common_cluster.cluster_type","attr_value": "es"}'
    }
    resp = http_get(url, params=params)
    # 处理数据，保持兼容老API格式
    data = resp.get('data') or []
    for _d in data:
        _d['table_name'] = _d.get('result_table_name')
    return resp
