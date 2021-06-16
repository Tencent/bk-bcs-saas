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
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet

from . import constants, serializers
from .utils import helm2_release
from .utils import release as release_utils
from .utils.parser import ReleaseParser


class HelmReleaseViewSet(SystemViewSet):
    def get_notes(self, request, project_id, cluster_id, namespace, release_name):
        """查询release下的notes"""
        return Response({"notes": release_utils.get_release_notes(request.ctx_cluster, namespace, release_name)})

    def list_releases(self, request, project_id, cluster_id):
        """查询集群或者命名空间下的 release 列表
        NOTE: 仅允许查询单个集群下的releases
        """
        params = self.params_validate(serializers.ListReleasesParamsSLZ)
        namespace = params.get("namespace")
        # 获取 release 列表，支持 helm2(kubectl) 部署的Release
        # 通过helm2(kubectl)部署的Release，则需要查询平台DB中的记录
        if params.get("engine") == constants.ReleaseEngine.Helm2.value:
            return helm2_release.list_releases(request.ctx_cluster, namespace=namespace)
        return Response(release_utils.list_releases(request.ctx_cluster, namespace=namespace))

    def release_info(self, request, project_id, cluster_id, namespace, release_name):
        """查询 release 详情
        包含:
        - release的基本信息
        - release的values
        - release使用的chart的基本信息
        """
        release = release_utils.get_release_detail(request.ctx_cluster, namespace, release_name)
        parser = ReleaseParser(release)
        data = parser.metadata
        data.update({"chart_metadata": parser.chart_metadata, "values": parser.values})

        return Response(data)
