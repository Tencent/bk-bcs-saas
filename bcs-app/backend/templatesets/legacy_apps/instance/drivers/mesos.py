# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

mesos底层API调用
"""
import logging

from django.utils.translation import ugettext_lazy as _

from backend.components.bcs import mesos
from backend.utils.error_codes import error_codes
from backend.utils.exceptions import ComponentError, Rollback

from .base import SchedulerBase

logger = logging.getLogger(__name__)


class Scheduler(SchedulerBase):
    def clean_ports(self, ports):
        """
        - containerPort
        - hostPort
        - protocol
        - name
        """
        clean_ports = []
        for port in ports:
            if port['containerPort'] and port['protocol']:
                clean_ports.append(port)
        return clean_ports

    def clean_service_ports(self, ports):
        """
        - servicePort
        - targetPort
        - protocol
        - name
        - path
        - domainName
        """
        clean_ports = []
        for port in ports:
            if port['servicePort'] and port['protocol'] and port['targetPort']:
                clean_ports.append(port)
        return clean_ports

    def clean_labels(self, labels):
        clean_labels = {}
        for k, v in labels.items():
            if k and v:
                clean_labels[k] = v
        return clean_labels

    def clean_volumes(self, volumes):
        pass

    def ensure_configmap(self, ns, cluster_id, configmap):
        """
        创建secret
        """
        datas = {}
        for item in configmap['items']:
            key = item.pop('dataKey')
            datas[key] = item

        spec = {
            'apiVersion': 'v4',
            'kind': 'configmap',
            'metadata': {'name': configmap['name'], 'namespace': ns, 'labels': {}},
            'datas': datas,
        }
        self.handler_configmap(ns, cluster_id, spec)

    def ensure_secret(self, ns, cluster_id, secret):
        """
        创建secret
        """
        datas = {}
        for item in secret['items']:
            key = item.pop('dataKey')
            datas[key] = item
        spec = {
            'apiVersion': 'v4',
            'kind': 'secret',
            'metadata': {'name': secret['secretName'], 'namespace': ns, 'labels': {}},
            'type': '',
            'datas': datas,
        }
        self.handler_secret(ns, cluster_id, spec)

    def handler_application(self, ns, cluster_id, spec):
        """
        - 去除空的配置项，非必须
        - container['ports'] 必须是有效值
        - configmap 必须先创建
        - secrets 必须先创建
        """
        # for container in spec['spec']['template']['spec']['containers']:
        #     container['ports'] = self.clean_ports(container['ports'])
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.create_application(ns, spec)
        if result.get('code') != 0:
            logger.warning('create application failed, %s, will try rollback.', result)
            raise Rollback(result)

    def rollback_application(self, ns, cluster_id, spec):
        name = spec['metadata']['name']
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.delete_mesos_app_instance(ns, name)
        if result.get('code') != 0:
            raise ComponentError(result.get('message', ''))

    def handler_update_application(self, ns, cluster_id, spec):
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.update_application(cluster_id, ns, spec)
        if result.get('code') != 0:
            raise error_codes.ComponentError(_("更新application失败，{}").format(result.get('message')))

    def handler_deployment(self, ns, cluster_id, spec):
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.create_deployment(ns, spec)
        if result.get('code') != 0:
            logger.warning('create deployment failed, %s, will try rollback.', result)
            raise Rollback(result)

    def rollback_deployment(self, ns, cluster_id, spec):
        name = spec['metadata']['name']
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.delete_deployment(ns, name)
        if result.get('code') != 0:
            raise ComponentError(result.get('message', ''))

    def handler_service(self, ns, cluster_id, spec):
        """
        - ports必须是有效值
        """
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.create_service(ns, spec)
        if result.get('code') != 0:
            logger.warning('create service failed, %s, will try rollback.', result)
            raise Rollback(result)

    def handler_update_service(self, ns, cluster_id, spec):
        """"""
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.update_service(ns, spec)
        if result.get('code') != 0:
            raise error_codes.ComponentError(_("更新service失败，{}".format(result.get('message'))))

    def rollback_service(self, ns, cluster_id, spec):
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        name = spec['metadata']['name']
        result = client.delete_service(ns, name)
        if result.get('code') != 0:
            raise ComponentError(result.get('message', ''))

    def handler_lb(self, ns, cluster_id, spec):
        """负载均衡"""

    def handler_configmap(self, ns, cluster_id, spec):
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.create_configmap(ns, spec)
        if result.get('code') != 0:
            logger.warning('create configmap failed, %s, will try rollback.', result)
            raise Rollback(result)

    def handler_update_configmap(self, ns, cluster_id, spec):
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.update_configmap(ns, spec)
        if result.get('code') != 0:
            raise ComponentError(_("更新configmap失败，{}".format(result.get('message'))))

    def rollback_configmap(self, ns, cluster_id, spec):
        name = spec['metadata']['name']
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.delete_configmap(ns, name)
        if result.get('code') != 0:
            raise ComponentError(result.get('message', ''))

    def handler_secret(self, ns, cluster_id, spec):
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.create_secret(ns, spec)
        if result.get('code') != 0:
            logger.warning('create secret failed, %s, will try rollback.', result)
            raise Rollback(result)

    def handler_update_secret(self, ns, cluster_id, spec):
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.update_secret(ns, spec)
        if result.get('code') != 0:
            raise ComponentError(_("更新secret失败，{}").format(result.get('message')))

    def rollback_secret(self, ns, cluster_id, spec):
        """删除使用"""
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        name = spec['metadata']['name']
        result = client.delete_secret(ns, name)
        if result.get('code') != 0:
            raise ComponentError(result.get('message', ''))

    def handler_metric(self, ns, cluster_id, spec):
        """绑定metric"""
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.set_metrics(data=spec)
        if result.get('code') != 0:
            logger.warning('set metric failed, %s, will try rollback.', result)
            raise Rollback(result)

    def handler_hpa(self, ns, cluster_id, spec):
        """绑定metric"""
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        result = client.apply_hpa(ns, spec=spec)
        if result.get('code') != 0:
            logger.warning('set metric failed, %s, will try rollback.', result)
            raise ComponentError(result.get('message', ''))

    def rollback_metric(self, ns, cluster_id, spec):
        """回滚metric"""
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        name = spec['name']
        result = client.delete_metrics(namespace=ns, metric_name=name)
        if result.get('code') != 0:
            raise ComponentError(result.get('message', ''))

    def handler_ingress(self, namespace, cluster_id, spec):
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        client.create_custom_resource(namespace, spec)

    def rollback_ingress(self, namespace, cluster_id, spec):
        """回滚metric"""
        client = mesos.MesosClient(self.access_token, self.project_id, cluster_id, env=None)
        name = spec['metadata']['name']
        client.delete_custom_resource(name, namespace)
