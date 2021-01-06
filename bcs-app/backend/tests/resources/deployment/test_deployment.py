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
import uuid
from unittest import mock
import pytest

from kubernetes import client

from ..conftest import FakeBcsKubeConfigurationService
from backend.resources.deployment.deployment import Deployment
from backend.resources.utils.kube_client import get_preferred_resource


class TestDeployment:
    @pytest.fixture(autouse=True)
    def use_faked_configuration(self):
        """Replace ConfigurationService with fake object"""
        with mock.patch(
            'backend.resources.deployment.deployment.BcsKubeConfigurationService',
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
        rs_body_dict = client_obj.dynamic_client.client.sanitize_for_serialization(rs_body)
        rs_api = get_preferred_resource(client_obj.dynamic_client, 'ReplicaSet')
        rs_api.create(namespace=random_name, body=rs_body_dict)

        rs_names = client_obj.get_rs_name_list(random_name)
        assert rs_names == [f'{random_name}-rs-demo']


def construct_deployment(name, replicas=1):
    """Construct a fake deployment body"""
    return client.V1beta2Deployment(
        api_version='extensions/v1beta1',
        kind='Deployment',
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1beta2DeploymentSpec(
            selector=client.V1LabelSelector(match_labels={'deployment-name': name}),
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[client.V1Container(image="busybox", name="main", command=["sleep", "3600"])]
                ),
                metadata=client.V1ObjectMeta(labels={"deployment-name": name}, name=name),
            ),
            replicas=replicas,
        ),
    )


def construct_replica_set(name, owner_deployment):
    """Construct a fake ReplicaSet body"""
    return client.V1ReplicaSet(
        api_version='extensions/v1beta1',
        kind='ReplicaSet',
        metadata=client.V1ObjectMeta(
            name=name,
            # Set owner reference to deployment
            owner_references=[
                client.V1OwnerReference(
                    api_version=owner_deployment.api_version,
                    uid=uuid.uuid4().hex,
                    name=owner_deployment.metadata.name,
                    kind='Deployment',
                )
            ],
        ),
        spec=client.V1ReplicaSetSpec(
            replicas=owner_deployment.spec.replicas,
            selector=client.V1LabelSelector(match_labels={'deployment-name': name}),
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[client.V1Container(image="busybox", name="main", command=["sleep", "3600"])]
                ),
                metadata=client.V1ObjectMeta(labels={"deployment-name": name}, name=name),
            ),
        ),
    )
