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
from functools import lru_cache
import os

from kubernetes import client

from backend.resources.utils.discovery import BcsLazyDiscoverer, DiscovererCache
from backend.resources.utils.kube_client import CoreDynamicClient


class LocalKubeConfigurationService:
    """指向本地集群的配置生成逻辑"""

    def __init__(self):
        self.api_key = os.environ.get('TESTING_SERVER_API_KEY')
        self.host = os.environ.get('TESTING_API_SERVER_URL')

    def make_configuration(self):
        configuration = client.Configuration()
        configuration.api_key = {'authorization': f"Bearer {self.api_key}"}
        configuration.verify_ssl = False
        configuration.host = self.host
        return configuration


@lru_cache(maxsize=128)
def get_dynamic_client(*args, **kwargs) -> CoreDynamicClient:
    """根据 token、cluster_id 等参数，构建访问 Kubernetes 集群的 Client 对象"""
    config = LocalKubeConfigurationService().make_configuration()
    discoverer_cache = DiscovererCache(cache_key=f"osrcp-cluster_id.json")
    return CoreDynamicClient(client.ApiClient(config), cache_file=discoverer_cache, discoverer=BcsLazyDiscoverer)