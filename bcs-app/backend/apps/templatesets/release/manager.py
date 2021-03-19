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
from typing import List, Tuple

from backend.utils.async_run import async_run

from .. import models


class ReleaseManager:
    def __init__(self, dynamic_client):
        self.dynamic_client = dynamic_client

    def update_or_create(self, operator: str, release_data: models.AppReleaseData) -> Tuple[models.AppRelease, bool]:
        app_release, created = models.AppRelease.objects.update_or_create(
            name=release_data.name,
            cluster_id=release_data.cluster_id,
            namespace=release_data.namespace,
            defaults={"template_id": release_data.template_id, "creator": operator, "updator": operator},
        )

        try:
            self._deploy(operator, app_release.id, release_data.resource_list)
        except Exception as e:
            app_release.update_status(models.ReleaseStatus.FAILED.value, str(e))
        else:
            app_release.update_status(models.ReleaseStatus.DEPLOYED.value)

        return app_release, created

    def _deploy(self, operator: str, app_release_id: int, resource_list: List[models.ResourceData]):
        res_mgr = ResourceManager(self.dynamic_client, app_release_id)
        tasks = [functools.partial(res_mgr.update_or_create, operator, resource) for resource in resource_list]
        async_run(tasks)

    def delete(self, operator: str, app_release_id: int):
        self._delete(operator, app_release_id)
        models.AppRelease.objects.filter(id=app_release_id).delete()

    def _delete(self, operator: str, app_release_id: int):
        res_mgr = ResourceManager(self.dynamic_client, app_release_id)
        tasks = [
            functools.partial(res_mgr.delete, operator, resource_inst.id)
            for resource_inst in models.ResourceInstance.objects.filter(app_release_id=app_release_id)
        ]
        async_run(tasks)


class ResourceManager:
    def __init__(self, dynamic_client, app_release_id: int):
        self.dynamic_client = dynamic_client
        self.app_release_id = app_release_id

    def update_or_create(self, operator: str, resource: models.ResourceData) -> Tuple[models.ResourceInstance, bool]:
        try:
            self.dynamic_client.update_or_create(resource.manifest)
        except Exception:
            raise

        return models.ResourceInstance.objects.update_or_create(
            app_release_id=self.app_release_id,
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

    def edit(self, operator: str, resource: models.ResourceData):
        """
        直接edit线上资源(类似kubectl edit)，不做manifest和version等信息的保存
        """
        try:
            self.dynamic_client.update_or_create(resource.manifest)
        except Exception:
            raise

        models.ResourceInstance.objects.filter(
            app_release_id=self.app_release_id, name=resource.name, namespace=resource.namespace, kind=resource.kind
        ).update(edited=True, updator=operator)

    def delete(self, operator: str, resource_inst_id: int):
        resource_inst = models.ResourceInstance.objects.get(id=resource_inst_id)
        self.dynamic_client.delete(resource_inst.name, resource_inst.namespace, resource_inst.kind)
        return resource_inst.delete()
