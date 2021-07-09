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
from unittest import mock

from backend.uniapps.application.instance_views import InstanceAPI

fake_app_name = ["demo", "demo-v1"]


@mock.patch(
    "backend.uniapps.application.instance_views.InstanceAPI.get_rc_name_by_deployment_base",
    return_value=["demo", "demo-v1", "demo"],
)
def test_get_application_by_deployment(request, cluster_id, random_name, namespace):
    client = InstanceAPI()
    app_name_list = client._get_mesos_app_names_by_deployment(
        request, cluster_id, random_name, namespace, "deployment"
    )
    assert len(app_name_list) == len(fake_app_name)
