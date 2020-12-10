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

from functools import lru_cache

from django.utils.translation import ugettext_lazy as _
from kubernetes import client

from backend.utils.error_codes import error_codes
from backend.components.bcs import k8s
from backend.components.bcs import k8s_client

logger = logging.getLogger(__name__)


@lru_cache(maxsize=64)
def create_api_client(access_token, project_id, cluster_id):
    client = k8s_client.K8SAPIClient(access_token, project_id, cluster_id, None)
    return client.api_client


class APIInstance:
    def __init__(self, access_token, project_id, cluster_id):
        self.api_client = create_api_client(access_token, project_id, cluster_id)
        for api_cls in self.get_api_cls_list(self.api_client):
            try:
                self.api_instance = getattr(client, api_cls)(self.api_client)
                return
            except AttributeError:
                continue
            except Exception as e:
                logger.error("")
                raise error_codes.APIError(f"kubernetes-python error: {e}")
        raise error_codes.APIError(_("kubernetes-python库中，未找到适合当前集群版本的的api version"))


class K8SClient:
    def __init__(self, access_token, project_id, cluster_id):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.client = k8s.K8SClient(access_token, project_id, cluster_id, None)
