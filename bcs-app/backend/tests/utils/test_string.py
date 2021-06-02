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

from backend.utils.string import decapitalize, gen_random_str


@pytest.mark.parametrize(
    'source, expired',
    [
        ('', ''),
        ('   ', '   '),
        ('True', 'true'),
        ('TrUe', 'trUe'),
        ('TRUE', 'tRUE'),
        ('true', 'true'),
        (' true', ' true'),
        (' True', ' True'),
    ],
)
def test_decapitalize(source, expired):
    assert decapitalize(source) == expired


def test_gen_random_str():
    """ 测试随机生成字符串 """

    # 指定长度不在支持的范围内的情况
    with pytest.raises(ValueError):
        gen_random_str(0)

    with pytest.raises(ValueError):
        gen_random_str(-5)

    with pytest.raises(ValueError):
        gen_random_str(48)

    # 默认情况（8位）
    ret = gen_random_str()
    assert len(ret) == 8

    ret = gen_random_str(1)
    assert len(ret) == 1

    ret = gen_random_str(32)
    assert len(ret) == 32
