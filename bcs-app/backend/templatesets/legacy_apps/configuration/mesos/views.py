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
"""
import json

from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.uniapps.application.constants import MESOS_KIND
from backend.uniapps.network.models import MesosLoadBlance
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer

from .. import models
from ..constants import MesosResourceName
from ..mixins import GetVersionedEntity


class ApplicationView(viewsets.ViewSet, GetVersionedEntity):
    """"""

    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list_apps(self, request, project_id, version_id):
        """查看模板集指定版本的 Application 列表"""
        ventity = self.get_versioned_entity(project_id, version_id)
        return Response(ventity.get_mesos_apps())

    def list_container_ports(self, request, project_id, version_id):
        """查看模板集指定版本的端口信息"""
        ventity = self.get_versioned_entity(project_id, version_id)

        app_ids = request.GET.get('app_ids')
        if not app_ids:
            raise error_codes.ValidateError(_("请选择关联的应用"))

        app_id_list = app_ids.split(',')
        ports = ventity.get_version_ports(app_id_list)
        return Response(ports)

    def check_port_associated_with_service(self, request, project_id, version_id, port_id):
        """检查指定的 port 是否被 service 关联"""
        ventity = self.get_versioned_entity(project_id, version_id)
        svc_id_list = ventity.get_resource_id_list(MesosResourceName.service.value)
        svc_qsets = models.Service.objects.filter(id__in=svc_id_list)
        for svc in svc_qsets:
            ports = svc.get_ports_config()
            for p in ports:
                if str(p.get('id')) == str(port_id):
                    raise error_codes.APIError(_("端口在 Service[{}] 中已经被关联,不能删除").format(svc.name))
        return Response({})

    def list_configmaps(self, request, project_id, version_id):
        """查看模板集指定版本的configmap信息"""
        ventity = self.get_versioned_entity(project_id, version_id)
        return Response(ventity.get_configmaps_by_kind(MESOS_KIND))

    def list_secrets(self, request, project_id, version_id):
        """查看模板集指定版本的configmap信息"""
        ventity = self.get_versioned_entity(project_id, version_id)
        return Response(ventity.get_secrets_by_kind(MESOS_KIND))

    def get_lbs(self, request, project_id, cluster_id):
        """查询 namespace 下的 loadbalance 信息
        NOTE: 允许使用集群下的所有的LB，因此，不需要传递命名空间信息
        """
        lb_records = MesosLoadBlance.objects.filter(project_id=project_id, cluster_id=cluster_id, is_deleted=False)
        lb_list = []
        for lb in lb_records:
            lb_data = json.loads(lb.data_dict)
            # 兼容已经存在记录，获取BCSGROUP赋值到lb_name，新建lb中lb name和BCSGROUP值相同
            lb_list.append({"lb_id": lb.id, "lb_name": lb_data.get("BCSGROUP") or lb.name})
        return Response(lb_list)


class DeploymentView(viewsets.ViewSet, GetVersionedEntity):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id, version_id):
        """查看模板集指定版本的 Deployment 列表"""
        ventity = self.get_versioned_entity(project_id, version_id)
        return Response(ventity.get_mesos_deploys())


class ServiceView(viewsets.ViewSet, GetVersionedEntity):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list_services(self, request, project_id, version_id):
        ventity = self.get_versioned_entity(project_id, version_id)
        return Response(ventity.get_mesos_services())
