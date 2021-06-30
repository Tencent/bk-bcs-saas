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
import json

import pytest
from mock import patch

from backend.templatesets.legacy_apps.configuration.constants import MesosResourceName
from backend.templatesets.legacy_apps.configuration.models.mesos import Deplpyment
from backend.templatesets.legacy_apps.configuration.models.template import ShowVersion, VersionedEntity
from backend.templatesets.legacy_apps.instance.models import InstanceConfig
from backend.tests.testing_utils.mocks.paas_cc import StubPaaSCCClient
from backend.uniapps.application.tools import mesos_instance

pytestmark = pytest.mark.django_db
fake_id = 1
fake_vars = {"demo": "test"}


@pytest.fixture(autouse=True)
def create_instance():
    InstanceConfig.objects.create(
        id=fake_id,
        instance_id=fake_id,
        namespace=fake_id,
        category=MesosResourceName.deployment.value,
        config='{"metadata":{"name": "test"}}',
        name="test",
    )


@pytest.fixture(autouse=True)
def create_deployment_and_versions():
    ShowVersion.objects.create(id=fake_id, real_version_id=fake_id, template_id=fake_id, name="v1")
    VersionedEntity.objects.create(id=fake_id, template_id=fake_id, entity='{"deployment": "1,2"}')
    Deplpyment.objects.create(id=fake_id, name="test", config='{"metadata":{"name": "test"}}')


def test_get_instance_id():
    inst = mesos_instance.get_instance(ns_id=fake_id, name="test", kind=MesosResourceName.deployment.value)
    assert inst.id == fake_id


def test_get_tmpl_id():
    render_data = mesos_instance.VersionInstanceData(
        instance_id=fake_id,
        name="test",
        username="admin",
        templateset_id=fake_id,
        namespace_id=fake_id,
        version_id=fake_id,
        show_version_id=fake_id,
        kind=MesosResourceName.deployment.value,
        variables={"test": "test"},
    )
    assert render_data.get_template_id() == fake_id


@patch(
    "backend.components.bcs.mesos.MesosClient.update_deployment",
    return_value={"code": 0, "message": "success", "data": {"name": "test"}},
)
@patch("backend.components.paas_cc.PaaSCCClient", new=StubPaaSCCClient)
@patch(
    "backend.uniapps.application.tools.mesos_instance.generate_manifest",
    return_value={"metadata": {"name": "test"}, "kind": MesosResourceName.deployment.value},
)
def test_scale_instance_resource(mock_generate_manifest, mock_update_deployment, ctx_cluster):
    inst_data = mesos_instance.InstanceData(
        kind=MesosResourceName.deployment.value,
        namespace="default",
        name="test",
        manifest={"metadata": {"name": "test"}},
        variables=fake_vars,
    )
    show_version = ShowVersion.objects.get(id=fake_id)
    mesos_instance.scale_instance_resource("admin", inst_data, ctx_cluster, show_version)
    inst = InstanceConfig.objects.get(id=fake_id)
    assert json.loads(inst.variables) == fake_vars
