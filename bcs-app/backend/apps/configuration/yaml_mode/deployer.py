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
import contextlib

from backend.utils.client import make_kubectl_client
from backend.utils.error_codes import error_codes
from backend.bcs_k8s.kubectl.exceptions import KubectlExecutionError


class DeployController:
    def __init__(self, access_token, release_data):
        self.access_token = access_token
        self.release_data = release_data
        self.namespace = release_data.namespace_info['namespace']

    @contextlib.contextmanager
    def make_kubectl_client(self):
        with make_kubectl_client(
                project_id=self.release_data.project_id,
                cluster_id=self.release_data.namespace_info['cluster_id'],
                access_token=self.access_token) as (client, err):
            yield client, err

    def _update_or_create_version_instance(self, operation):
        # TODO adaptor model VersionInstance and InstanceConfig
        pass

    def _to_manifests(self):
        template_files = self.release_data.template_files
        manifest_list = []
        for res_file in template_files:
            manifest_list += [f['content'] for f in res_file['files']]
        return '---\n'.join(manifest_list)

    def _run_with_kubectl(self, operation):
        print(self._to_manifests())
        # with self.make_kubectl_client() as (client, err):
        #     if err is not None:
        #         raise error_codes.APIError(f'make kubectl client failed: {err}')
        #
        #     self._update_or_create_version_instance(operation)
        #
        #     manifests = self._to_manifests()
        #     try:
        #         if operation == 'apply':
        #             client.ensure_namespace(self.namespace)
        #             client.apply(manifests, self.namespace)
        #
        #         elif operation == 'delete':
        #             client.ensure_namespace(self.namespace)
        #             client.delete(manifests, self.namespace)
        #     except KubectlExecutionError as e:
        #         raise error_codes.APIError(f'kubectl {operation} failed: {e}')

    def apply(self):
        self._run_with_kubectl('apply')

    def delete(self):
        self._run_with_kubectl('delete')
