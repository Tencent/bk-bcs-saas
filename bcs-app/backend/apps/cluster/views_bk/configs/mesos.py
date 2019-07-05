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
"""
MESOS 获取相关配置
"""
import json
import time
import base64

from backend.components import paas_cc
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.apps.cluster.models import CommonStatus


class BaseConfig(object):

    def get_config(self, cluster_id, master_ips, node_ip_list=[]):
        """渲染集群或节点配置
        """
        pass


class ClusterConfig(BaseConfig):

    def __init__(self, base_cluster_config, area_info, cluster_name=""):
        self.mesos_config = base_cluster_config
        self.area_config = json.loads(area_info.get('configuration', '{}'))
        self.cluster_name = cluster_name

    def get_request_config(self, cluster_id, master_ips, need_nat=True):
        self.mesos_config['check_iptables_nat'] = 'Y' if need_nat else 'N'
        return self.mesos_config

class NodeConfig(BaseConfig):

    def __init__(self, snapshot_config, op_type=None):
        self.mesos_config = snapshot_config

    def get_cluster_node_list(self, access_token, project_id, cluster_id):
        # TODO: 先兼容
        DEFAULT_NODE_LIMIT = 10000
        cluster_node_info = paas_cc.get_node_list(
            access_token, project_id, cluster_id,
            params={'limit': DEFAULT_NODE_LIMIT}
        )
        if cluster_node_info.get('code') != ErrorCode.NoError:
            raise error_codes.APIError.f(cluster_node_info.get('message'))
        ip_info_list = cluster_node_info.get('data', {}).get('results', [])
        if not ip_info_list:
            raise error_codes.APIError.f("获取集群节点为空，请确认后重试")
        return [
            info['inner_ip']
            for info in ip_info_list
            if info.get('status') not in [CommonStatus.Removed, CommonStatus.Removing]
        ]

    def get_config(self, node_ip_list=[]):
        """渲染集群或节点配置
        注意下发节点配置时，需要渲染exporter server 和cadvisor server
        """
        exporter_port = self.mesos_config.get('MESOS_NODE_EXPORTER_PORT')
        cadvisor_port = self.mesos_config.get('MESOS_CADVISOR_PORT')
        # render ip:port
        node_exporter_server_list_dump = json.dumps([
            '%s:%s' % (ip, exporter_port) for ip in node_ip_list
        ])
        cadvisor_server_list_dump = json.dumps([
            '%s:%s' % (ip, cadvisor_port) for ip in node_ip_list
        ])
        self.mesos_config.update({
            'ENCODE_LIST_MESOS_NODE_EXPORTER_SERVER': base64.b64encode(
                node_exporter_server_list_dump.encode(encoding='utf-8')).decode(),
            'ENCODE_LIST_MESOS_CADVISOR_SERVER': base64.b64encode(
                cadvisor_server_list_dump.encode(encoding='utf-8')).decode(),
            'OP_TIMESTAMP': str(int(time.time()))
        })

    def get_request_config(self, access_token, project_id, cluster_id, master_ip_list, ip_list):
        cluster_node_list = self.get_cluster_node_list(access_token, project_id, cluster_id)
        self.get_config(node_ip_list=cluster_node_list)
        return self.mesos_config
