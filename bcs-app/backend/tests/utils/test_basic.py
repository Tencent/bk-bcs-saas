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
import pytest

from backend.utils.basic import str2bool


@pytest.mark.parametrize(
    "source, value",
    [
        ("true", True),
        ("True", True),
        ("1", True),
        ("0", False),
        ("false", False),
        ("False", False)
    ]
)
def test_str2bool_success(source, value):
    assert str2bool(source) == value


@pytest.mark.parametrize(
    "source", [("2")]
)
def test_str2bool_valueerror(source):
    with pytest.raises(ValueError):
        str2bool(source)


@pytest.mark.parametrize(
    "source", [(1), (None)]
)
def test_str2bool_typeerror(source):
    with pytest.raises(ValueError):
        str2bool(source)
