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
from typing import Dict

from django.utils.translation import ugettext_lazy as _

from backend.dashboard.exceptions import ResourceNotExist
from backend.dashboard.workloads.constants import VOLUME_RESOURCE_NAME_KEY_MAP
from backend.resources.constants import K8sResourceKind
from backend.resources.resource import ResourceClient
from backend.resources.workloads.pod.formatter import PodFormatter
from backend.utils.basic import getitems
from backend.utils.string import decapitalize


class Pod(ResourceClient):
    """ Pod 相关资源 Client """

    kind = K8sResourceKind.Pod.value
    formatter = PodFormatter()

    def fetch_manifest(self, namespace: str, pod_name: str) -> Dict:
        """
        获取指定 Pod 配置信息

        :param ctx_cluster: 集群 Context
        :param namespace: 命名空间
        :param pod_name: Pod 名称
        :return: Pod 配置信息
        """
        pod = self.get(namespace=namespace, name=pod_name, is_format=False)
        if not pod:
            raise ResourceNotExist(_('Pod(Namespace: {}, Name: {})不存在').format(namespace, pod_name))
        return pod.to_dict()

    def filter_related_resources(self, client: ResourceClient, namespace: str, pod_name: str) -> Dict:
        """
        过滤与 Pod 相关联的资源

        :param client: 关联资源 client
        :param namespace: 命名空间
        :param pod_name: Pod 名称
        :return: 关联资源列表
        """
        pod_manifest = self.fetch_manifest(namespace, pod_name)
        # Pod 配置中资源类型为驼峰式，需要将 ResourceKind 首字母小写
        resource_kind, resource_name_key = decapitalize(client.kind), VOLUME_RESOURCE_NAME_KEY_MAP[client.kind]
        # 获取与指定 Pod 相关联的 某种资源 的资源名称列表
        resource_name_list = [
            volume[resource_kind][resource_name_key]
            for volume in getitems(pod_manifest, 'spec.volumes', [])
            if resource_kind in volume
        ]
        # 查询指定命名空间下该资源的所有实例，并根据名称列表过滤
        resources = client.list(namespace=namespace, is_format=False).to_dict()
        resources['items'] = [item for item in resources['items'] if item['metadata']['name'] in resource_name_list]
        # 组装展示用扩展信息等
        manifest_ext = {item['metadata']['uid']: client.formatter.format_dict(item) for item in resources['items']}
        return {'manifest': resources, 'manifest_ext': manifest_ext}
