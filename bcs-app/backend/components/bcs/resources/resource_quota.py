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

from kubernetes.client.rest import ApiException

from backend.utils.error_codes import error_codes

from .resource import Resource, CoreAPIClassMixins

logger = logging.getLogger(__name__)


class ResourceQuota(Resource, CoreAPIClassMixins):

    def list_namespaced_resource_quota(self, namespace):
        return self.api_instance.list_namespaced_resource_quota(namespace)

    def list_all_resource_quota(self):
        return self.api_instance.list_resource_quota_for_all_namespaces()

    def list_resource_quota(self, namespace=None):
        if namespace:
            return self.list_namespaced_resource_quota(namespace).items
        return self.list_all_resource_quota().items

    def create_resource_quota(self, namespace, body):
        try:
            return self.api_instance.create_namespaced_resource_quota(namespace, body)
        except ApiException as e:
            logger.error("create resource quota error, %s", e)
            if e.status == 409:
                return
            raise

    def delete_resource_quota(self, name, namespace):
        return self.api_instance.delete_namespaced_resource_quota(name, namespace)

    def update_resource_quota(self, name, namespace, body):
        return self.api_instance.replace_namespaced_resource_quota(name, namespace, body)

    def update_or_create(self, name, namespace, body):
        try:
            return self.update_resource_quota(name, namespace, body)
        except ApiException as e:
            logger.error("update resource quota error, %s", e)
            if e.status == 404:
                return self.create_resource_quota(namespace, body)
            raise
        except Exception as e:
            logger.error("request k8s resource quota api error, %s", e)
            raise error_codes.APIError(f"request k8s resource quota api error, {e}")
