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
from dataclasses import dataclass
from typing import List

from django.db import models
from django.utils import timezone
from jsonfield import JSONField

from backend.apps.configuration import models as config_models
from backend.utils.models import BaseModel, BaseTSModel


def gen_time_revision() -> str:
    return timezone.localtime().strftime('%Y%m%d%H%M%S')


@dataclass
class ResourceManifest:
    kind: str
    name: str
    namespace: str
    body: str


@dataclass
class AppReleaseData:
    name: str
    cluster_id: str
    namespace: str
    show_version: config_models.ShowVersion
    manifest_list: List[ResourceManifest]


class AppRelease(BaseModel):
    name = models.CharField(max_length=128)
    cluster_id = models.CharField(max_length=32)
    namespace = models.CharField(max_length=64)
    status = models.CharField()
    message = models.TextField()
    template_id = models.IntegerField("关联model Template")
    revision = models.CharField("release的修订版号", max_length=32)
    revision_history = JSONField(default=[])

    class Meta:
        db_table = 'templatesets_app_release'
        unique_together = ('name', 'cluster_id', 'namespace')

    def save(self, *args, **kwargs):
        self.revision_history.append(self.revision)
        return super().save(*args, **kwargs)

    @property
    def template(self):
        return config_models.Template.objects.get(id=self.template_id)

    @classmethod
    def create(cls, release_data: AppReleaseData):
        show_version = release_data.show_version
        app_release = cls(
            name=release_data.name,
            cluster_id=release_data.cluster_id,
            namespace=release_data.namespace,
            template_id=show_version.template_id,
            rel_revision=gen_time_revision(),
        )

    # def deploy(self, version: str, revision: str, manifest_list: List[ResourceManifest]):
    #     for manifest in manifest_list:
    #         try:
    #             ResourceInstance.objects.create(
    #                 app_release=self,
    #                 rel_revision=self.rel_revision,
    #                 kind=manifest.kind,
    #                 version=version,
    #                 revision=revision,
    #                 manifest=manifest.body,
    #             )
    #         except Exception:
    #             pass

    def update(self):
        pass

    def delete(self, *args, **kwargs):
        pass


class ResourceInstance(BaseTSModel):
    app_release = models.ForeignKey(AppRelease, on_delete=models.CASCADE, null=False)
    rel_revision = models.CharField("release的修订版号", max_length=32)
    kind = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    namespace = models.CharField(max_length=64)
    manifest = models.TextField()
    version = models.CharField("模板集版本名", max_length=255)
    revision = models.CharField("模板集版本名的修订版号", max_length=32)
    is_edited = models.BooleanField("是否在线编辑过", default=False)
    status = models.CharField()

    class Meta:
        db_table = 'templatesets_resource_instance'

    @classmethod
    def create(cls):
        # TODO 利用dynamic client部署到集群中
        pass

    @classmethod
    def copy(cls, rel_revision):
        return ResourceInstance.objects.create()
