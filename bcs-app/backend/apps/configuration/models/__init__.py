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
from .base import BaseModel, get_default_version, POD_RES_LIST
from .template import Template, get_template_by_project_and_id, ShowVersion, VersionedEntity, get_app_resource
from .mesos import Application, Deplpyment, Service, ConfigMap, Secret
from .k8s import K8sDeployment, K8sConfigMap, K8sSecret, K8sDaemonSet, K8sJob, K8sService, K8sStatefulSet, \
    K8sIngress, CATE_SHOW_NAME, CATE_ABBR_NAME
from .utils import get_model_class_by_resource_name, get_pod_related_service, get_service_related_statefulset, \
    get_application_related_resource, get_secret_name_by_certid, get_pod_qsets_by_tag, get_k8s_container_ports, \
    MODULE_DICT
from .resfile import ResourceFile
