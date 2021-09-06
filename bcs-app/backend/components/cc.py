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
import functools
import logging
import re
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from django.conf import settings
from requests import PreparedRequest
from requests.auth import AuthBase

from backend.components.base import BaseHttpClient, BkApiClient, response_handler, update_request_body
from backend.components.utils import http_post
from backend.utils.async_run import async_run
from backend.utils.basic import getitems
from backend.utils.errcodes import ErrorCode

CC_HOST = settings.BK_PAAS_INNER_HOST
BK_APP_CODE = settings.APP_ID
BK_APP_SECRET = settings.APP_TOKEN
PREFIX_PATH = "/api/c/compapi"
# CC resource map
FUNCTION_PATH_MAP = {
    "get_application": "/v2/cc/search_business/",
    "search_host": "/v2/cc/search_host/",
    "list_biz_hosts": "/v2/cc/list_biz_hosts/",
}
# 默认开发商账号
DEFAULT_SUPPLIER_ACCOUNT = None
# 默认查询主机字段
DEFAULT_HOST_FIELDS = [
    "bk_bak_operator",
    "classify_level_name",
    "svr_device_class",
    "bk_svr_type_id",
    "svr_type_name",
    "hard_memo",
    "bk_host_id",
    "bk_host_name",
    "idc_name",
    "bk_idc_area",
    "bk_idc_area_id",
    "idc_id",
    "idc_unit_name",
    "idc_unit_id",
    "bk_host_innerip",
    "bk_comment",
    "module_name",
    "operator",
    "bk_os_name",
    "bk_os_version",
    "bk_host_outerip",
    "rack",
    "bk_cloud_id",
]
# CMDB 单个请求最大 Limit 限制
CMDB_MAX_LIMIT = 500

logger = logging.getLogger(__name__)


def cmdb_base_request(suffix_path, username, data, bk_supplier_account=None):
    """请求"""
    data.update({"bk_app_code": BK_APP_CODE, "bk_app_secret": BK_APP_SECRET, "bk_username": username})
    if bk_supplier_account:
        data["bk_supplier_account"] = bk_supplier_account

    return http_post(f"{CC_HOST}{PREFIX_PATH}{suffix_path}", json=data)


def get_application(username, bk_supplier_account=None):
    resp = get_all_application(username, bk_supplier_account=bk_supplier_account)
    data = resp.get("data") or []
    ret_data = {}
    for info in data:
        info["DisplayName"] = info["bk_biz_name"]
        ret_data[info["bk_biz_id"]] = info
    return ret_data


def get_app_by_user_role(username):
    """获取运维和产品角色中包含username的业务"""
    username_regex_info = "^{username},|,{username},|,{username}$|^{username}$".format(username=username)
    regex_map = {"$regex": username_regex_info}
    # NOTE: CMDB建议查询方式: 以admin用户身份跳过资源查询权限，然后CMDB接口根据传递的condition中用户，返回过滤的业务
    maintainers_resp = get_all_application("admin", condition={"bk_biz_maintainer": regex_map})
    # 组装数据
    if maintainers_resp.get("code") != ErrorCode.NoError:
        return []
    data = maintainers_resp.get("data") or []

    return [{"id": item["bk_biz_id"], "name": item["bk_biz_name"]} for item in data]


def get_application_name(username, bk_biz_id, bk_supplier_account=None):
    """通过项目ID获取到项目名称
    TODO: 后面看实际耗时，再考虑是否缓存
    """
    resp = get_application_with_pagination(
        username, bk_supplier_account=bk_supplier_account, fields=["bk_biz_name"], condition={"bk_biz_id": bk_biz_id}
    )
    if resp.get("code") != ErrorCode.NoError:
        return ""
    biz_info = (resp.get("data") or {}).get("info") or []
    if not biz_info:
        return ""
    return biz_info[0].get("bk_biz_name") or ""


def get_all_application(username, bk_supplier_account=None, condition=None, start=0, limit=200):
    """获取用户有权限的所有业务"""
    condition = condition or {}
    resp_data = {"data": [], "message": "", "code": ErrorCode.NoError}
    while True:
        resp = get_application_with_pagination(
            username, bk_supplier_account=bk_supplier_account, condition=condition, start=start, limit=limit
        )
        if resp.get("code") != ErrorCode.NoError:
            resp_data["code"] = resp.get("code")
            resp_data["message"] = resp.get("message")
            break
        data = resp.get("data") or {}
        biz_info = data.get("info") or []
        resp_data["data"].extend(biz_info)

        start = start + limit
        if start >= data.get("count", 0) or not biz_info:
            break

    return resp_data


def get_app_hosts(username, bk_biz_id, bk_supplier_account=None, bk_module_ids=None):
    resp = list_biz_hosts(username, bk_biz_id, bk_supplier_account=bk_supplier_account, bk_module_ids=bk_module_ids)
    if not resp.get("result"):
        return resp
    data = resp.get("data") or []
    if not data:
        return resp
    ret_data = []
    for host in data:
        if not host:
            continue
        host["InnerIP"] = host["bk_host_innerip"]
        host["HostName"] = host["bk_host_name"]
        ret_data.append(host)
    return {"result": True, "data": ret_data}


def get_host_by_operator(bk_biz_id, username, bk_supplier_account=None):
    """获取业务下主备负责人为username的机器"""
    resp = list_biz_hosts(username, bk_biz_id, bk_supplier_account=bk_supplier_account)
    if resp.get("code") != ErrorCode.NoError:
        return resp
    data = resp.get("data") or []
    host_list = []
    for host in data:
        if not host:
            continue
        operator = host.get("operator", "")
        bak_operator = host.get("bk_bak_operator", "")
        if (username == operator) or (username == bak_operator):
            host["InnerIP"] = host["bk_host_innerip"]
            host["HostName"] = host["bk_host_name"]
            host_list.append(host)

    return {"result": True, "data": host_list}


def get_app_maintainers(username, bk_biz_id, bk_supplier_account=None):
    """获取业务下的所有运维"""
    resp = get_application_with_pagination(
        username,
        bk_supplier_account=bk_supplier_account,
        fields=["bk_biz_maintainer"],
        condition={"bk_biz_id": bk_biz_id},
    )
    if resp.get("code") != ErrorCode.NoError:
        return []
    biz_info = (resp.get("data") or {}).get("info") or []
    if not biz_info:
        return []
    maintainers = biz_info[0].get("bk_biz_maintainer") or ""
    return re.findall(r"[^,;]+", maintainers)


def get_cc_hosts(bk_biz_id, username, bk_module_ids=None):
    """查询业务下有权限的主机"""
    all_maintainers = get_app_maintainers(username, bk_biz_id)
    if username in all_maintainers:
        return get_app_hosts(username, bk_biz_id, bk_module_ids=bk_module_ids)
    return get_host_by_operator(bk_biz_id, username)


def get_application_host(username, bk_biz_id, inner_ip, bk_supplier_account=None):
    """获取服务器信息
    注意: 其中信息包含了先前get_host_base_info获取到的信息
    """
    resp = list_biz_hosts(
        username,
        bk_biz_id,
        host_property_filter={
            "condition": "OR",
            "rules": [
                {"field": "bk_bak_operator", "operator": "equal", "value": username},
                {"filed": "operator", "operator": "equal", "value": "username"},
            ],
        },
        bk_supplier_account=bk_supplier_account,
    )
    if resp.get("code") != ErrorCode.NoError:
        return {}
    data = resp.get("data")
    if not data:
        return {}
    return data[0].get("host") or {}


def get_host_base_info(username, bk_biz_id, inner_ip):
    data = get_application_host(username, bk_biz_id, inner_ip)
    ret_data = {
        "Cpu": {"CpuNum": data.get("bk_cpu", 0)},
        "Disk": {"Total": data.get("bk_disk", 0) * 1024 * 1024 * 1024},
        "InnerIP": data.get("bk_host_innerip", ""),
        "HostID": data.get("bk_host_id", ""),
        "Memory": {"Total": data.get("bk_mem", 0) * 1024 * 1024},
        "System": {
            "OS": data.get("bk_os_name", ""),
            "kernelVersion": data.get("bk_os_version", ""),
            "clientDockerVersion": "",
            "serverDockerVersion": "",
        },
        "provider": "CMDB",
    }
    return ret_data


def get_application_with_pagination(
    username, bk_supplier_account=None, condition=None, fields=None, start=0, limit=200
):
    """分页查询业务"""
    condition = condition or {}
    fields = fields or []
    data = {"condition": condition, "fields": fields, "page": {"start": start, "limit": limit}}
    return cmdb_base_request(
        FUNCTION_PATH_MAP["get_application"], username, data, bk_supplier_account=bk_supplier_account
    )


def search_host(username, bk_biz_id, bk_supplier_account=None, ip=None, condition=None):
    """查询所有主机"""
    resp_data = {"data": [], "message": "", "code": ErrorCode.NoError, "result": True}
    # 设置初始值
    start, limit = 0, 200
    while True:
        resp = search_host_with_page(
            username,
            bk_biz_id,
            bk_supplier_account=bk_supplier_account,
            condition=condition,
            ip=ip,
            start=start,
            limit=limit,
        )
        start = start + limit
        if resp.get("code") != ErrorCode.NoError:
            resp_data["code"] = resp.get("code")
            resp_data["message"] = resp.get("message")
            resp_data["result"] = resp.get("result")
            break
        data = resp.get("data") or {}
        biz_info = data.get("info") or []
        resp_data["data"].extend(biz_info)
        if len(resp_data["data"]) >= data.get("count", 0) or not biz_info:
            break

    return resp_data


def search_host_with_page(username, bk_biz_id, bk_supplier_account=None, ip=None, condition=None, start=0, limit=200):
    """获取业务下的主机"""
    data = {"bk_biz_id": bk_biz_id}
    if ip:
        data["ip"] = ip
    if condition:
        data["condition"] = condition

    return cmdb_base_request(FUNCTION_PATH_MAP["search_host"], username, data, bk_supplier_account=bk_supplier_account)


def list_biz_hosts(
    username, bk_biz_id, host_property_filter=None, bk_module_ids=None, start=0, limit=200, bk_supplier_account=None
):
    """获取业务下所有主机信息"""
    resp_data = {"data": [], "message": "", "code": ErrorCode.NoError, "result": True}
    while True:
        resp = list_hosts_by_pagination(
            username,
            bk_biz_id,
            host_property_filter=host_property_filter,
            bk_module_ids=bk_module_ids,
            start=start,
            limit=limit,
            bk_supplier_account=bk_supplier_account,
        )
        if resp.get("code") != ErrorCode.NoError:
            resp_data.update({"code": resp.get("code"), "message": resp.get("message"), "result": resp.get("result")})
            break
        data = resp.get("data") or {}
        biz_info = data.get("info") or []
        resp_data["data"].extend(biz_info)
        # 对比机器数量，满足条件时终止请求
        start = start + limit
        if start >= data.get("count", 0) or not biz_info:
            break

    return resp_data


def list_hosts_by_pagination(
    username, bk_biz_id, host_property_filter=None, bk_module_ids=None, start=0, limit=200, bk_supplier_account=None
):
    """根据分页参数，获取业务下主机信息"""
    data = {"bk_biz_id": bk_biz_id, "page": {"start": start, "limit": limit}}
    # host_property_filter 主机组合属性查询条件
    data["host_property_filter"] = host_property_filter
    # bk_module_ids 模块ID列表
    data["bk_module_ids"] = bk_module_ids
    # 添加fields字段
    data["fields"] = deepcopy(DEFAULT_HOST_FIELDS)

    return cmdb_base_request(
        FUNCTION_PATH_MAP["list_biz_hosts"], username, data, bk_supplier_account=bk_supplier_account
    )


def search_biz_inst_topo(username, bk_biz_id) -> Dict:
    """
    查询业务拓扑

    :param username: 查询者用户名
    :param bk_biz_id: 业务 ID
    :return: 业务，集群，模块拓扑信息
    """
    return cmdb_base_request('/v2/cc/search_biz_inst_topo/', username, {'bk_biz_id': bk_biz_id})


def fetch_host_count_by_topo(username, bk_biz_id, bk_set_ids=None, bk_module_ids=None) -> int:
    """ 查询指定条件下主机数量，用于后续并发查询用 """
    params = {
        'bk_biz_id': bk_biz_id,
        'page': {
            'start': 0,
            'limit': 1,
        },
        'bk_set_ids': bk_set_ids,
        'bk_module_ids': bk_module_ids,
        'fields': ['bk_host_innerip'],
    }
    resp = cmdb_base_request('/v2/cc/list_biz_hosts/', username, params)
    return getitems(resp, 'data.count', 0)


def list_all_hosts_by_topo(username, bk_biz_id, bk_set_ids=None, bk_module_ids=None) -> Dict:
    """
    并发查询 CMDB，获取符合条件的全量主机信息，目前仅支持按 业务，集群，模块ID 过滤

    :param username: 查询者用户名
    :param bk_biz_id: 业务 ID
    :param bk_set_ids: 集群 ID 列表
    :parma bk_module_ids: 模块 ID 列表
    :return: 主机详情信息
    """
    total = fetch_host_count_by_topo(username, bk_biz_id, bk_set_ids, bk_module_ids)
    default_params = {
        'bk_biz_id': bk_biz_id,
        'bk_set_ids': bk_set_ids,
        'bk_module_ids': bk_module_ids,
        'fields': deepcopy(DEFAULT_HOST_FIELDS),
    }
    tasks = []
    resp_data = {'data': [], 'message': '', 'code': ErrorCode.NoError, 'result': True}
    for start in range(0, total, CMDB_MAX_LIMIT):
        params = deepcopy(default_params)
        params['page'] = {'start': start, 'limit': CMDB_MAX_LIMIT}
        # 组装并行任务配置信息
        tasks.append(functools.partial(cmdb_base_request, '/v2/cc/list_biz_hosts/', username, params))

    try:
        results = async_run(tasks)
    except Exception as e:
        resp_data.update({'code': ErrorCode.SysError, 'result': False, 'message': str(e)})
        return resp_data

    # 任何一次请求不成功，都是不成功
    for r in results:
        if r.ret['code'] != ErrorCode.NoError:
            resp_data.update({'code': r.ret['code'], 'result': False, 'message': r.ret['message']})
            return resp_data

    # 所有的请求结果合并，即为全量数据
    for r in results:
        resp_data['data'].extend(r.ret['data']['info'])
    return resp_data


class BkCCConfig:
    """蓝鲸配置平台配置信息，提供后续使用的host， url等"""

    def __init__(self, host: str):
        # 请求域名
        self.host = host

        # 请求地址
        self.search_biz_url = f"{host}/{PREFIX_PATH}/v2/cc/search_business/"


class BkCCAuth(AuthBase):
    """用于蓝鲸配置平台接口的鉴权校验"""

    def __init__(self, username: str, bk_supplier_account: Optional[str] = DEFAULT_SUPPLIER_ACCOUNT):
        self.bk_app_code = settings.BCS_APP_CODE
        self.bk_app_secret = settings.BCS_APP_SECRET
        self.operator = username
        self.bk_username = username
        self.bk_supplier_account = bk_supplier_account

    def __call__(self, r: PreparedRequest):
        data = {
            "bk_app_code": self.bk_app_code,
            "bk_app_secret": self.bk_app_secret,
            "bk_username": self.bk_username,
            "operator": self.operator,
        }
        if self.bk_supplier_account:
            data["bk_supplier_account"] = self.bk_supplier_account
        r.body = update_request_body(r.body, data)
        return r


@dataclass
class PageData:
    start: int = 0
    limit: int = 200
    sort: str = ""  # 排序字段


class BkCCClient(BkApiClient):
    def __init__(self, username: str, bk_supplier_account: Optional[str] = DEFAULT_SUPPLIER_ACCOUNT):
        self._config = BkCCConfig(host=settings.COMPONENT_HOST)
        self._client = BaseHttpClient(BkCCAuth(username, bk_supplier_account=bk_supplier_account))

    @response_handler(default_data={})
    def search_biz(self, page: PageData, fields: Optional[List] = None, condition: Optional[Dict] = None) -> Dict:
        """获取业务信息
        :param page: 分页条件
        :param fields: 返回的字段
        :param condition: 查询条件
        :returns: 返回业务信息，格式:{'count': 1, 'info': [{'id': 1}]}
        """
        url = self._config.search_biz_url
        data = asdict(page)
        data.update({"fields": fields, "condition": condition})
        return self._client.request_json("POST", url, json=data)


# 加载cc_ext的函数
try:
    from .cc_ext import *  # noqa
except ImportError as e:
    logger.debug("Load extension failed: %s", e)
