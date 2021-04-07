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
import pytest

from backend.apps.templatesets.release.generator import generator
from backend.apps.templatesets.release.generator.res_context import ResContext

pytestmark = pytest.mark.django_db


class TestReleaseDataGenerator:
    def test_form_generator(self, bk_user, cluster_id, form_template, form_version_entity, form_show_version):
        instance_entity = {res_name: ids.split(',') for res_name, ids in form_version_entity.resource_entity.items()}

        context = ResContext(
            access_token=bk_user.token.access_token,
            username=bk_user.username,
            cluster_id=cluster_id,
            project_id=form_template.project_id,
            namespace='test',
            template=form_template,
            show_version=form_show_version,
            instance_entity=instance_entity,
        )
        data_generator = generator.ReleaseDataGenerator(name="nginx", res_ctx=context)
        release_data = data_generator.generate()
        # assert release_data.resource_list == ["1"]
