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
"""各版本差异常量定义
"""

# 不检查IP是否重复的业务
SKIP_BIZ_INFO = {}

# 白名单接入的业务
BIND_BIZ_ID = []
BIND_BIZ_ID_USER = {}

# CC MODULE INFO
CC_MODULE_INFO = {}

# k8s 平台服务用的集群
K8S_PLAT_CLUSTER_ID = []

# master in binded biz
BCS_APP_ID = ""

# verify resource code for perm
verify_resource_exist = False

# nginx ingress controller path
CONTROLLER_IMAGE_PATH = "bcs/k8s/nginx-ingress-controller"
BACKEND_IMAGE_PATH = "bcs/k8s/defaultbackend"
