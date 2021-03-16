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
from backend.apps.configuration.constants import TemplateEditMode
from backend.apps.templatesets.models import AppReleaseData

from .form_mode import FormtoResourceList
from .yaml_mode import YamltoResourceList

ResourceGenerator = {
    TemplateEditMode.PageForm.value: FormtoResourceList,
    TemplateEditMode.YAML.value: YamltoResourceList,
}


class ReleaseDataGenerator:
    def __init__(self, name: str, namespace: str, cluster_id: str, template_id: int, template_edit_mode: str):
        self.name = name
        self.namespace = namespace
        self.cluster_id = cluster_id
        self.template_id = template_id
        self.generator = ResourceGenerator[template_edit_mode]()

    def generate(self, *args, **kwargs) -> AppReleaseData:
        return AppReleaseData(
            name=self.name,
            cluster_id=self.cluster_id,
            namespace=self.namespace,
            template_id=self.template_id,
            resource_list=self.generator.generate(*args, **kwargs),
        )
