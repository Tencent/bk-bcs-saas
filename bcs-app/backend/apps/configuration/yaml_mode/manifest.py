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
import datetime
from io import StringIO
from collections import OrderedDict

from ruamel.yaml import YAML
from dataclasses import dataclass
from rest_framework.exceptions import ParseError

from backend.bcs_k8s.app import bcs_info_injector


# TODO use resources module function
def get_namespace_info(namespace_id):
    return {
        'cluster_id': 'BCS-K8S-25001',
        'namespace': 'test',
        'namespace_id': namespace_id
    }


@dataclass
class ManifestsData:
    project_id: str
    namespace_id: int
    show_version: OrderedDict
    template_files: list


class ManifestsRenderer:
    def __init__(self, user, raw_manifests, **extra_inject_fields):
        self.access_token = user.token.access_token
        self.username = user.username

        self.project_id = raw_manifests.project_id
        self.namespace_id = raw_manifests.namespace_id
        self.show_version = raw_manifests.show_version
        self.template_files = raw_manifests.template_files
        self.namespace_info = get_namespace_info(self.namespace_id)

        self.extra_inject_fields = extra_inject_fields

    def _parse_yaml(self, yaml_content):
        try:
            yaml = YAML()
            resources = list(yaml.load_all(yaml_content.encode('utf-8')))
        except Exception as e:
            raise ParseError(f'Parse manifest failed: \n{e}\n\nManifest content:\n{yaml_content}')
        else:
            return resources

    def _join_manifest(self, resources):
        try:
            yaml = YAML()
            s = StringIO()
            yaml.dump_all(resources, s)
        except Exception as e:
            raise ParseError(f'join manifest failed: {e}')
        else:
            print(s.getvalue())
            return s.getvalue()

    def _render_with_variables(self, raw_content):
        return raw_content

    def _set_namespace(self, resources):
        for res_manifest in resources:
            metadata = res_manifest['metadata']
            metadata['namespace'] = self.namespace_info['namespace']

    def _inject_bcs_info(self, yaml_content, inject_configs):
        resources = self._parse_yaml(yaml_content)
        # resources = bcs_info_injector.parse_manifest(yaml_content)
        context = {
            "creator": self.username,
            "updator": self.username,
            "version": self.show_version.name
        }
        manager = bcs_info_injector.InjectManager(
            configs=inject_configs,
            resources=resources,
            context=context
        )
        resources = manager.do_inject()
        self._set_namespace(resources)
        return self._join_manifest(resources)
        # return bcs_info_injector.join_manifest(resources)

    def _get_inject_configs(self):
        now = datetime.datetime.now()
        configs = bcs_info_injector.inject_configs(
            access_token=self.access_token,
            project_id=self.project_id,
            cluster_id=self.namespace_info['cluster_id'],
            namespace_id=self.namespace_id,
            namespace=self.namespace_info['namespace'],
            creator=self.username,
            updator=self.username,
            created_at=now,
            updated_at=now,
            version=self.show_version.name,
            source_type='template'
        )
        return configs

    def formalize(self, raw_content, inject_configs):
        content = self._render_with_variables(raw_content)
        content = self._inject_bcs_info(content, inject_configs)
        return content

    def render(self):
        inject_configs = self._get_inject_configs()
        for res_files in self.template_files:
            for f in res_files['files']:
                f['content'] = self.formalize(f['content'], inject_configs)
        return ManifestsData(self.project_id, self.namespace_id, self.show_version, self.template_files)
