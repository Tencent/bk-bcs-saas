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
import pytest

from ..conftest import FakeBcsKubeConfigurationService
from backend.resources.namespace.namespace_quota import NamespaceQuota


class TestNamespaceQuota:
    @pytest.fixture(autouse=True)
    def use_faked_configuration(self):
        """Replace ConfigurationService with fake object"""
        with mock.patch(
            'backend.resources.namespace.namespace_quota.BcsKubeConfigurationService',
            new=FakeBcsKubeConfigurationService,
        ):
            yield

    def test_create_namespace_quota(self, project_id, cluster_id, random_name):
        client = NamespaceQuota('token', project_id, cluster_id)
        client.create_namespace_quota(random_name, {'cpu': '1000m'})

    def test_get_namespace_quota(self, project_id, cluster_id, random_name):
        client = NamespaceQuota('token', project_id, cluster_id)
        client.create_namespace_quota(random_name, {'cpu': '1000m'})

        quota = client.get_namespace_quota(random_name)
        assert isinstance(quota, dict)
        assert 'hard' in quota

    def test_list_namespace_quota(self, project_id, cluster_id, random_name):
        client = NamespaceQuota('token', project_id, cluster_id)
        results = client.list_namespace_quota(random_name)
        assert len(results) == 0

        client.create_namespace_quota(random_name, {'cpu': '1000m'})
        results = client.list_namespace_quota(random_name)
        assert len(results) == 1

    def test_delete_namespace_quota(self, project_id, cluster_id, random_name):
        client = NamespaceQuota('token', project_id, cluster_id)
        client.create_namespace_quota(random_name, {'cpu': '1000m'})
        quota = client.get_namespace_quota(random_name)
        assert isinstance(quota, dict)

        client.delete_namespace_quota(random_name)
        assert not client.get_namespace_quota(random_name)

    def test_update_or_create_namespace_quota(self, project_id, cluster_id, random_name):
        client = NamespaceQuota('token', project_id, cluster_id)
        client.update_or_create_namespace_quota(random_name, {'cpu': '1000m'})

        quota = client.get_namespace_quota(random_name)
        assert isinstance(quota, dict)
