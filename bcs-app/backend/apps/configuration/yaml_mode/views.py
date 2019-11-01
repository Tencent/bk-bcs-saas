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
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer

from . import serializers
from .deployer import DeployController
from .manifest import ManifestsRenderer, ManifestsData
from backend.apps.configuration.mixins import TemplatePermission
from backend.apps.configuration.models import get_template_by_project_and_id
from backend.apps.configuration.showversion.serializers import GetShowVersionSLZ, GetLatestShowVersionSLZ
from backend.utils.renderers import BKAPIRenderer


class YamlViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    permission_classes = ()
    authentication_classes = ()


class YamlTemplateViewSet(YamlViewSet, TemplatePermission):

    def _template_data(self, request, **kwargs):
        template_data = request.data or {}
        template_data.update(**kwargs)
        return template_data

    def create_template(self, request, project_id):
        """
        request.data = {
            'name': '',
            'desc': '',
            'show_version': {
                'name': '',
            }
            'template_files': [{
                'resource_name': 'Deployment',
                'files': [{'name': 'nginx.yaml', 'content': 'Kind:Deployment', 'action': 'create'}]
            }]
        }
        """
        data = self._template_data(request, project_id=project_id)
        serializer = serializers.CreateTemplateSLZ(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        template = serializer.save()
        return Response({'template_id': template.id})

    def update_template(self, request, project_id, template_id):
        """
        request.data = {
            'name': '',
            'desc': '',
            'show_version': {
                'name': '',
                'show_version_id': '',
            }
            'template_files': [{
                'resource_name': 'Deployment',
                'files': [{'name': 'nginx.yaml', 'content': 'Kind:Deployment', 'action': 'update', 'id': 3}]
            }]
        }
        """
        template = get_template_by_project_and_id(project_id, template_id)
        data = self._template_data(request, project_id=project_id)
        serializer = serializers.UpdateTemplateSLZ(template, data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        template = serializer.save()
        return Response({'template_id': template.id})

    def get_template_by_show_version(self, request, project_id, template_id, show_version_id):
        serializer = GetShowVersionSLZ(data=self.kwargs)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        template = validated_data['template']
        # self.can_view_template(request, template)

        with_file_content = request.query_params.get('with_file_content')
        with_file_content = False if with_file_content == 'false' else True

        serializer = serializers.GetTemplateFilesSLZ(
            validated_data, context={'with_file_content': with_file_content}
        )
        return Response(serializer.data)

    def get_template(self, request, project_id, template_id):
        serializer = GetLatestShowVersionSLZ(data=self.kwargs)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        template = validated_data['template']
        # self.can_view_template(request, template)

        serializer = serializers.GetTemplateFilesSLZ(
            validated_data, context={'with_file_content': True}
        )
        return Response(serializer.data)


class TemplateResourceViewSet(YamlViewSet, TemplatePermission):

    def _request_data(self, request, project_id, template_id, show_version_id):
        request_data = request.data or {}
        show_version = {
            'show_version_id': show_version_id,
            'template_id': template_id,
            'project_id': project_id
        }
        request_data['show_version'] = show_version
        return request_data

    def _raw_manifests(self, project_id, initial_data):
        show_version = initial_data['show_version']
        raw_manifests = ManifestsData(
            project_id=project_id,
            namespace_id=initial_data['namespace_id'],
            show_version=show_version['show_version'],
            template_files=initial_data['template_files']
        )
        return raw_manifests

    def preview_or_apply(self, request, project_id, template_id, show_version_id):
        """
        request.data = {
            'is_preview': True,
            'namespace': 'test',
            'template_files': [{
                'resource_name': 'Deployment',
                'files': [{'name': 'nginx.yaml', 'id': 3}]
            }]
        }
        """
        data = self._request_data(request, project_id, template_id, show_version_id)
        serializer = serializers.PreviewTemplateFilesSLZ(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = request.user
        from backend.utils import FancyDict
        user = FancyDict({'username': '', 'token': FancyDict({'access_token': '$#ab$ffff3d#'})})

        renderer = ManifestsRenderer(user=user, raw_manifests=self._raw_manifests(project_id, validated_data))
        manifests = renderer.render()

        if validated_data['is_preview']:
            return Response(manifests.template_files)

        controller = DeployController(manifests)
        resp = controller.apply()
        return Response({})
