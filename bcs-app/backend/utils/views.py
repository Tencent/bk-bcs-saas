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
import logging

from django.conf import settings
from django.views.generic.base import TemplateView
from django.http import Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.compat import set_rollback
from rest_framework.exceptions import (AuthenticationFailed, MethodNotAllowed,
                                       NotAuthenticated, PermissionDenied,
                                       ValidationError, ParseError)
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.renderers import BrowsableAPIRenderer
from django.utils.translation import ugettext_lazy as _

from backend.utils import exceptions as backend_exceptions
from backend.utils.error_codes import APIError
from backend.utils.local import local
from backend.utils.error_codes import error_codes

logger = logging.getLogger(__name__)


def one_line_error(detail):
    """Extract one line error from error dict
    """
    try:
        for field, errmsg in detail.items():
            if field == 'non_field_errors':
                return errmsg[0]
            else:
                return '%s: %s' % (field, errmsg[0])
    except Exception:
        return _('参数格式错误')


def custom_exception_handler(exc, context):
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        data = {
            "code": error_codes.Unauthorized.code,
            "data": {
                "login_url": {
                    "full": settings.LOGIN_FULL,
                    "simple": settings.LOGIN_SIMPLE,
                }
            },
            'message': error_codes.Unauthorized.message,
            'request_id': local.request_id
        }
        return Response(data, status=error_codes.Unauthorized.status_code)

    elif isinstance(exc, (ValidationError, ParseError)):
        detail = exc.detail
        if 'non_field_errors' in exc.detail:
            message = detail['non_field_errors']
        else:
            message = detail
        data = {
            'code': 400,
            'message': message,
            'data': None,
            'request_id': local.request_id
        }
        set_rollback()
        return Response(data, status=200, headers={})

    elif isinstance(exc, APIError):
        # 更改返回的状态为为自定义错误类型的状态码
        data = {
            'code': exc.code,
            'message': exc.message,
            'data': None,
            'request_id': local.request_id
        }
        set_rollback()
        return Response(data)
    elif isinstance(exc, (MethodNotAllowed, PermissionDenied)):
        data = {
            'code': 400,
            'message': exc.detail,
            'data': None,
            'request_id': local.request_id
        }
        set_rollback()
        return Response(data, status=200)
    elif isinstance(exc, Http404):
        data = {
            'code': 404,
            'message': _('资源未找到'),
            'data': None
        }
        set_rollback()
        return Response(data, status=200)
    elif isinstance(exc, backend_exceptions.APIError):
        data = {
            'code': exc.code,
            'message': '%s' % exc,
            'data': exc.data,
            'request_id': local.request_id
        }
        set_rollback()
        return Response(data, status=exc.status_code)

    # Call REST framework's default exception handler to get the standard error response.
    response = exception_handler(exc, context)
    # Use a default error code
    if response is not None:
        response.data.update(code='ERROR')

    # catch all exception, if in prod/stag mode
    if settings.IS_COMMON_EXCEPTION_MSG and not settings.DEBUG and not response:
        logger.exception("restful api unhandle exception")

        data = {
            'code': 500,
            'message': _("数据请求失败，请稍后再试{}").format(settings.COMMON_EXCEPTION_MSG),
            'data': None,
            'request_id': local.request_id
        }
        return Response(data)

    return response


class FinalizeResponseMixin:

    def finalize_response(self, request, response, *args, **kwargs):
        if "code" not in response.data:
            code = response.status_code // 100
            response.data = {
                "code": 0 if code == 2 else response.status_code,
                "message": response.status_text,
                "data": response.data,
            }
        return super(FinalizeResponseMixin, self).finalize_response(
            request, response, *args, **kwargs
        )


class ProjectMixin:
    """ 从 url 中提取 project_id，使用该 mixin 前请确保 url 参数中有 project_id 这个 key """

    @property
    def project_id(self):
        return self.request.parser_context["kwargs"]["project_id"]


class FilterByProjectMixin(ProjectMixin):
    def get_queryset(self):
        return self.queryset.filter(project_id=self.project_id)


class AppMixin:
    """ 从 url 中提取 app_id，使用该 mixin 前请确保 url 参数中有 app_id 这个 key """

    @property
    def app_id(self):
        return self.request.parser_context["kwargs"]["app_id"]


class AccessTokenMixin:
    """ 从 url 中获取 access_token """

    @property
    def access_token(self):
        # FIXME maybe we should raise 401 when not login
        return self.request.user.token.access_token


class ActionSerializerMixin:
    action_serializers = {}

    def get_serializer_class(self):
        if self.action in self.action_serializers:
            return self.action_serializers.get(self.action, None)
        else:
            return super().get_serializer_class()


class CodeJSONRenderer(JSONRenderer):
    """
    采用统一的结构封装返回内容
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {
            "data": data,
            "code": 0,
            "message": "success"
        }
        if isinstance(data, dict):
            # helm app 的变更操作结果通过 `transitioning_result` 字段反应
            # note: 不要对GET操作的返回结果进行处理
            if renderer_context is not None \
                    and renderer_context["request"].method in ["POST", "PUT", "DELETE"] \
                    and "transitioning_result" in data:
                response_data = {
                    "data": data,
                    "code": 0 if data["transitioning_result"] is True else 400,
                    "message": data["transitioning_message"]
                }
            elif ("code" not in data or "message" not in data):
                code = data.get("code", 0)
                try:
                    code = int(code)
                except Exception:
                    code = 500

                message = data.get("message", "")

                response_data = {
                    "data": data,
                    "code": code,
                    "message": message
                }
            else:
                response_data = data

        response = super(CodeJSONRenderer, self).render(response_data, accepted_media_type, renderer_context)
        return response


def with_code_wrapper(func):
    func.renderer_classes = (BrowsableAPIRenderer, CodeJSONRenderer)
    return func


class VueTemplateView(TemplateView):
    if settings.REGION == 'ce':
        template_name = 'dist/index.html'
    else:
        template_name = f'{settings.REGION}/index.html'

    @xframe_options_exempt
    def get(self, request):
        context = {
            'DEVOPS_HOST': settings.DEVOPS_HOST,
            'DEVOPS_BCS_HOST': settings.DEVOPS_BCS_HOST,
            'DEVOPS_BCS_API_URL': settings.DEVOPS_BCS_API_URL,
            'DEVOPS_ARTIFACTORY_HOST': settings.DEVOPS_ARTIFACTORY_HOST,
            'RUN_ENV': settings.RUN_ENV,
            # 去除末尾的 /, 前端约定
            'STATIC_URL': settings.SITE_STATIC_URL,
            # 去除开头的 . document.domain需要
            'SESSION_COOKIE_DOMAIN': settings.SESSION_COOKIE_DOMAIN.lstrip('.'),
            'REGION': settings.REGION,
            'BK_CC_HOST': settings.BK_CC_HOST,
            'SITE_URL': settings.SITE_URL[:-1],
            'BK_IAM_APP_URL': settings.BK_IAM_APP_URL
        }
        response = super(VueTemplateView, self).get(request, **context)
        return response


class LoginSuccessView(VueTemplateView):
    template_name = f'{settings.REGION}/login_success.html'
