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
from requests_mock import ANY

from backend.components.cc import BkCCClient, PageData

fake_biz_id = 1
fake_bs2_id = 1


class TestBkCCClient:
    def test_search_biz(self, request_user, requests_mock):
        requests_mock.post(
            ANY, json={"code": 0, "data": {"count": 1, "info": [{"bs2_name_id": fake_bs2_id, "default": 0}]}}
        )
        page = PageData()
        client = BkCCClient(request_user.username)
        data = client.search_biz(page, ["bs2_name_id"], {"bk_biz_id": fake_biz_id})
        assert data["info"][0]["bs2_name_id"] == fake_bs2_id
        assert requests_mock.called
