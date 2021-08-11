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
import re

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..constants import MesosResourceName
from ..k8s.serializers import BCSResourceSLZ
from ..validator import validate_res_config, validate_variable_inconfig
from .validator import (
    MESOS_NAME_REGEX,
    get_config_schema,
    validate_app_in_ventity,
    validate_mesos_res_name,
    validate_port_duplicate_in_ventity,
    validate_res_duplicate,
)

NAME_REGEX = re.compile(r'^[a-z]{1}[a-z0-9-]{0,254}$')
NAME_ERROR_MSG = _("名称格式错误，只能包含：小写字母、数字、连字符(-)，首字母必须是字母，长度小于256个字符")


class ApplicationSLZ(BCSResourceSLZ):
    resource_name = serializers.CharField(default=MesosResourceName.application.value)
    desc = serializers.CharField(max_length=256, required=False, allow_blank=True)

    def _validate_volume_duplicate(self, containers):
        validate_res_duplicate(containers, 'volumes')

    def _validate_port_duplicate(self, containers):
        validate_res_duplicate(containers, 'ports')

    def _validate_config(self, data):
        config = data['config']
        resource_name = data['resource_name']
        capitalize_name = resource_name.capitalize()
        try:
            name = data['name']
            validate_mesos_res_name(name)
        except ValidationError as e:
            raise ValidationError(f'{capitalize_name} {e}')

        # 校验配置信息中的变量名是否规范
        validate_variable_inconfig(config)

        if settings.IS_TEMPLATE_VALIDATE:
            validate_res_config(config, capitalize_name, get_config_schema(resource_name))

        # 检查单个 APP 中端口名称/挂载名 是否重复
        containers = config.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
        try:
            self._validate_volume_duplicate(containers)
        except ValidationError as e:
            raise ValidationError(_("挂载名:{},请重新填写").format(e))
        try:
            self._validate_port_duplicate(containers)
        except ValidationError as e:
            raise ValidationError(_("端口名称:{},请重新填写").format(e))

        if data.get('version_id'):
            validate_port_duplicate_in_ventity(containers, data.get('resource_id'), data['version_id'])


class DeploymentSLZ(BCSResourceSLZ):
    resource_name = serializers.CharField(default=MesosResourceName.deployment.value)
    app_id = serializers.CharField(required=False, allow_blank=True)
    desc = serializers.CharField(max_length=256, required=False, allow_blank=True)
    name = serializers.RegexField(
        MESOS_NAME_REGEX,
        max_length=256,
        required=True,
        error_messages={'invalid': _("Deployment 名称格式错误，只能包含：小写字母、数字、连字符(-)，首字母必须是字母，长度小于256个字符")},
    )

    def _validate_config(self, data):
        config = data['config']
        resource_name = data['resource_name']
        capitalize_name = resource_name.capitalize()

        validate_variable_inconfig(config)

        if settings.IS_TEMPLATE_VALIDATE:
            resource_name = data['resource_name']
            validate_res_config(config, capitalize_name, get_config_schema(resource_name))

    def validate(self, data):
        if not data.get('version_id'):
            raise ValidationError(_("请先创建 Application，再创建 Deployment"))

        if not data.get('app_id'):
            raise ValidationError(_("Deployment模板中{}: 请选择关联的 Application").format(data.get('name')))

        data = super().validate(data)

        app_id_list = data['app_id'].split(',')
        validate_app_in_ventity(app_id_list, data['version_id'])

        return data


class ServiceSLZ(BCSResourceSLZ):
    resource_name = serializers.CharField(default=MesosResourceName.service.value)
    app_id = serializers.JSONField(required=True)
    # 更新service相关字段
    lb_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    namespace_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    creator = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    create_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_app_id(self, app_id):
        # 将app_id转换成list
        if not app_id:
            raise ValidationError(_("Service模板: 请选择关联的 Application"))

        if isinstance(app_id, list):
            return app_id
        elif isinstance(app_id, dict):
            if sum(app_id.values()) != 100:
                raise ValidationError(_("关联应用的权重之和不为100%"))
            return app_id
        else:
            raise ValidationError(_("关联应用参数格式错误"))

    def _validate_config(self, data):
        config = data['config']
        if settings.IS_TEMPLATE_VALIDATE:
            resource_name = data['resource_name']
            validate_res_config(config, resource_name.capitalize(), get_config_schema(resource_name))

    def validate(self, data):
        self._validate_config(data)

        if not data.get('namespace_id') and not data.get('instance_id'):
            # 校验配置信息中的变量名是否规范
            validate_variable_inconfig(data['config'])
            self._validate_name_duplicate(data)

        if isinstance(data['app_id'], dict):
            app_id_list = data['app_id'].keys()
        else:
            app_id_list = data['app_id']

        validate_app_in_ventity(app_id_list, data.get('version_id'))

        return data


class ConfigMapSLZ(BCSResourceSLZ):
    resource_name = serializers.CharField(default=MesosResourceName.configmap.value)
    namespace_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def _validate_config(self, data):
        config = data['config']
        resource_name = data['resource_name']
        capitalize_name = resource_name.capitalize()
        try:
            name = data['name']
            validate_mesos_res_name(name)
        except ValidationError as e:
            raise ValidationError(f'{capitalize_name} {e}')

        # 校验配置信息中的变量名是否规范
        validate_variable_inconfig(config)

        if settings.IS_TEMPLATE_VALIDATE:
            validate_res_config(config, capitalize_name, get_config_schema(resource_name))


class SecretSLZ(ConfigMapSLZ):
    resource_name = serializers.CharField(default=MesosResourceName.secret.value)


class HPASLZ(ConfigMapSLZ):
    resource_name = serializers.CharField(default=MesosResourceName.hpa.value)


class IngressSLZ(ConfigMapSLZ):
    resource_name = serializers.CharField(default=MesosResourceName.ingress.value)
