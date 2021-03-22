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

from django.conf import settings
from rest_framework.exceptions import ValidationError

from backend.apps.cluster import constants as cluster_constants
from backend.components import cc as cmdb
from backend.resources.cluster.constants import ClusterCOES
from backend.resources.cluster.utils import get_cluster_coes
from backend.utils.funutils import convert_mappings

logger = logging.getLogger(__name__)

# 1表示gse agent正常
AGENT_NORMAL_STATUS = 1


def use_tke(coes=None, access_token=None, project_id=None, cluster_id=None):
    """判断是否使用TKE"""
    if not (cluster_id or coes):
        raise ValidationError(_("集群ID或集群类型不能同时为空"))
    if not coes:
        coes = get_cluster_coes(access_token, project_id, cluster_id)

    if coes == ClusterCOES.TKE.value:
        return True
    return False


def get_ops_platform(request, coes=None, project_id=None, cluster_id=None):
    # 获取ops需要的平台类型，便于ops转发后面的标准运维
    # gcloud_v3_inner: 内部版标准运维v3, gcloud_v1_inner: 内部版标准运维v1, gcloud_v3_tke: tke流程
    access_token = request.user.token.access_token
    if use_tke(coes=coes, access_token=access_token, project_id=project_id, cluster_id=cluster_id):
        return 'gcloud_v3_tke'
    elif request.project.bg_id != getattr(settings, "IEG_ID", ""):
        return 'gcloud_v3_inner'
    else:
        return 'gcloud_v1_inner'


def get_cmdb_hosts(username, cc_app_id_list, host_property_filter):
    hosts = []
    for app_id in cc_app_id_list:
        resp = cmdb.list_biz_hosts(username, int(app_id), host_property_filter=host_property_filter)
        if resp.get("data"):
            hosts = resp["data"]
            break
    cluster_masters = []
    for info in hosts:
        convert_host = convert_mappings(cluster_constants.CCHostKeyMappings, info)
        convert_host["agent"] = AGENT_NORMAL_STATUS
        cluster_masters.append(convert_host)

    return cluster_masters


try:
    from .utils_ext import *  # noqa
except Exception as e:
    logger.debug("Load extension failed: %s", e)
