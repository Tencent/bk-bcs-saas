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
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .constants import SupportedScaleCRDs


class PatchCustomObjectSLZ(serializers.Serializer):
    namespace = serializers.CharField(required=False)
    body = serializers.JSONField()


class PatchCustomObjectScaleSLZ(PatchCustomObjectSLZ):
    """
    暂时先支持scope=Namespaced的CustomObject
    """

    crd_name = serializers.ChoiceField(choices=SupportedScaleCRDs.get_choices())
    namespace = serializers.CharField()
    body = serializers.JSONField()

    def validate_body(self, body):
        try:
            int(body["spec"]["replicas"])
        except KeyError as e:
            raise ValidationError(f"body key error: {e}")
        except TypeError as e:
            raise ValidationError(f"body type error: {e}")
        except ValueError as e:
            raise ValidationError(e)
        return body
