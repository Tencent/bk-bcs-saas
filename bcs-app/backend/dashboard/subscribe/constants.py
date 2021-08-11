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
from backend.resources.configs.configmap import ConfigMap
from backend.resources.configs.secret import Secret
from backend.resources.custom_object import CustomResourceDefinition
from backend.resources.event.client import Event
from backend.resources.hpa.client import HPA
from backend.resources.namespace.client import Namespace
from backend.resources.networks.endpoints import Endpoints
from backend.resources.networks.ingress import Ingress
from backend.resources.networks.service import Service
from backend.resources.rbac.service_account import ServiceAccount
from backend.resources.storages.persistent_volume import PersistentVolume
from backend.resources.storages.persistent_volume_claim import PersistentVolumeClaim
from backend.resources.storages.storage_class import StorageClass
from backend.resources.workloads.cronjob import CronJob
from backend.resources.workloads.daemonset import DaemonSet
from backend.resources.workloads.deployment import Deployment
from backend.resources.workloads.job import Job
from backend.resources.workloads.pod import Pod
from backend.resources.workloads.statefulset import StatefulSet

# 超时时间为负数，表示不需要持续监听，获取数据后立即结束
DEFAULT_SUBSCRIBE_TIMEOUT = -1

# k8s API Gone 状态码，一般出现在使用过期的 resourceVersion 进行 watch 的情况
# ref: https://kubernetes.io/docs/reference/using-api/api-concepts/#410-gone-responses
K8S_API_GONE_STATUS_CODE = 410

# K8S Client
K8S_RESOURCE_CLIENTS = [
    # workloads
    CronJob,
    DaemonSet,
    Deployment,
    Job,
    Pod,
    StatefulSet,
    # networks
    Endpoints,
    Ingress,
    Service,
    # rbac
    ServiceAccount,
    # storages
    PersistentVolume,
    PersistentVolumeClaim,
    StorageClass,
    # configurations
    ConfigMap,
    Secret,
    # CustomResource
    CustomResourceDefinition,
    # cluster
    Event,
    Namespace,
    # HPA
    HPA,
]

# K8S资源类型：Client
KIND_RESOURCE_CLIENT_MAP = {client.kind: client for client in K8S_RESOURCE_CLIENTS}
