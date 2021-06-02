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
from typing import Callable, Dict, List

import arrow
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.accounts import bcs_perm
from backend.activity_log import client as activity_client
from backend.activity_log.constants import BaseActivityStatus, BaseActivityType, BaseResourceType
from backend.apps.constants import ALL_LIMIT
from backend.bcs_web.viewsets import SystemViewSet
from backend.components import paas_cc
from backend.components.bcs.k8s import K8SClient
from backend.container_service.observability.metric import constants
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
            endpoint.setdefault('path', constants.DEFAULT_ENDPOINT_PATH)
            endpoint['interval'] = get_duration_seconds(endpoint.get('interval'), constants.DEFAULT_ENDPOINT_INTERVAL)
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
                    k: v for k, v in item['metadata'].items() if k not in constants.INNER_USE_SERVICE_METADATA_FIELDS
                }
                item['cluster_id'] = cluster_id
                item['namespace'] = item['metadata']['namespace']
                item['namespace_id'] = namespace_map.get((cluster_id, item['metadata']['namespace']))
                item['name'] = item['metadata']['name']
                item['instance_id'] = f"{item['namespace']}/{item['name']}"
                item['service_name'] = labels.get(constants.SM_SERVICE_NAME_LABEL)
                item['cluster_name'] = cluster_map[cluster_id]['name']
                item['environment'] = cluster_map[cluster_id]['environment']
                item['metadata']['service_name'] = labels.get(constants.SM_SERVICE_NAME_LABEL)
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
            if res['namespace'] not in constants.SM_NO_PERM_NAMESPACE:
                continue
            res['permissions'] = constants.SM_NO_PERM_MAP
        return resources

    def _validate_namespace_use_perm(self, project_id: str, cluster_id: str, namespaces: List):
        """ 检查是否有命名空间的使用权限 """
        namespace_map = self._get_namespace_map(project_id)
        for ns in namespaces:
            if ns in constants.SM_NO_PERM_NAMESPACE:
                raise error_codes.APIError(_('不允许操作命名空间 {}').format(ns))

            namespace_id = namespace_map.get((cluster_id, ns))
            # 检查是否有命名空间的使用权限
            perm = bcs_perm.Namespace(self.request, project_id, namespace_id)
            perm.can_use(raise_exception=True)

    def _activity_log(
        self,
        project_id: str,
        username: str,
        resource_name: str,
        description: str,
        activity_type: BaseActivityType,
        activity_status: BaseActivityStatus,
    ) -> None:
        """ 操作记录方法 """
        client = activity_client.ContextActivityLogClient(
            project_id=project_id, user=username, resource_type=BaseResourceType.Metric, resource=resource_name
        )
        # 根据不同的操作类型，使用不同的记录方法
        log_func = {
            BaseActivityType.Add: client.log_add,
            BaseActivityType.Delete: client.log_delete,
            BaseActivityType.Retrieve: client.log_note,
        }[activity_type]
        log_func(activity_status=activity_status, description=description)

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

    def _single_service_monitor_operate_handler(
        self,
        client_func: Callable,
        operate_str: str,
        project_id: str,
        activity_type: BaseActivityType,
        namespace: str,
        name: str,
        manifest: Dict = None,
        log_success: bool = False,
    ) -> Dict:
        """
        执行单个 ServiceMonitor 操作类的通用处理逻辑

        :param client_func: k8s client 方法
        :param operate_str: 操作描述，可选值为：创建，更新，删除
        :param project_id: 项目 ID
        :param activity_type: 操作类型
        :param namespace: 命名空间
        :param name: ServiceMonitor 名称
        :param manifest: 完整配置信息（创建用），若为 None 则非创建逻辑
        :param log_success: 操作成功时记录日志
        :return:
        """
        username = self.request.user.username
        result = (
            client_func(namespace, manifest) if activity_type == BaseActivityType.Add else client_func(namespace, name)
        )
        if result.get('status') == 'Failure':
            message = _('{} Metrics [{}/{}] 失败: {}').format(operate_str, namespace, name, result.get('message', ''))
            self._activity_log(project_id, username, name, message, activity_type, BaseActivityStatus.Failed)
            raise error_codes.APIError(result.get('message', ''))

        # 仅当指定需要记录 成功信息 才记录
        if log_success:
            message = _('{} Metrics [{}/{}] 成功').format(operate_str, namespace, name)
            self._activity_log(project_id, username, name, message, activity_type, BaseActivityStatus.Succeed)
        return result


class ServiceMonitorViewSet(SystemViewSet, ServiceMonitorMixin):
    """ 集群 ServiceMonitor 相关操作 """

    def list(self, request, project_id, cluster_id):
        """ 获取 ServiceMonitor 列表 """
        cluster_map = self._get_cluster_map(project_id)
        namespace_map = self._get_namespace_map(project_id)

        if cluster_id not in cluster_map:
            raise error_codes.APIError(_('集群 ID {} 不合法').format(cluster_id))

        client = K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        manifest = client.list_service_monitor()
        response_data = self._handle_items(cluster_id, cluster_map, namespace_map, manifest)

        perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES)
        response_data = perm.hook_perms(response_data, ns_id_flag='namespace_id')
        response_data = self._update_service_monitor_perm(response_data)
        return Response(response_data)

    def create(self, request, project_id, cluster_id):
        """ 创建 ServiceMonitor """
        params = self.params_validate(ServiceMonitorCreateSLZ)

        name, namespace = params['name'], params['namespace']
        endpoints = [
            {
                'path': params['path'],
                'interval': params['interval'],
                'port': params['port'],
                'params': params.get('params') or {},
            }
        ]
        manifest = {
            'apiVersion': 'monitoring.coreos.com/v1',
            'kind': 'ServiceMonitor',
            'metadata': {
                'labels': {
                    'release': 'po',
                    'io.tencent.paas.source_type': 'bcs',
                    'io.tencent.bcs.service_name': params['service_name'],
                },
                'name': name,
                'namespace': namespace,
            },
            'spec': {
                'endpoints': endpoints,
                'selector': {'matchLabels': params['selector']},
                'sampleLimit': params['sample_limit'],
            },
        }

        client = K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = self._single_service_monitor_operate_handler(
            client.create_service_monitor,
            _('创建'),
            project_id,
            BaseActivityType.Add,
            namespace,
            name,
            manifest,
            log_success=True,
        )
        return Response(result)

    @action(methods=['DELETE'], url_path='batch', detail=False)
    def batch_delete(self, request, project_id, cluster_id):
        """ 批量删除 ServiceMonitor """
        params = self.params_validate(ServiceMonitorBatchDeleteSLZ)
        svc_monitors = params['service_monitors']

        self._validate_namespace_use_perm(project_id, cluster_id, [sm['namespace'] for sm in svc_monitors])
        client = K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        for m in svc_monitors:
            self._single_service_monitor_operate_handler(
                client.delete_service_monitor, _('删除'), project_id, BaseActivityType.Delete, m['namespace'], m['name']
            )

        metrics_names = ','.join([f"{sm['namespace']}/{sm['name']}" for sm in svc_monitors])
        message = _('删除 Metrics: {} 成功').format(metrics_names)
        self._activity_log(
            project_id,
            request.user.username,
            metrics_names,
            message,
            BaseActivityType.Delete,
            BaseActivityStatus.Succeed,
        )
        return Response({'successes': svc_monitors})


class ServiceMonitorDetailViewSet(SystemViewSet, ServiceMonitorMixin):
    """ 单个 ServiceMonitor 相关操作 """

    lookup_field = 'name'

    def retrieve(self, request, project_id, cluster_id, namespace, name):
        """ 获取单个 ServiceMonitor """
        client = K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = client.get_service_monitor(namespace, name)
        if result.get('status') == 'Failure':
            raise error_codes.APIError(result.get('message', ''))

        labels = getitems(result, 'metadata.labels', {})
        result['metadata'] = {
            k: v for k, v in result['metadata'].items() if k not in constants.INNER_USE_SERVICE_METADATA_FIELDS
        }
        result['metadata']['service_name'] = labels.get(constants.SM_SERVICE_NAME_LABEL)

        if isinstance(getitems(result, 'spec.endpoints'), list):
            result['spec']['endpoints'] = self._handle_endpoints(result['spec']['endpoints'])

        return Response(result)

    def destroy(self, request, project_id, cluster_id, namespace, name):
        """ 删除 ServiceMonitor """
        self._validate_namespace_use_perm(project_id, cluster_id, namespace)
        client = K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = self._single_service_monitor_operate_handler(
            client.delete_service_monitor,
            _('删除'),
            project_id,
            BaseActivityType.Delete,
            namespace,
            name,
            manifest=None,
            log_success=True,
        )
        return Response(result)

    def update(self, request, project_id, cluster_id, namespace, name):
        """ 更新 ServiceMonitor (先删后增) """
        params = self.params_validate(ServiceMonitorUpdateSLZ)
        client = K8SClient(request.user.token.access_token, project_id, cluster_id, env=None)
        result = self._single_service_monitor_operate_handler(
            client.get_service_monitor, _('更新'), project_id, BaseActivityType.Retrieve, namespace, name
        )
        manifest = self._update_manifest(result, params)

        # 更新会合并 selector，因此先删除, 再创建
        self._single_service_monitor_operate_handler(
            client.delete_service_monitor, _('更新'), project_id, BaseActivityType.Delete, namespace, name
        )
        result = self._single_service_monitor_operate_handler(
            client.create_service_monitor,
            _('更新'),
            project_id,
            BaseActivityType.Add,
            namespace,
            name,
            manifest,
            log_success=True,
        )
        return Response(result)

    def _update_manifest(self, manifest: Dict, params: Dict) -> Dict:
        """ 使用 api 请求参数更新 manifest """
        manifest['metadata']['labels']['release'] = 'po'
        manifest['spec']['selector'] = {'matchLabels': params['selector']}
        manifest['spec']['sampleLimit'] = params['sample_limit']
        manifest['spec']['endpoints'] = [
            {
                'path': params['path'],
                'interval': params['interval'],
                'port': params['port'],
                'params': params.get('params') or {},
            }
        ]
        manifest['metadata'] = {
            k: v for k, v in manifest['metadata'].items() if k not in constants.INNER_USE_SERVICE_METADATA_FIELDS
        }
        return manifest
