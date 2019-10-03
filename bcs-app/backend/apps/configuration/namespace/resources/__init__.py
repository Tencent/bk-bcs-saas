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
from . import k8s, mesos
from backend.apps.constants import ProjectKind


class Namespace:

    def __init__(self, access_token, project_id, project_kind, cluster_id):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.client = k8s if project_kind == ProjectKind.K8S.value else mesos

    def delete(self, ns_name):
        return self.client.Namespace.delete(self.access_token, self.project_id, self.cluster_id, ns_name)