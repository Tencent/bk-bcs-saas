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
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.accounts import bcs_perm
from backend.apps.verfy import constants
from backend.apps.constants import verify_resource_exist

logger = logging.getLogger(__name__)


class PermVerifySLZ(serializers.Serializer):
    project_id = serializers.CharField()
    policy_code = serializers.ChoiceField(choices=bcs_perm.PermissionMeta.POLICY_LIST)
    resource_type = serializers.ChoiceField(choices=bcs_perm.PERMS_DICT)
    resource_code = serializers.CharField(required=False)
    resource_name = serializers.CharField(required=False)
    is_raise = serializers.BooleanField(required=False, default=True)

    def validate(self, data):
        if data['policy_code'] not in ['create', 'deploy', 'download']:
            if verify_resource_exist and (not data.get('resource_code')):
                raise ValidateError("【resource_code】不能为空")
            if not data.get('resource_name'):
                raise ValidationError("【resource_name】不能为空")
        else:
            data['resource_code'] = bcs_perm.NO_RES

        return data


class PermMultiVerifySLZ(serializers.Serializer):
    """批量接口
    """
    class ResourceListSLZ(serializers.Serializer):
        policy_code = serializers.ChoiceField(choices=bcs_perm.PermissionMeta.POLICY_LIST)
        resource_type = serializers.ChoiceField(choices=bcs_perm.PERMS_DICT)
        resource_code = serializers.CharField(required=False)
        resource_name = serializers.CharField(required=False)

        def validate(self, data):
            if data['policy_code'] not in ['create', 'deploy', 'download']:
                if verify_resource_exist and (not data.get('resource_code')):
                    raise ValidateError("【resource_code】不能为空")
                if not data.get('resource_name'):
                    raise ValidationError("【resource_name】不能为空")
            else:
                data['resource_code'] = bcs_perm.NO_RES

            return data

    project_id = serializers.CharField()
    operator = serializers.ChoiceField(choices=constants.PermMultiOperator.get_choices())
    resource_list = ResourceListSLZ(many=True)
