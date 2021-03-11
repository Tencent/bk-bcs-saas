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
from backend.apps.templatesets import models


class TestAppRelease:
    def test_create_app_release(self, cluster_id, template_id):
        version_id = 1
        version_name = "v1"
        version_suffix = "20210310151630"

        models.AppRelease.objects.create(
            name="test-nginx",
            cluster_id=cluster_id,
            namespace="default",
            template_id=template_id,
            version_id=version_id,
            version_name=version_name,
            version_suffix=version_suffix,
        )
