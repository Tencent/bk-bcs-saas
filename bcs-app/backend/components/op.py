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
import json

from django.conf import settings

from .utils import http_post

APIGW_OP_HOST = "%s/api/bk-op/%s" % (settings.APIGW_HOST, settings.APIGW_OP_ENV)

# timeout
DEFAULT_TIMEOUT = 20


def notify_project_to_op(access_token, data):
    """
    When project info add or changed, notify op system
    in order to update cache of project in op
    """
    url = "{host}/openapi/handleProjectInfo".format(
        host=APIGW_OP_HOST
    )
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token
        })
    }
    return http_post(url, json=data, headers=headers, timeout=DEFAULT_TIMEOUT)
