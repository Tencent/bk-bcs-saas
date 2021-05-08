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

from backend.activity_log.audit.auditors import HelmAuditor, TemplatesetAuditor
from backend.activity_log.audit.context import AuditContext
from backend.activity_log.audit.decorators import log_audit, log_audit_on_view
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
    @log_audit_on_view(TemplatesetAuditor, activity_type='list')
    def list(self, request, project_id):
        return Response()

    @log_audit_on_view(TemplatesetAuditor, activity_type='create')
    def create(self, request, project_id):
        request.audit_ctx.update_fields(resource='nginx')
        raise ValidationError('invalid manifest')

    @log_audit_on_view(TemplatesetAuditor, activity_type='delete', ignore_exceptions=(ValidationError,))
    def delete(self, request, project_id):
        raise ValidationError('test')


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
    def test_log_audit_on_view_succeed(self, bk_user, project_id):
        t_view = TemplatesetsViewSet.as_view({'get': 'list'})
        request = factory.get('/')
        force_authenticate(request, bk_user)
        t_view(request, project_id=project_id)

        activity_log = UserActivityLog.objects.get(project_id=project_id, user=bk_user.username, activity_type='list')
        assert activity_log.activity_status == 'succeed'
        assert activity_log.description == 'list templateset succeed'

    def test_log_audit_on_view_failed(self, bk_user, project_id):
        t_view = TemplatesetsViewSet.as_view({'post': 'create'})
        request = factory.post('/', data={'version': '1.6.0'})
        force_authenticate(request, bk_user)
        t_view(request, project_id=project_id)

        activity_log = UserActivityLog.objects.get(
            project_id=project_id, user=bk_user.username, activity_type='create'
        )
        assert activity_log.activity_status == 'failed'
        assert json.loads(activity_log.extra)['version'] == '1.6.0'
        assert activity_log.description == f"create templateset nginx failed: {ValidationError('invalid manifest')}"

    def test_log_audit_ignore_exceptions(self, bk_user, project_id):
        t_view = TemplatesetsViewSet.as_view({'delete': 'delete'})
        request_post = factory.delete('/')
        force_authenticate(request_post, bk_user)
        try:
            t_view(request_post, project_id=project_id)
        except Exception:
            pass

        assert (
            UserActivityLog.objects.filter(
                project_id=project_id, user=bk_user.username, activity_type='delete'
            ).count()
            == 0
        )

    def test_log_audit(self, bk_user, project_id):
        h_view = HelmViewSet.as_view({'post': 'create'})
        request = factory.post('/')
        force_authenticate(request, bk_user)
        h_view(request, project_id=project_id)

        activity_log = UserActivityLog.objects.get(project_id=project_id, user=bk_user.username, resource_type='helm')
        assert activity_log.activity_type == 'install'
        assert activity_log.description == 'test install helm'
        assert json.loads(activity_log.extra)['chart'] == 'http://example.chart.com/nginx/nginx1.12.tgz'
