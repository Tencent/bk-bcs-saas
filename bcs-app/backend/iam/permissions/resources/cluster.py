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
from dataclasses import dataclass
from typing import Dict, Optional

from backend.iam.permissions.perm import PermCtx, Permission, ResourceRequest
from backend.iam.permissions.resources.project import project_perm
from backend.packages.blue_krill.data_types.enum import EnumField, StructuredEnum


class ClusterAction(str, StructuredEnum):
    CREATE = EnumField('cluster_create', label='cluster_create')
    VIEW = EnumField('cluster_view', label='cluster_view')


@dataclass
class ClusterPermCtx(PermCtx):
    project_id: str
    cluster_id: Optional[str] = None


class ClusterRequest(ResourceRequest):
    """"""

    resource_type: str = 'cluster'
    attr = {'_bk_iam_path_': f'/project,{{project_id}}/'}

    def _make_attribute(self, res_id: str) -> Dict:
        self.attr['_bk_iam_path_'] = self.attr['_bk_iam_path_'].format(project_id=self.attr_kwargs['project_id'])
        return self.attr


class ClusterPermission(Permission):
    """集群权限"""

    resource_type = 'cluster'

    @project_perm(method_name='can_view')
    def can_view(self, perm_ctx: ClusterPermCtx, raise_exception: bool = True) -> bool:
        return self.can_action(perm_ctx, ClusterAction.VIEW, raise_exception)

    def _get_resource_id_from_ctx(self, perm_ctx: ClusterPermCtx) -> Optional[str]:
        return perm_ctx.cluster_id
