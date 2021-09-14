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
from typing import Dict, List, Optional

from backend.components.cc import PageData


class FakeBkCCClient:
    def __init__(self, *args, **kwargs):
        pass

    def search_biz(self, page: PageData, fields: Optional[List] = None, condition: Optional[Dict] = None) -> Dict:
        return {
            "count": 1,
            "info": [
                {
                    "bs2_name_id": 1,
                    "bk_oper_plan": "admin",
                    "bk_biz_developer": "admin",
                    "bk_biz_maintainer": "admin",
                    "bk_dept_name_id": 1,
                    "bk_biz_name": "demo",
                    "bk_product_name": "demo",
                    "default": 0,
                }
            ],
        }
