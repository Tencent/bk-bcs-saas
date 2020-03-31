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
from backend.apps.variable.models import NameSpaceVariable
from backend.apps.instance.models import InstanceConfig

from backend.bcs_k8s.app.models import App
from backend.apps.network.models import K8SLoadBlance, MesosLoadBlance


def delete_common_records_for_namespace(namespace_id):
    # 删除k8s和mesos都包含的db记录
    # 包含: InstanceConfig, NameSpaceVariable
    InstanceConfig.objects.filter(namespace=namespace_id).delete()
    NameSpaceVariable.objects.filter(ns_id=namespace_id).delete()


def delete_k8s_records_for_namespace(namespace_id, cluster_id=None, namespace_name=None):
    """删除k8s的db记录"""
    delete_common_records_for_namespace(namespace_id)
    # k8s相关的记录包含: chart release、k8s lb
    App.objects.filter(namespace_id=namespace_id).delete()
    K8SLoadBlance.objects.filter(namespace_id=namespace_id).delete()


def delete_mesos_records_for_namespace(namespace_id, cluster_id=None, namespace_name=None):
    """删除mesos的db记录"""
    delete_common_records_for_namespace(namespace_id)
    # mesos相关的记录包含: mesos lb
    MesosLoadBlance.objects.filter(namespace_id=namespace_id).delete()
