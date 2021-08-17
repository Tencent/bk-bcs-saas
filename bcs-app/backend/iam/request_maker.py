# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from .permissions import resources
from .permissions.request import ResourceRequest

ResourceType = resources.ResourceType

ResourceRequestMap = {
    ResourceType.Project: resources.ProjectRequest,
    ResourceType.Cluster: resources.ClusterRequest,
    ResourceType.Namespace: resources.NamespaceRequest,
    ResourceType.Templateset: resources.TemplatesetRequest,
}


def make_res_request(res_type: str, res_id: str, **attr_kwargs) -> ResourceRequest:
    return ResourceRequestMap[res_type](res_id, **attr_kwargs)
