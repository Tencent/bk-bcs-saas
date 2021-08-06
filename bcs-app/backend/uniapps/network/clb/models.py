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
import logging

from django.db import models

from backend.utils.error_codes import error_codes
from backend.utils.models import BaseModel

logger = logging.getLogger(__name__)


class Manager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def filter_by_project(self, project_id):
        return self.filter(project_id=project_id)

    def parse_record(self, record):
        config = record.config_value
        return {
            'id': record.id,
            'project_id': record.project_id,
            'cluster_id': record.cluster_id,
            'namespace': record.namespace,
            'clb_name': record.clb_name,
            'resource_name': record.resource_name,
            'region': record.region,
            'image': record.image,
            'status': record.status,
            'vpc_id': record.vpc_id,
            **config,
        }

    def get_clb_list(self, project_id, cluster_id=None):
        queryset = self.filter(project_id=project_id)
        if cluster_id:
            queryset = queryset.filter(cluster_id=cluster_id)
        data = []
        for record in queryset:
            data.append(self.parse_record(record))
        return data

    def retrieve(self, id):
        queryset = self.filter(id=id)
        if not queryset:
            raise error_codes.ResNotFoundError()
        return queryset[0]

    def retrieve_record(self, id):
        queryset = self.filter(id=id)
        if not queryset:
            raise error_codes.ResNotFoundError()
        return self.parse_record(queryset[0])

    def create(self, data):
        data['config'] = json.dumps(
            {
                'network_type': data.pop('network_type'),
                'clb_type': data.pop('clb_type'),
                'svc_discovery_type': data.pop('svc_discovery_type'),
                'clb_project_id': data.pop('clb_project_id'),
                'metric_port': data.pop('metric_port'),
                'implement_type': data.pop('implement_type'),
                'backend_type': data.pop('backend_type'),
            }
        )
        return super().create(**data)

    def update(self, id, data):
        queryset = self.filter(id=id)
        if not queryset:
            raise error_codes.ResNotFoundError()
        # 不允许变动的信息
        for key in ['cluster_id', 'region', 'clb_name', 'vpc_id']:
            data.pop(key, '')

        data['config'] = json.dumps(
            {
                'network_type': data.pop('network_type'),
                'clb_type': data.pop('clb_type'),
                'svc_discovery_type': data.pop('svc_discovery_type'),
                'clb_project_id': data.pop('clb_project_id'),
                'metric_port': data.pop('metric_port'),
                'implement_type': data.pop('implement_type'),
                'backend_type': data.pop('backend_type'),
            }
        )
        return queryset.update(**data)


class CloudLoadBlancer(BaseModel):
    clb_name = models.CharField(max_length=253)
    resource_name = models.CharField(max_length=253)
    project_id = models.CharField(max_length=32)
    cluster_id = models.CharField(max_length=32)
    namespace = models.CharField(max_length=253, default='bcs-system')
    region = models.CharField(max_length=32)
    image = models.CharField(max_length=512)
    config = models.TextField()
    vpc_id = models.CharField(max_length=32)
    status = models.CharField(max_length=32, default='not_created')

    objects = Manager()
    default_objects = models.Manager()

    @property
    def config_value(self):
        try:
            return json.loads(self.config)
        except Exception:
            return {}

    class Meta:
        db_table = 'cloud_load_blancer'
        unique_together = ('clb_name', 'cluster_id', 'namespace')
