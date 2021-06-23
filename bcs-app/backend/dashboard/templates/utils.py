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
import json
from typing import Dict

import yaml

from backend.dashboard.templates.constants import DEMO_RESOURCE_MANIFEST_DIR, TEMPLATE_CONFIG_DIR
from backend.utils.string import gen_random_str


def load_resource_template(kind: str) -> Dict:
    """ 获取指定 资源类型模版 信息 """
    with open(f'{TEMPLATE_CONFIG_DIR}/{kind}.json') as fr:
        return json.loads(fr.read())


def load_demo_manifest(file_path: str) -> Dict:
    """ 指定资源类型的 Demo 配置信息 """
    with open(f'{DEMO_RESOURCE_MANIFEST_DIR}/{file_path}.yaml') as fr:
        manifest = yaml.load(fr.read(), yaml.SafeLoader)

    # 避免名称重复，每次默认添加随机后缀
    new_resource_name = f"{manifest['metadata']['name']}-{gen_random_str()}"
    manifest['metadata']['name'] = new_resource_name
    # 对于 Deployment, DaemonSet, StatefulSet 需要更新默认的 selector.matchLabels 信息，防止发生冲突
    manifest['spec']['selector']['matchLabels'].update({'owner': new_resource_name})
    manifest['spec']['template']['metadata']['labels'].update({'owner': new_resource_name})
    return manifest
