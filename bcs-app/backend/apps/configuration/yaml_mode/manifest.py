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
from collections import OrderedDict

from dataclasses import dataclass

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

        self.extra_inject_fields = extra_inject_fields

    def _inject_bcs_info(self, data):
        now = datetime.datetime.now()
        namespace_info = get_namespace_info(self.namespace_id)

        configs = bcs_info_injector.inject_configs(
            access_token=self.access_token,
            project_id=self.project_id,
            cluster_id=namespace_info['cluster_id'],
            namespace_id=namespace_info['namespace_id'],
            namespace=namespace_info['namespace'],
            creator=self.username,
            updator=self.username,
            created_at=now,
            updated_at=now,
            version=self.show_version.name
        )
        resources_list = bcs_info_injector.parse_manifest(data)
        context = {
            "creator": self.username,
            "updator": self.username,
            "version": self.show_version.name
        }
        manager = bcs_info_injector.InjectManager(
            configs=configs,
            resources=resources_list,
            context=context
        )
        resources_list = manager.do_inject()
        content = bcs_info_injector.join_manifest(resources_list)
        return content

    def _render_with_variables(self, data):
        return data

    def _set_namespace(self, data):
        pass

    def formalize(self, raw_content):
        content = self._render_with_variables(raw_content)

        content = self._inject_bcs_info(content)

        return content

    def render(self):
        for res_files in self.template_files:
            for f in res_files['files']:
                f['content'] = self.formalize(f['content'])
        return ManifestsData(self.project_id, self.namespace_id, self.show_version, self.template_files)
