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
import logging

from kubernetes.client.exceptions import ApiException

from backend.resources.cluster.models import CtxCluster
from backend.resources.utils.kube_client import get_dynamic_client
from backend.utils.error_codes import error_codes

from . import constants

logger = logging.getLogger(__name__)


class Log:
    """Pod 子资源日志查询"""

    def __init__(self, ctx_cluster: CtxCluster, namespace: str, pod_name: str):
        self.ctx_cluster = ctx_cluster
        self.dynamic_client = get_dynamic_client(
            ctx_cluster.context.auth.access_token, ctx_cluster.project_id, ctx_cluster.id
        )

        pod_resource = self.dynamic_client.get_preferred_resource("Pod")
        self.resource = pod_resource.subresources['log']
        self.namespace = namespace
        self.pod_name = pod_name

    def fetch_log(self, params: dict):
        """获取日志"""
        params['timestamps'] = constants.LOG_SHOW_TIMESTAMPS

        # 强制限制返回大小
        params['limitBytes'] = constants.LOG_LIMIT_BYTES

        try:
            result = self.dynamic_client.get(self.resource, self.pod_name, self.namespace, query_params=params)
        except ApiException as error:
            body = json.loads(error.body)
            raise error_codes.APIError(body['message'])

        return result
