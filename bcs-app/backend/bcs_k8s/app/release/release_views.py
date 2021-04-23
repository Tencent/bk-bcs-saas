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
from bcs_web.viewsets import SystemViewSet

from .serializers import ReleaseListParamsSLZ


class ReleasesViewSet(SystemViewSet):
    """Release 相关 API"""

    def list(self, request, project_id):
        """查询 release 列表
        需要支持多集群
        """
        slz = ReleaseListParamsSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # 获取列表
