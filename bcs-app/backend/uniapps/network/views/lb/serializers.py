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
import json

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.uniapps.network.models import MesosLoadBlance as MesosLoadBalancer


class MesosLBSLZ(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    ip_list = serializers.SerializerMethodField()

    def get_ip_list(self, obj):
        return json.loads(obj.ip_list)

    def get_data(self, obj):
        return json.loads(obj.data_dict)

    class Meta:
        model = MesosLoadBalancer
        fields = ["id", "name", "cluster_id", "namespace", "ip_list", "status", "data"]


class CreateOrUpdateMesosLBSLZ(serializers.Serializer):
    name = serializers.CharField()
    cluster_id = serializers.CharField()
    namespace = serializers.CharField()
    namespace_id = serializers.IntegerField(default=0)
    instance_num = serializers.IntegerField(min_value=1)
    constraint = serializers.JSONField()
    use_custom_image_url = serializers.BooleanField(default=False)
    image_url = serializers.CharField()
    image_tag = serializers.CharField()
    use_custom_imagesecret = serializers.BooleanField(default=False)
    image_pull_user = serializers.CharField(default="")
    image_pull_password = serializers.CharField(default="")
    related_service_label = serializers.CharField()
    ip_list = serializers.ListField(default=[])
    configmaps = serializers.ListField(default=[])
    resources = serializers.DictField(default={})
    network_type = serializers.CharField()
    network_mode = serializers.CharField()
    custom_value = serializers.CharField(default="")
    container_port = serializers.IntegerField(default=80)
    host_port = serializers.IntegerField(default=31000, max_value=32000)
    forward_mode = serializers.CharField(required=True)

    def validate(self, data):
        # 如果 ip_list 存在，ip_list数量必须和instance num相同
        ip_list = data.get("ip_list")
        instance_num = data.get("instance_num")
        if not ip_list:
            return data
        if len(ip_list) != instance_num:
            raise ValidationError(_("参数【ip_list】数量必须和【instance_num】相同"))

        if data["use_custom_imagesecret"]:
            if not (data["image_pull_user"] and data["image_pull_password"]):
                raise ValidationError(_("启用添加镜像凭证，参数[image_pull_user]和[image_pull_password]不能为空"))
        return data
