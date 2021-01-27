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

from backend.resources.deployment.deployment import Deployment

from ..conftest import FakeBcsKubeConfigurationService, construct_deployment, construct_pod, construct_replica_set


class TestDeployment:
    @pytest.fixture(autouse=True)
    def use_faked_configuration(self):
        """Replace ConfigurationService with fake object"""
        with mock.patch(
            'backend.resources.utils.kube_client.BcsKubeConfigurationService',
            new=FakeBcsKubeConfigurationService,
        ):
            yield

    @pytest.fixture
    def client_obj(self, project_id, cluster_id, random_name):
        return Deployment('token', project_id, cluster_id, random_name)

    @pytest.fixture
    def create_default_deployment(self, client_obj, random_name):
        deployment_body = construct_deployment(random_name)
        client_obj.create(deployment_body)

    def test_create(self, client_obj, random_name):
        deployment_body = construct_deployment(random_name)
        client_obj.create(deployment_body)

    def test_get_deployments_by_namespace(self, client_obj, create_default_deployment, random_name):
        results = client_obj.get_deployments_by_namespace()
        assert len(results) == 1
        assert results[0]['metadata']['name'] == random_name

    def test_get_deployment(self, client_obj, create_default_deployment, random_name):
        results = client_obj.get_deployment(random_name)
        assert results[0]['metadata']['name'] == random_name

    def test_update_deployment(self, client_obj, create_default_deployment, random_name):
        new_body = construct_deployment(random_name, 12)
        client_obj.update_deployment(random_name, new_body)
        assert client_obj.get_deployment(random_name)[0]['spec']['replicas'] == 12

    def test_get_selector_labels(self, client_obj, create_default_deployment, random_name):
        labels = client_obj.get_selector_labels(random_name)
        assert isinstance(labels, dict)
        assert labels['deployment-name'] == random_name

    def test_get_rs_name_list(self, client_obj, random_name):
        rs_names = client_obj.get_rs_name_list(random_name)
        assert rs_names == []

        # Create ReplicaSet object
        deployment_body = construct_deployment(random_name)

        rs_body = construct_replica_set(f'{random_name}-rs-demo', deployment_body)
        rs_api = client_obj.dynamic_client.get_preferred_resource('ReplicaSet')
        rs_api.create(namespace=random_name, body=rs_body)

        rs_names = client_obj.get_rs_name_list(random_name)
        assert rs_names == [f'{random_name}-rs-demo']

    def test_get_pods_by_deployment(self, client_obj, random_name):
        # Create ReplicaSet object
        deployment_body = construct_deployment(random_name)
        rs_body = construct_replica_set(f'{random_name}-rs-demo', owner_deployment=deployment_body)
        pod_body = construct_pod(f'{random_name}-pod-demo', owner_replicaset=rs_body)

        client_obj.dynamic_client.get_preferred_resource('Deployment').create(
            namespace=random_name, body=deployment_body
        )
        client_obj.dynamic_client.get_preferred_resource('ReplicaSet').create(namespace=random_name, body=rs_body)
        client_obj.dynamic_client.get_preferred_resource('Pod').create(namespace=random_name, body=pod_body)

        pods = client_obj.get_pods_by_deployment(random_name)
        assert len(pods) == 1
        assert pods[0]['resourceName'] == f'{random_name}-pod-demo'
