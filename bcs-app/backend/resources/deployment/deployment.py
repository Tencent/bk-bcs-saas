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
from backend.resources.resource import ResourceClient
from backend.resources.pod import Pod
from backend.utils.basic import getitems, base64_encode_params


class Deployment(ResourceClient):
    def __init__(self, access_token, project_id, cluster_id, namespace):
        super().__init__(access_token, project_id, cluster_id, namespace)
        self.pod = Pod(access_token, project_id, cluster_id, namespace)

    def get_deployments_by_namespace(self):
        resp = self.k8s_client.get_deployment({'namespace': self.namespace})
        return self._to_data(resp)

    def get_deployment(self, deploy_name):
        resp = self.k8s_client.get_deployment({'namespace': self.namespace, 'name': deploy_name})
        return self._to_data(resp)

    def update_deployment(self, deploy_name, manifest):
        resp = self.k8s_client.update_deployment(self.namespace, deploy_name, manifest)
        return self._to_data(resp)

    def get_selector_labels(self, deploy_name):
        deployment_list = self.get_deployment(deploy_name)
        if deployment_list:
            return getitems(deployment_list[0], ['data', 'spec', 'selector', 'matchLabels'], {})
        return {}

    def get_rs_name_list(self, deploy_name):
        extra_data = {
            'data.metadata.ownerReferences.name': deploy_name,
            'data.metadata.ownerReferences.kind': 'Deployment',
        }
        params = {'extra': base64_encode_params(extra_data), 'namespace': self.namespace, 'field': 'resourceName'}
        resp = self.k8s_client.get_rs(params)

        return [rs.get('resourceName') for rs in self._to_data(resp)]

    def get_pods_by_deployment(self, deploy_name):
        selector_labels = self.get_selector_labels(deploy_name)
        pods = self.pod.get_pod_by_labels(selector_labels)

        rs_name_list = self.get_rs_name_list(deploy_name)
        pods_in_deployment = []
        for pod in pods:
            owner_references = getitems(pod, ['data', 'metadata', 'ownerReferences'], [''])[0]
            if owner_references['name'] in rs_name_list:
                pods_in_deployment.append(pod)

        return pods_in_deployment
