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

from rest_framework.decorators import action
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.dashboard.utils.resp import ListApiRespBuilder, RetrieveApiRespBuilder
from backend.dashboard.workloads.constants import VOLUME_RESOURCE_NAME_KEY_MAP
from backend.dashboard.workloads.serializers import ListPodSLZ
from backend.dashboard.workloads.utils.resources import fetch_pod_manifest
from backend.resources.cluster.models import CtxCluster
from backend.resources.configs.configmap import ConfigMap
from backend.resources.configs.secret import Secret
from backend.resources.resource import ResourceClient
from backend.resources.storages.persistent_volume_claim import PersistentVolumeClaim
from backend.resources.workloads.pod import Pod
from backend.utils.basic import getitems
from backend.utils.string import decapitalize


class PodViewSet(SystemViewSet):

    lookup_field = 'pod_name'

    def list(self, request, project_id, cluster_id, namespace=None):
        """ 获取 Pod 列表，支持 labelSelector """
        params = self.params_validate(ListPodSLZ)
        client = Pod(request.ctx_cluster)
        response_data = ListApiRespBuilder(client, **params).build()
        return Response(response_data)

    def retrieve(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取单个 Pod 详细信息 """
        client = Pod(request.ctx_cluster)
        response_data = RetrieveApiRespBuilder(client, namespace, pod_name).build()
        return Response(response_data)

    @action(methods=['GET'], url_path='pvcs', detail=True)
    def persistent_volume_claims(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取 Pod Persistent Volume Claim 信息 """
        response_data = self._filter_pod_related_resource(
            request.ctx_cluster, PersistentVolumeClaim(request.ctx_cluster), namespace, pod_name
        )
        return Response(response_data)

    @action(methods=['GET'], url_path='configmaps', detail=True)
    def configmaps(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取 Pod ConfigMap 信息 """
        response_data = self._filter_pod_related_resource(
            request.ctx_cluster, ConfigMap(request.ctx_cluster), namespace, pod_name
        )
        return Response(response_data)

    @action(methods=['GET'], url_path='secrets', detail=True)
    def secrets(self, request, project_id, cluster_id, namespace, pod_name):
        """ 获取 Pod Secret 信息 """
        response_data = self._filter_pod_related_resource(
            request.ctx_cluster, Secret(request.ctx_cluster), namespace, pod_name
        )
        return Response(response_data)

    def _filter_pod_related_resource(
        self, ctx_cluster: CtxCluster, client: ResourceClient, namespace: str, pod_name: str
    ) -> Dict:
        """
        过滤与 Pod 相关联的资源

        :param ctx_cluster: 集群 Context
        :param client: 关联资源 client
        :param namespace: 命名空间
        :param pod_name: Pod 名称
        :return: 关联资源列表
        """
        pod_manifest = fetch_pod_manifest(ctx_cluster, namespace, pod_name)
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
