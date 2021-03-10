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
#
import os.path
from unittest import mock

import pytest
import yaml

from backend.resources.hpa import hpa as hpa_client
from backend.resources.utils.auths import ClusterAuth
from backend.utils.basic import getitems

from ..conftest import FakeBcsKubeConfigurationService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestHPA:
    @pytest.fixture(autouse=True)
    def use_faked_configuration(self):
        """Replace ConfigurationService with fake object"""
        with mock.patch(
            'backend.resources.utils.kube_client.BcsKubeConfigurationService', new=FakeBcsKubeConfigurationService,
        ):
            yield

    @pytest.fixture(autouse=True)
    def use_fake_db(self):
        with mock.patch("backend.apps.instance.models.InstanceConfig.objects"):
            yield

    @pytest.fixture()
    def cpu_workload(self):
        with open(os.path.join(BASE_DIR, "sample_cpu_hpa.yaml")) as fh:
            return yaml.load(fh.read())

    @pytest.fixture
    def client(self, project_id, cluster_id):
        client = hpa_client.HPA(ClusterAuth('token', project_id, cluster_id))
        return client

    def test_list(self, client):
        hpa_list = client.list(namespace="default")
        assert len(hpa_list) == 0

    @pytest.fixture
    def sample_hpa(self, client, cpu_workload):
        client.update_or_create(body=cpu_workload, is_format=False)
        yield
        client.delete_ignore_nonexistent(
            namespace="default", name=getitems(cpu_workload, "metadata.name"), namespace_id="", username=""
        )

    def test_update_or_create(self, client, cpu_workload, sample_hpa):
        res, created = client.update_or_create(body=cpu_workload, is_format=False)
        assert created is False

    def test_delete(self, client, cpu_workload):
        client.update_or_create(body=cpu_workload, is_format=False)

        result = client.delete_ignore_nonexistent(
            namespace="default", name=getitems(cpu_workload, "metadata.name"), namespace_id="", username=""
        )
        assert result.status == 'Success'
