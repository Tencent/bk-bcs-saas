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
import logging
import json
import re

from django.utils import timezone
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from jsonschema import ValidationError as JsonValidationError, SchemaError, validate as json_validate

from backend.apps.instance.constants import InsState
from .models import (Template, VersionedEntity, Application, get_app_resource, ShowVersion, K8sIngress,
                     MODULE_DICT, POD_RES_LIST, K8sService, K8sStatefulSet, CATE_SHOW_NAME)
from .constants_bak import APPLICATION_SCHEMA, DEPLPYMENT_SCHNEA, SERVICE_SCHEM, CONFIGMAP_SCHEM, SECRET_SCHEM
from .constants_k8s import (K8S_SECRET_SCHEM, K8S_CONFIGMAP_SCHEM, K8S_SERVICE_SCHEM, K8S_DEPLPYMENT_SCHNEA,
                            K8S_DAEMONSET_SCHNEA, K8S_JOB_SCHNEA, K8S_STATEFULSET_SCHNEA, AFFINITY_SCHNEA)
from backend.apps.configuration.utils import get_real_category, check_var_by_config
from backend.apps.instance.models import VersionInstance, InstanceConfig
from backend.accounts import bcs_perm
from backend.apps.configuration.k8s import constants as constants_k8s

logger = logging.getLogger(__name__)

RE_NAME = re.compile(r'^[a-z]{1}[a-z0-9-]{0,254}$')
RE_SHOW_NAME = re.compile(r'^[a-zA-Z0-9-_.]{1,45}$')


# TODO refactor 后面去除check_resource_name
def check_resource_name(resource_name, data, name):
    # 校验配置信息中的变量名是否规范
    check_var_by_config(data['config'])

    if ('item_id' in data or 'resource_id' in data) and 'project_id' in data:
        if 'item_id' in data:
            result = Template.check_resource_name(
                data['project_id'], resource_name, data['item_id'], name, data['version_id'])
        else:
            result = Template.check_resource_name(
                data['project_id'], resource_name, data['resource_id'], name, data['version_id'])
        if not result:
            raise ValidationError(
                u"%s名称:%s已经在项目模板中被占用,请重新填写" % (resource_name, name))
    return data


def check_app_id(data, data_app_id):
    # data_app_id = data['app_id']:
    if not data['version_id']:
        raise ValidationError(u"请先创建 Application ，再创建 Deplpyment")

    if not data_app_id:
        raise ValidationError(u"请选择关联的 Application")

    req_app_id_list = data_app_id.split(',')

    try:
        version_entity = VersionedEntity.objects.get(id=data['version_id'])
    except Exception:
        raise ValidationError(u"模板集版本(id:%s)不存在" % data['version_id'])

    app_list = version_entity.get_mesos_apps()
    app_id_list = [app.get('app_id') for app in app_list]

    if not set(req_app_id_list).issubset(set(app_id_list)):
        raise ValidationError(
            u"关联的 Application (app_id: %s) 不合法" % data_app_id)
    return data


def is_tempalte_instance(template_id):
    """模板是否被实例化过
    """
    ins_id_list = VersionInstance.objects.filter(
        template_id=template_id, is_bcs_success=True, is_deleted=False
    ).values_list('id', flat=True)
    is_exists = InstanceConfig.objects.filter(
        instance_id__in=ins_id_list, is_deleted=False, is_bcs_success=True
    ).exclude(ins_state=InsState.NO_INS.value).exists()
    return is_exists


def filter_instance_resource_by_version(data, version_id):
    """只返回实例化过的版本内的资源
    """
    exist_instance_ids = VersionInstance.objects.filter(
        version_id=version_id, is_bcs_success=True, is_deleted=False).values_list('id', flat=True)
    _exist_config = InstanceConfig.objects.filter(
        instance_id__in=exist_instance_ids, is_deleted=False, is_bcs_success=True
    )

    new_data = {}
    for _cate in data:
        new_res_list = []
        res_list = data[_cate]
        for _res in res_list:
            _name = _res['name']
            _is_exist = _exist_config.filter(
                category=_cate, name=_name).exists()
            if _is_exist:
                new_res_list.append(_res)
        if len(new_res_list):
            new_data[_cate] = new_res_list
    return new_data


def get_tempate_info(tem, kind):
    """获取模板的基本信息（模板&模板列表）,不再使用 TemplateSLZ
    """
    lasetest_ver = ShowVersion.objects.filter(
        template_id=tem.id).order_by('-updated').first()
    if lasetest_ver:
        latest_show_version = lasetest_ver.name
        latest_show_version_id = lasetest_ver.id
        latest_version = lasetest_ver.real_version_id
        latest_version_id = lasetest_ver.real_version_id
    else:
        latest_version = ''
        latest_version_id = 0

        draft = tem.get_draft
        latest_show_version_id = -1
        if draft:
            latest_show_version = u"草稿"
        else:
            latest_show_version = ""

    data = {
        "id": tem.id,
        "name": tem.name,
        "category": tem.category,
        "desc": tem.desc,
        "creator": tem.creator,
        "updator": tem.updator,
        "created": timezone.localtime(tem.created).strftime('%Y-%m-%d %H:%M:%S'),
        "updated": timezone.localtime(tem.updated).strftime('%Y-%m-%d %H:%M:%S'),
        "category_name": tem.get_category_display(),
        "logo": tem.log_url,
        "containers": tem.get_containers(kind, lasetest_ver),
        "is_locked": tem.is_locked,
        "locker": tem.locker,

        "latest_version": latest_version,
        "latest_version_id": latest_version_id,
        "latest_show_version": latest_show_version,
        "latest_show_version_id": latest_show_version_id,
    }
    return data


class TemplateSLZ(serializers.ModelSerializer):
    """模板集， 返回模板列表数据
    """
    category_name = serializers.CharField(
        source='get_category_display', read_only=True)
    logo = serializers.CharField(source='get_log_url', read_only=True)
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj):
        request = self.context.get('request')
        perm = bcs_perm.Templates(request, obj.project_id, obj.id, obj.name)
        data = {
            'id': obj.id,
            'name': obj.name
        }
        data_list = perm.hook_perms([data])
        permissions = data_list[0].get('permissions')
        return permissions

    class Meta:
        model = Template
        fields = (
            "id",
            "name",
            "category",
            "desc",
            "category_name",
            "logo",
            "latest_version",
            "latest_version_id",
            "creator",
            "created",
            "updated",
            "updator",
            "latest_show_version",
            "latest_show_version_id",
            "permissions"
        )
        read_only_fields = ("creator", "created", "updated", "updator", "permissions")


class ResourceSLZ(serializers.ModelSerializer):
    """模板集版本中的资源信息
    """
    data = serializers.SerializerMethodField()
    lb_services = serializers.JSONField(
        source='get_lb_services', read_only=True)

    class Meta:
        model = VersionedEntity
        fields = (
            "data",
            "lb_services",
        )

    def get_data(self, obj):
        data = obj.get_version_instance_resources()
        category = self.context.get('category')
        name = self.context.get('tmpl_app_name')
        # 应用-实例化：只显示应用相关的资源
        if (category in ['deployment', 'application']) or (category in POD_RES_LIST):
            # 只查询单个应用实例化所需要的资源
            data = get_app_resource(
                data, category, name, is_related_res=True, version_id=obj.id)
        # 传给前端的资源类型统一
        new_data = {CATE_SHOW_NAME.get(x, x): data[x] for x in data}
        return new_data


class ResourceRequstSLZ(serializers.Serializer):
    """资源的请求参数
    """
    category = serializers.CharField(required=False, allow_blank=True)
    tmpl_app_name = serializers.CharField(required=False, allow_blank=True)
    is_filter_version = serializers.CharField(required=False, allow_blank=True)

    def validate_category(self, category):
        project_kind = self.context.get('project_kind')
        return get_real_category(project_kind, category)


class TemplateCreateSLZ(serializers.Serializer):
    """创建／更新模板集基本信息
    """
    name = serializers.CharField(max_length=30, required=True)
    desc = serializers.CharField(
        max_length=50, required=False, allow_blank=True)
    project_id = serializers.CharField(max_length=64)

    def validate(self, data):
        is_exist = Template.default_objects.filter(
            name=data['name'], project_id=data['project_id']).exists()
        if is_exist:
            detail = {
                'field': [u"模板集名称[%s]已经存在" % data['name']]
            }
            raise ValidationError(detail=detail)
        return data


class TemplateUpdateSLZ(serializers.Serializer):
    """更新模板集基本信息
    """
    name = serializers.CharField(max_length=30, required=True)
    desc = serializers.CharField(
        max_length=50, required=False, allow_blank=True)


class ServiceCreateOrUpdateSLZ(serializers.Serializer):
    app_id = serializers.JSONField(required=True)
    config = serializers.JSONField(required=True)
    version_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    project_id = serializers.CharField(required=False)
    # 更新service相关字段
    lb_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    namespace_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    creator = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    create_time = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    def validate_config(self, config):
        # Service 名称可以支持变量
        # name = config.get('metadata', {}).get('name') or ""
        # if not RE_NAME.match(name):
        #     raise ValidationError(
        #         u"Service 名称格式错误，只能包含：小写字母、数字、连字符(-)，首字母必须是字母，长度小于256个字符")

        if settings.IS_TEMPLATE_VALIDATE:
            try:
                json_validate(config, SERVICE_SCHEM)
            except JsonValidationError as e:
                raise ValidationError(u"Service 配置信息格式错误:%s" % e.message)
            except SchemaError as e:
                raise ValidationError(u"Service 配置信息格式错误:%s" % e)

        return json.dumps(config)

    def validate(self, data):
        config = json.loads(data['config'])
        name = config.get('metadata', {}).get('name') or ""

        if not data.get('namespace_id') and not data.get('instance_id'):
            check_resource_name("service", data, name)

        app_id = data['app_id']
        if isinstance(app_id, list):
            req_app_id = ','.join(app_id)
            data['app_id'] = req_app_id
        elif isinstance(app_id, dict):
            req_app_id = ','.join(app_id.keys())
            # 验证权重之和是否为 100
            data_app_values = app_id.values()
            if sum(data_app_values) != 100:
                raise ValidationError(u"关联应用的权重之和不为100%")
            data['app_id'] = json.dumps(app_id)
        else:
            raise ValidationError(u"关联应用参数格式错误")

        return check_app_id(data, req_app_id)


class ConfigMapCreateOrUpdateSLZ(serializers.Serializer):
    """
    """
    config = serializers.JSONField(required=True)
    version_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    project_id = serializers.CharField(required=False)

    namespace_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    def validate_config(self, config):
        name = config.get('metadata', {}).get('name') or ""
        if not RE_NAME.match(name):
            raise ValidationError(
                u"ConfigMap 名称格式错误，只能包含：小写字母、数字、连字符(-)，首字母必须是字母，长度小于256个字符")

        if settings.IS_TEMPLATE_VALIDATE:
            try:
                json_validate(config, CONFIGMAP_SCHEM)
            except JsonValidationError as e:
                raise ValidationError(u"ConfigMap 配置信息格式错误:%s" % e.message)
            except SchemaError as e:
                raise ValidationError(u"ConfigMap 配置信息格式错误:%s" % e)

        return json.dumps(config)

    def validate(self, data):
        config = json.loads(data['config'])
        name = config.get('metadata', {}).get('name') or ""
        return check_resource_name("configmap", data, name)


class SecretCreateOrUpdateSLZ(serializers.Serializer):
    """
    """
    config = serializers.JSONField(required=True)
    version_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    project_id = serializers.CharField(required=False)

    namespace_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    def validate_config(self, config):
        name = config.get('metadata', {}).get('name') or ""
        if not RE_NAME.match(name):
            raise ValidationError(
                u"Secret 名称格式错误，只能包含：小写字母、数字、连字符(-)，首字母必须是字母，长度小于256个字符")

        if settings.IS_TEMPLATE_VALIDATE:
            try:
                json_validate(config, SECRET_SCHEM)
            except JsonValidationError as e:
                raise ValidationError(u"Secret 配置信息格式错误:%s" % e.message)
            except SchemaError as e:
                raise ValidationError(u"Secret 配置信息格式错误:%s" % e)

        return json.dumps(config)

    def validate(self, data):
        config = json.loads(data['config'])
        name = config.get('metadata', {}).get('name') or ""
        return check_resource_name("secret", data, name)


# ############################## k8s 相关资源
K8S_RENAME = re.compile(
    r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$')
K8S_NAME_ERROR_MSG = u"名称格式错误，以小写字母或数字开头，只能包含：小写字母、数字、连字符(-)、点(.)"


def check_k8s_deployment_id(data, deploy_tag_list):
    """检查 k8s Service 中关联的 Deployment 是否合法
    """
    if not data['version_id']:
        raise ValidationError(u"请先创建 Deplpyment ，再创建 Service")

    if not deploy_tag_list:
        raise ValidationError(u"请选择关联的 Deplpyment")

    return data


class K8sServiceCreateOrUpdateSLZ(serializers.Serializer):
    # k8s 中 service 可不关联应用
    deploy_tag_list = serializers.JSONField(required=False)
    config = serializers.JSONField(required=True)
    version_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    project_id = serializers.CharField(required=False)

    resource_version = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    namespace_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    creator = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    create_time = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    def validate_config(self, config):
        # k8s Service 名称可以支持变量
        # name = config.get('metadata', {}).get('name') or ""
        # if not K8S_RENAME.match(name):
        #     raise ValidationError(
        #         u"Service %s" % K8S_NAME_ERROR_MSG)

        if settings.IS_TEMPLATE_VALIDATE:
            try:
                json_validate(config, K8S_SERVICE_SCHEM)
            except JsonValidationError as e:
                raise ValidationError(u"Service 配置信息格式错误:%s" % e.message)
            except SchemaError as e:
                raise ValidationError(u"Service 配置信息格式错误:%s" % e)

        return json.dumps(config)

    def validate_deploy_tag_list(self, deploy_tag_list):
        if not deploy_tag_list:
            deploy_tag_list = []
        return json.dumps(deploy_tag_list)

    def validate(self, data):
        config = json.loads(data['config'])
        name = config.get('metadata', {}).get('name') or ""

        if not data.get('namespace_id') and not data.get('instance_id'):
            check_resource_name("K8sService", data, name)

        deploy_tag_list = data.get('deploy_tag_list')
        try:
            deploy_tag_list = json.loads(deploy_tag_list)
        except Exception:
            deploy_tag_list = []
        # k8s 中 service 可不关联应用
        data['deploy_tag_list'] = deploy_tag_list
        if not deploy_tag_list:
            return data
        elif not isinstance(deploy_tag_list, list):
            raise ValidationError(u"关联Deployment参数格式错误")

        return check_k8s_deployment_id(data, deploy_tag_list)


class K8sConfigMapCreateOrUpdateSLZ(serializers.Serializer):
    config = serializers.JSONField(required=True)
    version_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    project_id = serializers.CharField(required=False)

    namespace_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    def validate_config(self, config):
        name = config.get('metadata', {}).get('name') or ""
        if not K8S_RENAME.match(name):
            raise ValidationError(
                u"ConfigMap %s" % K8S_NAME_ERROR_MSG)

        if settings.IS_TEMPLATE_VALIDATE:
            try:
                json_validate(config, K8S_CONFIGMAP_SCHEM)
            except JsonValidationError as e:
                raise ValidationError(u"ConfigMap 配置信息格式错误:%s" % e.message)
            except SchemaError as e:
                raise ValidationError(u"ConfigMap 配置信息格式错误:%s" % e)

        return json.dumps(config)

    def validate(self, data):
        config = json.loads(data['config'])
        name = config.get('metadata', {}).get('name') or ""
        return check_resource_name("K8sConfigMap", data, name)


class K8sSecretCreateOrUpdateSLZ(serializers.Serializer):
    config = serializers.JSONField(required=True)
    version_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    project_id = serializers.CharField(required=False)

    namespace_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    def validate_config(self, config):
        name = config.get('metadata', {}).get('name') or ""
        if not K8S_RENAME.match(name):
            raise ValidationError(
                u"Secret %s" % K8S_NAME_ERROR_MSG)

        if settings.IS_TEMPLATE_VALIDATE:
            try:
                json_validate(config, K8S_SECRET_SCHEM)
            except JsonValidationError as e:
                raise ValidationError(u"Secret 配置信息格式错误:%s" % e.message)
            except SchemaError as e:
                raise ValidationError(u"Secret 配置信息格式错误:%s" % e)

        return json.dumps(config)

    def validate(self, data):
        config = json.loads(data['config'])
        name = config.get('metadata', {}).get('name') or ""
        return check_resource_name("K8sSecret", data, name)


class K8sIngressCreateOrUpdateSLZ(serializers.Serializer):
    config = serializers.JSONField(required=True)
    version_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    project_id = serializers.CharField(required=False)

    namespace_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    instance_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    def validate_config(self, config):
        name = config.get('metadata', {}).get('name') or ''
        if not K8S_RENAME.match(name):
            raise ValidationError(f'Ingress {K8S_NAME_ERROR_MSG}')

        if settings.IS_TEMPLATE_VALIDATE:
            try:
                json_validate(config, constants_k8s.K8S_INGRESS_SCHEMA)
            except JsonValidationError as e:
                raise ValidationError(f'Ingress 配置信息格式错误:{e.message}')
            except SchemaError as e:
                raise ValidationError(f'Ingress 配置信息格式错误:{e}')

        return json.dumps(config)

    def validate(self, data):
        config = json.loads(data['config'])
        name = config.get('metadata', {}).get('name') or ''
        return check_resource_name("K8sIngress", data, name)