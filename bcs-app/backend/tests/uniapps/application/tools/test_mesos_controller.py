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
from mock import patch

from backend.uniapps.application.tools.mesos_controller import InstanceController, InstanceData

fake_resource_data = InstanceData(
    kind="deployment",
    namespace="default",
    name="test",
    manifest={"metadata": {"name": "test"}},
    variables={"test": "test"},
)


class TestInstanceController:
    @patch(
        "backend.components.bcs.mesos.MesosClient.update_deployment",
        return_value={"code": 0, "message": "success", "data": {"name": "test"}},
    )
    def test_update_deployment(self, mock_update_deployment, ctx_cluster):
        controller = InstanceController(ctx_cluster, fake_resource_data)
        data = controller.scale_resource()
        assert data["name"] == "test"
