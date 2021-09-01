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
from typing import Dict

from backend.components import cc
from backend.utils.basic import getitems
from backend.utils.error_codes import error_codes


class CMDBClient:
    def __init__(self, request):
        self.request = request
        self.cc_app_id = request.project.cc_app_id
        self.username = request.user.username

    def get_cc_hosts(self, bk_module_ids=None):
        resp = cc.get_app_hosts(self.request.user.username, self.cc_app_id, bk_module_ids)
        if not resp.get("result"):
            raise error_codes.APIError(resp.get("message"))
        return resp.get("data") or []

    def get_cc_application_name(self):
        return cc.get_application_name(self.username, self.cc_app_id)

    def get_host_base_info(self, inner_ip):
        return cc.get_host_base_info(self.username, self.cc_app_id, inner_ip)

    def get_idle_module_info(self) -> Dict:
        """ 获取空闲机模块信息 """
        resp = cc.get_biz_internal_module(self.request.user.username, self.cc_app_id)
        if not resp.get("result"):
            raise error_codes.APIError(resp.get("message"))
        for module in getitems(resp, 'data.module', []):
            # 空闲机模块 default 值为 1
            if module.get('default') == 1:
                return module
        return {}
