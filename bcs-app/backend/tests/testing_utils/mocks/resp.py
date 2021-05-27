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


class MockRetrieveApiRespBuilder:
    """ Mock 用详情请求结果构造器 """

    def __init__(self, *args, **kwargs):
        """ 构造器初始化 """
        pass

    def build(self) -> Dict:
        """ 构造 Mock 用响应内容 """
        return {
            'manifest': {},
            'manifest_ext': {},
        }
