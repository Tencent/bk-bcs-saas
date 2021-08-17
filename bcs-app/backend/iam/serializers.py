# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .permissions.resources.constants import ResourceType


class ResourceRequestSLZ(serializers.Serializer):
    resource_type = serializers.ChoiceField(choices=ResourceType.get_choices(), required=False)
    resource_id = serializers.CharField(required=False)
    iam_path_attrs = serializers.JSONField(default=dict)

    def validate(self, data):
        if 'resource_type' in data and 'resource_id' not in data:
            raise ValidationError('missing param resource_id')
        return data


class ResourceActionSLZ(ResourceRequestSLZ):
    action_id = serializers.CharField()


class ResourceMultiActionsSLZ(ResourceRequestSLZ):
    action_ids = serializers.ListField(child=serializers.CharField(), min_length=1)
