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
"""
import logging

from backend.apps import constants
from backend.components.bcs.mesos import MesosClient
from backend.container_service.clusters.constants import MESOS_SKIP_NS_LIST
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes

logger = logging.getLogger(__name__)


class MesosDriver:
    def __init__(self, request, project_id, cluster_id):
        self.request = request
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.client = MesosClient(self.request.user.token.access_token, self.project_id, self.cluster_id, None)

    def host_container_map(self, resp):
        host_container_map = {}
        for info in resp.get('data') or []:
            if info["namespace"] in MESOS_SKIP_NS_LIST:
                continue
            host_ip = info.get('data', {}).get('hostIP')
            container_count = len(info['data']['containerStatuses'])
            if host_ip in host_container_map:
                host_container_map[host_ip] += container_count
            else:
                host_container_map[host_ip] = container_count
        return host_container_map

    def get_unit_info(self, inner_ip, fields, raise_exception=True):
        """get the resource unit info"""
        resp = self.client.get_taskgroup(inner_ip, fields=fields)
        if resp.get('code') != ErrorCode.NoError:
            logger.error("request taskgroup api error, %s", resp.get("message"))
            if raise_exception:
                raise error_codes.APIError(resp.get('message'))

        return resp

    def get_host_container_count(self, host_ips):
        field_list = ['data.containerStatuses.containerID', 'data.hostIP', "namespace"]
        resp = self.get_unit_info(host_ips, ','.join(field_list))
        # compose the host container data
        return self.host_container_map(resp)

    def flatten_container_info(self, inner_ip):
        """flatten container info by inner_ip"""

        def iter_container(tg):
            for g in tg:
                if g.get("namespace") in MESOS_SKIP_NS_LIST:
                    continue
                for d in g['data']['containerStatuses']:
                    c = {
                        'name': d['name'],
                        'image': d['image'],
                        'status': d['status'].lower(),
                        'container_id': d['containerID'],
                    }
                    yield c

        taskgroups = self.get_unit_info(inner_ip, fields='data,namespace').get('data') or []
        containers = sorted(
            [i for i in iter_container(taskgroups)],
            key=lambda x: constants.DockerStatusOrdering.get(x['status'], constants.DockerStatusDefaultOrder),
        )
        return containers

    def disable_node(self, ip):
        node_resp = self.client.disable_agent(ip)
        if node_resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(node_resp.get('message'))

    def enable_node(self, ip):
        node_resp = self.client.enable_agent(ip)
        if node_resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(node_resp.get('message'))

    def get_host_unit_list(self, ip, raise_exception=True):
        """get exist pods on the node"""
        unit_list = []
        fields = 'namespace,resourceName,data.rcname'
        resp = self.get_unit_info([ip], fields, raise_exception=raise_exception)
        for i in resp.get('data') or []:
            unit_list.append(
                {
                    'namespace': i.get('namespace'),
                    'app_name': i.get('data', {}).get('rcname'),
                    'taskgroup_name': i.get('resourceName'),
                }
            )
        return unit_list

    def reschedule_pod(self, pod_info, raise_exception=True):
        resp = self.client.rescheduler_mesos_taskgroup(
            pod_info['namespace'], pod_info['app_name'], pod_info['taskgroup_name']
        )
        if resp.get('code') != ErrorCode.NoError:
            logger.error("request rescheduler taskgroup api error, %s", resp.get("message"))
            if raise_exception:
                raise error_codes.APIError(resp.get('message'))

        return resp

    def reschedule_host_pods(self, ip, raise_exception=True):
        unit_list = self.get_host_unit_list(ip, raise_exception=raise_exception)
        for info in unit_list:
            self.reschedule_pod(info, raise_exception=raise_exception)
        return
