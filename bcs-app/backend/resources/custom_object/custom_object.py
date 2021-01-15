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
from typing import Optional

from ..resource import ResourceClient
from .format import CustomObjectFormatter
from .crd import CustomResourceDefinition


class CustomObject(ResourceClient):
    formatter = CustomObjectFormatter()

    def __init__(
        self, access_token: str, project_id: str, cluster_id: str, kind: str, api_version: Optional[str] = None
    ):
        self.kind = kind
        super().__init__(access_token, project_id, cluster_id, api_version)


def get_custom_object_api_by_crd(access_token: str, project_id: str, cluster_id: str, crd_name: str) -> CustomObject:
    crd_api = CustomResourceDefinition(access_token, project_id, cluster_id)
    crd = crd_api.get(name=crd_name, is_format=False)
    return CustomObject(access_token, project_id, cluster_id, kind=crd.spec.names.kind)
