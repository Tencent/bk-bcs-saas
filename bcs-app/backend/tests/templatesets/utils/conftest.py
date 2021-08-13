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
import pytest


# todo  待优化 和iam/open_apis/conftest中数据重复
@pytest.fixture()
def template_data(fake_project_id, fake_templateset_ids):
    template_data = [
        {"id": fake_templateset_ids[0], "project_id": fake_project_id, "name": "templateset_0001"},
        {"id": fake_templateset_ids[1], "project_id": fake_project_id, "name": "templateset_0002"},
    ]
    return template_data


@pytest.fixture
def fake_project_id():
    return "project_code_0001"


@pytest.fixture
def fake_templateset_ids():
    return [1, 2]
