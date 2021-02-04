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
import copy
import logging

from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets

from backend.apps import utils as app_utils
from backend.apps.application.base_views import BaseAPI
from backend.apps.application.utils import APIResponse
from backend.apps.configuration.k8s.serializers import K8sIngressSLZ
from backend.apps.constants import ClusterType
from backend.apps.instance.constants import K8S_INGRESS_SYS_CONFIG
from backend.apps.resource.views import ResourceOperate
from backend.components.bcs import k8s
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes

logger = logging.getLogger(__name__)


class IngressResource(viewsets.ViewSet, BaseAPI, ResourceOperate):
    def get_ingress_by_cluser_id(self, request, params, project_id, cluster_id):
        """查询configmaps"""
        access_token = request.user.token.access_token
        client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
        resp = client.get_ingress(params)

        if resp.get("code") != ErrorCode.NoError:
            logger.error(u"bcs_api error: %s" % resp.get("message", ""))
            return resp.get("code", ErrorCode.UnknownError), resp.get("message", _("请求出现异常!"))
        data = resp.get("data") or []
        return 0, data

    def get(self, request, project_id):
        """获取项目下的所有Ingress"""
        project_kind = request.project.kind
        project_kind_name = ClusterType.get(project_kind)

        if project_kind_name != 'Kubernetes':
            raise error_codes.CheckFailed(_("K8S项目才有Ingress"))

        cluster_dicts = self.get_project_cluster_info(request, project_id)
        cluster_data = cluster_dicts.get('results', {}) or {}

        # 获取命名空间的id
        namespace_dict = app_utils.get_ns_id_map(request.user.token.access_token, project_id)

        s_cate = 'K8sIngress'
        is_decode = False
        params = {}
        access_token = request.user.token.access_token
        data = []
        # 如果请求参数中cluster_id存在，根据cluster_id过滤集群信息
        query_cluster_id = request.query_params.get("cluster_id")
        if query_cluster_id:
            cluster_data = [info for info in cluster_data if query_cluster_id == info.get('cluster_id')]

        for cluster_info in cluster_data:
            cluster_id = cluster_info.get('cluster_id')
            cluster_env = cluster_info.get('environment')
            code, cluster_data = self.get_ingress_by_cluser_id(request, params, project_id, cluster_id)
            # 单个集群错误时，不抛出异常信息
            if code != ErrorCode.NoError:
                continue
            self.handle_data(
                request,
                cluster_data,
                project_kind,
                s_cate,
                access_token,
                project_id,
                cluster_id,
                is_decode,
                cluster_env,
                cluster_info.get('name', ''),
                namespace_dict=namespace_dict,
            )
            data += cluster_data

        # 按时间倒序排列
        data.sort(key=lambda x: x.get('createTime', ''), reverse=True)

        return APIResponse({"code": ErrorCode.NoError, "data": {"data": data, "length": len(data)}, "message": "ok"})

    def delete_ingress(self, request, project_id, cluster_id, namespace, name):
        self.category = 'ingress'
        self.k8s_cate = 'K8sIngress'
        return self.delete_resource(request, project_id, cluster_id, namespace, name)

    def batch_delete_ingress(self, request, project_id):
        self.category = 'ingress'
        self.k8s_cate = 'K8sIngress'
        return self.batch_delete_resource(request, project_id)

    def update_ingress(self, request, project_id, cluster_id, namespace, name):
        self.category = 'ingress'
        self.k8s_cate = 'K8sIngress'
        self.k8s_slz = K8sIngressSLZ
        self.k8s_sys_config = K8S_INGRESS_SYS_CONFIG
        return self.update_resource(request, project_id, cluster_id, namespace, name)
