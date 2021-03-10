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
import logging
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

from kubernetes import client
from kubernetes.client.exceptions import ApiException
from kubernetes.dynamic import DynamicClient, Resource, ResourceInstance
from kubernetes.dynamic.exceptions import ResourceNotUniqueError

from ..client import BcsKubeConfigurationService
from .discovery import BcsLazyDiscoverer, DiscovererCache

logger = logging.getLogger(__name__)


class CoreDynamicClient(DynamicClient):
    """为官方 SDK 里的 DynamicClient 追加新功能：

    - 使用 sanitize_for_serialization 处理 body
    - 提供获取 preferred resource 方法
    - 包装请求失败时的 ApiException
    - 提供 get_or_none、update_or_create 等方法
    """

    def serialize_body(self, body: Any) -> Dict:
        """使用 sanitize 方法剔除 OpenAPI 对象里的 None 值"""
        body = self.client.sanitize_for_serialization(body)
        return body or {}

    def get_preferred_resource(self, kind: str) -> Resource:
        """尝试获取动态 Resource 对象，优先使用 preferred=True 的 ApiGroup

        :param kind: 资源种类，比如 Deployment
        :raises: ResourceNotUniqueError 匹配到多个不同版本资源，ResourceNotFoundError 没有找到资源
        """
        try:
            return self.resources.get(kind=kind, preferred=True)
        except ResourceNotUniqueError:
            # 如果使用 preferred=True 仍然能匹配到多个 ApiGroup，使用第一个结果
            resources = self.resources.search(kind=kind, preferred=True)
            return resources[0]

    def get_or_none(
        self, resource: Resource, name: Optional[str] = None, namespace: Optional[str] = None, **kwargs
    ) -> Optional[ResourceInstance]:
        """查询资源，当资源不存在抛出 404 错误时返回 None"""
        try:
            return self.get(resource, name=name, namespace=namespace, **kwargs)
        except ApiException as e:
            if e.status == 404:
                return None
            raise

    def delete_ignore_nonexistent(
        self,
        resource: Resource,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        body: Optional[Dict] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        **kwargs,
    ) -> Optional[ResourceInstance]:
        """删除资源，但是当资源不存在时忽略错误"""
        try:
            return resource.delete(
                name=name,
                namespace=namespace,
                body=body,
                label_selector=label_selector,
                field_selector=field_selector,
                **kwargs,
            )
        except ApiException as e:
            if e.status == 404:
                logger.info(
                    f"Delete a non-existent resource {resource.kind}:{name} in namespace:{namespace}, error captured."
                )
                return
            raise

    def update_or_create(
        self,
        resource: Resource,
        body: Optional[Dict] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        update_method: str = "replace",
        **kwargs,
    ) -> Tuple[ResourceInstance, bool]:
        """创建或修改一个 Kubernetes 资源

        :param update_method: 修改类型，默认为 replace，可选值 patch
        :returns: (instance, created)
        :raises: 当 update_method 不正确时，抛出 ValueError。调用 API 错误时，抛出 ApiException
        """
        if update_method not in ["replace", "patch"]:
            raise ValueError("Invalid update_method {}".format(update_method))

        try:
            update_func_obj = getattr(resource, update_method)
            obj = update_func_obj(body=body, name=name, namespace=namespace, **kwargs)
            return obj, False
        except ApiException as e:
            # Only continue when resource is not found
            if e.status != 404:
                raise

        logger.info(f"Updating {resource.kind}:{name} failed, resource not exists, continue creating")
        obj = resource.create(body=body, namespace=namespace, **kwargs)
        return obj, True

    def request(self, method, path, body=None, **params):
        # TODO: 包装转换请求异常
        return super().request(method, path, body=body, **params)


@lru_cache(maxsize=128)
def get_dynamic_client(access_token: str, project_id: str, cluster_id: str) -> CoreDynamicClient:
    """根据 token、cluster_id 等参数，构建访问 Kubernetes 集群的 Client 对象"""
    config = BcsKubeConfigurationService(access_token, project_id, cluster_id).make_configuration()
    # TODO 考虑集群可能升级k8s版本的情况, 缓存文件会失效
    discoverer_cache = DiscovererCache(cache_key=f"osrcp-{cluster_id}.json")
    return CoreDynamicClient(client.ApiClient(config), cache_file=discoverer_cache, discoverer=BcsLazyDiscoverer)


def make_labels_string(labels: Dict) -> str:
    """Turn a labels dict into string format

    :param labels: dict of labels
    """
    return ",".join("{}={}".format(key, value) for key, value in labels.items())
