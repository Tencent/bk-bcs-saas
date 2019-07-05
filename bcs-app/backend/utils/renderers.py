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
from rest_framework.renderers import JSONRenderer

from backend.utils.local import local


class BKAPIRenderer(JSONRenderer):
    """
    采用统一的结构封装返回内容
    """
    SUCCESS_CODE = 0
    SUCCESS_MESSAGE = 'OK'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict) and 'code' in data:
            data['request_id'] = local.request_id
        else:
            data = {
                'data': data,
                'code': self.SUCCESS_CODE,
                'message': self.SUCCESS_MESSAGE,
                'request_id': local.request_id
            }

        if renderer_context and renderer_context.get('permissions'):
            data['permissions'] = renderer_context['permissions']

        if renderer_context and renderer_context.get('message'):
            data['message'] = renderer_context['message']

        response = super(BKAPIRenderer, self).render(data, accepted_media_type, renderer_context)
        return response
