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
from dataclasses import dataclass
from typing import Union

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response

from backend.utils.local import local


class APIResult(JsonResponse):
    """正常返回，免去填写code=0等其他必填项
    data: dict | list
    message: str
    permissions: dict
    """

    def __init__(self, data, message='', permissions=None):
        assert isinstance(data, (list, dict)), _("data必须是list或者dict类型")

        result = {'code': 0, 'data': data, 'message': message, 'request_id': local.request_id}

        if permissions:
            result['permissions'] = permissions

        return super(APIResult, self).__init__(result)


class APIResponse(APIResult):
    """same for api result for now"""

    pass


class APIForbiddenResult(JsonResponse):
    """无权限返回，免去填写code=403等其他必填项
    data: dict | list
    message: str
    """

    def __init__(self, data, message=''):
        assert isinstance(data, (list, dict)), _("data必须是list或者dict类型")

        result = {'code': 403, 'data': data, 'message': message}
        return super(APIForbiddenResult, self).__init__(result)


class ResNotFoundResult(JsonResponse):
    """无资源返回，免去填写code=404等其他必填项
    data: dict | list
    message: str
    """

    def __init__(self, data, message=''):
        assert isinstance(data, (list, dict)), _("data必须是list或者dict类型")

        result = {'code': 404, 'data': data, 'message': message}
        return super(ResNotFoundResult, self).__init__(result)


class BKAPIResponse(Response):
    """APIResponse封装"""

    def __init__(self, data: Union[list, dict], message: str = '', permissions: Union[None, dict] = None):
        assert isinstance(data, (list, dict)), _("data必须是list或者dict类型")
        self.message = message
        self.permissions = permissions

        super(BKAPIResponse, self).__init__(data)

    @property
    def rendered_content(self):
        context = getattr(self, 'renderer_context', None)
        assert context is not None, ".renderer_context not set on Response"

        # 自定义context
        context['message'] = self.message
        context['permissions'] = self.permissions
        return super(BKAPIResponse, self).rendered_content


@dataclass
class ComponentData:
    result: bool
    data: Union[list, dict]
    message: str
