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
import logging

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer

from backend.accounts import bcs_perm
from backend.bcs_web.audit_log import client
from backend.components import paas_cc
from backend.uniapps.network.clb import constants as clb_constants
from backend.uniapps.network.clb import serializers
from backend.uniapps.network.clb import utils as clb_utils
from backend.uniapps.network.clb.models import CloudLoadBlancer
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer


class DescribeCLBNamesViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id):
        data = clb_utils.describe_clb_detail(
            request.user.token.access_token,
            request.user.username,
            request.project.cc_app_id,
            request.query_params.get('region'),
        )
        return response.Response(data.keys())


class CLBListCreateViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def add_status_and_cluster_name(self, request, project_id, data):
        # 只有已经启动的clb，才能查询到状态
        cluster_id_list = [info['cluster_id'] for info in data]
        clb_dict = {}
        for cluster_id in cluster_id_list:
            clb_dict.update(
                clb_utils.get_deployments(
                    request.user.token.access_token, project_id, request.project.kind, cluster_id
                )
            )
        # add status and cluster_name to data
        cluster_id_names = clb_utils.get_cluster_id_names_map(request.user.token.access_token, project_id)
        for info in data:
            filter_key = (info['cluster_id'], info['resource_name'])
            info['cluster_name'] = cluster_id_names.get(info['cluster_id']) or ''
            if filter_key in clb_dict:
                info.update(clb_dict[filter_key])
        return data

    def list(self, request, project_id):
        cluster_id = request.query_params.get("cluster_id")
        data = CloudLoadBlancer.objects.get_clb_list(project_id, cluster_id=cluster_id)
        data = self.add_status_and_cluster_name(request, project_id, data)

        # 添加权限
        data = bcs_perm.Cluster.hook_perms(request, project_id, data)

        return response.Response(data)

    def get_vpc_id(self, request, region, clb_name):
        data = clb_utils.describe_clb_detail(
            request.user.token.access_token, request.user.username, request.project.cc_app_id, region
        )
        if clb_name not in data:
            raise error_codes.CheckFailed(f'clb:[{clb_name}] not found')
        return data[clb_name]['vpc_id']

    def create(self, request, project_id):
        slz = serializers.CreateCLBSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        # 校验集群权限
        clb_utils.can_use_cluster(request, project_id, data['cluster_id'])

        # 通过clb_name渲染deployment
        # 替换clb中的'_'为'-', 后缀使用6位随机字符,并且长度限制为253以内，以满足后台的限制
        # resource_name包含: clb_name[:246] + '-' + random(6)
        replaced_name = data['clb_name'].replace('_', '-')
        data['resource_name'] = f'{replaced_name[:246]}-{get_random_string(6).lower()}'
        data['creator'] = data['updator'] = request.user.username
        data['project_id'] = request.project.project_id
        data['vpc_id'] = self.get_vpc_id(request, data['region'], data['clb_name'])

        # 创建并返回记录
        with client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource=data['clb_name'],
            description=_("集群:{}, 创建云lb controler").format(data['cluster_id']),
        ).log_add():
            record = CloudLoadBlancer.objects.create(data)
            data = CloudLoadBlancer.objects.parse_record(record)

        return response.Response(data)


class MesosCLBOperateViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def update_clb_status(self, clb_id, status):
        CloudLoadBlancer.objects.filter(id=clb_id).update(status=status)

    def post(self, request, project_id, clb_id):
        # 获取配置
        record = CloudLoadBlancer.objects.retrieve_record(clb_id)
        # 校验使用集群权限
        clb_utils.can_use_cluster(request, project_id, record['cluster_id'])
        # 获取 repo 地址
        repo_domain = paas_cc.get_jfrog_domain(request.user.token.access_token, project_id, record['cluster_id'])
        if not repo_domain:
            repo_domain = settings.DEFAUT_MESOS_LB_JFROG_DOMAIN
        record['repo_domain'] = repo_domain
        mesos_json = json.loads(render_to_string('mesos.json', record))

        with client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource=record['resource_name'],
            description=_("集群:{}, 创建clb关联deployment:{}").format(record['cluster_id'], record['resource_name']),
        ).log_add():
            clb_utils.create_mesos_deployment(
                request.user.token.access_token, project_id, record['cluster_id'], record['namespace'], mesos_json
            )
        # 更改状态
        self.update_clb_status(clb_id, clb_constants.CLB_CREATED_STATUS)

        return response.Response()

    def delete(self, request, project_id, clb_id):
        record = CloudLoadBlancer.objects.retrieve_record(clb_id)
        # 校验使用集群权限
        clb_utils.can_use_cluster(request, project_id, record['cluster_id'])

        with client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource=record['resource_name'],
            description=_("集群:{}, 删除clb关联deployment:{}").format(record['cluster_id'], record['resource_name']),
        ).log_delete():
            clb_utils.delete_mesos_deployment(
                request.user.token.access_token,
                project_id,
                record['cluster_id'],
                record['namespace'],
                record['resource_name'],
            )
        # 更新状态
        self.update_clb_status(clb_id, clb_constants.CLB_DELETED_STATUS)

        return response.Response()


class CLBRetrieveOperateViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def add_status(self, request, data):
        if data['status'] != clb_constants.CLB_CREATED_STATUS:
            return data
        deployment_status = clb_utils.get_deployments(
            request.user.token.access_token,
            data['project_id'],
            request.project.kind,
            data['cluster_id'],
            name=data['resource_name'],
        )
        data.update(deployment_status)
        return data

    def retrieve(self, request, project_id, clb_id):
        data = CloudLoadBlancer.objects.retrieve_record(clb_id)
        data = self.add_status(request, data)
        # 添加集群名称
        data['cluster_name'] = clb_utils.get_cluster_name(
            request.user.token.access_token, project_id, data['cluster_id']
        )

        return response.Response(data)

    def delete(self, request, project_id, clb_id):
        # 获取操作对象
        record = CloudLoadBlancer.objects.retrieve(clb_id)
        if record.status not in clb_constants.ALLOW_UPDATE_DELETE_STATUS_LIST:
            raise error_codes.CheckFailed(_('当前clb状态不允许进行删除操作'))
        # 校验使用集群权限
        clb_utils.can_use_cluster(request, project_id, record.cluster_id)

        with client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource=record.clb_name,
            description=_("集群:{}, 删除clb:{}").format(record.cluster_id, record.clb_name),
        ).log_delete():
            record.delete()

        return response.Response()

    def update(self, request, project_id, clb_id):
        slz = serializers.UpdateCLBSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        # 校验使用集群权限
        clb_utils.can_use_cluster(request, project_id, data['cluster_id'])

        with client.ContextActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='lb',
            resource=data['clb_name'],
            description=_("集群:{}, 更新clb:{}").format(data['cluster_id'], data['clb_name']),
        ).log_delete():
            CloudLoadBlancer.objects.update(clb_id, data)
            data = CloudLoadBlancer.objects.retrieve_record(clb_id)

        return response.Response(data)


class CLBStatusViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def compose_data(self, listeners):
        data = []
        for info in listeners:
            item = {'name': info['Name'], 'port': info['listenPort'], 'rules': info['healthStatus']['rules']}
            data.append(item)
        return data

    def retrieve_status(self, request, project_id, clb_id):
        record = CloudLoadBlancer.objects.retrieve_record(clb_id)
        status_detail = clb_utils.request_clb_status(request, project_id, record)
        remote_listeners = status_detail.get('remoteListeners') or []
        data = self.compose_data(remote_listeners)
        return response.Response(data)


class GetCLBRegionsViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request, project_id):
        data = clb_utils.get_clb_region_list(
            request.user.token.access_token,
        )
        return response.Response(data)
