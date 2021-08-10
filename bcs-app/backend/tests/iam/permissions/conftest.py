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

from typing import List
from unittest import mock

import pytest

from backend.iam.permissions.apply_url import ApplyURLGenerator
from backend.iam.permissions.perm import ActionResourcesRequest
from backend.tests.testing_utils.base import generate_random_string


@pytest.fixture
def namespace_id():
    return generate_random_string(32)


@pytest.fixture
def template_id():
    """生成一个随机模板集 ID"""
    return generate_random_string(32)


def generate_apply_url(username: str, action_request_list: List[ActionResourcesRequest]) -> List[str]:
    expect = []
    for req in action_request_list:
        suffix = ''
        if req.resources:
            suffix = ''.join(req.resources)
        expect.append(f'{req.resource_type}{req.action_id}{suffix}')

    return expect


@pytest.fixture(autouse=True)
def patch_generate_apply_url():
    with mock.patch.object(ApplyURLGenerator, 'generate_apply_url', new=generate_apply_url):
        yield
