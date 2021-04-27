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
from backend.dashboard.subscribe.constants import DEFAULT_SUBSCRIBE_TIMEOUT, KIND_RESOURCE_CLIENT_MAP
from backend.dashboard.subscribe.serializers import FetchResourceWatchResultSLZ
from backend.utils.basic import getitems


class SubscribeViewSet(SystemViewSet):

    def list(self, request, project_id, cluster_id):
        """获取指定资源某resource_version后变更记录"""
        slz = FetchResourceWatchResultSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        resource_client = KIND_RESOURCE_CLIENT_MAP[params['kind']](request.ctx_cluster)
        events = resource_client.watch(
            resource_version=params['resource_version'], timeout=DEFAULT_SUBSCRIBE_TIMEOUT
        )
        # events 默认按时间排序，取最后一个 ResourceVersion 即为最新值
        max_rv = getitems(events[-1], 'manifest.metadata.resourceVersion') if events else None

        response_data = {'events': events, 'max_rv': max_rv}
        return Response(response_data)
