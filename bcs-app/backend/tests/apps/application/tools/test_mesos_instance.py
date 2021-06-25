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
from mock import patch

from backend.templatesets.legacy_apps.configuration.constants import MesosResourceName
from backend.templatesets.legacy_apps.configuration.models.mesos import Deplpyment
from backend.templatesets.legacy_apps.configuration.models.template import ShowVersion, VersionedEntity
from backend.templatesets.legacy_apps.instance.models import InstanceConfig
from backend.uniapps.application.tools import mesos_instance

pytestmark = pytest.mark.django_db
fake_id = 1


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
def create_show_version():
    ShowVersion.objects.create(id=fake_id, real_version_id=fake_id, template_id=fake_id, name="v1")


@pytest.fixture(autouse=True)
def create_version_entity():
    VersionedEntity.objects.create(id=fake_id, template_id=fake_id, entity='{"deployment": "1,2"}')


@pytest.fixture(autouse=True)
def create_application():
    Deplpyment.objects.create(id=fake_id, name="test", config='{"metadata":{"name": "test"}}')


def test_get_instance_id():
    inst = mesos_instance.get_mesos_instance(ns_id=fake_id, name="test", kind=MesosResourceName.deployment.value)
    assert inst.id == fake_id


def test_get_tmpl_id():
    render_data = mesos_instance.RenderResourceData(
        name="test",
        username="admin",
        templateset_id=fake_id,
        namespace_id=fake_id,
        version_id=fake_id,
        show_version_id=fake_id,
        kind=MesosResourceName.deployment.value,
        variable_dict={"test": "test"},
    )
    assert render_data.get_tmpl_id() == fake_id
