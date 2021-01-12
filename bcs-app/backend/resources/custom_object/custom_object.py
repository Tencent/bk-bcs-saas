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
from kubernetes import client

from backend.utils.error_codes import error_codes

from ..client import APIInstance
from ..mixins import CustomObjectsAPIClassMixins
from .constants import gamestatefulset_name, gamedeployment_name
from .crd import CustomResourceDefinition
from .custom_objects_api import CustomObjectsApi


def use_json_patch(crd_name):
    if crd_name in [gamestatefulset_name, gamedeployment_name]:
        return True
    return False


# class CustomObject1:
#     def __init__(self, access_token: str, project_id: str, cluster_id: str, crd_name: str):
#         crd_api =


class CustomObject(CustomObjectsAPIClassMixins, APIInstance):
    def __init__(self, access_token, project_id, cluster_id, crd_name):
        crd_client = CustomResourceDefinition(access_token, project_id, cluster_id)
        crd = crd_client.get_custom_resource_definition(crd_name)
        self.crd_name = crd_name
        self.api_group = crd.spec.group
        self.api_version = crd.spec.version
        self.scope = crd.spec.scope
        self.api_plural = crd.spec.names.plural

        super().__init__(access_token, project_id, cluster_id)

        if use_json_patch(self.crd_name):
            self.api_instance = CustomObjectsApi(self.api_client)

    def list_namespaced_custom_object(self, namespace):
        return self.api_instance.list_namespaced_custom_object(
            self.api_group, self.api_version, namespace, self.api_plural
        )

    def list_cluster_custom_object(self):
        return self.api_instance.list_cluster_custom_object(self.api_group, self.api_version, self.api_plural)

    def get_cluster_custom_object(self, name):
        return self.api_instance.get_cluster_custom_object(self.api_group, self.api_version, self.api_plural, name)

    def get_namespaced_custom_object(self, namespace, name):
        return self.api_instance.get_namespaced_custom_object(
            self.api_group, self.api_version, namespace, self.api_plural, name
        )

    def patch_cluster_custom_object(self, name, body):
        try:
            return self.api_instance.patch_cluster_custom_object(
                self.api_group, self.api_version, self.api_plural, name, body
            )
        except Exception as e:
            raise error_codes.APIError(f"patch_cluster_custom_object error: {e}")

    def patch_namespaced_custom_object(self, namespace, name, body):
        try:
            return self.api_instance.patch_namespaced_custom_object(
                self.api_group, self.api_version, namespace, self.api_plural, name, body
            )
        except Exception as e:
            raise error_codes.APIError(f"patch_namespaced_custom_object error: {e}")

    def patch_namespaced_custom_object_scale(self, namespace, name, body):
        try:
            return self.api_instance.patch_namespaced_custom_object_scale(
                self.api_group, self.api_version, namespace, self.api_plural, name, body
            )
        except Exception as e:
            raise error_codes.APIError(f"patch_namespaced_custom_object_scale error: {e}")

    def delete_cluster_custom_object(self, name):
        try:
            return self.api_instance.delete_cluster_custom_object(
                self.api_group, self.api_version, self.api_plural, name, body=client.V1DeleteOptions()
            )
        except Exception as e:
            raise error_codes.APIError(f"delete_cluster_custom_object error: {e}")

    def delete_namespaced_custom_object(self, namespace, name):
        try:
            return self.api_instance.delete_namespaced_custom_object(
                self.api_group, self.api_version, namespace, self.api_plural, name, body=client.V1DeleteOptions()
            )
        except Exception as e:
            raise error_codes.APIError(f"delete_namespaced_custom_object error: {e}")
