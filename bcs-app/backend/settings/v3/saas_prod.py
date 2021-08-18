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

# ******************************** 日志 配置 ********************************
LOG_LEVEL = 'INFO'
BK_LOG_DIR = os.environ.get('BKV3_LOG_DIR', '/data/paas/apps/logs/')
LOGGING_DIR = os.path.join(BK_LOG_DIR, 'logs', APP_ID)
LOG_CLASS = 'logging.handlers.RotatingFileHandler'
if RUN_MODE == 'DEVELOP':
    LOG_LEVEL = 'DEBUG'
elif RUN_MODE == 'TEST':
    LOGGING_DIR = os.path.join(BK_LOG_DIR, APP_ID)
    LOG_LEVEL = 'INFO'
elif RUN_MODE == 'PRODUCT':
    LOGGING_DIR = os.path.join(BK_LOG_DIR, APP_ID)
    LOG_LEVEL = 'ERROR'

# 兼容企业版
LOGGING_DIR = os.environ.get('LOGGING_DIR', LOGGING_DIR)

# 自动建立日志目录
if not os.path.exists(LOGGING_DIR):
    os.makedirs(LOGGING_DIR)

LOG_FILE = os.path.join(LOGGING_DIR, f'{APP_ID}.log')
LOGGING = get_logging_config(LOG_LEVEL, None, LOG_FILE)

# ******************************** 容器服务相关配置 ********************************

APIGW_ENV = ''

# 测试环境先禁用掉集群创建时的【prod】环境
DISABLE_PROD = True

# PaaS域名，发送邮件链接需要
PAAS_HOST = BK_PAAS_HOST
PAAS_ENV = 'dev'

# BKE 配置
# note：BKE_SERVER_HOST 配置为None时表示不使用bke，而是直接用本地kubectl
BKE_CACERT = ''

BKE_SERVER_HOST = BCS_SERVER_HOST

HELM_INSECURE_SKIP_TLS_VERIFY = True
