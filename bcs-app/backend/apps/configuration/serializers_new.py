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

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.utils.exceptions import ResNotFoundError
from backend.apps.configuration import models
from backend.apps.configuration.k8s import serializers as kserializers
from backend.apps.configuration.mesos import serializers as mserializers
from django.core.exceptions import ObjectDoesNotExist
from .constants import RESOURCE_NAMES, MesosResourceName

SLZ_CLASS = [kserializers.K8sDeploymentSLZ, kserializers.K8sDaemonsetSLZ, kserializers.K8sJobSLZ,
             kserializers.K8sStatefulSetSLZ, kserializers.K8sServiceSLZ, kserializers.K8sConfigMapSLZ,
             kserializers.K8sSecretSLZ, kserializers.K8sIngressSLZ, kserializers.K8sHPASLZ, mserializers.ApplicationSLZ,
             mserializers.DeploymentSLZ, mserializers.ServiceSLZ,
             mserializers.ConfigMapSLZ, mserializers.SecretSLZ]
RESOURCE_SLZ_MAP = dict(zip(RESOURCE_NAMES, SLZ_CLASS))

logger = logging.getLogger(__name__)


def get_slz_class_by_resource_name(resource_name):
    return RESOURCE_SLZ_MAP[resource_name]


def can_delete_resource(ventity, resource_name, resource_id):
    # 验证 pod 资源是否被 Service 关联
    if resource_name in models.POD_RES_LIST:
        pod_res_name, related_svc_names = models.get_pod_related_service(ventity, resource_name, resource_id)
        if related_svc_names:
            raise ValidationError(f"{resource_name}[{pod_res_name}] 被以下资源关联，不能被删除: "
                                  f"{','.join(related_svc_names)}")

    # 删除 Application 时，需要先判断 Deployment 和 service 的依赖关系
    if resource_name == MesosResourceName.application.value:
        app_name, related_resource_names = models.get_application_related_resource(ventity, resource_id)
        if related_resource_names:
            raise ValidationError(f"{resource_name}[{app_name}] 被以下资源关联，不能删除: "
                                  f"{','.join(related_resource_names)}")


class SearchTemplateSLZ(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(required=True)
    offset = serializers.IntegerField(required=True)
    perm_can_use = serializers.BooleanField(required=False, default='0')

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['search'] = data.get('search', '')
        return data


class CreateTemplateSLZ(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30, required=True)
    desc = serializers.CharField(max_length=50, required=False, allow_blank=True)
    project_id = serializers.CharField(max_length=64)

    class Meta:
        model = models.Template
        fields = ('name', 'desc', 'project_id')


class TemplateDraftSLZ(serializers.ModelSerializer):
    draft = serializers.JSONField(required=True)
    real_version_id = serializers.IntegerField(required=True)

    class Meta:
        model = models.Template
        fields = ('id', 'draft', 'draft_time', 'draft_version', 'draft_updator', 'real_version_id')

    def validate(self, data):
        real_version_id = data['real_version_id']
        if real_version_id > 0:
            template_id = self.context['template_id']
            try:
                models.VersionedEntity.objects.get(id=real_version_id, template_id=template_id)
            except models.VersionedEntity.DoesNotExist:
                raise ValidationError(f"模板集版本(id:{real_version_id})不属于该模板(id:{template_id})")
        return data

    def update(self, instance, validated_data):
        instance.draft = json.dumps(validated_data.get('draft'))
        instance.draft_version = validated_data.get('real_version_id')
        instance.draft_updator = validated_data.get('draft_updator')
        instance.draft_time = timezone.now()
        instance.save()
        return instance


class ListTemplateSLZ(serializers.ModelSerializer):
    logo = serializers.CharField(source='log_url')
    category_name = serializers.CharField(source='get_category_display')

    class Meta:
        model = models.Template
        fields = ('id', 'name', 'category', 'desc', 'creator', 'updator', 'created', 'updated',
                  'logo', 'is_locked', 'locker', 'category_name')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        latest_version = ''
        latest_version_id = 0
        latest_show_version_id = -1
        latest_show_version = "草稿" if instance.get_draft() else ""

        show_version = models.ShowVersion.objects.get_latest_by_template(instance.id)
        if show_version:
            latest_version = show_version.real_version_id
            latest_version_id = show_version.real_version_id
            latest_show_version = show_version.name
            latest_show_version_id = show_version.id

        data.update({
            "latest_version": latest_version,
            "latest_version_id": latest_version_id,
            "latest_show_version": latest_show_version,
            "latest_show_version_id": latest_show_version_id,
            "containers": instance.get_containers(self.context['kind'], show_version),
        })
        return data


class VentityWithTemplateSLZ(serializers.Serializer):
    version_id = serializers.IntegerField(required=True)
    project_id = serializers.CharField(required=True)

    def validate(self, data):
        version_id = data['version_id']
        try:
            ventity = models.VersionedEntity.objects.get(id=version_id)
        except models.VersionedEntity.DoesNotExist:
            raise ResNotFoundError(f"模板集版本(id:{version_id})不存在")
        else:
            data['ventity'] = ventity

        project_id = data['project_id']
        try:
            template = models.get_template_by_project_and_id(project_id, ventity.template_id)
        except ValidationError:
            raise ValidationError(f"模板集版本(id:{version_id})不属于该项目(id:{project_id})")
        else:
            data['template'] = template

        return data


class TemplateResourceSLZ(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    version_id = serializers.IntegerField(required=True)

    def validate(self, data):
        version_id = data['version_id']
        try:
            ventity = models.VersionedEntity.objects.get(id=version_id)
            template = models.Template.objects.get(id=ventity.template_id)

        except ObjectDoesNotExist:
            raise ResNotFoundError(f"模板集版本(id:{version_id})不存在")

        except Exception as error:
            logger.exceptions('get template error, %s', error)
            raise ResNotFoundError(f"模板集版本(id:{version_id})获取失败")

        project_id = data['project_id']
        if project_id != template.project_id:
            raise ValidationError(f"模板集版本(id:{version_id})不属于该项目(id:{project_id})")

        data['ventity'] = ventity
        return data
