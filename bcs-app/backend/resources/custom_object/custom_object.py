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

from django.utils.translation import ugettext_lazy as _

from backend.utils.error_codes import error_codes

from ..resource import ResourceClient
from .crd import CustomResourceDefinition
from .format import CustomObjectFormatter


class CustomObject(ResourceClient):
    formatter = CustomObjectFormatter()

    def __init__(
        self, access_token: str, project_id: str, cluster_id: str, kind: str, api_version: Optional[str] = None
    ):
        self.kind = kind
        super().__init__(access_token, project_id, cluster_id, api_version)


def get_custom_object_client_by_crd(
    access_token: str, project_id: str, cluster_id: str, crd_name: str
) -> CustomObject:
    crd_client = CustomResourceDefinition(access_token, project_id, cluster_id)
    crd = crd_client.get(name=crd_name, is_format=False)
    if crd:
        return CustomObject(access_token, project_id, cluster_id, kind=crd.spec.names.kind)
    raise error_codes.ResNotFoundError(_("集群({})中未注册自定义资源({})").format(cluster_id, crd_name))
