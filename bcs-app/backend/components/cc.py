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
import re

from django.conf import settings

from backend.components.utils import http_post
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes


CC_HOST = settings.BK_PAAS_HOST
BK_APP_CODE = settings.APP_ID
BK_APP_SECRET = settings.APP_TOKEN
PREFIX_PATH = '/api/c/compapi'
# CC resource map
FUNCTION_PATH_MAP = {
    'get_application': '/v2/cc/search_business/',
    'search_host': '/v2/cc/search_host/',
    'get_set': '/v2/cc/search_set/',
    'create_set': '/v2/cc/create_set/',
    'delete_set': '/v2/cc/delete_set/',
    'create_module': '/v2/cc/create_module/',
    'get_module': '/v2/cc/search_module/',
    'add_host_lock': '/v2/cc/add_host_lock',
    'delete_host_lock': '/v2/cc/delete_host_lock/',
    'search_host_lock': '/v2/cc/search_host_lock/'
}

SKIP_BIZ_NAME_LIST = ["蓝鲸"]


def get_application(username, bk_supplier_account=None):
    resp = get_all_application(username, bk_supplier_account=bk_supplier_account)
    data = resp.get('data') or []
    ret_data = {}
    for info in data:
        info['DisplayName'] = info['bk_biz_name']
        ret_data[info['bk_biz_id']] = info
    return ret_data


def get_app_by_user_role(username, bk_supplier_account=None):
    """获取运维和产品角色中包含username的业务
    """
    username_regex_info = '^{username},|,{username},|,{username}$|^{username}$'.format(username=username)
    regex_map = {'$regex': username_regex_info}
    maintainers_resp = get_all_application(
        username, bk_supplier_account=bk_supplier_account, condition={'bk_biz_maintainer': regex_map}
    )
    productor_resp = get_all_application(
        username, bk_supplier_account=bk_supplier_account, condition={'bk_biz_productor': regex_map}
    )
    # 组装数据
    if (maintainers_resp.get('code') != ErrorCode.NoError) or \
            (productor_resp.get('code') != ErrorCode.NoError):
        return {}
    data = maintainers_resp.get('data') or []
    data.extend(productor_resp.get('data') or [])
    return [
        {
            'id': item['bk_biz_id'],
            'name': item['bk_biz_name']
        }
        for item in data
        if item['bk_biz_name'] not in SKIP_BIZ_NAME_LIST
    ]


def get_application_name(username, bk_biz_id, bk_supplier_account=None):
    """通过项目ID获取到项目名称
    TODO: 后面看实际耗时，再考虑是否缓存
    """
    resp = get_application_with_page(
        username, bk_supplier_account=bk_supplier_account,
        fields=['bk_biz_name'], condition={'bk_biz_id': bk_biz_id}
    )
    if resp.get('code') != ErrorCode.NoError:
        return ''
    biz_info = (resp.get('data') or {}).get('info') or []
    if not biz_info:
        return ''
    return biz_info[0].get('bk_biz_name') or ''


def get_all_application(username, bk_supplier_account=None, condition={}):
    """获取用户有权限的所有业务
    """
    resp_data = {"data": [], 'message': '', 'code': ErrorCode.NoError}
    # 设置初始值
    start, limit = 0, 200
    while(True):
        resp = get_application_with_page(
            username, bk_supplier_account=bk_supplier_account,
            condition=condition, start=start, limit=limit
        )
        start = start + limit
        if resp.get('code') != ErrorCode.NoError:
            resp_data['code'] = resp.get('code')
            resp_data['message'] = resp.get('message')
            break
        data = resp.get('data') or {}
        biz_info = data.get('info') or []
        resp_data['data'].extend(biz_info)
        if len(resp_data['data']) >= data.get('count', 0) or not biz_info:
            break

    return resp_data


def get_app_hosts(username, bk_biz_id, bk_supplier_account=None):
    resp = search_host(
        username, bk_biz_id, bk_supplier_account=bk_supplier_account
    )
    if not resp.get('result'):
        return resp
    data = resp.get('data') or []
    if not data:
        return resp
    ret_data = []
    for info in data:
        host = info.get('host', {})
        if not host:
            continue
        host['InnerIP'] = host['bk_host_innerip']
        host['HostName'] = host['bk_host_name']
        ret_data.append(host)
    return {'result': True, 'data': ret_data}


def get_application_staff(username, bk_biz_id, fields=None):
    """获取业务的成员列表
    """
    if not fields:
        fields = ['bk_biz_developer', 'bk_biz_maintainer', 'bk_biz_tester', 'bk_biz_productor']
    resp = get_application_with_page(username, fields=fields, condition={'bk_biz_id': bk_biz_id})
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.CheckFailed.f('该项目关联的业务不正确，请确认后重试', replace=True)
    data = resp.get('data') or {}
    info = data.get('info') or []
    if not info:
        raise error_codes.CheckFailed.f('查询项目信息为空', replace=True)
    return info[0]


def get_host_by_operator(bk_biz_id, username, bk_supplier_account=None):
    """获取业务下主备负责人为username的机器
    """
    resp = search_host(username, bk_biz_id, bk_supplier_account=bk_supplier_account)
    if resp.get('code') != ErrorCode.NoError:
        return resp
    data = resp.get('data') or []
    host_list = []
    for ip_info in data:
        host = ip_info.get('host') or {}
        if not host:
            continue
        operator = host.get('operator', '')
        bak_operator = host.get('bk_bak_operator', '')
        if (username == operator) or (username == bak_operator):
            host['InnerIP'] = host['bk_host_innerip']
            host['HostName'] = host['bk_host_name']
            host_list.append(host)

    return {'result': True, 'data': host_list}


def get_app_maintainers(username, bk_biz_id, bk_supplier_account=None):
    """获取业务下的所有运维
    """
    resp = get_application_with_page(
        username, bk_supplier_account=bk_supplier_account,
        fields=['bk_biz_maintainer'], condition={'bk_biz_id': bk_biz_id}
    )
    if resp.get('code') != ErrorCode.NoError:
        return []
    biz_info = (resp.get('data') or {}).get('info') or []
    if not biz_info:
        return []
    maintainers = biz_info[0].get('bk_biz_maintainer') or ''
    return re.findall(r'[^,;]+', maintainers)


def get_cc_hosts(bk_biz_id, username):
    """查询业务下有权限的主机
    """
    all_maintainers = get_app_maintainers(username, bk_biz_id)
    if username in all_maintainers:
        return get_app_hosts(username, bk_biz_id)
    return get_host_by_operator(bk_biz_id, username)


def check_ips(bk_biz_id, username, req_ip_list):
    """检查用户是都有权限使用请求的IP
    """
    all_ip_info = get_cc_hosts(bk_biz_id, username)
    if not all_ip_info.get('result'):
        raise error_codes.APIError.f("用户[%s]没有权限使用主机" % username)
    perm_ip_list = []
    for info in all_ip_info.get('data') or []:
        inner_ip = info.get('bk_host_innerip', '')
        inner_ip_list = re.findall(r'[^;,]+', inner_ip)
        perm_ip_list.extend(inner_ip_list)

    diff_ip_list = set(req_ip_list) - set(perm_ip_list)
    if diff_ip_list:
        raise error_codes.CheckFailed.f("当前用户没有权限操作ip: %s" % ",".join(diff_ip_list))


def get_application_host(username, bk_biz_id, inner_ip, bk_supplier_account=None):
    """获取服务器信息
    注意: 其中信息包含了先前get_host_base_info获取到的信息
    """
    resp = search_host(
        username, bk_biz_id, bk_supplier_account=bk_supplier_account,
        condition=[{
            "bk_obj_id": "host",
            "condition": [{"field": "bk_host_innerip", "operator": "$eq", "value": inner_ip}]
        }]
    )
    if resp.get('code') != ErrorCode.NoError:
        return {}
    data = resp.get('data')
    if not data:
        return {}
    return data[0].get('host') or {}


def get_host_base_info(username, bk_biz_id, inner_ip):
    data = get_application_host(username, bk_biz_id, inner_ip)
    ret_data = {
        'Cpu': {
            'CpuNum': data.get('bk_cpu', 0)
        },
        'Disk': {
            'Total': data.get('bk_disk', 0) * 1024 * 1024 * 1024
        },
        'InnerIP': data.get('bk_host_innerip', ''),
        'HostID': data.get('bk_host_id', ''),
        'Memory': {
            'Total': data.get('bk_mem', 0) * 1024 * 1024
        },
        'System': {
            'OS': data.get('bk_os_name', ''),
            'kernelVersion': data.get('bk_os_version', ''),
            'clientDockerVersion': '',
            'serverDockerVersion': ''
        },
        'provider': 'CMDB'
    }
    return ret_data


def host_lock(username, ip_list, bk_cloud_id=0):
    """主机加锁
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['add_host_lock']
    )
    data = {'ip_list': ip_list}
    if bk_cloud_id:
        data['bk_cloud_id'] = bk_cloud_id
    return cmdb_base_request(url, username, data)


def remove_host_lock(username, ip_list, bk_cloud_id=0):
    """主机解锁
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['delete_host_lock']
    )
    data = {'ip_list': ip_list}
    if bk_cloud_id:
        data['bk_cloud_id'] = bk_cloud_id
    return cmdb_base_request(url, username, data)


def get_host_lock_status(username, ip_list, bk_cloud_id=0):
    """查询主机锁状态
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['search_host_lock']
    )
    data = {'ip_list': ip_list}
    if bk_cloud_id:
        data['bk_cloud_id'] = bk_cloud_id
    return cmdb_base_request(url, username, data)


def cc_set_instance(username, bk_biz_id, bk_set_name, bk_supplier_account=None):
    """实例化set
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['create_set']
    )
    # Set是在业务的层级下，所以bk_parent_id为业务ID
    data = {
        'bk_biz_id': bk_biz_id,
        'data': {
            'bk_parent_id': bk_biz_id,
            'bk_set_name': bk_set_name
        }
    }
    return cmdb_base_request(url, username, data, bk_supplier_account=bk_supplier_account)


def get_set_id(username, bk_biz_id, bk_set_name, bk_supplier_account=None):
    """查询set
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['get_set']
    )
    data = {
        'bk_biz_id': bk_biz_id,
        'condition': {'bk_set_name': bk_set_name},
        'fields': ['bk_set_id']
    }
    resp = cmdb_base_request(url, username, data, bk_supplier_account=bk_supplier_account)
    if resp.get('code') != ErrorCode.NoError:
        return None
    info = (resp.get('data') or {}).get('info') or []
    if not info:
        return None
    return info[0]['bk_set_id']


def delete_set(username, bk_biz_id, bk_set_id, bk_supplier_account=None):
    """删除set
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['delete_set']
    )
    # Set是在业务的层级下，所以bk_parent_id为业务ID
    data = {'bk_biz_id': bk_biz_id, 'bk_set_id': bk_set_id}
    return cmdb_base_request(url, username, data, bk_supplier_account=bk_supplier_account)


def cc_module_instance(username, bk_biz_id, bk_set_id, bk_module_name, bk_supplier_account=None):
    """实例化模块
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['create_module']
    )
    data = {
        'bk_biz_id': bk_biz_id,
        'bk_set_id': bk_set_id,
        'data': {
            'bk_parent_id': bk_set_id,
            'bk_module_name': bk_module_name
        }
    }
    return cmdb_base_request(url, username, data, bk_supplier_account=bk_supplier_account)


def search_set_module(username, bk_biz_id, bk_set_id, bk_module_name=None, bk_supplier_account=None):
    """查询set下module
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['get_module']
    )
    data = {
        'bk_biz_id': bk_biz_id,
        'bk_set_id': bk_set_id,
    }
    if bk_module_name:
        data['condition'] = {
            'bk_module_name': bk_module_name
        }
    return cmdb_base_request(url, username, data, bk_supplier_account=bk_supplier_account)


def get_application_with_page(username, bk_supplier_account=None, condition={}, fields=[], start=0, limit=200):
    """分页查询业务
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['get_application']
    )
    data = {
        'condition': condition,
        'fields': fields,
        'page': {
            'start': start,
            'limit': limit
        }
    }
    return cmdb_base_request(url, username, data, bk_supplier_account=bk_supplier_account)


def search_host(username, bk_biz_id, bk_supplier_account=None, ip=None, condition=None):
    """查询所有主机
    """
    resp_data = {"data": [], 'message': '', 'code': ErrorCode.NoError, 'result': True}
    # 设置初始值
    start, limit = 0, 200
    while(True):
        resp = search_host_with_page(
            username, bk_biz_id, bk_supplier_account=bk_supplier_account,
            condition=condition, ip=ip, start=start, limit=limit
        )
        start = start + limit
        if resp.get('code') != ErrorCode.NoError:
            resp_data['code'] = resp.get('code')
            resp_data['message'] = resp.get('message')
            resp_data['result'] = resp.get('result')
            break
        data = resp.get('data') or {}
        biz_info = data.get('info') or []
        resp_data['data'].extend(biz_info)
        if len(resp_data['data']) >= data.get('count', 0) or not biz_info:
            break

    return resp_data


def search_host_with_page(username, bk_biz_id, bk_supplier_account=None, ip=None, condition=None, start=0, limit=200):
    """获取业务下的主机
    """
    url = '{host}{prefix_path}{path}'.format(
        host=CC_HOST, prefix_path=PREFIX_PATH, path=FUNCTION_PATH_MAP['search_host']
    )
    data = {
        'bk_biz_id': bk_biz_id
    }
    if ip:
        data['ip'] = ip
    if condition:
        data['condition'] = condition

    return cmdb_base_request(url, username, data, bk_supplier_account=bk_supplier_account)


def cmdb_base_request(url, username, data, bk_supplier_account=None):
    """请求
    """
    data.update(
        {
            'bk_app_code': BK_APP_CODE,
            'bk_app_secret': BK_APP_SECRET,
            'bk_username': username
        }
    )
    if bk_supplier_account:
        data['bk_supplier_account'] = bk_supplier_account
    return http_post(url, json=data)
