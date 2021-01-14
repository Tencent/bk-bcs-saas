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

from backend.utils.basic import getitems
from backend.resources.custom_object.crd import CustomResourceDefinition
from backend.resources.custom_object.custom_object import get_custom_object_api_by_crd
from backend.resources.constants import PatchTypes

from ..conftest import FakeBcsKubeConfigurationService


# https://github.com/kubernetes/sample-controller
# 运行单元测试时，确保测试集群中已部署sample-controller
sample_crd = {
    "apiVersion": "apiextensions.k8s.io/v1beta1",
    "kind": "CustomResourceDefinition",
    "metadata": {
        "name": "foos.samplecontroller.k8s.io",
        "annotations": {"api-approved.kubernetes.io": "unapproved, experimental-only"},
    },
    "spec": {
        "group": "samplecontroller.k8s.io",
        "version": "v1alpha1",
        "versions": [{"name": "v1alpha1", "served": True, "storage": True}],
        "names": {"kind": "Foo", "plural": "foos"},
        "scope": "Namespaced",
    },
}

sample_custom_object = {
    "apiVersion": "samplecontroller.k8s.io/v1alpha1",
    "kind": "Foo",
    "metadata": {"name": "example-foo"},
    "spec": {"deploymentName": "example-foo", "replicas": 1},
}


class TestCRDAndCustomObject:
    @pytest.fixture(autouse=True)
    def use_faked_configuration(self):
        """Replace ConfigurationService with fake object"""
        with mock.patch(
            'backend.resources.utils.kube_client.BcsKubeConfigurationService', new=FakeBcsKubeConfigurationService,
        ):
            yield

    @pytest.fixture
    def crd_api(self, project_id, cluster_id):
        return CustomResourceDefinition('token', project_id, cluster_id, api_version=sample_crd["apiVersion"])

    @pytest.fixture
    def update_or_create_crd(self, crd_api):
        crd_api.update_or_create(body=sample_crd)
        yield
        crd_api.delete_ignore_nonexistent(name=getitems(sample_crd, "metadata.name"), namespace="default")

    @pytest.fixture
    def cobj_api(self, project_id, cluster_id):
        return get_custom_object_api_by_crd(
            'token', project_id, cluster_id, crd_name=getitems(sample_crd, "metadata.name")
        )

    @pytest.fixture
    def update_or_create_custom_object(self, cobj_api):
        cobj_api.update_or_create(
            body=sample_custom_object, namespace="default", name=getitems(sample_custom_object, "metadata.name")
        )
        yield
        cobj_api.delete_ignore_nonexistent(name=getitems(sample_custom_object, "metadata.name"), namespace="default")

    def test_crd_list(self, crd_api, update_or_create_crd):
        crd_lists = crd_api.list(is_format=True)
        assert isinstance(crd_lists, list)

    def test_crd_get(self, crd_api, update_or_create_crd):
        crd = crd_api.get(name=getitems(sample_crd, "metadata.name"))
        assert crd.spec.scope == "Namespaced"

        crd = crd_api.get(name="no.k3s.cattle.io")
        assert crd is None

    def test_custom_object_patch(self, update_or_create_crd, cobj_api, update_or_create_custom_object):
        cobj = cobj_api.patch(
            name=getitems(sample_custom_object, "metadata.name"),
            namespace="default",
            body={"spec": {"replicas": 2}},
            content_type=PatchTypes.MergePatchJson.value,
        )
        assert cobj.spec.replicas == 2
