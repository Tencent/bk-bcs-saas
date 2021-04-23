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
import base64
import gzip
import json
from typing import Dict, List, Union

from kubernetes.dynamic.resource import ResourceInstance

from backend.resources.utils.format import ResourceDefaultFormatter
from backend.utils.basic import getitems


class ReleaseSecretFormatter(ResourceDefaultFormatter):
    def format_dict(self, resource_dict: Dict) -> Dict:
        release_data = getitems(resource_dict, "data.data.release", "")
        if not release_data:
            return {}
        # 解析release data
        release_data = self.parse_release_data(release_data)
        # 组装release列表数据，包含release的基本信息、chart信息等

    def parse_release_data(self, release_data: bytes) -> Dict:
        """解析release data
        解析release data数据，需要两次 base64，然后 gzip 解压，最后json处理
        ref: https://faun.pub/decoding-a-helm-chart-releases-53fce6bffbfb
        """
        # 两次base64解码
        release_data = base64.b64decode(base64.b64decode(release_data))
        # gzip解压
        release_data = gzip.decompress(release_data).decode("utf8")
        # json处理
        return json.loads(release_data)

    def refine_data(self, release_data: Dict) -> Dict:
        data = {
            "name": "",
            "namespace": "",
            "chart_name": "",
            "created": "",
            "updated": "",
            "creator": "",
            "current_version": "",
            "enable_helm": True,
        }
