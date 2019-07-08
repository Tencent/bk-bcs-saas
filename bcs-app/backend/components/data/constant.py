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

from django.conf import settings


# 是否开启数据平台功能
IS_DATA_OPEN = False

# 接入ESB后，走ESB访问，确认访问路径
DATA_API_V3_PREFIX = f'{settings.BK_PAAS_HOST}/api/c/compapi/data/v3'
# 测试阶段，绕过用户登录态验证
DATA_TOKEN = ''

APP_CODE = settings.APP_ID
APP_SECRET = settings.APP_TOKEN
