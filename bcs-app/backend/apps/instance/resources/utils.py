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
import re

from django.utils.translation import ugettext_lazy as _

from backend.utils.error_codes import error_codes
from backend.apps.configuration.constants import NUM_VAR_PATTERN

REAL_NUM_VAR_PATTERN = re.compile(r"%s" % NUM_VAR_PATTERN)


def is_rate_number(var):
    try:
        if var[-1] != '%':
            return False
        int(var[:-1])
    except Exception:
        return False
    return True


def handle_number_var(var, name, is_preview, is_validate=True):
    if isinstance(var, int) or isinstance(var, float):
        return var

    if is_rate_number(var):
        return var

    # 与前端的约定: 预览模式下数字变量增加"|toInt"标记，表示前端需要将该值显示成数字
    if is_preview:
        if REAL_NUM_VAR_PATTERN.match(var):
            return var.replace("}}", "|toInt}}")
    try:
        var = int(var)
    except Exception:
        if is_validate:
            raise error_codes.ValidateError(_("{} 的值[{}]不是一个有效数字").format(name, var))
    return var
