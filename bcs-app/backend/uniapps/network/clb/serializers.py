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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.uniapps.network.clb.models import CloudLoadBlancer


class BaseCLBParamsSLZ(serializers.Serializer):
    # 拉取到的clb名称，也用于渲染deployment
    clb_name = serializers.CharField(max_length=253)
    cluster_id = serializers.CharField()
    region = serializers.CharField(max_length=32)
    # clb的类型
    clb_type = serializers.ChoiceField(choices=['private', 'public'], default='private')
    image = serializers.CharField()
    # 网络类型
    network_type = serializers.ChoiceField(choices=['underlay', 'overlay'], default='underlay')
    # 服务发现类型
    svc_discovery_type = serializers.ChoiceField(choices=['custom', 'mesos'], default='custom')
    # 下面参数先不透漏
    clb_project_id = serializers.IntegerField(required=False, default=0)
    metric_port = serializers.IntegerField(required=False, default=59050)
    implement_type = serializers.CharField(required=False, default='sdk')
    backend_type = serializers.CharField(required=False, default='eni')


class CreateCLBSLZ(BaseCLBParamsSLZ):
    def validate(self, data):
        # 因为命名空间固定，所以只需要限制clb name和cluster_id
        queryset = CloudLoadBlancer.objects.filter(clb_name=data['clb_name'], cluster_id=data['cluster_id'])
        if queryset:
            raise ValidationError(_("clb:[{}]已经被占用，请确认后重试").format(data['clb_name']))
        return data


class UpdateCLBSLZ(BaseCLBParamsSLZ):
    pass
