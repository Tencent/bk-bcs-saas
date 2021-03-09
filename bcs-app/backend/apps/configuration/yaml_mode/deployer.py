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
import json

from backend.activity_log import client
from backend.utils.client import KubectlClient


class DeployController:
    def __init__(self, user, release_data):
        self.username = user.username
        self.release_data = release_data
        self.namespace = release_data.namespace_info['name']

        self.kubectl = KubectlClient(
            user.token.access_token, release_data.project_id, release_data.namespace_info['cluster_id']
        )

    def _log_activity(self, status, msg=''):
        show_version = self.release_data.show_version
        template = show_version.related_template

        if status == 'succeed':
            description = f'deploy template [{template.name}] in ns [{self.namespace}] success'
        else:
            description = f'deploy template [{template.name}] in ns [{self.namespace}] failed: {msg}'

        extra = {}
        for res_file in self.release_data.template_files:
            files_ids = [str(f['id']) for f in res_file['files']]
            extra[res_file['resource_name']] = ','.join(files_ids)

        log_params = {
            'project_id': self.release_data.project_id,
            'user': self.username,
            'resource_type': 'template',
            'resource': template.name,
            'resource_id': template.id,
            'extra': json.dumps(extra),
            'description': description,
        }
        client.ContextActivityLogClient(**log_params).log_add(activity_status=status)

    def _to_manifests(self):
        template_files = self.release_data.template_files
        manifest_list = []
        for res_file in template_files:
            manifest_list += [f['content'] for f in res_file['files']]
        return '---\n'.join(manifest_list)

    def _run_with_kubectl(self, operation):
        try:
            manifests = self._to_manifests()
            if operation == 'apply':
                self.kubectl.apply(self.namespace, manifests)
            elif operation == 'delete':
                self.kubectl.delete(self.namespace, manifests)
        except Exception as e:
            self._log_activity('failed', str(e))
            raise
        else:
            self._log_activity('succeed')

    def apply(self):
        self._run_with_kubectl('apply')

    def delete(self):
        self._run_with_kubectl('delete')
