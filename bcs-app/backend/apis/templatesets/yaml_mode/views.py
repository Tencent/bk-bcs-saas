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
from rest_framework.response import Response

from backend.apis.views import NoAccessTokenBaseAPIViewSet
from backend.apps.configuration.mixins import TemplatePermission
from backend.apps.configuration.yaml_mode.deployer import DeployController
from backend.apps.configuration.yaml_mode.release import ReleaseData, ReleaseDataProcessor
from backend.apps.datalog.utils import create_and_start_standard_data_flow, create_data_project

from .serializers import TemplateReleaseSLZ


class TemplateReleaseViewSet(NoAccessTokenBaseAPIViewSet, TemplatePermission):
    def _request_data(self, request, **kwargs):
        request_data = request.data.copy() or {}
        request_data.update(**kwargs)
        return request_data

    def apply(self, request, project_id_or_code):
        project_id = request.project.project_id
        data = self._request_data(request, project_id=project_id)
        serializer = TemplateReleaseSLZ(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        self.can_use_template(request, validated_data["template"])

        # 在数据平台创建项目信息
        username = request.user.username
        cc_app_id = request.project.cc_app_id
        english_name = request.project.english_name
        create_data_project(username, project_id, cc_app_id, english_name)
        # 创建/启动标准日志采集任务
        create_and_start_standard_data_flow(username, project_id, cc_app_id)

        validated_data = serializer.validated_data
        processor = ReleaseDataProcessor(
            user=self.request.user,
            raw_release_data=ReleaseData(
                project_id=project_id,
                namespace_info=validated_data["namespace_info"],
                show_version=validated_data["show_version"],
                template_files=validated_data["template_files"],
                template_variables=validated_data["template_variables"],
            ),
        )

        controller = DeployController(user=self.request.user, release_data=processor.release_data())

        controller.apply()
        return Response()
