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

import mock
import pytest
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.validators import ValidationError

from backend.activity_log.audit.auditors import HelmAuditor, TemplatesetsAuditor
from backend.activity_log.audit.context import AuditContext
from backend.activity_log.audit.decorator import log_audit, log_audit_on_view
from backend.activity_log.models import UserActivityLog
from backend.bcs_web.viewsets import SystemViewSet
from backend.tests.bcs_mocks.misc import FakeProjectPermissionAllowAll
from backend.tests.testing_utils.mocks.paas_cc import StubPaaSCCClient

pytestmark = pytest.mark.django_db

factory = APIRequestFactory()


@pytest.fixture(autouse=True)
def patch_permissions():
    """Patch permission checks to allow API requests"""
    with mock.patch('backend.bcs_web.permissions.PaaSCCClient', new=StubPaaSCCClient), mock.patch(
        'backend.bcs_web.permissions.permissions.ProjectPermission', new=FakeProjectPermissionAllowAll
    ), mock.patch('backend.components.apigw.get_api_public_key', return_value=None):
        yield


class TemplatesetsViewSet(SystemViewSet):
    @log_audit_on_view(TemplatesetsAuditor, activity_type='list')
    def list(self, request, project_id):
        return Response()

    @log_audit_on_view(TemplatesetsAuditor, activity_type='create')
    def create(self, request, project_id):
        request.audit_ctx.update_fields(resource='nginx')
        raise ValidationError('invalid manifest')


@log_audit(HelmAuditor, activity_type='install')
def install_chart(audit_ctx: AuditContext):
    audit_ctx.update_fields(
        description='test install helm', extra={'chart': 'http://example.chart.com/nginx/nginx1.12.tgz'}
    )


class HelmViewSet(SystemViewSet):
    def create(self, request, project_id):
        install_chart(request.audit_ctx)
        return Response()


class TestAuditDecorator:
    def test_log_audit_on_view(self, bk_user, project_id):
        t_view = TemplatesetsViewSet.as_view({'get': 'list', 'post': 'create'})

        request_get = factory.get('/')
        force_authenticate(request_get, bk_user)
        t_view(request_get, project_id=project_id)
        activity_log = UserActivityLog.objects.get(project_id=project_id, user=bk_user.username, activity_type='list')
        assert activity_log.activity_status == 'succeed'
        assert activity_log.description == 'list templatesets succeed'

        request_post = factory.post('/', data={'version': '1.6.0'})
        force_authenticate(request_post, bk_user)
        t_view(request_post, project_id=project_id)
        activity_log = UserActivityLog.objects.get(
            project_id=project_id, user=bk_user.username, activity_type='create'
        )
        assert activity_log.activity_status == 'failed'
        assert json.loads(activity_log.extra)['version'] == '1.6.0'
        assert activity_log.description == f"create templatesets nginx failed: {ValidationError('invalid manifest')}"

    def test_log_audit(self, bk_user, project_id):
        h_view = HelmViewSet.as_view({'post': 'create'})
        request = factory.post('/')
        force_authenticate(request, bk_user)
        h_view(request, project_id=project_id)

        activity_log = UserActivityLog.objects.get(project_id=project_id, user=bk_user.username, resource_type='helm')
        assert activity_log.activity_type == 'install'
        assert activity_log.description == 'test install helm'
        assert json.loads(activity_log.extra)['chart'] == 'http://example.chart.com/nginx/nginx1.12.tgz'
