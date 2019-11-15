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
"""各版本差异常量定义
"""
import re
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

GUIDE_MESSAGE = [
    'Guide: https://docs.bk.tencent.com/bcs/',
    _('支持常用Bash快捷键; Windows下Ctrl-W为关闭窗口快捷键, 请使用Alt-W代替'),
]

MGR_GUIDE_MESSAGE = [
    'Guide: https://docs.bk.tencent.com/bcs/',
    _('支持常用Bash快捷键; Windows下Ctrl-W为关闭窗口快捷键, 请使用Alt-W代替; 使用Alt-Num切换Tab'),
]

# pod版本
KUBECTLD_VERSION = OrderedDict({
    '1.12.3_debian_0.1': [
        re.compile(r'^[vV]?1\.12\.\w+$'),
    ],
})

DEFAULT_KUBECTLD_VERSION = '1.12.3_debian_0.1'
