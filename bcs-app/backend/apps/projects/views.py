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

from rest_framework import viewsets
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from django.conf import settings

from backend.activity_log import client
from backend.apps import constants as app_constants
from backend.apps.projects import serializers
from backend.components import cc, paas_cc, paas_auth
from backend.utils import notify
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.utils.renderers import BKAPIRenderer
from backend.utils.cache import region
from backend.apps.configuration.init_data import init_template
from backend.apps.projects.utils import start_tasks_for_project, get_app_by_user_role, get_application_name
from backend.apps.projects.drivers.base import BaseDriver
from backend.utils.basic import normalize_datetime

logger = logging.getLogger(__name__)


class Projects(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def normalize_create_update_time(self, created_at, updated_at):
        return normalize_datetime(created_at), normalize_datetime(updated_at)

    def deploy_type_list(self, deploy_type):
        """转换deploy_type为list类型
        """
        if not deploy_type:
            return []
        if str.isdigit(str(deploy_type)):
            deploy_type_list = [int(deploy_type)]
        else:
            try:
                deploy_type_list = json.loads(deploy_type)
            except Exception as err:
                logger.error("解析部署类型失败，详情: %s", err)
                return []
        return deploy_type_list

    def list(self, request):
        """获取项目列表
        """
        # 获取已经授权的项目
        access_token = request.user.token.access_token
        # 直接调用配置中心接口去获取信息
        projects = paas_cc.get_auth_project(access_token)
        if projects.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(projects.get('message'))
        data = projects.get('data')
        # 兼容先前，返回array/list
        if not data:
            return Response([])
        # 按数据倒序排序
        data.sort(key=lambda x: x['created_at'], reverse=True)
        # 数据处理
        for info in data:
            info['created_at'], info['updated_at'] = self.normalize_create_update_time(
                info['created_at'], info['updated_at'])
            info['project_code'] = info['english_name']
            info["deploy_type"] = self.deploy_type_list(info.get("deploy_type"))

        return Response(data)

    def has_cluster(self, request, project_id):
        """判断项目下是否有集群
        """
        resp = paas_cc.get_all_clusters(request.user.token.access_token, project_id)
        if resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(resp.get('message'))
        # 存在集群时，不允许修改
        if resp.get('data', {}).get('count') > 0:
            return True
        return False

    def is_manager(self, request, project_id):
        """判断用户是否为项目管理员
        """
        resp = paas_auth.get_project_user(
            request.user.token.access_token,
            project_id,
            group_code='Manager'
        )
        if resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(resp.get('message'))
        data = resp.get('data') or []
        if request.user.username in data:
            return True
        return False

    def can_edit(self, request, project_id):
        """判断是否允许修改项目
        - 项目下有集群，不允许更改项目的调度类型和绑定业务
        - 非管理员权限，不允许修改项目
        """
        if (self.has_cluster(request, project_id)) or \
                (not self.is_manager(request, project_id)):
            return False
        return True

    def info(self, request, project_id):
        """单个项目信息
        """
        project_resp = paas_cc.get_project(request.user.token.access_token, project_id)
        if project_resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(f'not found project info, {project_resp.get("message")}')
        data = project_resp['data']
        data['created_at'], data['updated_at'] = self.normalize_create_update_time(
            data['created_at'], data['updated_at'])
        # 添加业务名称
        data['cc_app_name'] = get_application_name(request)
        data['can_edit'] = self.can_edit(request, project_id)
        return Response(data)

    def validate_update_project_data(self, request):
        serializer = serializers.UpdateProjectNewSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.data

    def invalid_project_cache(self, project_id):
        """当变更项目信息时，详细缓存信息失效
        """
        region.delete(f'BK_DEVOPS_BCS:HAS_BCS_SERVICE:{project_id}')

    def update(self, request, project_id):
        """更新项目信息
        """
        if not self.can_edit(request, project_id):
            raise error_codes.CheckFailed("请确认有项目管理员权限，并且项目下无集群", replace=True)
        data = self.validate_update_project_data(request)
        access_token = request.user.token.access_token
        data['updator'] = request.user.username
        # 编辑之前项目绑定的业务和调度类型，用户后面判断是否进行相应的操作
        pre_cc_app_id = request.project.cc_app_id
        pre_kind = request.project.kind

        # 添加操作日志
        ual_client = client.UserActivityLogClient(
            project_id=project_id,
            user=request.user.username,
            resource_type='project',
            resource=request.project.project_name,
            resource_id=project_id,
            description="更新项目: %s" % request.project.project_name,
        )
        project = paas_cc.update_project_new(access_token, project_id, data)
        if project.get('code') != 0:
            ual_client.log_modify(activity_status='failed')
            raise error_codes.APIError(project.get('message', "更新项目成功"))
        ual_client.log_modify(activity_status='succeed')
        project_data = project.get('data')
        if project_data:
            project_data['created_at'], project_data['updated_at'] = self.normalize_create_update_time(
                project_data['created_at'], project_data['updated_at'])

        # 主动令缓存失效
        self.invalid_project_cache(project_id)
        # 触发后台任务
        start_tasks_for_project(request, project_id, data)

        return Response(project_data)


class CC(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def list(self, request):
        """获取当前用户CC列表
        """
        data = get_app_by_user_role(request)
        return Response(data)
