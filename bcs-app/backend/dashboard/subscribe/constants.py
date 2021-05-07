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
from backend.resources.constants import K8sResourceKind
from backend.resources.workloads.cronjob import CronJob
from backend.resources.workloads.daemonset import DaemonSet
from backend.resources.workloads.deployment import Deployment
from backend.resources.workloads.job import Job
from backend.resources.workloads.pod import Pod
from backend.resources.workloads.statefulset import StatefulSet

# 默认监听时间：1s
DEFAULT_SUBSCRIBE_TIMEOUT = 1

# K8S资源类型：Client
KIND_RESOURCE_CLIENT_MAP = {
    K8sResourceKind.CronJob.value: CronJob,
    K8sResourceKind.DaemonSet.value: DaemonSet,
    K8sResourceKind.Deployment.value: Deployment,
    K8sResourceKind.Job.value: Job,
    K8sResourceKind.Pod.value: Pod,
    K8sResourceKind.StatefulSet.value: StatefulSet,
}
