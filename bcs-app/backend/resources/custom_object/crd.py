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
from django.utils.translation import ugettext_lazy as _

from backend.utils.error_codes import error_codes

from ..mixins import APIExtensionsAPIClassMixins
from ..client import APIInstance


class CustomResourceDefinition(APIExtensionsAPIClassMixins, APIInstance):
    def list_custom_resource_definition(self):
        try:
            return self.api_instance.list_custom_resource_definition()
        except Exception:
            raise error_codes.APIError(_("当前集群版本过低，不支持页面展示CRD，请通过WebConsole查看"))

    def get_custom_resource_definition(self, name):
        crds = self.list_custom_resource_definition()
        for crd in crds.items:
            if crd.metadata.name == name:
                return crd
        raise error_codes.ResNotFoundError(f"no crd {name}")
