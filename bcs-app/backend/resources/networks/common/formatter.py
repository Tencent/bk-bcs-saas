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
from copy import deepcopy
from typing import Dict

from backend.resources.utils.common import calculate_age
from backend.resources.utils.format import ResourceDefaultFormatter


class NetworkFormatter(ResourceDefaultFormatter):
    """ 网络类 资源通用格式化器 """

    def format_common_dict(self, resource_dict: Dict) -> Dict:
        metadata = deepcopy(resource_dict['metadata'])
        self.set_metadata_null_values(metadata)

        create_time, update_time = self.parse_create_update_time(metadata)
        return {'age': calculate_age(create_time), 'createTime': create_time, 'updateTime': update_time}
