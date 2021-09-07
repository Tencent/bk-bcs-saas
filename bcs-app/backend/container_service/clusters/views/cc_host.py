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
from typing import Dict, List

from rest_framework.decorators import action
from rest_framework.response import Response

from backend.bcs_web.viewsets import SystemViewSet
from backend.components import cc, gse, paas_cc
from backend.container_service.clusters.models import CommonStatus
from backend.container_service.clusters.serializers import FetchCCHostSLZ
from backend.utils.basic import get_with_placeholder
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.utils.filter import filter_by_ips
from backend.utils.paginator import custom_paginator

logger = logging.getLogger(__name__)


class CCViewSet(SystemViewSet):
    """ CMDB 主机查询相关接口 """

    @action(methods=['GET'], url_path='topology', detail=False)
    def biz_inst_topo(self, request, project_id):
        """ 查询业务实例拓扑 """
        resp = cc.search_biz_inst_topo(request.user.username, request.project.cc_app_id)
        if not resp.get('result'):
            raise error_codes.APIError(resp.get('message'))
        topo_info = resp.get('data') or []
        return Response(data=topo_info)

    @action(methods=['POST'], url_path='hosts', detail=False)
    def hosts(self, request, project_id):
        """ 查询指定业务拓扑下主机列表 """
        params = self.params_validate(FetchCCHostSLZ)

        # 从 CMDB 获取可用主机信息，业务名称信息
        host_list = self._fetch_cc_app_hosts(params['set_id'], params['module_id'])
        cc_app_name = cc.get_application_name(request.user.username, request.project.cc_app_id)

        # 根据指定的 IP 过滤
        host_list = filter_by_ips(host_list, params['ip_list'], key='bk_host_innerip', fuzzy=params['fuzzy'])

        response_data = {
            'results': [],
            'count': 0,
            'cc_application_name': cc_app_name,
            'unavailable_ip_count': 0,
        }
        # 补充节点使用情况，包含使用的项目 & 集群
        project_cluster_info = self._fetch_project_cluster_info()
        all_cluster_nodes = self._fetch_all_cluster_nodes()
        host_list = self._update_host_info(host_list, all_cluster_nodes, project_cluster_info)

        # 如没有符合过滤条件的，直接返回默认值
        if not host_list:
            return Response(response_data)

        # 被使用 / agent 异常的机器均视为 不可使用
        response_data['unavailable_ip_count'] = len([h for h in host_list if h['is_used'] or not h['is_valid']])

        ret = custom_paginator(host_list, params['offset'], params['limit'])
        # 更新 Host 的 GSE Agent 状态信息
        ret['results'] = self._update_gse_agent_status(ret['results'])

        response_data['results'] = ret['results']
        response_data['count'] = ret['count']
        return Response(response_data)

    def _fetch_cc_app_hosts(self, bk_module_id=None, bk_set_id=None) -> List[Dict]:
        """
        拉取 业务 下机器列表（业务/集群/模块全量）
        TODO 当前场景只需要支持单模块/集群，后续有需要可扩展

        :return: CMDB 业务下机器列表
        """
        bk_module_ids = [bk_module_id] if bk_module_id else None
        bk_set_ids = [bk_set_id] if bk_set_id else None
        resp = cc.list_all_hosts_by_topo(
            self.request.user.username, self.request.project.cc_app_id, bk_module_ids, bk_set_ids
        )
        if resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(resp.get('message'))
        return resp.get('data') or []

    def _fetch_all_cluster_nodes(self) -> Dict:
        """
        获取所有集群中使用的主机信息

        :return: {'ip': node_info}
        """
        nodes = paas_cc.get_all_cluster_hosts(
            self.request.user.token.access_token, exclude_status_list=[CommonStatus.Removed]
        )
        return {n['inner_ip']: n for n in nodes}

    def _fetch_project_cluster_info(self) -> Dict:
        """
        获取 项目 & 集群信息

        :return: {cluster_id: {'project_name': p_name, 'cluster_name': c_name}
        """
        resp = paas_cc.get_project_cluster_resource(self.request.user.token.access_token)
        if resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(resp.get('message'))
        ret = resp.get('data') or []
        return {
            cluster['id']: {'project_name': project['name'], 'cluster_name': cluster['name']}
            for project in ret
            if project
            for cluster in project['cluster_list']
            if cluster
        }

    def _update_host_info(self, host_list: List, all_cluster_nodes: Dict, project_cluster_info: Dict) -> List:
        """
        更新节点使用状态 & 是否类型可用，补充项目，集群等信息

        :param host_list: 原始主机列表
        :param all_cluster_nodes: 全集群节点信息
        :param project_cluster_info: 项目 & 集群信息
        :return: 包含使用信息的主机列表
        """
        new_host_list, used_host_list = [], []
        for host in host_list:
            is_used = False
            if 'bk_host_innerip' not in host or not host['bk_host_innerip']:
                continue
            project_name, cluster_name, cluster_id = '', '', ''
            for ip in host['bk_host_innerip'].split(','):
                node_info = all_cluster_nodes.get(ip)
                if not node_info:
                    continue
                is_used = True
                cluster_id = node_info.get('cluster_id')
                name_dict = project_cluster_info.get(cluster_id) or {}
                project_name = get_with_placeholder(name_dict, 'project_name')
                cluster_name = get_with_placeholder(name_dict, 'cluster_name')
                break

            host.update(
                {
                    'project_name': project_name,
                    'cluster_name': cluster_name,
                    'cluster_id': cluster_id,
                    'is_used': is_used,
                    "is_valid": self._is_vaild_machine(host),
                }
            )
            if is_used:
                used_host_list.append(host)
            else:
                new_host_list.append(host)

        # 已被使用的 Host 放列表最后
        new_host_list.extend(used_host_list)
        return new_host_list

    def _is_vaild_machine(self, host: Dict) -> bool:
        """ 判断是否为机器类型是否可用 """
        # docker 机不可用，判断条件为 svr_device_class 以 D 开头
        return not host.get('svr_device_class', '').startswith('D')

    def _update_gse_agent_status(self, host_list: List) -> List:
        """ 更新 GSE Agent 状态信息 """
        gse_params = []
        for info in host_list:
            bk_cloud_id = info.get('bk_cloud_id') or 0
            gse_params.extend(
                [
                    {'plat_id': bk_cloud_id, 'bk_cloud_id': bk_cloud_id, 'ip': ip}
                    for ip in info.get('bk_host_innerip', '').split(',')
                ]
            )
        gse_host_status_map = {
            info['ip']: info for info in gse.get_agent_status(self.request.user.username, gse_params)
        }
        # 根据 IP 匹配更新 Agent 信息
        cc_host_map = {host['bk_host_innerip']: host for host in host_list}
        for ips in cc_host_map:
            # 同主机可能存在多个 IP，任一 IP Agent 正常即可
            for ip in ips.split(','):
                if ip not in gse_host_status_map:
                    continue
                ip_status = gse_host_status_map[ip]
                cc_host_map[ips]['agent_alive'] = ip_status.get('bk_agent_alive')
                break

        return list(cc_host_map.values())
