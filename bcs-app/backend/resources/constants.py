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
from backend.utils.basic import ChoicesEnum

# cronjob 不在 preferred resource 中，需要指定 api_version
DEFAULT_CRON_JOB_API_VERSION = 'v1beta1'


class WorkloadTypes(ChoicesEnum):
    Deployment = "Deployment"
    StatefulSet = "StatefulSet"
    DaemonSet = "DaemonSet"
    Job = "Job"
    GameStatefulSet = "GameStatefulSet"
    GameDeployment = "GameDeployment"

    _choices_labels = (
        (Deployment, "Deployment"),
        (StatefulSet, "StatefulSet"),
        (DaemonSet, "DaemonSet"),
        (Job, "Job"),
        (GameStatefulSet, "GameStatefulSet"),
        (GameDeployment, "GameDeployment"),
    )


class K8sResourceKind(ChoicesEnum):
    # workload
    Deployment = "Deployment"
    StatefulSet = "StatefulSet"
    DaemonSet = "DaemonSet"
    CronJob = "CronJob"
    Job = "Job"
    Pod = "Pod"
    # network
    Ingress = "Ingress"
    Service = "Service"
    Endpoints = "Endpoints"
    # configuration
    ConfigMap = "ConfigMap"
    Secret = "Secret"
    # storage
    PersistentVolume = "PersistentVolume"
    PersistentVolumeClaim = "PersistentVolumeClaim"
    StorageClass = "StorageClass"
    # rbac
    ServiceAccount = "ServiceAccount"
    # other
    Event = "Event"
    Namespace = "Namespace"
    Node = "Node"

    _choices_labels = (
        # workload
        (Deployment, "Deployment"),
        (StatefulSet, "StatefulSet"),
        (DaemonSet, "DaemonSet"),
        (CronJob, "CronJob"),
        (Job, "Job"),
        (Pod, "Pod"),
        # network
        (Endpoints, "Endpoints"),
        (Ingress, "Ingress"),
        (Service, "service"),
        # configuration
        (ConfigMap, "ConfigMap"),
        (Secret, "Secret"),
        # storage
        (PersistentVolume, "PersistentVolume"),
        (PersistentVolumeClaim, "PersistentVolumeClaim"),
        (StorageClass, "StorageClass"),
        # rbac
        (ServiceAccount, "ServiceAccount"),
        # other
        (Event, "Event"),
        (Namespace, "Namespace"),
        (Node, "Node"),
    )


class K8sServiceTypes(ChoicesEnum):
    ClusterIP = "ClusterIP"
    NodePort = "NodePort"
    LoadBalancer = "LoadBalancer"

    _choices_labels = ((ClusterIP, "ClusterIP"), (NodePort, "NodePort"), (LoadBalancer, "LoadBalancer"))


class PatchType(ChoicesEnum):
    JSON_PATCH_JSON = "application/json-patch+json"
    MERGE_PATCH_JSON = "application/merge-patch+json"
    STRATEGIC_MERGE_PATCH_JSON = "application/strategic-merge-patch+json"
    APPLY_PATCH_YAML = "application/apply-patch+yaml"

    _choices_labels = (
        (JSON_PATCH_JSON, "application/json-patch+json"),
        (MERGE_PATCH_JSON, "application/merge-patch+json"),
        (STRATEGIC_MERGE_PATCH_JSON, "application/strategic-merge-patch+json"),
        (APPLY_PATCH_YAML, "application/apply-patch+yaml"),
    )


class PodConditionType(ChoicesEnum):
    """ k8s PodConditionType """

    PodScheduled = 'PodScheduled'
    PodReady = 'Ready'
    PodInitialized = 'Initialized'
    PodReasonUnschedulable = 'Unschedulable'
    ContainersReady = 'ContainersReady'


class PodPhase(ChoicesEnum):
    """ k8s PodPhase """

    PodPending = 'Pending'
    PodRunning = 'Running'
    PodSucceeded = 'Succeeded'
    PodFailed = 'Failed'
    PodUnknown = 'Unknown'


class SimplePodStatus(ChoicesEnum):
    """
    用于页面展示的简单 Pod 状态
    在 k8s PodPhase 基础上细分了状态
    """

    # 原始 PodPhase 状态
    PodPending = 'Pending'
    PodRunning = 'Running'
    PodSucceeded = 'Succeeded'
    PodFailed = 'Failed'
    PodUnknown = 'Unknown'
    # 细分状态
    NotReady = 'NotReady'
    Terminating = 'Terminating'
    Completed = 'Completed'


class ConditionStatus(ChoicesEnum):
    """ k8s ConditionStatus """

    ConditionTrue = 'True'
    ConditionFalse = 'False'
    ConditionUnknown = 'Unknown'


class PersistentVolumeAccessMode(str, StructuredEnum):
    """ k8s PersistentVolumeAccessMode """

    ReadWriteOnce = EnumField('ReadWriteOnce', label='RWO')
    ReadOnlyMany = EnumField('ReadOnlyMany', label='ROX')
    ReadWriteMany = EnumField('ReadWriteMany', label='RWX')

    @property
    def shortname(self):
        """ k8s 官方缩写 """
        return self.get_choice_label(self.value)
