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
from typing import Dict

from backend.components.base import ComponentAuth

from .data import paas_cc_json


class FakeBCSCCMod:
    """A fake object for replacing the real components.paas_cc.PaaSCCClient module"""

    def __init__(self, access_token: ComponentAuth = None):
        pass

    def get_node_list(self, project_id: str, cluster_id: str, params: Dict = None) -> Dict:
        return paas_cc_json.fake_get_node_list_ok_resp
