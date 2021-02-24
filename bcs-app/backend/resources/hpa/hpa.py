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
from typing import Optional
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from kubernetes.dynamic.resource import ResourceInstance
from backend.apps.configuration.constants import K8sResourceName
from backend.apps.application import constants as app_constants
from backend.apps.instance.models import InstanceConfig

from ..resource import ResourceClient
from ..utils.auths import ClusterAuth
from .format import HPAFormatter


logger = logging.getLogger(__name__)


class DeleteHPAError(Exception):
    pass


class HPA(ResourceClient):
    preferred_api_version = "autoscaling/v2beta2"
    kind = "HorizontalPodAutoscaler"

    def __init__(
        self,
        cluster_auth: ClusterAuth,
        project_code: Optional[str] = None,
        cluster_name: Optional[str] = None,
        cluster_env: Optional[str] = None,
    ):
        super().__init__(cluster_auth, self.preferred_api_version)

        self.formatter = HPAFormatter(cluster_auth.cluster_id, project_code, cluster_name, cluster_env)

    def delete_ignore_nonexistent(
        self, namespace: str, namespace_id: int, name: str, username: str
    ) -> Optional[ResourceInstance]:

        try:
            result = super().delete_ignore_nonexistent(name=name, namespace=namespace)
        except Exception as error:
            logger.error("delete hpa error, %s", error)
            raise DeleteHPAError(_("删除HPA资源失败"))

        # 删除成功则更新状态
        InstanceConfig.objects.filter(namespace=namespace_id, category=K8sResourceName.K8sHPA.value, name=name).update(
            updator=username,
            oper_type=app_constants.DELETE_INSTANCE,
            deleted_time=timezone.now(),
            is_deleted=True,
            is_bcs_success=True,
        )

        return result
