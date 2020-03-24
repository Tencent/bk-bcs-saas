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
数据平台查询相关API
"""
import time
import json
import logging
from enum import Enum

from backend.components.utils import http_post
from .constant import DATA_API_V3_PREFIX, APP_CODE, APP_SECRET, IS_DATA_OPEN

logger = logging.getLogger(__name__)


def http_post_common(url, params=None, data=None, json=None, **kwargs):
    """
    封装标准的http请求方法
    """
    if IS_DATA_OPEN:
        return http_post(url, params=None, data=None, json=None, **kwargs)

    try:
        res = http_post(url, params=None, data=None, json=None, **kwargs)
    except Exception:
        # 没有开启数据平台功能，不跑出错误信息
        res = {
            "message": "",
            "data": None,
            "result": False
        }
    return res


# ################## get_data 相关方法封装 start  ############################
DEFAULT_SEARCH_SIZE = 100
API_URL = f'{DATA_API_V3_PREFIX}/dataquery/query/'

DockerMetricFields = {
    'cpu_summary': ['cpu_totalusage', 'id', 'container_name'],  # 使用率 cpu_totalusage
    'mem': ['rss', 'total', 'rss_pct', 'id', 'container_name'],  # 使用率 rss/total
    'disk': ['used_pct', 'device_name', 'container_name'],
    'net': ['rxbytes', 'txbytes', 'rxpackets', 'txpackets', 'container_name']
}

NodeMetricFields = {
    'cpu_summary': ['usage'],
    'mem': ['total', 'used'],
    'disk': ['in_use', 'device_name'],
    'net': ['speedSent', 'speedRecv', 'device_name'],
    'io': ['rkb_s', 'wkb_s', 'util', 'device_name']
}


class Ordering(Enum):
    # 降序排列
    DESC = 'DESC'
    # 升序排序
    ASC = 'ASE'


def get_docker_metrics(metric, app_id, contain_id, start_at=None, end_at=None, limit=None, order_by='desc'):
    """通过容器ID获取监控信息
    """

    now = int(time.time() * 1000)
    if not start_at:
        start_at = now - 12 * 3600 * 1000  # 时间单位是毫秒
    if not end_at:
        end_at = now

    field = ', '.join(DockerMetricFields[metric])
    _metric = '{app_id}_docker_{metric}'.format(app_id=app_id, metric=metric)
    sql = 'SELECT {field} FROM {metric} WHERE time > {start_at} AND time < {end_at}'
    sql = sql.format(field=field, metric=_metric, start_at=start_at, end_at=end_at)

    if isinstance(contain_id, list):
        sql += ' AND ( '
        sql += ' OR '.join('id = "{container_id}"'.format(container_id=i) for i in contain_id)
        sql += ' ) GROUP BY id'
    else:
        sql += ' AND id = "{contain_id}"'.format(contain_id=contain_id)

    # 网络暂时只能显示eth0
    if metric == 'net':
        sql += ' AND device_name = "eth0"'

    if order_by:
        sql += ' order by time {order_by}'.format(order_by=order_by)

    if not limit:
        limit = int((end_at - start_at) / 1000 / 60)
        # if isinstance(contain_id, list):
        #    limit *= len(contain_id)

    sql += ' LIMIT {limit}'.format(limit=limit)

    data = {
        "sql": sql,
        "app_code": APP_CODE,
        "bk_app_secret": APP_SECRET,
        "prefer_storage": ""
    }
    result = http_post_common(API_URL, json=data, timeout=60)
    # if not result.get('result'):
    #    raise error_codes.ComponentError.f(result.get('message', ''))
    data = result['data'] or {'list': []}
    return data


def get_metric_query(table, fields, app_id, start_at, end_at, delta, where=None, groupby=None, order_by='desc'):
    """数据平台裸接口,提供给metric使用
    """
    _metric = '{app_id}_{table}'.format(app_id=app_id, table=table)
    fields = ', '.join(fields)
    sql = 'SELECT {fields} FROM {metric} WHERE time > {start_at} AND time < {end_at}'
    sql = sql.format(fields=fields, metric=_metric, start_at=start_at, end_at=end_at)

    # add where
    if where:
        where = ' AND '.join('%s %s "%s"' % (i[0], i[2], i[1]) for i in where)
        sql += ' AND ' + where

    if groupby:
        groupby = ', '.join(groupby)
        sql += ' group by ' + groupby

    # add order
    sql += ' order by time {order_by}'.format(order_by=order_by)

    # add limit
    limit = int((end_at - start_at) / 1000 / delta)
    sql += ' LIMIT {limit}'.format(limit=limit)

    data = {
        "sql": sql,
        "bk_app_code": APP_CODE,
        "bk_app_secret": APP_SECRET,
        "prefer_storage": ""
    }
    result = http_post_common(API_URL, json=data, timeout=60)
    data = result['data'] or {'list': []}
    return data


def get_metric_query_agg(table, fields, app_id, start_at, end_at,
                         where=None, groupby=None, order_by='desc'):
    """数据平台裸接口,多次批量拉取
    """
    _metric = '{app_id}_{table}'.format(app_id=app_id, table=table)
    fields = ', '.join(fields)
    sql = 'SELECT {fields} FROM {metric} WHERE time > {start_at} AND time < {end_at}'
    sql = sql.format(fields=fields, metric=_metric, start_at=start_at, end_at=end_at)

    # add where
    if where:
        where = '( %s )' % where
        sql += ' AND ' + where

    if groupby:
        groupby = ', '.join(groupby)
        sql += ' GROUP BY ' + groupby

    # add order
    sql += ' order by time {order_by}'.format(order_by=order_by)

    data = {
        "bk_app_code": APP_CODE,
        "bk_app_secret": APP_SECRET,
        "prefer_storage": ""
    }
    search_data = []

    # add limit
    # limit = int((end_at - start_at) / 1000 / delta)
    # 切片查询，单次查询不超过1天的数据
    step = 15000
    start = 0
    end = start + step
    while True:
        data['sql'] = sql + ' LIMIT {start},{end}'.format(start=start, end=end)
        result = http_post_common(API_URL, json=data, timeout=60)
        try:
            result = result['data']['list']
            search_data.extend(result)
        except Exception:
            result = []
        if len(result) < step:
            break
        start += step
        end += step
    return {'list': search_data}


def get_node_metrics(metric, app_id, ip, start_at=None, end_at=None, limit=None, order_by='desc'):
    """节点监控
    """

    now = int(time.time() * 1000)
    if not start_at:
        start_at = now - 12 * 3600 * 1000  # 时间单位是毫秒
    if not end_at:
        end_at = now

    field = ', '.join(NodeMetricFields[metric])
    _metric = '{app_id}_system_{metric}'.format(app_id=app_id, metric=metric)
    sql = 'SELECT {field} FROM {metric} WHERE ip = "{ip}" AND time > {start_at} AND time < {end_at}'
    sql = sql.format(field=field, metric=_metric, ip=ip,
                     start_at=start_at, end_at=end_at)

    # 网络暂时只能显示eth0
    if metric == 'net':
        sql += ' AND device_name = "eth1"'

    if order_by:
        sql += ' order by time {order_by}'.format(order_by=order_by)

    if not limit:
        limit = int((end_at - start_at) / 1000 / 60)

    sql += ' LIMIT {limit}'.format(limit=limit)

    data = {
        "sql": sql,
        "bk_app_code": APP_CODE,
        "bk_app_secret": APP_SECRET,
        "prefer_storage": ""
    }

    result = http_post_common(API_URL, json=data, timeout=60)
    # if not result.get('result'):
    #    raise error_codes.ComponentError.f(result.get('message', ''))
    data = result.get('data') or {'list': []}
    return data


def get_node_metrics_order(metric, app_id, ip, start_at=None, end_at=None, limit=1, order_by=Ordering.DESC):
    """节点总体排序使用
    ASC 升序排序
    DESC 降序排列
    """
    now = int(time.time() * 1000)
    if not start_at:
        start_at = now - 60 * 60 * 1000  # 时间单位是毫秒
    if not end_at:
        end_at = now

    field = ', '.join(NodeMetricFields[metric])
    _metric = '{app_id}_system_{metric}'.format(app_id=app_id, metric=metric)
    if not isinstance(ip, list):
        ip = [ip]
    sql = 'SELECT {field} FROM {metric} WHERE'
    ip_filter_sql = ' OR '.join(" ip = '{ip}'".format(ip=i) for i in ip)
    sql += ' ( {ip_filter} ) '.format(ip_filter=ip_filter_sql)
    sql += 'AND time > {start_at} AND time < {end_at} GROUP BY ip'
    sql = sql.format(field=field, metric=_metric, ip=ip,
                     start_at=start_at, end_at=end_at)

    # 网络暂时只能显示eth0
    if metric == 'net':
        sql += ' AND device_name = "eth0"'

    if order_by:
        sql += ' order by time {order_by}'.format(order_by=order_by.value)

    if not limit:
        limit = int((end_at - start_at) / 1000 / 60)

    sql += ' LIMIT {limit}'.format(limit=limit)

    data = {
        "sql": sql,
        "bk_app_code": APP_CODE,
        "bk_app_secret": APP_SECRET,
        "prefer_storage": ""
    }

    result = http_post_common(API_URL, json=data, timeout=60)
    # if not result.get('result'):
    #    raise error_codes.ComponentError.f(result.get('message', ''))
    data = result.get('data') or {'list': []}
    return data


def get_container_logs(username, container_id=None, index=None):
    """查询容器日志
    """
    sql_payload = {
        "body": {
            "sort": [
                {
                    "dtEventTimeStamp": {"order": "desc"}
                }
            ],
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": "*",
                                "analyze_wildcard": True,
                            }
                        },
                        {
                            "term": {
                                "container_id": container_id
                            }
                        }
                    ],
                },
            },
            "from": 0,
            "size": DEFAULT_SEARCH_SIZE
        },
        "index": index,
        "doc_type": "1"
    }

    data = {'sql': json.dumps(sql_payload), 'bk_app_code': APP_CODE,
            'bk_app_secret': APP_SECRET, 'prefer_storage': 'es'}
    result = http_post_common(API_URL, json=data, timeout=60)
    return result


def get_es_log(index='591_etl_paas_docker_stdout_*', start_at=None, end_at=None):
    """获取容器日志
    """
    now = int(time.time() * 1000)
    if not start_at:
        start_at = now - 12 * 3600 * 1000  # 时间单位是毫秒
    if not end_at:
        end_at = now

    sql_payload = {"body": {"sort": [{
        "dtEventTimeStamp": {"order": "desc"}}],
        "query": {"bool": {"filter": [{"range": {"dtEventTimeStamp": {
            "gte": start_at, "lte": end_at, "format": "epoch_millis"}}}], "must": [
            {"query_string": {"query": "*",
                              "analyze_wildcard": True}}]}}, "from": 0, "size": 20},
        "index": index, "doc_type": "1"}

    data = {'sql': json.dumps(sql_payload), 'bk_app_code': APP_CODE,
            'bk_app_secret': APP_SECRET, 'prefer_storage': 'es'}
    result = http_post_common(API_URL, json=data, timeout=60)
    return result


def get_es_mapping(index_name):
    """获取ES的mapping
    """
    data = {
        'bk_app_code': APP_CODE,
        'bk_app_secret': APP_SECRET,
        'prefer_storage': 'es'
    }
    sql = {'index': index_name, 'mapping': True, 'doc_type': 1}
    data['sql'] = json.dumps(sql)
    return http_post_common(API_URL, json=data)


def get_es_data(sql):
    """获取ES日志数据，监控使用
    """
    data = {
        'bk_app_code': APP_CODE,
        'bk_app_secret': APP_SECRET,
        'prefer_storage': 'es'
    }
    data['sql'] = json.dumps(sql)
    return http_post(API_URL, json=data)


def get_data(sql):
    """获取数据平台
    """
    data = {
        "sql": sql,
        "bk_app_code": APP_CODE,
        "bk_app_secret": APP_SECRET,
        "prefer_storage": ""
    }
    result = http_post_common(API_URL, json=data, timeout=60)
    data = result['data'] or {'list': []}
    return data

# ################## get_data 相关方法封装 end  ############################
