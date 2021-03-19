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
from backend.apps.templatesets.release.generator.generator import ReleaseDataGenerator


class TestReleaseDataGenerator:
    def test_form_generator(self, cluster_id, form_show_version_obj):
        data_generator = ReleaseDataGenerator(
            name="nginx",
            namespace="test",
            cluster_id=cluster_id,
            template_id=form_show_version_obj.template_id,
        )
        release_data = data_generator.generate()
        assert release_data.resource_list == ["1"]
