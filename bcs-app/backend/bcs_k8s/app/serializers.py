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
import datetime
import subprocess

from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ParseError
from django.utils.translation import ugettext_lazy as _

from backend.utils.error_codes import error_codes
from backend.components import paas_cc

from .models import App
from backend.bcs_k8s.helm.models import ChartVersion
from backend.bcs_k8s.helm.serializers import ChartReleaseSLZ, RepoSLZ
from backend.bcs_k8s.kubehelm.helm import KubeHelmClient
from backend.bcs_k8s.kubehelm import exceptions as helm_exceptions
from backend.bcs_k8s.diff.parser import parse
from backend.bcs_k8s.diff.diff import simple_diff
from backend.utils.serializers import YamlField, HelmValueField
from backend.utils.tempfile import save_to_temporary_dir
from backend.utils.client import make_kubectl_client, get_bcs_client
from backend.bcs_k8s.helm.constants import KEEP_TEMPLATE_UNCHANGED, RESOURCE_NAME_REGEX, DEFAULT_VALUES_FILE_NAME
from backend.bcs_k8s.helm.utils.util import merge_rancher_answers
from backend.bcs_k8s.permissions import check_cluster_perm
from backend.bcs_k8s.helm.bcs_variable import (
    collect_system_variable,
    get_valuefile_with_bcs_variable_injected)
from .deployer import AppDeployer
from . import bcs_info_injector
from . import utils


def preview_parse(manifest, namespace):
    data = parse(manifest, namespace)
    result = dict()
    for key in data:
        r_key = "/".join(key.split(", "))
        result[r_key] = data[key].content
    return result


class AppMixin:
    """ app serializer 公用方法 """
    @property
    def project_id(self):
        return self.context["request"].parser_context["kwargs"]["project_id"]

    @property
    def app_id(self):
        return self.context["request"].parser_context["kwargs"]["app_id"]

    @property
    def access_token(self):
        return self.context["request"].user.token.access_token

    @property
    def request_username(self):
        return self.context["request"].user.username

    def get_available_ns(self):
        result = paas_cc.get_namespace_list(self.access_token, self.project_id)
        return result["data"]["results"]

    def get_ns_info_by_id(self, namespace_id):
        result = paas_cc.get_namespace(self.access_token, self.project_id, namespace_id)
        if result.get('code') != 0:
            raise error_codes.APIError.f(result.get('message', ''))

        namespace_info = result["data"]
        return namespace_info

    def get_upgrade_version_selections(self):
        # get selections for upgrade, all chart versions and a special option indicate not change with template.
        instance = self.current_instance
        return instance.get_upgrade_version_selections()

    def get_history_releases(self):
        # get history release for rollback, all current app releases eliminate current.
        instance = self.current_instance
        return instance.get_history_releases()

    @property
    def current_instance(self):
        # this property can only be used when pk in url
        app_id = self.context["request"].parser_context["kwargs"]["app_id"]
        return App.objects.get(id=app_id)


class AppBaseSLZ(AppMixin, serializers.ModelSerializer):
    def save(self, **kwargs):
        instance = super(AppBaseSLZ, self).save(**kwargs)

        # AppDeployer(app=instance, access_token=self.access_token).install_app()
        instance.refresh_from_db()
        return instance


class NamespaceInfoField(serializers.RelatedField):
    cluster_id = serializers.CharField()
    created_at = serializers.CharField()
    creator = serializers.CharField()
    description = serializers.CharField()
    env_type = serializers.CharField()
    id = serializers.IntegerField()
    name = serializers.CharField()
    project_id = serializers.CharField()
    status = serializers.CharField()
    updated_at = serializers.CharField()

    def to_representation(self, value):
        if isinstance(value, dict):
            return value["id"]
        return str(value)

    def get_queryset(self):
        return self.parent.get_available_ns()

    def display_value(self, instance):
        if isinstance(instance, dict):
            return '{cluster_id}: {id}-{name}'.format(**instance)

        return instance

    def to_internal_value(self, value):
        return value


class AppSLZ(AppBaseSLZ):
    name = serializers.RegexField(
        RESOURCE_NAME_REGEX,
        error_messages={"invalid": _('不符合k8s资源名规范, 只能由小写字母数字或者-组成，正则:{}').format(RESOURCE_NAME_REGEX)}
    )
    namespace_info = NamespaceInfoField(write_only=True, label="Namespace")
    chart_version = serializers.PrimaryKeyRelatedField(queryset=ChartVersion.objects.all(), write_only=True)
    answers = HelmValueField(
        initial=[],
        write_only=True,
        label="Answers",
        help_text="JSON format data",
        source="get_answers",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    customs = HelmValueField(
        initial=[],
        write_only=True,
        label="Customs",
        help_text="JSON format data",
        source="get_customs",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    valuefile = YamlField(
        initial="",
        write_only=True,
        allow_blank=True,
        default="",
        label="ValueFile",
        help_text="Yaml format data",
        source="get_valuefile",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )
    valuefile_name = serializers.CharField(
        source="get_valuefile_name", write_only=True, default=DEFAULT_VALUES_FILE_NAME)

    current_version = serializers.CharField(source="get_current_version", read_only=True)

    def create(self, validated_data):
        namespace_info = self.get_ns_info_by_id(validated_data["namespace_info"])

        check_cluster_perm(
            user=self.context["request"].user,
            project_id=namespace_info["project_id"],
            cluster_id=namespace_info["cluster_id"],
            request=self.context["request"]
        )

        # 检查集群已经成功注册到 bcs, 否则让用户先完成注册逻辑
        bcs_client = get_bcs_client(
            project_id=namespace_info["project_id"],
            cluster_id=namespace_info["cluster_id"],
            access_token=self.context["request"].user.token.access_token
        )
        bcs_client.get_cluster_credential()

        sys_variables = collect_system_variable(
            access_token=self.context["request"].user.token.access_token,
            project_id=namespace_info["project_id"],
            namespace_id=namespace_info["id"])

        return App.objects.initialize_app(
            access_token=self.access_token,
            name=validated_data.get("name"),
            project_id=self.project_id,
            cluster_id=namespace_info["cluster_id"],
            namespace_id=namespace_info["id"],
            namespace=namespace_info["name"],
            chart_version=validated_data["chart_version"],
            answers=validated_data["get_answers"],
            customs=validated_data["get_customs"],
            valuefile=validated_data.get("get_valuefile"),
            creator=self.request_username,
            updator=self.request_username,
            sys_variables=sys_variables,
            valuefile_name=validated_data.get('get_valuefile_name')
        )

    def validate_name(self, value):
        """make sure app name is starts with alphabet character,
        if the name used as resource name, numeric will forbidded by api server
        """
        if value and (not value.islower() or not value[:1].islower()):
            raise serializers.ValidationError("name must starts with lower alphabet character")
        return value

    class Meta:
        model = App
        fields = (
            "name",
            "namespace",
            "namespace_id",
            "cluster_id",
            "namespace_info",
            "chart_version",
            "answers",
            "customs",
            "valuefile",
            "project_id",
            "chart",
            "transitioning_result",
            "transitioning_message",
            "transitioning_on",
            "transitioning_action",
            "created",
            "updated",
            "creator",
            "updator",
            "current_version",
            "id",
            "valuefile_name",
        )
        read_only_fields = (
            "namespace",
            "namespace_id",
            "cluster_id",
            "project_id",
            "chart",
            "transitioning_result",
            "transitioning_message",
            "transitioning_on",
            "transitioning_action",
            "created",
            "updated",
            "creator",
            "updator",
            "current_version",
        )


class AppDetailSLZ(AppBaseSLZ):
    namespace_info = NamespaceInfoField(write_only=True, label="Namespace")
    chart_info = serializers.JSONField(read_only=True, label="Chart Info")
    chart_version = serializers.PrimaryKeyRelatedField(queryset=ChartVersion.objects.all(), write_only=True)
    release = ChartReleaseSLZ(read_only=True)

    answers = HelmValueField(
        initial=[],
        read_only=True,
        label="Answers",
        help_text="JSON format data",
        source="get_answers",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    customs = HelmValueField(
        initial=[],
        read_only=True,
        label="Customs",
        help_text="JSON format data",
        source="get_customs",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    valuefile = YamlField(
        initial="",
        read_only=True,
        default="",
        label="ValueFile",
        help_text="Yaml format data",
        source="get_valuefile",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )
    valuefile_name = serializers.CharField(source="get_valuefile_name", read_only=True)

    class Meta:
        model = App
        fields = (
            "id",
            "name",
            "namespace",
            "namespace_id",
            "cluster_id",
            "namespace_info",
            "chart_version",
            "chart_info",
            "answers",
            "customs",
            "valuefile",
            "project_id",
            "chart",
            "transitioning_result",
            "transitioning_message",
            "transitioning_on",
            "transitioning_action",
            "release",
            "creator",
            "updator",
            "created",
            "updated",
            "valuefile_name",
        )


class UpgradeVersionField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, dict):
            return value["id"]
        return str(value)

    def get_queryset(self):
        return self.parent.get_upgrade_version_selections()

    def display_value(self, instance):
        if isinstance(instance, dict):
            return '{id}: {version}'.format(**instance)
        return instance

    def to_internal_value(self, value):
        return value


class AppUpgradeSLZ(AppBaseSLZ):
    upgrade_verion = UpgradeVersionField(write_only=True, required=True)
    answers = HelmValueField(
        label="Answers",
        help_text="JSON format data",
        source="get_answers",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )
    customs = HelmValueField(
        label="Customs",
        help_text="JSON format data",
        source="get_customs",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    valuefile = YamlField(
        initial="",
        default="",
        label="ValueFile",
        allow_blank=True,
        help_text="Yaml format data",
        source="get_valuefile",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )
    valuefile_name = serializers.CharField(
        source="get_valuefile_name", write_only=True, default=DEFAULT_VALUES_FILE_NAME)

    def update(self, instance, validated_data):
        # update sys variable
        sys_variables = collect_system_variable(
            access_token=self.context["request"].user.token.access_token,
            project_id=instance.project_id,
            namespace_id=instance.namespace_id)

        return instance.upgrade_app(
            access_token=self.access_token,
            chart_version_id=validated_data["upgrade_verion"],
            answers=validated_data["get_answers"],
            customs=validated_data["get_customs"],
            valuefile=validated_data.get("get_valuefile"),
            updator=self.request_username,
            sys_variables=sys_variables,
            valuefile_name=validated_data.get("get_valuefile_name"),
        )

    class Meta:
        model = App
        fields = (
            "name",
            "namespace",
            "upgrade_verion",
            "answers",
            "customs",
            "valuefile",
            "project_id",
            "cluster_id",
            "chart",
            "transitioning_result",
            "transitioning_message",
            "transitioning_on",
            "transitioning_action",
            "id",
            "valuefile_name"
        )
        read_only_fields = (
            "name",
            "namespace",
            "project_id",
            "cluster_id",
            "chart",
            "transitioning_result",
            "transitioning_message",
            "transitioning_on",
            "transitioning_action",
        )
        extra_kwargs = {
            "answers": {
                "write_only": True
            },
            "customs": {
                "write_only": True
            },
            "valuefile": {
                "write_only": True
            },
            "upgrade_verion": {
                "write_only": True
            },
            "valuefile_name": {
                "write_only": True
            },
        }


class HistoryReleaseField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, dict):
            return value["id"]
        return str(value)

    def get_queryset(self):
        return self.parent.get_history_releases()

    def display_value(self, instance):
        if isinstance(instance, dict):
            return '{id}: {version}-{short_name}'.format(**instance)

        return instance

    def to_internal_value(self, value):
        return value


class AppRollbackSLZ(AppBaseSLZ):
    release = HistoryReleaseField(write_only=True, required=True)

    def update(self, instance, validated_data):
        check_cluster_perm(
            user=self.context["request"].user,
            project_id=instance.project_id,
            cluster_id=instance.cluster_id,
            request=self.context["request"]
        )

        # operation record
        return instance.rollback_app(
            username=self.request_username,
            access_token=self.access_token,
            release_id=validated_data["release"],
        )

    class Meta:
        model = App
        fields = "__all__"
        read_only_fields = (
            "name",
            "namespace",
            "namespace_id",
            "project_id",
            "cluster_id",
            "chart",
            "transitioning_result",
            "transitioning_message",
            "transitioning_on",
            "transitioning_action",
            "creator",
            "updator",
            "created",
            "updated",
        )


class NamespaceSLZ(serializers.Serializer):
    id = serializers.IntegerField()
    cluster_id = serializers.CharField(max_length=64)
    created_at = serializers.CharField(max_length=64)
    creator = serializers.CharField(max_length=64)
    description = serializers.CharField(max_length=64)
    env_type = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=64)
    project_id = serializers.CharField(max_length=64)
    status = serializers.CharField(max_length=64)
    updated_at = serializers.CharField(max_length=64)


class AppUpgradeVersionsSLZ(serializers.Serializer):
    id = serializers.IntegerField()
    version = serializers.CharField(max_length=64)


class AppRollbackSelectionsSLZ(serializers.Serializer):
    id = serializers.IntegerField()
    short_name = serializers.CharField(max_length=64)
    version = serializers.CharField(max_length=64)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


class AppReleaseDiffSLZ(serializers.Serializer):
    release = HistoryReleaseField(write_only=True, required=True)
    difference = serializers.CharField(read_only=True)

    def create(self, validated_data):
        difference = self.app.diff_release(release_id=validated_data["release"])
        return {"difference": difference}

    @property
    def app(self):
        app_id = self.context["request"].parser_context["kwargs"]["app_id"]
        return App.objects.get(id=app_id)

    def get_history_releases(self):
        return self.app.get_history_releases()

    class Meta:
        fields = ("release", "difference")
        read_only_fields = ("difference",)


class AppReleasePreviewSLZ(AppMixin, serializers.Serializer):
    """ 发布预览 """
    upgrade_verion = UpgradeVersionField(write_only=True, required=True)
    answers = HelmValueField(
        initial=[],
        write_only=True,
        label="Answers",
        help_text="JSON format data",
        source="get_answers",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    customs = HelmValueField(
        initial=[],
        write_only=True,
        label="Customs",
        help_text="JSON format data",
        source="get_customs",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    valuefile = YamlField(
        initial="",
        write_only=True,
        allow_blank=True,
        required=False,
        default="",
        label="ValueFile",
        help_text="Yaml format data",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    content = serializers.JSONField(read_only=True)
    notes = serializers.JSONField(read_only=True)
    difference = serializers.JSONField(read_only=True)
    chart_version_changed = serializers.BooleanField(read_only=True)
    old_content = serializers.JSONField(read_only=True)
    # 方便前端渲染
    new_content = serializers.JSONField(read_only=True)

    def create(self, validated_data):
        """ 应用更新时的预览数据，这个时候目标release还没有创建 """
        instance = App.objects.get(id=self.app_id)

        check_cluster_perm(
            user=self.context["request"].user,
            project_id=instance.project_id,
            cluster_id=instance.cluster_id,
            request=self.context["request"]
        )

        # 标记Chart中的values.yaml是否发生变化，用于提醒用户
        chart_version_changed = False

        # prepare parameters
        parameters = merge_rancher_answers(validated_data["get_answers"], validated_data["get_customs"])

        chart_version_id = validated_data["upgrade_verion"]
        chart_version_id = int(chart_version_id)
        if chart_version_id == KEEP_TEMPLATE_UNCHANGED:
            files = instance.release.chartVersionSnapshot.files
        else:
            chart_version_changed = True
            chart_version = ChartVersion.objects.get(id=chart_version_id)
            files = chart_version.files

        valuefile = get_valuefile_with_bcs_variable_injected(
            access_token=self.context["request"].user.token.access_token,
            project_id=instance.project_id,
            namespace_id=instance.namespace_id,
            valuefile=validated_data["valuefile"],
            cluster_id=instance.cluster_id
        )
        client = KubeHelmClient(helm_bin=settings.HELM_BIN)
        try:
            content, notes = client.template(
                files=files,
                namespace=instance.namespace,
                name=instance.name,
                parameters=parameters,
                valuefile=valuefile,
            )
        except helm_exceptions.HelmBaseException as e:
            raise ParseError(str(e))

        # inject bcs info
        now = datetime.datetime.now()
        content = bcs_info_injector.inject_bcs_info(
            access_token=self.access_token,
            project_id=instance.project_id,
            cluster_id=instance.cluster_id,
            namespace_id=instance.namespace_id,
            namespace=instance.namespace,
            creator=instance.creator,
            updator=self.context["request"].user.username,
            created_at=instance.created,
            updated_at=now,
            resources=content,
            version=instance.release.chartVersionSnapshot.version,
        )

        # compute diff
        old_content = instance.release.content
        if not old_content:
            old_content, _ = instance.render_app(
                username=self.context["request"].user.username,
                access_token=self.access_token)
        difference = simple_diff(old_content, content, instance.namespace)
        return {
            "content": preview_parse(content, instance.namespace),
            "notes": notes,
            "difference": difference,
            "chart_version_changed": chart_version_changed,
            "old_content": old_content,
            "new_content": content
        }

    class Meta:
        fields = (
            "name",
            "namespace_info",
            "chart_version",
            "answers",
            "customs",
            "valuefile",
            "content",
            "notes",
            "difference",
            "chart_version_changed",
        )
        read_only_fields = (
            "content",
            "notes",
            "chart_version_changed",
        )


class AppRollbackPreviewSLZ(AppMixin, serializers.Serializer):
    """ 回滚预览 """
    release = HistoryReleaseField(write_only=True, required=True)

    # response fields
    content = serializers.JSONField(read_only=True)
    notes = serializers.JSONField(read_only=True)
    difference = serializers.JSONField(read_only=True)

    def create(self, validated_data):
        """ 生成应用的预览数据 """
        instance = App.objects.get(id=self.app_id)

        check_cluster_perm(
            user=self.context["request"].user,
            project_id=instance.project_id,
            cluster_id=instance.cluster_id,
            request=self.context["request"]
        )

        difference = instance.diff_release(release_id=validated_data["release"])
        content, notes = instance.render_app(
            username=self.context["request"].user.username,
            access_token=self.access_token)
        return {
            "difference": difference,
            "content": preview_parse(content, instance.namespace),
            "notes": notes,
        }

    class Meta:
        fields = (
            "release",
            "content",
            "notes",
            "difference",
        )
        read_only_fields = (
            "content",
            "notes",
            "difference",
        )


class AppPreviewSLZ(serializers.Serializer):
    """ 获取 app 的预览信息 """
    content = serializers.JSONField(read_only=True)
    notes = serializers.JSONField(read_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        fields = (
            "content",
            "notes",
            "token",
        )
        read_only_fields = (
            "content",
            "notes",
            "token",
        )


class AppCreatePreviewSLZ(AppMixin, serializers.Serializer):
    """ 创建预览 """
    name = serializers.CharField(write_only=True)
    namespace_info = NamespaceInfoField(write_only=True, label="Namespace")
    chart_version = serializers.PrimaryKeyRelatedField(queryset=ChartVersion.objects.all(), write_only=True)
    answers = HelmValueField(
        initial=[],
        write_only=True,
        label="Answers",
        help_text="JSON format data",
        source="get_answers",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    customs = HelmValueField(
        initial=[],
        write_only=True,
        label="Customs",
        help_text="JSON format data",
        source="get_customs",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    valuefile = YamlField(
        initial="",
        write_only=True,
        allow_blank=True,
        default="",
        label="ValueFile",
        help_text="Yaml format data",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    content = serializers.JSONField(read_only=True)
    notes = serializers.JSONField(read_only=True)

    def create(self, validated_data):
        """ 生成应用的预览数据，这个时候应用没有创建，release也没有创建 """
        namespace_info = self.get_ns_info_by_id(validated_data["namespace_info"])

        check_cluster_perm(
            user=self.context["request"].user,
            project_id=namespace_info["project_id"],
            cluster_id=namespace_info["cluster_id"],
            request=self.context["request"]
        )

        # prepare parameters
        parameters = merge_rancher_answers(validated_data["get_answers"], validated_data["get_customs"])

        valuefile = get_valuefile_with_bcs_variable_injected(
            access_token=self.context["request"].user.token.access_token,
            project_id=namespace_info["project_id"],
            namespace_id=namespace_info["id"],
            valuefile=validated_data["valuefile"],
            cluster_id=namespace_info["cluster_id"]
        )
        client = KubeHelmClient(helm_bin=settings.HELM_BIN)
        try:
            content, notes = client.template(
                files=validated_data["chart_version"].files,
                namespace=namespace_info["name"],
                name=validated_data.get("name"),
                parameters=parameters,
                valuefile=valuefile,
            )
        except helm_exceptions.HelmBaseException as e:
            raise ParseError(str(e))

        # inject bcs info
        now = datetime.datetime.now()
        username = self.context["request"].user.username
        content = bcs_info_injector.inject_bcs_info(
            access_token=self.access_token,
            project_id=self.project_id,
            cluster_id=namespace_info["cluster_id"],
            namespace_id=namespace_info["id"],
            namespace=namespace_info["name"],
            creator=username,
            updator=username,
            created_at=now,
            updated_at=now,
            resources=content,
            version=validated_data["chart_version"].version
        )
        return {
            "content": preview_parse(content, namespace_info["name"]),
            "notes": notes
        }

    class Meta:
        fields = (
            "name",
            "namespace_info",
            "chart_version",
            "answers",
            "customs",
            "valuefile",
            "content",
            "notes",
        )
        read_only_fields = (
            "content",
            "notes",
        )


class ClusterImportSLZ(serializers.Serializer):
    cluster_id = serializers.CharField()


class ClusterKubeConfigSLZ(serializers.Serializer):
    cluster_id = serializers.CharField()


class SyncDict2YamlToolSLZ(serializers.Serializer):
    dict = serializers.JSONField(
        initial={},
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )
    yaml = YamlField(
        initial=[],
        label="Yaml",
        help_text="Yaml format data",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    def create(self, validated_data):
        content = utils.sync_dict2yaml(validated_data["dict"], validated_data["yaml"])
        return {
            "yaml": content,
            "dict": validated_data["dict"]
        }

    class Meta:
        fields = (
            "yaml",
            "dict",
        )


class SyncYaml2DictToolSLZ(serializers.Serializer):
    dict = serializers.JSONField(
        initial={},
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )
    yaml = YamlField(
        initial=[],
        label="Yaml",
        help_text="Yaml format data",
        style={
            "base_template": "textarea.html",
            "rows": 10
        }
    )

    def create(self, validated_data):
        dict_list = utils.sync_yaml2dict(validated_data["dict"], validated_data["yaml"])
        return {
            "yaml": validated_data["yaml"],
            "dict": dict_list
        }

    class Meta:
        fields = (
            "yaml",
            "dict",
        )


class ClusterHelmInitSLZ(serializers.Serializer):
    cluster_id = serializers.CharField(write_only=True)
    public_repos = RepoSLZ(read_only=True, many=True)
    private_repos = RepoSLZ(read_only=True, many=True)
    initialized = serializers.BooleanField(read_only=True)

    class Meta:
        fields = (
            "cluster_id",
            "public_repos",
            "private_repos",
            "initialized",
        )


class AppCreatePreviewDiffWithClusterSLZ(AppCreatePreviewSLZ):
    difference = serializers.JSONField(read_only=True)

    class Meta:
        fields = (
            "name",
            "namespace_info",
            "chart_version",
            "answers",
            "customs",
            "valuefile",
            "content",
            "notes",
            "difference",
        )
        read_only_fields = (
            "content",
            "notes",
            "difference",
        )

    def create(self, validated_data):
        data = super(AppCreatePreviewDiffWithClusterSLZ, self).create(validated_data)
        namespace_info = self.get_ns_info_by_id(validated_data["namespace_info"])

        check_cluster_perm(
            user=self.context["request"].user,
            project_id=namespace_info["project_id"],
            cluster_id=namespace_info["cluster_id"],
            request=self.context["request"]
        )

        with save_to_temporary_dir(data["content"]) as tempdir:
            with make_kubectl_client(
                project_id=self.project_id,
                cluster_id=namespace_info["cluster_id"],
                access_token=self.access_token
            ) as (client, err):
                if err:
                    raise serializers.ValidationError("make kubectl client failed, %s", err)

                args = ["kubediff", "--kubeconfig", client.kubeconfig, "--json", "--no-error-on-diff", tempdir]
                difference = subprocess.check_output(args)
                difference = json.loads(difference)
                data.update(difference=difference)

        return data


class AppStateSLZ(serializers.Serializer):
    replicas = serializers.IntegerField(read_only=True)
    readyReplicas = serializers.IntegerField(read_only=True)
    availableReplicas = serializers.IntegerField(read_only=True)
    updatedReplicas = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            "replicas",
            "readyReplicas",
            "availableReplicas",
            "updatedReplicas",
        )

class AppUpgradeByAPISLZ(AppUpgradeSLZ):
    def update(self, instance, validated_data, *args, **kwargs):
        token = self.context["request"].user.token

        # validate wtih token
        validated_data["app_id"] = instance.id
        validated_data["cluster_id"] = instance.cluster_id
        validated_data["project_id"] = instance.project_id
        token.validate_request_data(validated_data)

        extra_inject_source = token.config.get("extra_inject_source")
        kubeconfig = token.config.get("kubeconfig")

        # merge valuefile
        valuefile = utils.merge_valuefile(instance.get_valuefile(), validated_data.get("get_valuefile"))

        return instance.upgrade_app(
            access_token=None,
            chart_version_id=validated_data["upgrade_verion"],
            answers=validated_data["get_answers"],
            customs=validated_data["get_customs"],
            valuefile=valuefile,
            updator=self.request_username,
            kubeconfig_content=kubeconfig,
            ignore_empty_access_token=True,
            extra_inject_source=extra_inject_source,
        )

    class Meta:
        model = App
        fields = (
            "name",
            "namespace",
            "upgrade_verion",
            "answers",
            "customs",
            "valuefile",
            "project_id",
            "cluster_id",
            "chart",
            "transitioning_result",
            "transitioning_message",
            "transitioning_on",
            "transitioning_action",
            "id",
        )
        read_only_fields = (
            "name",
            "namespace",
            "project_id",
            "cluster_id",
            "chart",
            "transitioning_result",
            "transitioning_message",
            "transitioning_on",
            "transitioning_action",
        )
        extra_kwargs = {
            "answers": {
                "write_only": True
            },
            "customs": {
                "write_only": True
            },
            "valuefile": {
                "write_only": True
            },
            "upgrade_verion": {
                "write_only": True
            },
        }
