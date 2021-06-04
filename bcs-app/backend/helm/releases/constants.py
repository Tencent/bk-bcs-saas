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
from backend.packages.blue_krill.data_types.enum import EnumField, StructuredEnum


class ReleaseStatus(str, StructuredEnum):
    """Release的发布状态"""

    Deployed = EnumField("deployed", label="Deployed")
    Superseded = EnumField("superseded", label="Superseded")
    Failed = EnumField("failed", label="Failed")
    Uninstalled = EnumField("uninstalled", label="Uninstalled")
    Uninstalling = EnumField("uninstalling", label="Uninstalling")
    PendingInstall = EnumField("pending-install", label="PendingInstall")
    PendingUpgrade = EnumField("pending-upgrade", label="PendingUpgrade")
    PendingRollback = EnumField("pending-rollback", label="PendingRollback")
    Unknown = EnumField("unknown", label="Unknown")


# BCS 注入的updater中的annotation，兼容【io.tencent.paas.updator】
BCS_INJECT_UPDATER_ANNOTATIONS = ["io.tencent.paas.updater", "io.tencent.paas.updator"]
