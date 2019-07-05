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
from django.db import models


class RepositoryManager(models.Manager):
    pass


class ChartManager(models.Manager):
    pass


class ChartVersionManager(models.Manager):
    pass


class RepositoryAuthManager(models.Manager):
    pass


class ChartVersionSnapshotManager(models.Manager):
    def make_snapshot(self, chart_version):
        snapshot, created = self.get_or_create(
            digest=chart_version.digest,
            defaults={
                "name": chart_version.name,
                "home": chart_version,
                "description": chart_version.description,
                "engine": chart_version.engine,
                "maintainers": chart_version.maintainers,
                "sources": chart_version.sources,
                "urls": chart_version.urls,
                "files": chart_version.files,
                "questions": chart_version.questions,
                "version": chart_version.version,
                "digest": chart_version.digest,
                "created": chart_version.created,
                "version_id": chart_version.id
            })
        return snapshot
