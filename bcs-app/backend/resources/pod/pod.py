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
from backend.utils.basic import b64encode_json


class Pod(ResourceClient):
    def get_pod(self, pod_name):
        extra_data = {'resourceName': pod_name}

        resp = self.k8s_client.get_pod(params={'extra': b64encode_json(extra_data), 'namespace': self.namespace})
        return self._to_data(resp)

    def get_pod_by_labels(self, selector_labels):
        # TODO 支持k中包含.号的场景
        extra_data = {f'data.metadata.labels.{k}': v for k, v in selector_labels.items()}
        resp = self.k8s_client.get_pod(params={'extra': b64encode_json(extra_data), 'namespace': self.namespace})
        return self._to_data(resp)

    def get_pods_by_rs(self, rs_name):
        extra_data = {'data.metadata.ownerReferences.name': rs_name}
        resp = self.k8s_client.get_pod(params={'extra': b64encode_json(extra_data), 'namespace': self.namespace})
        return self._to_data(resp)
