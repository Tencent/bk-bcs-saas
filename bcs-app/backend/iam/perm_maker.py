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
from .permissions.perm import PermCtx, Permission

ResourceType = resources.ResourceType

ResourcePermMap = {
    ResourceType.Project: resources.ProjectPermission,
    ResourceType.Cluster: resources.ClusterPermission,
    ResourceType.Namespace: resources.NamespacePermission,
    ResourceType.Templateset: resources.TemplatesetPermission,
}


def make_perm_ctx(username: str, res_type: str, **ctx_kwargs) -> PermCtx:

    if res_type == ResourceType.Project:
        return resources.ProjectPermCtx(username=username, project_id=ctx_kwargs.get('project_id'))

    if res_type == ResourceType.Cluster:
        return resources.ClusterPermCtx(
            username=username, project_id=ctx_kwargs['project_id'], cluster_id=ctx_kwargs.get('cluster_id')
        )

    if res_type == ResourceType.Namespace:
        return resources.NamespacePermCtx(
            username=username,
            project_id=ctx_kwargs['project_id'],
            cluster_id=ctx_kwargs['cluster_id'],
            name=ctx_kwargs.get('name'),
        )

    if res_type == ResourceType.Templateset:
        return resources.TemplatesetPermCtx(
            username=username, project_id=ctx_kwargs['project_id'], template_id=ctx_kwargs.get('template_id')
        )

    raise ValueError(f'resource {res_type} has no perm ctx')


def make_res_permission(res_type: str) -> Permission:
    """"""
    return ResourcePermMap[res_type]()
