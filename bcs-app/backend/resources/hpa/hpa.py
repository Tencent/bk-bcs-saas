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
from typing import Optional

from ..resource import ResourceClient
from ..utils.auths import ClusterAuth
from .format import HPAFormatter


class HPA(ResourceClient):
    preferred_api_version = "autoscaling/v2beta2"
    kind = "HorizontalPodAutoscaler"

    def __init__(self, cluster_auth: ClusterAuth, project_code: str, cluster_name: str, cluster_env: str):
        super().__init__(cluster_auth, self.preferred_api_version)

        self.formatter = HPAFormatter(cluster_auth.cluster_id, project_code, cluster_name, cluster_env)
