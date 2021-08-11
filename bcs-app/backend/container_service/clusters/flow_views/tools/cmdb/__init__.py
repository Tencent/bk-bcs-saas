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
from backend.components import cc
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes


class CMDBClient:
    def __init__(self, request):
        self.request = request
        self.cc_app_id = request.project.cc_app_id
        self.username = request.user.username

    def get_cc_hosts(self):
        cc_host_info = cc.get_app_hosts(self.request.user.username, self.cc_app_id)
        if not cc_host_info.get("result"):
            raise error_codes.APIError(cc_host_info.get("message"))
        return cc_host_info.get("data") or []

    def get_cc_application_name(self):
        return cc.get_application_name(self.username, self.cc_app_id)

    def get_host_base_info(self, inner_ip):
        return cc.get_host_base_info(self.username, self.cc_app_id, inner_ip)
