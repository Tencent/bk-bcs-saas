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

from ..conftest import FakeBcsKubeConfigurationService


class TestCRD:
    @pytest.fixture(autouse=True)
    def use_faked_configuration(self):
        """Replace ConfigurationService with fake object"""
        with mock.patch(
            'backend.resources.utils.kube_client.BcsKubeConfigurationService', new=FakeBcsKubeConfigurationService,
        ):
            yield

    @pytest.fixture
    def crd_api(self, project_id, cluster_id):
        return CustomResourceDefinition('token', project_id, cluster_id)

    def test_list(self, crd_api):
        crd_lists = crd_api.list(is_format=True)
        assert isinstance(crd_lists, list)

        crd = crd_api.get(name="addons.k3s.cattle.io")
        assert crd.spec.scope == "Namespaced"
