# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import pytest

from backend.templatesets.legacy_apps.configuration.models import Template
from backend.templatesets.legacy_apps.configuration.utils import list_templatesets

pytestmark = pytest.mark.django_db


@pytest.fixture
def generate_templateset_data(template_data):
    template_objs = [Template(id=i["id"], project_id=i["project_id"], name=i["name"]) for i in template_data]
    templateset_objs = Template.objects.bulk_create(template_objs)
    return templateset_objs


class TestTemplatesetModelOperateUtils:
    """Template model相关操作测试"""

    def test_filter_templatesets_with_templateset_ids(
        self, fake_project_id, fake_templateset_ids, generate_templateset_data
    ):
        """测试根据templateset_id的过滤"""
        result = list_templatesets(fake_project_id, [fake_templateset_ids[1]], ["id", "project_id", "name"])
        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_filter_templatesets_without_templateset_ids(self, fake_project_id, generate_templateset_data):
        """测试获取全部数据"""
        result = list_templatesets(fake_project_id, fields=["id", "project_id", "name"])
        assert len(result) == 2
