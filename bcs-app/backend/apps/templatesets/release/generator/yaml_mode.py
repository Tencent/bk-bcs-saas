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
from typing import List

from backend.apps.templatesets.models import ResourceData

from .res_context import ResContext


class YamltoResourceList:
    """YAML模板集资源转换生成List[ResourceData]"""

    def __init__(self, res_ctx: ResContext):
        self.res_ctx = res_ctx

    def generate(self) -> List[ResourceData]:
        inject_configs = self._get_inject_configs()
        bcs_variables = self._get_bcs_variables()
        return []

        # if self.template_variables:
        #     bcs_variables.update(self.template_variables)
        #
        # for res_files in self.template_files:
        #     for f in res_files["files"]:
        #         f["content"] = self._inject(f["content"], inject_configs, bcs_variables)
        # return ReleaseData(
        #     self.project_id, self.namespace_info, self.show_version, self.template_files, self.template_variables
        # )

    def _get_inject_configs(self):
        pass

    def _get_bcs_variables(self):
        pass
