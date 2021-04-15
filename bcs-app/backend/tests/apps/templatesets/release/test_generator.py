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
import mock
import pytest

from backend.apps.templatesets.release.generator import generator
from backend.apps.templatesets.release.generator.res_context import ResContext
from backend.tests.bcs_mocks.misc import FakePaaSCCMod
from backend.utils.basic import getitems

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def use_dummy_settings_config(settings):
    settings.DEVOPS_ARTIFACTORY_HOST = "http://harbor-api.service.consul"


class TestReleaseDataGenerator:
    def test_form_generator(self, bk_user, cluster_id, form_template, form_version_entity, form_show_version):
        instance_entity = {res_name: ids.split(',') for res_name, ids in form_version_entity.resource_entity.items()}

        namespace = 'test'
        context = ResContext(
            access_token=bk_user.token.access_token,
            username=bk_user.username,
            cluster_id=cluster_id,
            project_id=form_template.project_id,
            namespace=namespace,
            template=form_template,
            show_version=form_show_version,
            instance_entity=instance_entity,
            is_preview=True,
            namespace_id=1,
        )

        with mock.patch(
            'backend.apps.templatesets.release.generator.form_mode.get_ns_variable', return_value=(False, '1.12.3', {})
        ), mock.patch('backend.apps.instance.generator.paas_cc', new=FakePaaSCCMod()):

            data_generator = generator.ReleaseDataGenerator(name="nginx", res_ctx=context)
            release_data = data_generator.generate()

            for res in release_data.resource_list:
                assert res.name == getitems(res.manifest, 'metadata.name')
                assert res.kind == getitems(res.manifest, 'kind')
                assert res.namespace == getitems(res.manifest, 'metadata.namespace')
                assert res.version == form_show_version.name
                assert getitems(res.manifest, 'webCache') is None
                assert 'io.tencent.bcs.cluster' in getitems(res.manifest, 'metadata.annotations')

                if res.kind == 'Service':
                    assert getitems(res.manifest, 'spec.type') == 'ClusterIP'

    def test_yaml_generator(self, bk_user, cluster_id, yaml_template, yaml_version_entity, yaml_show_version):
        instance_entity = {res_name: ids.split(',') for res_name, ids in yaml_version_entity.resource_entity.items()}
        namespace = 'test'
        context = ResContext(
            access_token=bk_user.token.access_token,
            username=bk_user.username,
            cluster_id=cluster_id,
            project_id=yaml_template.project_id,
            namespace=namespace,
            template=yaml_template,
            show_version=yaml_show_version,
            instance_entity=instance_entity,
            is_preview=True,
            namespace_id=1,
        )

        with mock.patch('backend.bcs_k8s.app.bcs_info_provider.paas_cc', new=FakePaaSCCMod()), mock.patch(
            'backend.bcs_k8s.helm.bcs_variable.paas_cc', new=FakePaaSCCMod()
        ):
            data_generator = generator.ReleaseDataGenerator(name="gw", res_ctx=context)
            release_data = data_generator.generate()

            assert len(release_data.resource_list) == 4

            for res in release_data.resource_list:
                assert res.name == getitems(res.manifest, 'metadata.name')
                assert res.kind == getitems(res.manifest, 'kind')
                assert res.namespace == getitems(res.manifest, 'metadata.namespace')
                assert res.version == yaml_show_version.name

                if res.kind == 'Endpoints':
                    assert getitems(res.manifest, 'subsets')[0]['addresses'][0]['ip'] == '0.0.0.1'
                    continue

                if res.kind == 'Pod':
                    assert getitems(res.manifest, 'spec.containers')[0]['image'] == 'redis:5.0.4'
