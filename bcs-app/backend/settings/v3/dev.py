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
from .base import *  # noqa

LOG_LEVEL = 'DEBUG'
LOGGING = get_logging_config(LOG_LEVEL)

# PaaS域名，发送邮件链接需要
PAAS_HOST = BK_PAAS_HOST
PAAS_ENV = 'local'

# BCS CC PATH
BCS_CC_CLUSTER_CONFIG = '/v1/clusters/{cluster_id}/cluster_version_config/'
BCS_CC_GET_CLUSTER_MASTERS = '/projects/{project_id}/clusters/{cluster_id}/manager_masters/'
BCS_CC_GET_PROJECT_MASTERS = '/projects/{project_id}/clusters/null/manager_masters/'
BCS_CC_GET_PROJECT_NODES = '/projects/{project_id}/clusters/null/nodes/'
BCS_CC_OPER_PROJECT_NODE = '/projects/{project_id}/clusters/null/nodes/{node_id}/'
BCS_CC_OPER_PROJECT_NAMESPACES = '/projects/{project_id}/clusters/null/namespaces/'
BCS_CC_OPER_PROJECT_NAMESPACE = '/projects/{project_id}/clusters/null/namespaces/{namespace_id}/'
