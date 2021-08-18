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

from backend.utils.basic import get_with_placeholder, getitems, md5, str2bool


@pytest.mark.parametrize(
    "source, value",
    [
        ("true", True),
        ("True", True),
        ("1", True),
        (1, True),
        ("0", False),
        ("false", False),
        ("False", False),
        (0, False),
        (2, False),
        ("2", False),
        (None, False),
    ],
)
def test_str2bool(source, value):
    assert str2bool(source) == value


# 用于测试的 Dict 结构数据
DICT_OBJ = {
    'a': ['a1', 'a2', 'a3'],
    'b': {
        'b1': 'b11',
        'b2': {'b21'},
        'b3': {
            'b31': 'b311',
            'b32': 'b321',
        },
        'b4': ('b41', 'b42'),
    },
    'c': 'c1',
}


@pytest.mark.parametrize(
    'items, expected, default',
    [
        ('a', ['a1', 'a2', 'a3'], None),
        (['a'], ['a1', 'a2', 'a3'], None),
        ('b.b1', 'b11', None),
        (['b', 'b1'], 'b11', None),
        ('b.b2', {'b21'}, None),
        ('b.b3.b31', 'b311', None),
        (['b', 'b3', 'b32'], 'b321', None),
        ('b.b5', None, None),
        ('b.b4.b41', None, None),
        ('b.b4.b42', '--', '--'),
    ],
)
def test_getitems(items, expected, default):
    assert getitems(DICT_OBJ, items, default) == expected


@pytest.mark.parametrize(
    'items, expected',
    [
        ('a', ['a1', 'a2', 'a3']),
        (['a'], ['a1', 'a2', 'a3']),
        ('b.b1', 'b11'),
        (['b', 'b1'], 'b11'),
        ('b.b2', {'b21'}),
        ('b.b3.b31', 'b311'),
        (['b', 'b3', 'b32'], 'b321'),
        ('b.b5', '--'),
        ('b.b4.b41', '--'),
        ('b.b4.b42', '--'),
    ],
)
def test_get_with_placeholder(items, expected):
    assert get_with_placeholder(DICT_OBJ, items) == expected


@pytest.mark.parametrize(
    'content, expected',
    [
        ('BCS-K8S-40000:test-default', '7f63b7f479c97c3c3a49863e974557ca'),
        ('abc' * 30, 'daa54284568d250dde2cc8578c2e116a'),
    ],
)
def test_md5(content, expected):
    assert md5(content) == expected
