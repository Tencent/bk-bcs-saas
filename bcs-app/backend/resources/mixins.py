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


class APIExtensionsAPIClassMixins:
    """
    支持资源类型: Ingress
    """

    def get_api_cls_list(self, api_client):
        resp = client.ApiextensionsApi(api_client).get_api_group()
        # 假定preferred_version.group_version在第一个
        group_versions = [v.group_version for v in resp.versions]

        api_cls_list = []
        for group_version in group_versions:
            group, version = group_version.split("/")
            api_cls_list.append(f"{group.split('.')[0].capitalize()}{version.capitalize()}Api")
        return api_cls_list


class CustomObjectsAPIClassMixins:
    def get_api_cls_list(self, api_client):
        return ["CustomObjectsApi"]


class CoreAPIClassMixins:
    """
    支持资源类型: ConfigMap/Endpoints/Event/Namespace/Node/Pod/PersistentVolume/secret等
    """
    def get_api_cls_list(self, api_client):
        versions = client.CoreApi(api_client).get_api_versions()
        return [f"Core{ver.capitalize()}Api" for ver in versions.versions]
