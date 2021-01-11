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

from ..conftest import FakeBcsKubeConfigurationService, construct_replica_set, construct_pod
from backend.resources.pod.pod import Pod


class TestPod:
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
        return Pod('token', project_id, cluster_id, random_name)

    def test_get_pod(self, client_obj, random_name):
        client_obj.api.create(namespace=random_name, body=construct_pod(random_name))
        pods = client_obj.get_pod(random_name)
        assert pods[0]['namespace'] == random_name
        assert pods[0]['resourceName'] == random_name

    @pytest.mark.parametrize(
        'query_labels,expected_result_names',
        [
            ({}, {'pod-web', 'pod-worker'}),
            ({'type': 'web'}, {'pod-web'}),
            ({'type': 'invalid-type'}, set()),
        ],
    )
    def test_get_pod_by_labels(self, query_labels, expected_result_names, client_obj, random_name):
        client_obj.api.create(namespace=random_name, body=construct_pod('pod-web', labels={'type': 'web'}))
        client_obj.api.create(namespace=random_name, body=construct_pod('pod-worker', labels={'type': 'worker'}))
        pods = client_obj.get_pod_by_labels(query_labels)

        result_names = {res['resourceName'] for res in pods}
        assert result_names == expected_result_names

    @pytest.mark.parametrize(
        'rs_name,expected_result_names',
        [
            ('demo-rs', {'pod-owned-by-rs'}),
            ('nonexistent-rs', set()),
        ],
    )
    def test_get_pods_by_rs(self, rs_name, expected_result_names, client_obj, random_name):
        rs = construct_replica_set('demo-rs')
        client_obj.api.create(namespace=random_name, body=construct_pod('pod-owned-by-rs', owner_replicaset=rs))
        client_obj.api.create(namespace=random_name, body=construct_pod('pod-demo'))
        pods = client_obj.get_pods_by_rs(rs_name)

        result_names = {res['resourceName'] for res in pods}
        assert result_names == expected_result_names
