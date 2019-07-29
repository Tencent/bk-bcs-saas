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
from backend.apps.instance.resources import BCSResource


class Pod(BCSResource):
    def set_resources(self, resources):
        limits = resources.get('limits') or {}
        limits['cpu'] = str(limits.get('cpu') or '')
        limits['memory'] = str(limits.get('memory') or '')

        requests = resources.get('requests') or {}
        requests['cpu'] = str(requests.get('cpu') or '')
        requests['memory'] = str(requests.get('memory') or '')
