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
import functools
from dataclasses import dataclass
from typing import List, Tuple

from django.db import models

from backend.apps.configuration import models as config_models
from backend.utils.async_run import async_run
from backend.utils.models import BaseModel

from ..constants import ReleaseStatus


def mock_dynamic_request(manifest):
    return manifest


@dataclass
class ResourceData:
    kind: str
    name: str
    namespace: str
    manifest: str
    version: str = ""
    revision: str = ""


@dataclass
class AppReleaseData:
    name: str
    cluster_id: str
    namespace: str
    template_id: str
    resource_list: List[ResourceData]


class AppRelease(BaseModel):
    name = models.CharField(max_length=128)
    cluster_id = models.CharField(max_length=32)
    namespace = models.CharField(max_length=64)
    status = models.CharField(choices=ReleaseStatus.get_choices(), default=ReleaseStatus.PENDING.value, max_length=32)
    message = models.TextField(default='')
    template_id = models.IntegerField("关联model Template")

    class Meta:
        db_table = 'templatesets_app_release'
        unique_together = ('name', 'cluster_id', 'namespace')

    @property
    def template(self):
        return config_models.Template.objects.get(id=self.template_id)

    @classmethod
    def create(cls, operator: str, release_data: AppReleaseData) -> 'AppRelease':
        app_release = cls(
            name=release_data.name,
            cluster_id=release_data.cluster_id,
            namespace=release_data.namespace,
            template_id=release_data.template_id,
            creator=operator,
            updator=operator,
        )

        try:
            app_release.deploy(operator, release_data.resource_list)
        except Exception as e:
            app_release._update_status(ReleaseStatus.FAILED.value, str(e))
        else:
            app_release._update_status(ReleaseStatus.DEPLOYED.value)

        app_release.save()
        return app_release

    def deploy(self, operator: str, resource_list: List[ResourceData]):
        async_run([functools.partial(self._deploy, operator, resource) for resource in resource_list])

    def _deploy(self, operator: str, resource: ResourceData):
        ResourceInstance.update_or_create(operator, self.id, resource)

    def _update_status(self, status: str, message: str = 'success'):
        """
        not touch db
        """
        self.status = status
        self.message = message

    def update(self, operator: str, release_data: AppReleaseData):
        try:
            self.deploy(operator, release_data.resource_list)
        except Exception as e:
            self._update_status(ReleaseStatus.FAILED.value, str(e))
        else:
            self._update_status(ReleaseStatus.DEPLOYED.value)

        self.save()

    def do_delete(self, operator: str):
        return self.delete()

    def delete(self, *args, **kwargs):
        self.resourceinstance_set.delete()
        return super().delete()


class ResourceInstance(BaseModel):
    app_release = models.ForeignKey(AppRelease, on_delete=models.CASCADE, null=False)
    kind = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    namespace = models.CharField(max_length=64)
    manifest = models.TextField()
    version = models.CharField("模板集版本名", max_length=255)
    revision = models.CharField("模板集版本名的修订版号", max_length=32)
    edited = models.BooleanField("是否在线编辑过", default=False)

    class Meta:
        db_table = 'templatesets_resource_instance'
        unique_together = ('app_release', 'kind', 'name', 'namespace')

    @classmethod
    def update_or_create(
        cls, operator: str, app_release_id: int, resource: ResourceData
    ) -> Tuple['ResourceInstance', bool]:
        """
        用于通过模板集版本进行更新
        """
        try:
            mock_dynamic_request(resource.manifest)
        except Exception:
            raise

        return cls.objects.update_or_create(
            app_release_id=app_release_id,
            kind=resource.kind,
            name=resource.name,
            namespace=resource.namespace,
            defaults={
                'manifest': resource.manifest,
                'version': resource.version,
                'revision': resource.revision,
                'updator': operator,
                'creator': operator,
            },
        )

    def edit(self, operator: str, resource: ResourceData):
        """
        直接edit线上资源(类似kubectl edit)，不做manifest和version等信息的保存
        """
        try:
            mock_dynamic_request(resource.manifest)
        except Exception:
            raise

        self.edited = True
        self.updator = operator
        self.save()

    def do_delete(self, operator: str):
        return self.delete()

    def delete(self, *args, **kwargs):
        try:
            mock_dynamic_request({"name": self.name, "namespace": self.namespace, "kind": self.kind})
        except Exception:
            raise

        return super().delete()
