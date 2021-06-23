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

from backend.bcs_web.audit_log.audit.auditors import HelmAuditor
from backend.bcs_web.audit_log.audit.context import AuditContext
from backend.bcs_web.audit_log.audit.decorators import log_audit, log_audit_on_view
from backend.bcs_web.audit_log.constants import BaseActivityStatus, BaseActivityType, BaseResourceType
from backend.bcs_web.audit_log.models import UserActivityLog
from backend.bcs_web.viewsets import SystemViewSet
from backend.templatesets.legacy_apps.configuration.auditor import TemplatesetAuditor
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
    @log_audit_on_view(TemplatesetAuditor, activity_type=BaseActivityType.Retrieve)
    def list(self, request, project_id):
        return Response()

    @log_audit_on_view(TemplatesetAuditor, activity_type=BaseActivityType.Add)
    def create(self, request, project_id):
        request.audit_ctx.update_fields(resource='nginx')
        raise ValidationError('invalid manifest')

    @log_audit_on_view(TemplatesetAuditor, activity_type=BaseActivityType.Delete, ignore_exceptions=(ValidationError,))
    def delete(self, request, project_id):
        raise ValidationError('test')


@log_audit(HelmAuditor, activity_type=BaseActivityType.Add)
def install_chart(audit_ctx: AuditContext):
    audit_ctx.update_fields(
        description=f'test {BaseActivityType.Add} {BaseResourceType.HelmApp}',
        extra={'chart': 'http://example.chart.com/nginx/nginx1.12.tgz'},
    )


class HelmViewSet(SystemViewSet):
    def create(self, request, project_id):
        install_chart(request.audit_ctx)
        return Response()

    def upgrade(self, request, project_id):
        self._upgrade(request, project_id)
        return Response()

    @log_audit(HelmAuditor, activity_type=BaseActivityType.Modify)
    def _upgrade(self, request, project_id):
        self.audit_ctx.update_fields(
            project_id=project_id,
            user=request.user.username,
            description=f'test {BaseActivityType.Modify} {BaseResourceType.HelmApp}',
            extra={'chart': 'http://example.chart.com/nginx/nginx1.12.tgz'},
        )


class TestAuditDecorator:
    def test_log_audit_on_view_succeed(self, bk_user, project_id):
        t_view = TemplatesetsViewSet.as_view({'get': 'list'})
        request = factory.get('/')
        force_authenticate(request, bk_user)
        t_view(request, project_id=project_id)

        activity_log = UserActivityLog.objects.get(
            project_id=project_id, user=bk_user.username, activity_type=BaseActivityType.Retrieve
        )
        assert activity_log.activity_status == BaseActivityStatus.Succeed
        assert (
            activity_log.description
            == f'{BaseActivityType.Retrieve} template {BaseActivityStatus.get_choice_label(BaseActivityStatus.Succeed)}'
        )

    def test_log_audit_on_view_failed(self, bk_user, project_id):
        t_view = TemplatesetsViewSet.as_view({'post': 'create'})
        request = factory.post('/', data={'version': '1.6.0'})
        force_authenticate(request, bk_user)
        t_view(request, project_id=project_id)

        activity_log = UserActivityLog.objects.get(
            project_id=project_id, user=bk_user.username, activity_type=BaseActivityType.Add
        )
        assert activity_log.activity_status == BaseActivityStatus.Failed
        assert json.loads(activity_log.extra)['version'] == '1.6.0'
        assert (
            activity_log.description == f"{BaseActivityType.Add} template nginx "
            f"{BaseActivityStatus.get_choice_label(BaseActivityStatus.Failed)}: {ValidationError('invalid manifest')}"
        )

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
                project_id=project_id, user=bk_user.username, activity_type=BaseActivityType.Delete
            ).count()
            == 0
        )

    def test_log_audit_for_func(self, bk_user, project_id):
        h_view = HelmViewSet.as_view({'post': 'create'})
        request = factory.post('/')
        force_authenticate(request, bk_user)
        h_view(request, project_id=project_id)

        activity_log = UserActivityLog.objects.get(
            project_id=project_id, user=bk_user.username, resource_type=BaseResourceType.HelmApp
        )
        assert activity_log.activity_type == BaseActivityType.Add
        assert (
            activity_log.description == f'test {BaseActivityType.Add} {BaseResourceType.HelmApp} '
            f'{BaseActivityStatus.get_choice_label(BaseActivityStatus.Succeed)}'
        )
        assert json.loads(activity_log.extra)['chart'] == 'http://example.chart.com/nginx/nginx1.12.tgz'

    def test_log_audit_for_method(self, bk_user, project_id):
        h_view = HelmViewSet.as_view({'put': 'upgrade'})
        request = factory.put('/')
        force_authenticate(request, bk_user)
        h_view(request, project_id=project_id)

        activity_log = UserActivityLog.objects.get(
            project_id=project_id, user=bk_user.username, resource_type=BaseResourceType.HelmApp
        )
        assert activity_log.activity_type == BaseActivityType.Modify
        assert (
            activity_log.description == f'test {BaseActivityType.Modify} {BaseResourceType.HelmApp} '
            f'{BaseActivityStatus.get_choice_label(BaseActivityStatus.Succeed)}'
        )
        assert json.loads(activity_log.extra)['chart'] == 'http://example.chart.com/nginx/nginx1.12.tgz'
