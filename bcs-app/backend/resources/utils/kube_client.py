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
import json
import logging
from typing import Dict, Optional, Tuple

from kubernetes.dynamic import Resource, ResourceInstance
from kubernetes.client.exceptions import ApiException


logger = logging.getLogger(__name__)


def delete_ignore_nonexistent(resource: Resource, *args, **kwargs) -> ResourceInstance:
    """删除资源，但是当资源不存在时忽略错误"""
    try:
        return resource.delete(*args, **kwargs)
    except ApiException as e:
        if e.status == 404:
            logger.info(f'Delete a non-existent resource {resource.kind}, error captured.')
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
        update_method = getattr(resource, update_method)
        obj = update_method(body=body, name=name, namespace=namespace, **kwargs)
        return obj, False
    except ApiException as e:
        # Only continue when resource is not found
        if e.status != 404:
            raise

    logger.info(f"Updating {resource.kind}:{name} failed, resource not exists, continue creating")
    obj = resource.create(body=body, namespace=namespace, **kwargs)
    return obj, True