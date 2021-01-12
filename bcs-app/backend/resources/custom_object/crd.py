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
from backend.resources.utils.kube_client import get_dynamic_client

from .format import CRDFormatter


class CustomResourceDefinition:
    def __init__(self, access_token: str, project_id: str, cluster_id: str):
        self.dynamic_client = get_dynamic_client(access_token, project_id, cluster_id)
        self.api = self.dynamic_client.get_preferred_resource("CustomResourceDefinition")
        self.formatter = CRDFormatter()

    def list(self, is_format: bool = False, **kwargs):
        resp = self.api.get_or_none(**kwargs)
        if is_format:
            return self.formatter.format_list(resp)
        return resp

    def get(self, name, is_format: bool = False, **kwargs):
        resp = self.api.get_or_none(name=name, **kwargs)
        if is_format:
            return self.formatter.format(resp)
        return resp
