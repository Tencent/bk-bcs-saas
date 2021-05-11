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

# 没有指定时间范围的情况下，默认获取一小时的数据
METRICS_DEFAULT_TIMEDELTA = 3600

# 默认查询的命名空间（所有）
METRICS_DEFAULT_NAMESPACE = '.*'

# 默认查询POD下所有的容器
METRICS_DEFAULT_CONTAINER_LIST = [".*"]
