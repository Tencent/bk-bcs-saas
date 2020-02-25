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
import copy
import arrow
import logging

from django.utils import timezone
from rest_framework import viewsets, response
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import BrowsableAPIRenderer
from django.utils.translation import ugettext_lazy as _

from backend.activity_log import client as log_client
from backend.accounts import bcs_perm
from backend.components.bcs import mesos
from backend.utils.basic import getitems
from backend.utils.renderers import BKAPIRenderer
from backend.apps.network import utils as network_utils
from backend.apps.instance.models import InstanceConfig
from backend.apps.instance.generator import IngressProfileGenerator
from backend.apps.instance.constants import INGRESS_SYS_CONFIG
from backend.apps.instance.funutils import update_nested_dict, render_mako_context

logger = logging.getLogger(__name__)

DEFAULT_NAMESPACE_ID = -1
CLB_NAME_LABEL = 'bmsf.tencent.com/clbname'
CLB_REGION_LABEL = 'io.tencent.bcs.clb.region'


class BaseIngress(viewsets.ViewSet):

    def get_project_namespaces(self, request, project_id):
        namespaces = network_utils.get_project_namespaces(request.user.token.access_token, project_id)
        return {(info['cluster_id'], info['name']): info for info in namespaces}

    def get_cluster_namespaces(self, request, project_id, cluster_id):
        namespaces = network_utils.get_cluster_namespaces(request.user.token.access_token, project_id, cluster_id)
        return {info['name']: info for info in namespaces}


class IngressListViewSet(BaseIngress):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_clusters(self, request, project_id):
        clusters = network_utils.get_project_clusters(request.user.token.access_token, project_id)
        return {info['cluster_id']: info for info in clusters}

    def list(self, request, project_id):
        """通过项目或集群拉取ingress
        """
        cluster_id = request.query_params.get('cluster_id')
        project_clusters = self.get_clusters(request, project_id)
        project_namespaces = self.get_project_namespaces(request, project_id)
        cluster_id_list = [cluster_id] if cluster_id else project_clusters.keys()
        # 通过集群拉取ingress数据
        ingress_list = []
        for cluster_id in cluster_id_list:
            try:
                # 不抛出异常，返回为空
                data = network_utils.get_cluster_ingresses(request.user.token.access_token, project_id, cluster_id)
            except Exception as err:
                logger.error(_("获取集群ingress信息异常，{}").format(err))
                continue
            for info in data:
                create_time = getitems(info, ['metadata', 'creationTimestamp'])
                if create_time:
                    d_time = arrow.get(create_time).datetime
                    create_time = timezone.localtime(d_time).strftime('%Y-%m-%d %H:%M:%S')
                update_time = getitems(info, ['metadata', 'annotations', 'io.tencent.paas.updateTime'])
                namespace_name = getitems(info, ['metadata', 'namespace'], default='')
                namespace_id = project_namespaces.get((cluster_id, namespace_name), {}).get('id', DEFAULT_NAMESPACE_ID)
                ingress_list.append({
                    'name': getitems(info, ['metadata', 'name'], default=''),
                    'namespace': namespace_name,
                    'namespace_id': namespace_id,
                    'cluster_id': cluster_id,
                    'spec': info['spec'],
                    'config': info,
                    'cluster_name': project_clusters[cluster_id]['name'],
                    'environment': project_clusters[cluster_id]['environment'],
                    'create_time': create_time,
                    'update_time': update_time if update_time else create_time
                })
        if ingress_list:
            # 检查是否用命名空间的使用权限
            perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES)
            ingress_list = perm.hook_perms(ingress_list, ns_id_flag='namespace_id', ns_name_flag='namespace')
            # 按照更新时间排序
            ingress_list.sort(key=lambda info: info['update_time'], reverse=True)

        return response.Response(ingress_list)


class IngressRetrieveOperteViewSet(BaseIngress):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def can_view(self, request, project_id, cluster_id, namespace_id):
        perm = bcs_perm.Namespace(request, project_id, namespace_id, cluster_id=cluster_id)
        perm.can_view(raise_exception=True)

    def can_use(self, request, project_id, cluster_id, namespace_id):
        perm = bcs_perm.Namespace(request, project_id, namespace_id, cluster_id=cluster_id)
        perm.can_use(raise_exception=True)

    def get_namespace_id(self, request, project_id, cluster_id, namespace, name):
        cluster_namespaces = self.get_cluster_namespaces(request, project_id, cluster_id)
        namespace_id = cluster_namespaces.get(namespace, {}).get('id')
        if not namespace_id:
            raise ValidationError(_("命名空间查询不到，请确认是否通过平台创建或者已经同步"))
        return namespace_id

    def retrieve(self, request, project_id, cluster_id, namespace, name):
        namespace_id = self.get_namespace_id(request, project_id, cluster_id, namespace, name)
        # 校验查看权限
        self.can_view(request, project_id, cluster_id, namespace_id)
        client = mesos.MesosClient(
            request.user.token.access_token, project_id, cluster_id, env=None)
        result = client.get_custom_resource(name, namespace)
        data = {
            'name': name,
            'namespace': namespace,
            'namespace_id': namespace_id,
            'cluster_id': cluster_id,
            'clb_name': getitems(result, ['metadata', 'labels', CLB_NAME_LABEL], default=''),
            'clb_region': getitems(result, ['metadata', 'labels', CLB_REGION_LABEL], default=''),
            'spec': result['spec'],
            'config': result
        }
        return response.Response(data)

    def delete(self, request, project_id, cluster_id, namespace, name):
        namespace_id = self.get_namespace_id(request, project_id, cluster_id, namespace, name)
        # 校验查看权限
        self.can_use(request, project_id, cluster_id, namespace_id)
        with log_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='ingress',
            resource=name,
            description=_("集群:{}, 删除mesos ingress:{}").format(cluster_id, name)
        ).log_delete():
            client = mesos.MesosClient(
                request.user.token.access_token, project_id, cluster_id, env=None)
            client.delete_custom_resource(name, namespace)
        # 删除成功则更新记录
        now_time = timezone.now()
        InstanceConfig.objects.filter(
            namespace=namespace_id, category='ingress', name=name
        ).update(
            updator=request.user.username,
            updated=now_time,
            deleted_time=now_time,
            is_deleted=True,
            is_bcs_success=True
        )

        return response.Response()

    def update(self, request, project_id, cluster_id, namespace, name):
        namespace_id = self.get_namespace_id(request, project_id, cluster_id, namespace, name)
        # 校验查看权限
        self.can_use(request, project_id, cluster_id, namespace_id)
        config = request.data['config']
        # 下发配置
        with log_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='ingress',
            resource=name,
            description=_("集群:{}, 更新mesos ingress:{}").format(cluster_id, name)
        ).log_modify():
            client = mesos.MesosClient(
                request.user.token.access_token, project_id, cluster_id, env=None)
            client.update_custom_resource(name, namespace, config)
        # 集群，命名空间，ingress确定唯一
        InstanceConfig.objects.filter(
            namespace=namespace_id, category='ingress', name=name, is_deleted=False
        ).update(
            updator=request.user.username,
            updated=timezone.now(),
            is_bcs_success=True,
            config=config
        )
        return response.Response()
