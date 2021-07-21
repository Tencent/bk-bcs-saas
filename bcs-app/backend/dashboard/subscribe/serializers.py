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
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.resources.constants import K8sResourceKind


class FetchResourceWatchResultSLZ(serializers.Serializer):
    """获取单类资源一段时间内的变更记录"""

    resource_version = serializers.CharField(label=_('资源版本号'), max_length=32)
    kind = serializers.ChoiceField(label=_('资源类型'), choices=K8sResourceKind.get_choices())
    custom_obj_kind = serializers.CharField(label=_('自定义资源类型'), max_length=128, required=False)
    api_version = serializers.CharField(label=_('API版本'), max_length=16, required=False)

    def validate(self, attrs):
        """ 自定义类型资源需要指定 custom_obj_kind, apiVersion，以免需要先查询 CRD 获取 """
        if attrs['kind'] == K8sResourceKind.CustomObject.value:
            if not attrs.get('custom_obj_kind'):
                raise ValidationError(_('当资源类型为自定义对象时，需要指定具体的 Kind (crd.spec.names.kind)'))
            if not attrs.get('api_version'):
                raise ValidationError(_('当资源类型为自定义对象时，需要指定 ApiVersion'))
        return attrs
