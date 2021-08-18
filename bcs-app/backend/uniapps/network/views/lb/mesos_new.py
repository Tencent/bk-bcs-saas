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
import copy
import json
import logging

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from backend.bcs_web.audit_log import client as activity_client
from backend.uniapps.network.models import MesosLoadBlance as MesosLoadBalancer
from backend.uniapps.network.views.lb import constants as mesos_lb_constants
from backend.uniapps.network.views.lb import serializers as lb_slz
from backend.utils.renderers import BKAPIRenderer

from . import utils as lb_utils

logger = logging.getLogger(__name__)


class LoadBalancersViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id):
        cluster_id = request.query_params.get("cluster_id")
        queryset = MesosLoadBalancer.objects.filter(project_id=project_id, is_deleted=False).order_by("-updated")
        if cluster_id:
            queryset = queryset.filter(cluster_id=cluster_id)
        slz = lb_slz.MesosLBSLZ(queryset, many=True)
        data = slz.data
        lbs = {lb.id: lb for lb in queryset}
        # 添加lb对应的deployment和application状态
        access_token = request.user.token.access_token
        for item in data:
            item.update(
                lb_utils.get_mesos_lb_status_detail(
                    access_token,
                    project_id,
                    item["cluster_id"],
                    item["namespace"],
                    item["name"],
                    item["status"],
                    lb_obj=lbs[item["id"]],
                )
            )
        return Response(data)

    def create(self, request, project_id):
        """创建lb
        1. 下发service
        2. 下发deployment
        """
        slz = lb_slz.CreateOrUpdateMesosLBSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.data

        # 保存数据，便于后续下发时，组装下发配置
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type="lb",
            resource=data["name"],
            extra=json.dumps(data),
        ).log_add():
            MesosLoadBalancer.objects.create(
                project_id=project_id,
                cluster_id=data["cluster_id"],
                name=data["name"],
                ip_list=json.dumps(data["ip_list"]),
                data_dict=json.dumps(data),
                status=mesos_lb_constants.MESOS_LB_STATUS.NOT_DEPLOYED.value,
                namespace=data["namespace"],
            )

        return Response()


class LoadBalancerViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_lb_queryset(self, project_id, cluster_id, namespace, name):
        lbs = MesosLoadBalancer.objects.filter(
            project_id=project_id, cluster_id=cluster_id, namespace=namespace, name=name
        )
        if not lbs.exists():
            raise ValidationError(_("没有查询到集群{}-命名空间{}-名称{}下的LB记录").format(cluster_id, namespace, name))
        return lbs

    def update_record(self, request, project_id, cluster_id, namespace, name):
        """更新执行集群+namespace+name的lb记录"""
        lb_queryset = self.get_lb_queryset(project_id, cluster_id, namespace, name)
        # 仅允许LB处于未部署状态时，才允许编辑
        if lb_queryset.first().status not in [
            mesos_lb_constants.MESOS_LB_STATUS.NOT_DEPLOYED.value,
            mesos_lb_constants.MESOS_LB_STATUS.STOPPED.value,
        ]:
            raise ValidationError(_("LB必须处于未部署状态或停用状态，当前状态不允许更新"))

        # 获取数据
        slz = lb_slz.CreateOrUpdateMesosLBSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.data

        # 更新属性
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type="lb",
            resource=name,
            extra=json.dumps(data),
            description=_("更新Mesos LB, 集群: {},命名空间: {},名称: {}").format(cluster_id, namespace, name),
        ).log_modify():
            lb_queryset.update(ip_list=json.dumps(data["ip_list"]), data_dict=json.dumps(data))

        return Response()

    def delete_record(self, request, project_id, cluster_id, namespace, name):
        lb_queryset = self.get_lb_queryset(project_id, cluster_id, namespace, name)
        # 仅允许LB处于未部署状态时，才允许删除
        if lb_queryset.first().status not in [
            mesos_lb_constants.MESOS_LB_STATUS.NOT_DEPLOYED.value,
            mesos_lb_constants.MESOS_LB_STATUS.STOPPED.value,
        ]:
            raise ValidationError(_("LB必须处于未部署状态或停用状态，当前状态不允许更新"))

        # 删除记录
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type="lb",
            resource=name,
            description=_("删除Mesos LB, 集群: {},命名空间: {},名称: {}").format(cluster_id, namespace, name),
        ).log_delete():
            lb_queryset.delete()

        return Response()

    def lb_detail(self, request, project_id, cluster_id, namespace, name):
        """查询LB的详情，包含实时状态
        需要查询状态，如果处于部署中或者删除中，需要根据对应的deployment状态更新LB状态
        """
        lb_queryset = self.get_lb_queryset(project_id, cluster_id, namespace, name)
        lb = lb_queryset.first()

        slz = lb_slz.MesosLBSLZ(lb)
        lb_detail = dict(slz.data)
        # 查询deployment状态
        access_token = request.user.token.access_token
        lb_detail.update(
            lb_utils.get_mesos_lb_status_detail(access_token, project_id, cluster_id, namespace, name, lb.status)
        )
        lb_queryset.update(status=lb_detail["status"])
        return Response(lb_detail)

    def deploy(self, request, project_id, cluster_id, namespace, name):
        """部署LB到集群"""
        lb_queryset = self.get_lb_queryset(project_id, cluster_id, namespace, name)
        lb = lb_queryset.first()

        access_token = request.user.token.access_token
        # 组装下发配置
        lb_conf = lb_utils.MesosLBConfig(access_token, project_id, cluster_id, lb)
        svc_conf = lb_conf._service_config()
        deploy_conf = lb_conf._deployment_config()

        # 创建lb，包含service和deployment
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type="lb",
            resource=name,
            description=_("启动Mesos LoadBalancer"),
        ).log_start():
            lb_utils.deploy_mesos_lb(access_token, project_id, cluster_id, svc_conf, deploy_conf)
            lb_queryset.update(status=mesos_lb_constants.MESOS_LB_STATUS.DEPLOYING.value)
        return Response()

    def stop(self, request, project_id, cluster_id, namespace, name):
        """LB停止服务
        删除对应的deployment和service
        """
        lb_queryset = self.get_lb_queryset(project_id, cluster_id, namespace, name)
        lb = lb_queryset.first()

        access_token = request.user.token.access_token
        # 创建lb，包含service和deployment
        with activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type="lb",
            resource=name,
            description=_("启动Mesos LoadBalancer"),
        ).log_stop():
            lb_utils.stop_mesos_lb(access_token, project_id, cluster_id, lb.namespace, lb.name)
            lb_queryset.update(status=mesos_lb_constants.MESOS_LB_STATUS.STOPPING.value)

        return Response()
