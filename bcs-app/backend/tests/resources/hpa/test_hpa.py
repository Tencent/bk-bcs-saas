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
    @pytest.fixture()
    def cpu_workload(self):
        with open(os.path.join(BASE_DIR), "simple_cpu_hpa.yaml") as fh:
            return yaml.loads(fh.read())

    @pytest.fixture(autouse=True)
    def use_faked_configuration(self):
        """Replace ConfigurationService with fake object"""
        with mock.patch(
            'backend.resources.utils.kube_client.BcsKubeConfigurationService', new=FakeBcsKubeConfigurationService,
        ):
            yield

    @pytest.fixture
    def client(self, project_id, cluster_id):
        client = hpa_client.HPA(ClusterAuth('token', project_id, cluster_id))
        client.set_formatter("fake_project_code", "fake_cluster_name", "fake_cluster_env")
        return client

    @pytest.fixture
    def update_or_create_hpa(self, client, cpu_workload):
        client.update_or_create(body=cpu_workload)
        yield
        client.delete_ignore_nonexistent(name=getitems(cpu_workload, "metadata.name"), namespace="default")

    def test_list(self, client, update_or_create_hpa):
        hpa_list = client.list()
        assert isinstance(hpa_list, list)

    def test_delete(self, client, cpu_workload):
        client.delete_ignore_nonexistent(name=getitems(cpu_workload, "metadata.name"), namespace="default")
