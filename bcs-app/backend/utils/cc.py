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

from django.utils.translation import ugettext_lazy as _

from backend.components import cc as cmdb
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes


def get_application_staff(username, bk_biz_id, fields=None):
    """获取业务的成员列表
    """
    if not fields:
        fields = ['bk_biz_developer', 'bk_biz_maintainer', 'bk_biz_tester', 'bk_biz_productor']
    resp = cmdb.get_application_with_page(username, fields=fields, condition={'bk_biz_id': bk_biz_id})
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.CheckFailed(_('该项目关联的业务不正确，请确认后重试'))
    data = resp.get('data') or {}
    info = data.get('info') or []
    if not info:
        raise error_codes.CheckFailed(_('查询项目信息为空'))
    return info[0]


def get_host_by_operator(bk_biz_id, username, bk_supplier_account=None):
    """获取业务下主备负责人为username的机器
    """
    resp = cmdb.search_host(username, bk_biz_id, bk_supplier_account=bk_supplier_account)
    if not resp.get('result'):
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


def get_app_hosts(username, bk_biz_id, bk_supplier_account=None):
    resp = cmdb.search_host(
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


def get_app_maintainers(username, bk_biz_id, bk_supplier_account=None):
    """获取业务下的所有运维
    """
    resp = cmdb.get_application_with_page(
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
        raise error_codes.APIError(_('用户{username}没有权限使用主机').format(username=username))
    perm_ip_list = []
    for info in all_ip_info.get('data') or []:
        inner_ip = info.get('bk_host_innerip', '')
        inner_ip_list = re.findall(r'[^;,]+', inner_ip)
        perm_ip_list.extend(inner_ip_list)

    diff_ip_list = set(req_ip_list) - set(perm_ip_list)
    if diff_ip_list:
        raise error_codes.CheckFailed(_('当前用户没有权限操作ip:{ip_list}').format(ip_list=','.join(diff_ip_list)))
