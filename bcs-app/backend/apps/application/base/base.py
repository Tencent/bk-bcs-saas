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
import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import views

from backend.apps.application import constants
from backend.apps.application.utils import cluster_env
from backend.apps.configuration.models import Template
from backend.apps.instance.models import InstanceConfig, VersionInstance
from backend.components import paas_cc
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes


class BaseAPI(views.APIView):
    def project_kind(self, request):
        """
        处理项目project info
        """
        kind = request.project.get("kind")
        if kind not in [constants.K8S_KIND, constants.MESOS_KIND]:
            raise error_codes.CheckFailed(_("项目类型必须为k8s/mesos, 请确认后重试!"))
        return kind

    def get_params(self, request):
        """获取请求参数"""
        name = request.GET.get("name")
        namespace = request.GET.get("namespace")
        category = request.GET.get("category")
        if not (name and namespace and category):
            raise error_codes.CheckFailed(_("参数[name]、[namespace]、[category]不能为空"))
        return name, namespace, category

    def get_project_cluster_info(self, request, project_id):
        """获取项目下所有集群信息"""
        resp = paas_cc.get_all_clusters(request.user.token.access_token, project_id, desire_all_data=1)
        if resp.get("code") != ErrorCode.NoError:
            raise error_codes.apierror.f(resp.get("message"))
        return resp.get("data") or {}

    def get_cluster_id_env(self, request, project_id):
        """获取集群和环境"""
        data = self.get_project_cluster_info(request, project_id)
        if not data.get("results"):
            return {}
        cluster_results = data.get("results") or []
        return {
            info["cluster_id"]: {
                "cluster_name": info["name"],
                "cluster_env": cluster_env(info["environment"]),
                "cluster_env_str": cluster_env(info["environment"], ret_num_flag=False),
            }
            for info in cluster_results
            if not info["disabled"]
        }

    def get_request_category(self, request, project_kind):
        """获取请求类型"""
        category = None
        if project_kind == constants.K8S_KIND:
            category = request.GET.get("category")
            if not category:
                raise error_codes.CheckFailed(_("应用类型不能为空"))
        return category


class BaseMetric(views.APIView):
    def get_filter_params(self, request):
        """获取过滤参数"""
        cluster_type = request.GET.get("cluster_type")
        if not cluster_type or cluster_type not in constants.CLUSTER_TYPE:
            raise error_codes.CheckFailed(_("集群类型不正确，请确认后重试!"))
        app_status = request.GET.get("app_status")
        if app_status and app_status not in constants.APP_STATUS:
            raise error_codes.CheckFailed(_("应用状态不正确，请确认后重试!"))
        tmpl_set_id = request.GET.get("muster_id")
        app_id = request.GET.get("app_id")
        ns_id = request.GET.get("ns_id")

        return cluster_type, app_status, tmpl_set_id, app_id, ns_id

    def get_filter_tmpl_set(self, project_id, tmpl_set_id):
        """获取模板集"""
        all_tmpl_set = Template.objects.filter(project_id=project_id, is_deleted=False).order_by(
            "-updated", "-created"
        )
        if tmpl_set_id:
            all_tmpl_set = all_tmpl_set.filter(id=tmpl_set_id)
        return all_tmpl_set

    def get_filter_version_instances(self, tmpl_set_id_list):
        """根据模板集获取相应的版本实例"""
        version_inst = VersionInstance.objects.filter(template_id__in=tmpl_set_id_list, is_deleted=False)
        version_inst_id_tmpl_set_id_map = {info.id: info.template_id for info in version_inst}
        return version_inst_id_tmpl_set_id_map

    def get_filter_insts(self, version_inst_ids, category=None):
        """获取实例"""
        all_insts = InstanceConfig.objects.filter(instance_id__in=version_inst_ids, is_deleted=False)
        if category:
            all_insts.filter(category__in=category)
        ret_data = []
        for info in all_insts:
            conf = json.loads(info.config)
            metadata = conf.get("metadata") or {}
            labels = metadata.get("labels") or {}
            cluster_id = labels.get("io.tencent.bcs.clusterid")
            if not cluster_id:
                continue
            ret_data.append(
                {"id": info.id, "version_inst_id": info.instance_id, "cluster_id": cluster_id, "name": info.name}
            )
        return ret_data

    def get_category(self, request, kind):
        """获取类型"""
        category = request.GET.get("category")
        if kind == constants.K8S_KIND:
            if not category:
                raise error_codes.CheckFailed(_("应用类型不能为空"))
            else:
                if category not in constants.CATEGORY_MAP:
                    raise error_codes.CheckFailed(_("类型不正确，请确认"))
                category = [constants.CATEGORY_MAP[category]]
        else:
            category = constants.MESOS_APPLICATION_TYPE
        return category

    def get_inst_name(self, inst_id):
        """根据实例ID获取实例名称"""
        if not inst_id:
            return None
        inst_info = InstanceConfig.objects.filter(id=inst_id, is_deleted=False)
        if inst_info:
            return inst_info[0].name
        else:
            return None
