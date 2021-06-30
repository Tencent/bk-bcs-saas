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

from ..tools import mesos_instance
from .serializers import MesosInstSLZ


class MesosInstanceViewSets(SystemViewSet):
    def scale_resource(self, request, project_id, cluster_id, namespace, name):
        """mesos 实例的资源原地扩缩容"""
        params = self.params_validate(MesosInstSLZ)
        inst_data = mesos_instance.InstanceData(
            kind=params["kind"],
            namespace=namespace,
            name=name,
            manifest=params["manifest"],
            variables=params["variables"],
        )
        mesos_instance.scale_instance_resource(
            request.user.username, inst_data, request.ctx_cluster, params.get("show_version")
        )
        return Response()
