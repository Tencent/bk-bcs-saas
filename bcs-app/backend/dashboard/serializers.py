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

from backend.resources.constants import K8sResourceKind


class ListResourceSLZ(serializers.Serializer):
    """ 查询 K8S 资源列表 """

    # NOTE：暂时只先支持 label_selector
    label_selector = serializers.CharField(label='标签选择算符', max_length=512, required=False)


class CreateResourceSLZ(serializers.Serializer):
    """ 创建 K8S 资源对象 """

    apiVersion = serializers.CharField(label='API 版本', max_length=64)
    kind = serializers.ChoiceField(label='资源类型', choices=K8sResourceKind.get_choices())
    metadata = serializers.JSONField(label='Metadata')
    spec = serializers.JSONField(label='Spec')


class UpdateResourceSLZ(CreateResourceSLZ):
    """ 更新 K8S 资源对象 """

    pass
