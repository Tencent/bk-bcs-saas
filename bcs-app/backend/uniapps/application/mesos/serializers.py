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

from backend.templatesets.legacy_apps.configuration.constants import MesosResourceName
from backend.templatesets.legacy_apps.configuration.models.template import ShowVersion


class MesosInstSLZ(serializers.Serializer):
    kind = serializers.ChoiceField(choices=[MesosResourceName.deployment.value, MesosResourceName.application.value])
    show_version_id = serializers.IntegerField(required=False)
    variables = serializers.JSONField(default={})
    manifest = serializers.JSONField(default={})

    def validate(self, data):
        if not data.get("show_version_id"):
            if not data.get("manifest"):
                raise ValidationError(_("版本或资源配置不能同时为空"))
            return data
        # 获取show version信息
        show_version_qs = ShowVersion.objects.filter(id=data["show_version_id"])
        show_version = show_version_qs.first()
        if not show_version:
            raise ValidationError(_("版本{}不存在").format(data["show_version_id"]))

        data["show_version"] = show_version
        return data
