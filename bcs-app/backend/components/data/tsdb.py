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
数据平台 tsdb API
基础性能数据走 Prometheus ，不再依赖数据平该API
"""
import json

from backend.components.utils import http_get

from .constants import APP_CODE, APP_SECRET, DATA_API_V3_PREFIX


def check_tsdb_exist(biz_id=0, db="system"):
    return True


def deploy_tsdb(biz_id=0, db="system"):
    return {"result": False, "message": "", "data": None}


def tsdb_list_tables(cc_app_id, prefix='bcs'):
    """
    获取表列表，监控使用
    prefix: system|docker|bcs
    """

    url = f'{DATA_API_V3_PREFIX}/storekit/tsdb/list_tables/'
    db_name = '{prefix}_{app_id}'.format(prefix=prefix, app_id=cc_app_id)
    payload = {
        'db_name': db_name,
        'bk_app_code': APP_CODE,
        'bk_app_secret': APP_SECRET,
    }
    return http_get(url, params=payload)


def tsdb_show_tag_value(cc_app_id, table_name, tag_key, conditions=None):
    """获取维度字段值"""
    result_table_id = '{app_id}_{table_name}'.format(app_id=cc_app_id, table_name=table_name)

    return get_tsdb_show_tag_value(result_table_id, tag_key, conditions)


def get_tsdb_show_tag_value(result_table_id, tag_key, conditions=None):
    """获取维度字段值"""
    url = f'{DATA_API_V3_PREFIX}/storekit/tsdb/show_tag_values/'
    payload = {
        'bk_app_code': APP_CODE,
        'bk_app_secret': APP_SECRET,
        'result_table_id': result_table_id,
        'tag_key': tag_key,
    }
    # 过滤条件
    if conditions:
        payload['filter_conditions'] = json.dumps(conditions)

    return http_get(url, params=payload)
