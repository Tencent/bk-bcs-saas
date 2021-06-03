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

import yaml

from backend.dashboard.templates.constants import DEMO_RESOURCE_MANIFEST_DIR
from backend.utils.string import gen_random_str


def load_demo_manifest(resource_kind: str) -> Dict:
    """ 指定资源类型的 Demo 配置信息 """
    with open(f"{DEMO_RESOURCE_MANIFEST_DIR}/{resource_kind}.yaml") as fr:
        manifest = yaml.load(fr.read(), yaml.SafeLoader)

    # 避免名称重复，每次默认添加随机后缀
    manifest['metadata']['name'] = f"{manifest['metadata']['name']}-{gen_random_str()}"
    return manifest
