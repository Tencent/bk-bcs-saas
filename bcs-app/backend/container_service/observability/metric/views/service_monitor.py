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
import logging
from typing import Dict, List

import arrow
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response

from backend.accounts import bcs_perm
from backend.activity_log import client as activity_client
from backend.apps.constants import ALL_LIMIT
from backend.bcs_web.viewsets import SystemViewSet
from backend.components import paas_cc
from backend.components.bcs import k8s
from backend.container_service.observability.metric.constants import (
    DEFAULT_ENDPOINT_INTERVAL,
    DEFAULT_ENDPOINT_PATH,
    INNER_USE_SERVICE_METADATA_FIELDS,
    SM_NO_PERM_MAP,
    SM_NO_PERM_NAMESPACE,
    SM_SERVICE_NAME_LABEL,
)
from backend.container_service.observability.metric.serializers import (
    ServiceMonitorBatchDeleteSLZ,
    ServiceMonitorCreateSLZ,
    ServiceMonitorUpdateSLZ,
)
from backend.utils.basic import getitems
from backend.utils.datetime import get_duration_seconds
from backend.utils.error_codes import error_codes

logger = logging.getLogger(__name__)


class ServiceMonitorMixin:
    """ 一些通用的方法 """

    def _handle_endpoints(self, endpoints: List[Dict]) -> List[Dict]:
        """
        Endpoints 配置填充数据

        :param endpoints: 原始数据
        :return: 完成补充的数据
        """
        for endpoint in endpoints:
            endpoint.setdefault('path', DEFAULT_ENDPOINT_PATH)
            endpoint['interval'] = get_duration_seconds(endpoint.get('interval'), DEFAULT_ENDPOINT_INTERVAL)
        return endpoints

    def _handle_items(self, cluster_id: str, cluster_map: Dict, namespace_map: Dict, manifest: Dict) -> List[Dict]:
        """
        ServiceMonitor 配置填充数据

        :param cluster_id: 集群 ID
        :param cluster_map: {cluster_id: cluster_info}
        :param namespace_map: {(cluster_id, name): id}
        :param manifest: ServiceMonitor 配置信息
        :return: ServiceMonitor 列表
        """
        items = manifest.get('items') or []
        new_items = []

        for item in items:
            try:
                labels = item['metadata'].get('labels') or {}
                item['metadata'] = {
                    k: v for k, v in item['metadata'].items() if k not in INNER_USE_SERVICE_METADATA_FIELDS
                }
                item['cluster_id'] = cluster_id
                item['namespace'] = item['metadata']['namespace']
                item['namespace_id'] = namespace_map.get((cluster_id, item['metadata']['namespace']))
                item['name'] = item['metadata']['name']
                item['instance_id'] = f"{item['namespace']}/{item['name']}"
                item['service_name'] = labels.get(SM_SERVICE_NAME_LABEL)
                item['cluster_name'] = cluster_map[cluster_id]['name']
                item['environment'] = cluster_map[cluster_id]['environment']
                item['metadata']['service_name'] = labels.get(SM_SERVICE_NAME_LABEL)
                item['create_time'] = (
                    arrow.get(item['metadata']['creationTimestamp'])
                    .to(settings.TIME_ZONE)
                    .format('YYYY-MM-DD HH:mm:ss')
                )
                if isinstance(item['spec'].get('endpoints'), list):
                    item['spec']['endpoints'] = self._handle_endpoints(item['spec']['endpoints'])
                new_items.append(item)
            except Exception as e:
                logger.error('handle item error, %s, %s', e, item)

        new_items = sorted(new_items, key=lambda x: x['create_time'], reverse=True)
        return new_items

    def _update_service_monitor_perm(self, resources: List[Dict]) -> List[Dict]:
        """ 更新相关权限信息 """
        for res in resources:
            res['permissions']['delete'] = res['permissions']['edit']
            res['permissions']['delete_msg'] = res['permissions']['edit_msg']
            if res['namespace'] not in SM_NO_PERM_NAMESPACE:
                continue
            res['permissions'] = SM_NO_PERM_MAP
        return resources

    def _validate_namespace_use_perm(self, project_id: str, cluster_id: str, namespaces: List):
        """ 检查是否有命名空间的使用权限 """
        namespace_map = self._get_namespace_map(project_id)
        for ns in namespaces:
            if ns in SM_NO_PERM_NAMESPACE:
                raise error_codes.APIError(_('不允许操作命名空间 {}').format(ns))

            namespace_id = namespace_map.get((cluster_id, ns))
            # 检查是否有命名空间的使用权限
            perm = bcs_perm.Namespace(self.request, project_id, namespace_id)
            perm.can_use(raise_exception=True)

    def _activity_log(self, project_id: str, username: str, resource_name: str, description: str, status: bool):
        """ 操作记录方法 TODO 考虑使用装饰器实现 """
        client = activity_client.ContextActivityLogClient(
            project_id=project_id, user=username, resource_type='metric', resource=resource_name
        )
        if status is True:
            client.log_delete(activity_status='succeed', description=description)
        else:
            client.log_delete(activity_status='failed', description=description)

    def _get_cluster_map(self, project_id: str) -> Dict:
        """
        获取集群配置信息

        :param project_id: 项目 ID
        :return: {cluster_id: cluster_info}
        """
        resp = paas_cc.get_all_clusters(self.request.user.token.access_token, project_id)
        clusters = getitems(resp, 'data.results', [])
        return {i['cluster_id']: i for i in clusters}

    def _get_namespace_map(self, project_id: str) -> Dict:
        """
        获取命名空间配置信息

        :param project_id: 项目 ID
        :return: {(cluster_id, name): id}
        """
        resp = paas_cc.get_namespace_list(self.request.user.token.access_token, project_id, limit=ALL_LIMIT)
        namespaces = getitems(resp, 'data.results', [])
        return {(i['cluster_id'], i['name']): i['id'] for i in namespaces}


class ServiceMonitorViewSet(SystemViewSet, ServiceMonitorMixin):
    """集群ServiceMonitor"""

    def list(self, request, project_id, cluster_id):
        cluster_map = self._get_cluster_map(project_id)
        namespace_map = self._get_namespace_map(project_id)

        if cluster_id not in cluster_map:
            raise error_codes.APIError(_('集群 ID {} 不合法').format(cluster_id))

        client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        manifest = client.list_service_monitor()
        response_data = self._handle_items(cluster_id, cluster_map, namespace_map, manifest)

        perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES)
        response_data = perm.hook_perms(response_data, ns_id_flag='namespace_id')
        response_data = self._update_service_monitor_perm(response_data)

        return Response(response_data)

    def create(self, request, project_id, cluster_id):
        params = self.params_validate(ServiceMonitorCreateSLZ)

        endpoints = [
            {
                'path': params['path'],
                'interval': params['interval'],
                'port': params['port'],
                'params': params.get('params', {}),
            }
        ]

        spec = {
            'apiVersion': 'monitoring.coreos.com/v1',
            'kind': 'ServiceMonitor',
            'metadata': {
                'labels': {
                    'release': 'po',
                    'io.tencent.paas.source_type': 'bcs',
                    'io.tencent.bcs.service_name': params['service_name'],
                },
                'name': params['name'],
                'namespace': params['namespace'],
            },
            'spec': {
                'endpoints': endpoints,
                'selector': {'matchLabels': params['selector']},
                'sampleLimit': params['sample_limit'],
            },
        }

        client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = client.create_service_monitor(params['namespace'], spec)
        if result.get('status') == 'Failure':
            message = _('创建Metrics:{}失败, [命名空间:{}], {}').format(
                params['name'], params['namespace'], result.get('message', '')
            )
            self._activity_log(project_id, request.user.username, params['name'], message, False)
            raise error_codes.APIError(result.get('message', ''))

        message = _('创建Metrics:{}成功, [命名空间:{}]').format(params['name'], params['namespace'])
        self._activity_log(project_id, request.user.username, params['name'], message, True)
        return Response(result)

    def bacth_delete(self, request, project_id, cluster_id):
        """批量删除"""
        params = self.params_validate(ServiceMonitorBatchDeleteSLZ)
        svc_monitors = params['servicemonitors']

        self._validate_namespace_use_perm(project_id, cluster_id, [sm['namespace'] for sm in svc_monitors])

        client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        successes = []
        for monitor in svc_monitors:
            result = client.delete_service_monitor(monitor['namespace'], monitor['name'])
            if result.get('status') == 'Failure':
                message = _('删除Metrics:{}失败, [命名空间:{}], {}').format(
                    monitor['name'], monitor['namespace'], result.get('message', '')
                )
                self._activity_log(project_id, request.user.username, monitor['name'], message, False)
                raise error_codes.APIError(result.get('message', ''))
            else:
                successes.append(monitor)

        names = ','.join(i['name'] for i in successes)
        message = _('删除Metrics:{}成功, [命名空间:{}]').format(names, ','.join(i['namespace'] for i in successes))
        self._activity_log(project_id, request.user.username, names, message, True)
        return Response({'successes': successes})


class ServiceMonitorDetailViewSet(SystemViewSet, ServiceMonitorMixin):
    def get(self, request, project_id, cluster_id, namespace, name):
        """ 获取单个serviceMonitor """
        client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = client.get_service_monitor(namespace, name)
        if result.get('status') == 'Failure':
            raise error_codes.APIError(result.get('message', ''))

        labels = result['metadata'].get('labels') or {}
        result['metadata'] = {
            k: v for k, v in result['metadata'].items() if k not in INNER_USE_SERVICE_METADATA_FIELDS
        }
        result['metadata']['service_name'] = labels.get(SM_SERVICE_NAME_LABEL)

        if isinstance(result['spec'].get('endpoints'), list):
            result['spec']['endpoints'] = self._handle_endpoints(result['spec']['endpoints'])

        return Response(result)

    def delete(self, request, project_id, cluster_id, namespace, name):
        """ 删除servicemonitor """
        self._validate_namespace_use_perm(project_id, cluster_id, namespace)
        client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = client.delete_service_monitor(namespace, name)
        if result.get('status') == 'Failure':
            message = _('删除Metrics:{}失败, [命名空间:{}], {}').format(name, namespace, result.get('message', ''))
            self._activity_log(project_id, request.user.username, name, message, False)
            raise error_codes.APIError(result.get('message', ''))

        message = _('删除Metrics:{}成功, [命名空间:{}]').format(name, namespace)
        self._activity_log(project_id, request.user.username, name, message, True)
        return Response(result)

    def update(self, request, project_id, cluster_id, namespace, name):
        params = self.params_validate(ServiceMonitorUpdateSLZ)

        client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = client.get_service_monitor(namespace, name)
        if result.get('status') == 'Failure':
            message = _('更新Metrics:{}失败, [命名空间:{}], {}').format(name, namespace, result.get('message', ''))
            self._activity_log(project_id, request.user.username, name, message, False)
            raise error_codes.APIError(result.get('message', ''))

        spec = self._merge_spec(result, params)

        # 更新会合并selector，所有是先删除, 再创建
        result = client.delete_service_monitor(namespace, name)
        if result.get('status') == 'Failure':
            message = _('更新Metrics:{}失败, [命名空间:{}], {}').format(name, namespace, result.get('message', ''))
            self._activity_log(project_id, request.user.username, name, message, False)
            raise error_codes.APIError(result.get('message', ''))

        result = client.create_service_monitor(namespace, spec)
        if result.get('status') == 'Failure':
            message = _('更新Metrics:{}失败, [命名空间:{}], {}').format(name, namespace, result.get('message', ''))
            self._activity_log(project_id, request.user.username, name, message, False)
            raise error_codes.APIError(result.get('message', ''))

        message = _('更新Metrics:{}成功, [命名空间:{}]').format(name, namespace)
        self._activity_log(project_id, request.user.username, name, message, True)
        return Response(result)

    def _merge_spec(self, spec, validated_data):
        spec['metadata']['labels']['release'] = 'po'
        spec['spec']['selector'] = {'matchLabels': validated_data['selector']}
        spec['spec']['sampleLimit'] = validated_data['sample_limit']
        spec['spec']['endpoints'] = [
            {
                'path': validated_data['path'],
                'interval': validated_data['interval'],
                'port': validated_data['port'],
                'params': validated_data.get('params', {}),
            }
        ]
        spec['metadata'] = {k: v for k, v in spec['metadata'].items() if k not in INNER_USE_SERVICE_METADATA_FIELDS}

        return spec
