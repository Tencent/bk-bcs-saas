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
from unittest import mock
import pytest

from ..conftest import FakeBcsKubeConfigurationService, construct_deployment, construct_replica_set
from backend.resources.utils.filters import filter_by_owners
from backend.resources.utils.format import InstanceAccessor
from backend.resources.utils.kube_client import get_dynamic_client


@pytest.fixture(autouse=True)
def use_faked_configuration():
    """Replace ConfigurationService with fake object"""
    with mock.patch(
        'backend.resources.utils.kube_client.BcsKubeConfigurationService',
        new=FakeBcsKubeConfigurationService,
    ):
        yield


@pytest.mark.parametrize(
    'kind,name,expected_names',
    [
        ('Deployment', 'foo-deployment', ['foo-rs-owned-by-deployment']),
        ('Deployment', 'nonexistent-deployment', []),
        # Wrong type
        ('ConfigMap', 'foo-deployment', []),
    ],
)
def test_filter_by_owners(kind, name, expected_names, project_id, cluster_id, random_name):
    client_obj = get_dynamic_client('token', project_id, cluster_id)

    rs_body = construct_replica_set('foo-rs-demo')
    deployment_body = construct_deployment('foo-deployment')
    rs_with_owner_body = construct_replica_set('foo-rs-owned-by-deployment', deployment_body)

    rs_api = client_obj.get_preferred_resource('ReplicaSet')
    rs_api.create(namespace=random_name, body=rs_body)
    rs_api.create(namespace=random_name, body=rs_with_owner_body)

    results = rs_api.get(namespace=random_name)
    filtered_results = filter_by_owners(results.items, kind, [name])

    names = [InstanceAccessor(res).name for res in filtered_results]
    assert names == expected_names
