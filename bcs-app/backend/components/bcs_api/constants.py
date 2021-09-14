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
from django.utils.translation import ugettext as _

from backend.packages.blue_krill.data_types.enum import EnumField, StructuredEnum

# bcs api的版本
BCS_API_VERSION = "v4"

# 资源记录不存在的code
RECORD_NOT_EXIST_CODE = 1405420
# 资源记录存在的code
RECORD_EXIST_CODE = 1405405


class DeployType(str, StructuredEnum):
    """部署类型, 使用物理机或者容器部署"""

    Physical = EnumField(1, label=_("物理机部署"))
    Container = EnumField(2, label=_("容器部署"))


class ProjectType(str, StructuredEnum):
    """项目类型，项目属于平台或者业务"""

    Platform = EnumField(1, label="platform")
    Business = EnumField(2, label="business")


class ManageType(str, StructuredEnum):
    """集群管理类型"""

    MANAGED_CLUSTER = EnumField("MANAGED_CLUSTER", label=_("云上托管集群"))
    INDEPENDENT_CLUSTER = EnumField("INDEPENDENT_CLUSTER", label=_("独立集群，自行维护"))


class ClusterManageType(str, StructuredEnum):
    """集群管理类型"""

    SINGLE = EnumField("single", label=_("独立集群"))
    FEDERATION = EnumField("federation", label=_("联邦集群"))
