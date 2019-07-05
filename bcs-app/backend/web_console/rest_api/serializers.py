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
from django.conf import settings
from rest_framework import serializers

from backend.utils.error_codes import error_codes

from .utils import get_k8s_context, get_mesos_context


class MesosWebConsoleSLZ(serializers.Serializer):
    container_id = serializers.CharField()

    def validate(self, data):
        context = get_mesos_context(
            self.context['client'], data['container_id'])

        if not context:
            raise error_codes.APIError("container_id不正确，请检查参数%s" % settings.COMMON_EXCEPTION_MSG)

        data.update(context)
        return data


class K8SWebConsoleSLZ(serializers.Serializer):
    # k8s 容器id不是必填项
    container_id = serializers.CharField(required=False)

    def validate(self, data):
        container_id = data.get('container_id')
        if not container_id:
            return data

        # 有container_id才检查
        context = get_k8s_context(self.context['client'], container_id)
        if not context:
            raise error_codes.APIError("container_id不正确或者容器不是运行状态，请检查参数%s" % settings.COMMON_EXCEPTION_MSG)

        data.update(context)
        return data
