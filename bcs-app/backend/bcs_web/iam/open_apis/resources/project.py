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
try:
    from iam.resource.provider import ListResult, ResourceProvider
except Exception:
    pass
from backend.components import ssm
from backend.container_service.projects.base import filter_projects


class ProjectProvider(ResourceProvider):
    def list_attr(self, **options):
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter, page, **options):
        return ListResult(results=[], count=0)

    def list_instance(self, filter, page, **options):
        access_token = ssm.get_client_access_token()["access_token"]
        projects = filter_projects(access_token)
        count = len(projects)
        projects = projects[page.slice_from : page.slice_to]  # noqa
        results = [{"id": p["project_id"], "display_name": p["project_name"]} for p in projects]
        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter, **options):
        access_token = ssm.get_client_access_token()["access_token"]
        query_params = None
        if filter.ids:
            query_params = {"project_ids": ",".join(filter.ids)}
        projects = filter_projects(access_token, query_params)
        results = [{"id": p["project_id"], "display_name": p["project_name"]} for p in projects]
        return ListResult(results=results, count=len(results))

    def list_instance_by_policy(self, filter, page, **options):
        # TODO 确认基于实例的查询是不是就是id的过滤查询
        return ListResult(results=[], count=0)
