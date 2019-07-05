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

# *********************************** Helm Config Begin *****************************
DEFAULT_MANAGE_CLUSTER = {
    'id': '',
    'project_id': ''
}

DEFAULT_REPO_NAMESPACE_INFO = {
    'name': '',
    'id': ''
}

PLATFORM_REPO_INFO = {
    'name': 'platform',
    'url': '',
    'provider': 'chartmuseum',
    'project_id': ''
}

RGW_CONFIG = {
    "admin_host": "",
    "access_key": "",
    "secret_key": "",
    "admin_endpoint": "",
    "tenant": "",
    "default_policy": "",
    "max_size": 1048576
}

# 用于区分chart路径
HELM_REPO_ENV = "stag"
PLATFORM_REPO_DOMAIN = ""

HELM_DOC_TRICKS = "https://bk.tencent.com/docs/"
HELM_SYNC_DO_DEPLOY = False
# *********************************** Helm Config End *****************************

SENTRY_DSN = ''

# 默认超级用户
ADMIN_SUPERUSERS = []

# 集群信息变更等的通知人
DEFAULT_OPER_USER = ""

# so初始化错误信息查看
SO_ERROR_MSG = ""

# op系统通知人
OP_MAINTAINERS = []

# 容器服务API测试环境测试用户
DEFAULT_API_TEST_USER = ''

# 提供给流水线API调用的默认用户
PIPELINE_DEFAULT_USER = ""
# 提供给标准运维API调用的默认用户
GCLOUD_DEFAULT_USER = ""

# Mesos中LB的默认仓库域名
DEFAUT_MESOS_LB_JFROG_DOMAIN = ''

# 平台名称
PLAT_SHOW_NAME = "蓝鲸容器管理平台"

# 小游戏示例代码下载链接
RUMPETROLL_DEMO_DOWNLOAD_URL = 'http://bkopen-10032816.file.myqcloud.com/rumpetroll-1.0.0.tgz'

# 直接开启的功能开关，不需要在db中配置
DIRECT_ON_FUNC_CODE = ['HAS_IMAGE_SECRET']
