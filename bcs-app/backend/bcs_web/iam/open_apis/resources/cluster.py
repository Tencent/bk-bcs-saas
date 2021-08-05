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
from backend.container_service.clusters.base import get_clusters
from backend.container_service.projects.base import get_project

try:
    from iam.resource.provider import ListResult, ResourceProvider
except Exception:
    pass
from backend.components import ssm
from backend.utils.error_codes import error_codes


class ClusterProvider(ResourceProvider):
    access_token = ssm.get_client_access_token()["access_token"]

    @staticmethod
    def _get_project_id(fliter_obj):
        """
        校验参数中project_id是否存在, 存在则返回，不存在抛出异常。
        Parameters
        ----------
        fliter_obj (object):

        Returns
        -------

        """
        try:
            project_id = fliter_obj.parent["id"]
        except Exception:
            raise error_codes.ParamMissError("miss parameter parent in get cluster")
        else:
            return project_id

    def list_attr(self, **options):
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter_obj, page, **options):
        return ListResult(results=[], count=0)

    def list_instance(self, filter_obj, page, **options):
        """
        必须依赖project_id。project同时也是cluster的上级资源。
        Parameters
        ----------
        filter_obj
        page
        options

        Returns
        -------

        """
        # todo 未找到不根据project_id获取cluster的接口 filter_obj.parent不存在时，无法拉取资源
        project_id = self._get_project_id(filter_obj)
        clusters = get_clusters(self.access_token, project_id)
        count = len(clusters)
        clusters = clusters[page.slice_from : page.slice_to]  # noqa
        project = get_project(self.access_token, project_id)
        results = [
            {
                "id": c["cluster_id"],
                "display_name": c["name"],
                "path": [{"type": "project", "id": str(project.project_id), "display_name": project.project_name}],
            }
            for c in clusters
        ]
        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter_obj, **options):
        project_id = self._get_project_id(filter_obj)
        clusters = get_clusters(self.access_token, project_id)
        project = get_project(self.access_token, project_id)
        if filter_obj.ids:
            results = [
                {
                    "id": c["cluster_id"],
                    "display_name": c["name"],
                    "path": [{"type": "project", "id": str(project.project_id), "display_name": project.project_name}],
                }
                for c in clusters
                if c["cluster_id"] in filter_obj.ids
            ]
        else:
            results = [
                {
                    "id": p["cluster_id"],
                    "display_name": p["name"],
                    "path": [{"type": "project", "id": str(project.project_id), "display_name": project.project_name}],
                }
                for p in clusters
            ]
        return ListResult(results=results, count=len(results))

    def list_instance_by_policy(self, filter_obj, page, **options):
        # TODO 确认基于实例的查询是不是就是id的过滤查询
        return ListResult(results=[], count=0)
