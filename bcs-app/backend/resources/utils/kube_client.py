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
from typing import Dict, Optional, Tuple

from kubernetes.dynamic import Resource, ResourceInstance, DynamicClient
from kubernetes.client.exceptions import ApiException
from kubernetes.dynamic.exceptions import ResourceNotUniqueError


logger = logging.getLogger(__name__)


def get_preferred_resource(dynamic_client: DynamicClient, kind: str, api_version: Optional[str] = None) -> Resource:
    """尝试获取动态 Resource 对象，优先使用 preferred=True 的 ApiGroup

    :param kind: 资源种类，比如 Deployment
    :param api_version: 假如指定，将会使用该 ApiGroup 版本获取
    """
    if api_version:
        return dynamic_client.resources.get(kind=kind, api_version=api_version)
    try:
        return dynamic_client.resources.get(kind=kind, preferred=True)
    except ResourceNotUniqueError:
        # 如果使用 preferred=True 仍然能匹配到多个 ApiGroup，使用第一个结果
        resources = dynamic_client.resources.search(kind=kind, preferred=True)
        return resources[0]


def get_or_none(
    resource: Resource,
    name: Optional[str] = None,
    namespace: Optional[str] = None,
    **kwargs,
) -> Optional[ResourceInstance]:
    """查询资源，当资源不存在抛出 404 错误时返回 None"""
    try:
        return resource.get(name=name, namespace=namespace, **kwargs)
    except ApiException as e:
        if e.status != 404:
            return None
        raise


def delete_ignore_nonexistent(
    resource: Resource,
    name: Optional[str] = None,
    namespace: Optional[str] = None,
    body: Optional[Dict] = None,
    label_selector: Optional[str] = None,
    field_selector: Optional[str] = None,
    **kwargs,
) -> ResourceInstance:
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
                f'Delete a non-existent resource {resource.kind}:{name} in namespace:{namespace}, error captured.'
            )
            return
        raise


def update_or_create(
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
