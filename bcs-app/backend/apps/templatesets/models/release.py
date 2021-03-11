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
from jsonfield import JSONField

from backend.apps.configuration import models as config_models
from backend.utils.models import BaseModel, BaseTSModel


@dataclass
class ResourceManifest:
    kind: str
    name: str
    namespace: str
    body: str


class AppRelease(BaseModel):
    name = models.CharField(max_length=128)
    cluster_id = models.CharField(max_length=32)
    namespace = models.CharField(max_length=64)
    # 关联模板集
    template_id = models.IntegerField("关联model Template")
    rel_revision = models.CharField("release的修订版号", max_length=32)
    rel_revision_history = JSONField(default=[])

    class Meta:
        db_table = 'templatesets_app_release'
        unique_together = ('name', 'cluster_id', 'namespace')

    def save(self, *args, **kwargs):
        self.rel_revision_history.append(self.rel_revision)
        return super().save(*args, **kwargs)

    @property
    def template(self):
        return config_models.Template.objects.get(id=self.template_id)

    def deploy(self, version: str, revision: str, manifest_list: List[ResourceManifest]):
        for manifest in manifest_list:
            try:
                ResourceInstance.objects.create(
                    app_release=self,
                    rel_revision=self.rel_revision,
                    kind=manifest.kind,
                    version=version,
                    revision=revision,
                    manifest=manifest.body,
                )
            except Exception:
                pass

    def update(self):
        pass

    def delete(self, *args, **kwargs):
        pass


# class ReleaseRevision(BaseModel):
#     app_release = models.ForeignKey(AppRelease, on_delete=models.CASCADE, null=False)
#     version_suffix = models.CharField("区分小版本的后缀", max_length=32)


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

    class Meta:
        db_table = 'templatesets_resource_instance'

    @classmethod
    def deploy(cls):
        # TODO 利用dynamic client部署到集群中
        pass

    def copy(self, rel_revision):
        return ResourceInstance.objects.create()
