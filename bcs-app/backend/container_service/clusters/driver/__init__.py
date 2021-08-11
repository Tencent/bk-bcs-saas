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
from . import k8s, mesos


class BaseDriver:

    # 1：k8s 2: mesos
    KIND_DRIVER = {1: k8s.K8SDriver, 2: mesos.MesosDriver, 3: k8s.K8SDriver}

    def __init__(self, project_kind):
        self.driver = self.KIND_DRIVER[project_kind]
