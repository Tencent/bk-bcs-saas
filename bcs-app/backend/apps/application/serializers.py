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
import re

from rest_framework import serializers


class StringListField(serializers.ListField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = re.findall(r'[^,; ]+', data)
        elif isinstance(data, list):
            data = data
        data = list(set(data))
        return super(StringListField, self).to_internal_value(data)


class BaseParams(serializers.Serializer):
    pass


class InstanceParams(BaseParams):
    version_id = serializers.CharField(label=u"模板版本", required=True)
    namespace = StringListField(
        child=serializers.CharField(min_length=1),
        min_length=1,
        required=True
    )


class UpdateInstanceParams(BaseParams):
    """滚动升级需要参数
    """
    oper_type = serializers.ChoiceField(
        label=u"操作类型", choices=[("Recreate", u"重新创建"), ("RollingUpdate", u"滚动升级")])
    delete_num = serializers.IntegerField(label=u"周期删除数", required=True)
    add_num = serializers.IntegerField(label=u"周期新增数", required=True)
    interval_time = serializers.IntegerField(label=u"更新间隔", required=True)
    oper_order = serializers.ChoiceField(
        label=u"滚动顺序", choices=[("CreateFirst", u"先创建"), ("DeleteFirst", u"先删除")])
    version_id = serializers.IntegerField(label=u"版本ID", required=True)
    version = serializers.CharField(label=u"版本号", required=False)
    show_version_id = serializers.IntegerField(required=True)