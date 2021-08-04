# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

MESOS 获取相关配置
"""
import base64
import json
import time

from django.utils.translation import ugettext_lazy as _

from backend.components import paas_cc
from backend.container_service.clusters.models import CommonStatus
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes


class BaseConfig(object):
    def get_config(self, cluster_id, master_ips, node_ip_list=[]):
        """渲染集群或节点配置"""
        pass


class ClusterConfig(BaseConfig):
    def __init__(self, base_cluster_config, area_info, cluster_name=""):
        self.mesos_config = base_cluster_config
        self.area_config = json.loads(area_info.get('configuration', '{}'))
        self.cluster_name = cluster_name

    def get_request_config(self, cluster_id, master_ips, need_nat=True, **kwargs):
        self.mesos_config.update(
            {
                "master_iplist": ",".join(master_ips),
                "cluster_id": cluster_id,
                "check_iptables_nat": "Y" if need_nat else "N",
            }
        )
        return self.mesos_config


class NodeConfig(BaseConfig):
    def __init__(self, snapshot_config, op_type=None):
        self.mesos_config = snapshot_config

    def get_request_config(self, access_token, project_id, cluster_id, master_ip_list, ip_list):
        # TODO：现阶段slave安装和master安装配置一样，后续再增加其它
        return self.mesos_config
