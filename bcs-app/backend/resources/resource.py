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
import time
from typing import Dict, List, Optional, Tuple, Union

from kubernetes.dynamic.resource import ResourceInstance

from backend.resources.cluster.models import CtxCluster
from backend.resources.utils.kube_client import get_dynamic_client

from .constants import PatchType
from .utils.format import ResourceDefaultFormatter

logger = logging.getLogger(__name__)


class ResourceClient:
    """
    资源基类
    """

    kind = "Resource"
    formatter = ResourceDefaultFormatter()

    def __init__(self, ctx_cluster: CtxCluster, api_version: Optional[str] = None):
        self.dynamic_client = get_dynamic_client(
            ctx_cluster.context.auth.access_token, ctx_cluster.project_id, ctx_cluster.id
        )
        if api_version:
            self.api = self.dynamic_client.resources.get(kind=self.kind, api_version=api_version)
        else:
            self.api = self.dynamic_client.get_preferred_resource(self.kind)

    def list(
        self, is_format: bool = True, formatter: Optional[ResourceDefaultFormatter] = None, **kwargs
    ) -> Union[ResourceInstance, List, None]:
        resp = self.api.get_or_none(**kwargs)

        if not is_format:
            return resp
        if formatter:
            return formatter.format_list(resp)
        return self.formatter.format_list(resp)

    def get(
        self, name, is_format: bool = True, formatter: Optional[ResourceDefaultFormatter] = None, **kwargs
    ) -> Union[ResourceInstance, Dict, None]:
        resp = self.api.get_or_none(name=name, **kwargs)

        if not is_format:
            return resp
        if formatter:
            return formatter.format(resp)
        return self.formatter.format(resp)

    def create(
        self,
        body: Optional[Dict] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        is_format: bool = True,
        **kwargs,
    ) -> Union[ResourceInstance, Dict]:
        obj = self.api.create(body=body, name=name, namespace=namespace, update_method="replace", **kwargs)
        if is_format:
            return self.formatter.format(obj)
        return obj

    def update_or_create(
        self,
        body: Optional[Dict] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        is_format: bool = True,
        **kwargs,
    ) -> Tuple[Union[ResourceInstance, Dict], bool]:
        obj, created = self.api.update_or_create(
            body=body, name=name, namespace=namespace, update_method="replace", **kwargs
        )
        if is_format:
            return self.formatter.format(obj), created
        return obj, created

    def patch(
        self,
        body: Optional[Dict] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        is_format: bool = True,
        **kwargs,
    ) -> Union[ResourceInstance, Dict]:
        # 参考kubernetes/client/rest.py中RESTClientObject类的request方法中对PATCH的处理
        # 如果指定的是json-patch+json但body不是list，则设置为strategic-merge-patch+json
        if kwargs.get("content_type") == PatchType.JSON_PATCH_JSON.value:
            if not isinstance(body, list):
                kwargs["content_type"] = PatchType.STRATEGIC_MERGE_PATCH_JSON.value

        obj, _ = self.api.update_or_create(body=body, name=name, namespace=namespace, update_method="patch", **kwargs)
        if is_format:
            return self.formatter.format(obj)
        return obj

    def delete_ignore_nonexistent(
        self,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        body: Optional[Dict] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        **kwargs,
    ) -> Optional[ResourceInstance]:
        """删除某个资源，当目标不存在时忽略错误"""
        return self.api.delete_ignore_nonexistent(name, namespace, body, label_selector, field_selector, **kwargs)

    def delete_wait_finished(
        self,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        body: Optional[Dict] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        max_wait_seconds: int = 10,
        **kwargs,
    ) -> Optional[ResourceInstance]:
        """删除某个资源，一直轮询等到删除成功后返回，默认忽略资源不存在的情况

        :param max_wait_seconds: 最长等待时间，默认为 10 秒
        :raises: 当超过最长等待时间，资源仍然没有删掉时抛出 RuntimeError
        """
        ret = self.api.delete_ignore_nonexistent(name, namespace, body, label_selector, field_selector, **kwargs)

        # 开始轮询检查资源删除情况，默认每 0.1 秒检查一次
        check_interval = 0.1
        start_time = time.time()
        while True:
            if time.time() - start_time >= max_wait_seconds:
                raise RuntimeError('Max wait seconds exceeded, resource(s) still existed after deletion')

            items = self.list(
                name=name,
                namespace=namespace,
                label_selector=label_selector,
                field_selector=field_selector,
                is_format=False,
            )
            if not items:
                return ret

            logger.debug(f'Resource(s) still exists, starting next check in {check_interval}')
            time.sleep(check_interval)

    def delete(
        self,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        body: Optional[Dict] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        **kwargs,
    ) -> Optional[ResourceInstance]:
        """删除某个资源"""
        return self.api.delete(name, namespace, body, label_selector, field_selector, **kwargs)
