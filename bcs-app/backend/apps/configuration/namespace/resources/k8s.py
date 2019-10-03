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
import logging

from backend.components.bcs.k8s import K8SClient
from backend.utils.error_codes import error_codes
from backend.utils.errcodes import ErrorCode

logger = logging.getLogger(__name__)


class Namespace:

    @classmethod
    def delete(cls, access_token, project_id, cluster_id, ns_name):
        client = K8SClient(access_token, project_id, cluster_id, env=None)
        resp = client.delete_namespace(ns_name)
        if resp.get('code') == ErrorCode.NoError:
            return
        if 'not found' in resp.get('message'):
            return
        raise error_codes.APIError(f'delete namespace error, name: {ns_name}, {resp.get("message")}')
