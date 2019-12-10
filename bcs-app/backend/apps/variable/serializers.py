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
import json
import logging
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from backend.apps.variable.models import Variable
from backend.apps.instance.serializers import InstanceNamespaceSLZ
from backend.apps.configuration.constants import VARIABLE_PATTERN
from .utils import get_variable_quote_num
from .constants import VariableScope, VariableCategory

logger = logging.getLogger(__name__)

RE_KEY = re.compile(r'^%s{0,63}$' % VARIABLE_PATTERN)
SYS_KEYS = ['SYS_BCS_ZK', 'SYS_CC_ZK', 'SYS_BCSGROUP',
            'SYS_TEMPLATE_ID', 'SYS_VERSION_ID', 'SYS_VERSION', 'SYS_INSTANCE_ID', 'SYS_CREATOR',
            'SYS_UPDATOR', 'SYS_OPERATOR', 'SYS_CREATE_TIME', 'SYS_UPDATE_TIME']


class SearchVariableSLZ(serializers.Serializer):
    type = serializers.CharField(default='with_quote_num')
    scope = serializers.CharField(default='')
    search_key = serializers.CharField(default='')
    limit = serializers.IntegerField(default=10)
    offset = serializers.IntegerField(default=0)


class ListVariableSLZ(serializers.ModelSerializer):
    default = serializers.DictField(source='get_default_data')
    quote_num = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    scope_name = serializers.SerializerMethodField()

    class Meta:
        model = Variable
        fields = (
            'id', 'name', 'key', 'default', 'default_value', 'desc', 'category', 'category_name', 'scope',
            'scope_name', 'quote_num', 'creator', 'created', 'updated', 'updator')

    def get_quote_num(self, obj):
        search_type = self.context['search_type']
        if search_type == 'base':
            return 0
        return get_variable_quote_num(obj.key, self.context['project_id'])

    def get_name(self, obj):
        return _(obj.name)

    def get_category_name(self, obj):
        return _(obj.get_category_display())

    def get_scope_name(self, obj):
        return _(obj.get_scope_display())


class VariableSLZ(serializers.ModelSerializer):
    scope = serializers.ChoiceField(choices=VariableScope.get_choices(), required=True)
    name = serializers.CharField(max_length=256, required=True)
    key = serializers.RegexField(
        RE_KEY,
        max_length=64,
        required=True,
        error_messages={
            'invalid': _("KEY 只能包含字母、数字和下划线，且以字母开头，最大长度为64个字符")
        }
    )
    default = serializers.JSONField(required=False)
    desc = serializers.CharField(max_length=256, required=False, allow_blank=True)
    project_id = serializers.CharField(max_length=64, required=True)

    class Meta:
        model = Variable
        fields = ('id', 'name', 'key', 'default', 'desc', 'category', 'scope', 'project_id')

    # TODO add validate_project_id

    def validate_default(self, default):
        if not isinstance(default, dict):
            raise ValidationError(_("default字段非字典类型"))
        if 'value' not in default:
            raise ValidationError(_("default字段没有以value作为键值"))
        return default

    def validate_key(self, key):
        if key in SYS_KEYS:
            raise ValidationError('KEY[{}]{}'.format(key, _("为系统变量名，不允许添加")))
        return key

    def to_representation(self, instance):
        instance.default = instance.get_default_data()
        return super().to_representation(instance)


class CreateVariableSLZ(VariableSLZ):
    def create(self, validated_data):
        exists = Variable.objects.filter(key=validated_data['key'], project_id=validated_data['project_id']).exists()
        if exists:
            detail = {
                'field': ['{}KEY{}{}'.format(_("变量"), validated_data['key'], _("已经存在"))]
            }
            raise ValidationError(detail=detail)

        variable = Variable.objects.create(**validated_data)
        return variable


class UpdateVariableSLZ(VariableSLZ):
    def update(self, instance, validated_data):
        if instance.category == VariableCategory.SYSTEM.value:
            raise ValidationError(_("系统内置变量不允许操作"))

        old_key = instance.key
        new_key = validated_data.get('key')

        if new_key != old_key:
            if get_variable_quote_num(old_key, validated_data.get('project_id')) > 0:
                raise ValidationError('KEY{}{}'.format(old_key, _("已经被引用，不能修改KEY")))

            if Variable.objects.filter(key=new_key, project_id=validated_data['project_id']).exists():
                detail = {
                    'field': ['{}KEY{}{}'.format(_("变量"), validated_data['key'], _("已经存在"))]
                }
                raise ValidationError(detail=detail)

        instance.key = new_key
        instance.scope = validated_data.get('scope')
        instance.name = validated_data.get('name')
        instance.default = validated_data.get('default')
        instance.desc = validated_data.get('desc')
        instance.updator = validated_data.get('updator')
        instance.save()
        return instance


class SearchVariableWithNamespaceSLZ(InstanceNamespaceSLZ):
    namespaces = serializers.CharField(required=True)

    def validate(self, data):
        pass

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['namespaces'] = data['namespaces'].split(',')
        return data


class VariableDeleteSLZ(serializers.Serializer):
    id_list = serializers.JSONField(required=True)


class ClusterVariableSLZ(serializers.Serializer):
    cluster_vars = serializers.JSONField(required=True)


class NsVariableSLZ(serializers.Serializer):
    ns_vars = serializers.JSONField(required=True)
