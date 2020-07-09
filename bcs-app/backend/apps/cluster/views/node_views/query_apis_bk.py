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
from rest_framework import response, viewsets
from rest_framework.renderers import BrowsableAPIRenderer

from backend.components import paas_cc
from backend.utils.renderers import BKAPIRenderer
from backend.utils.funutils import convert_mappings
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.apps.cluster.utils import custom_paginator
from backend.apps.cluster import constants as cluster_constants
from backend.apps.cluster.views.node import NodeBase, NodeHandler
from backend.apps.cluster import serializers as node_serializers
from backend.apps.cluster.views_bk.tools import cmdb, gse


class CCHostListViewSet(NodeBase, NodeHandler, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_data(self, request):
        """serialize request data
        """
        slz = node_serializers.ListNodeSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        return dict(slz.validated_data)

    def get_all_nodes(self, request, project_id):
        data = paas_cc.get_project_all_nodes(
            request.user.token.access_token, project_id
        )
        return {
            info['inner_ip']: info
            for info in data
        }

    def get_cc_host_mappings(self, host_list):
        data = {
            info['InnerIP']: convert_mappings(cluster_constants.CCHostKeyMappings, info)
            for info in host_list
        }
        return data

    def get_project_cluster_resource(self, request):
        """get all master/node info
        """
        resp = paas_cc.get_project_cluster_resource(request.user.token.access_token)
        if resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(resp.get('message'))
        data = resp.get('data') or []
        # return format: {cluster_id: {project_name: xxx, cluster_name: xxx}}
        format_data = {
            cluster['id']: {'project_name': project['name'], 'cluster_name': cluster['name']}
            for project in data if project
            for cluster in project['cluster_list'] if cluster
        }
        return format_data

    def update_agent_status(self, cc_host_map, gse_host_status):
        gse_host_status_map = {info['ip']: info for info in gse_host_status}
        for ips in cc_host_map:
            # one host may has many eth(ip)
            ip_list = ips.split(',')
            exist = -1
            for item in ip_list:
                if item not in gse_host_status_map or exist > 0:
                    continue
                item_info = gse_host_status_map[item]
                item_exist = item_info.get('exist') or item_info.get('bk_agent_alive')
                # 防止出现None情况
                exist = exist if exist > 0 else (item_exist or exist)
            # render agent status
            cc_host_map[ips]['agent'] = exist if exist else -1

    def render_node_with_use_status(self, host_list, exist_node_info, project_cluster_resource):
        # node_list: not used node list; used_node_list: used node list
        node_list = []
        used_node_list = []
        # handler
        for ip_info in host_list:
            used_status = False
            ips = ip_info.get('InnerIP')
            if not ips:
                continue
            # init the filed value
            project_name, cluster_name, cluster_id = '', '', ''
            for ip in ips.split(','):
                used_ip_info = exist_node_info.get(ip)
                if not used_ip_info:
                    continue
                used_status = True
                cluster_id = used_ip_info.get('cluster_id')
                project_cluster_name = project_cluster_resource.get(cluster_id) or {}
                project_name = project_cluster_name.get('project_name', '')
                cluster_name = project_cluster_name.get('cluster_name', '')
                break
            # update fields and value
            ip_info.update({
                'project_name': project_name,
                'cluster_name': cluster_name,
                'cluster_id': cluster_id,
                'is_used': used_status,
                # 添加是否docker机类型，docker机不允许使用
                # 判断条件为，以`D`开头则为docker机
                "is_valid": False if ip_info.get("DeviceClass", "").startswith("D") else True

            })
            if used_status:
                used_node_list.append(ip_info)
            else:
                node_list.append(ip_info)
        # append used node list
        node_list.extend(used_node_list)
        return node_list

    def post(self, request, project_id):
        """get cmdb host info, include gse status, use status
        """
        # get request data
        data = self.get_data(request)
        cmdb_client = cmdb.CMDBClient(request)
        host_list = cmdb_client.get_cc_hosts()
        # filter node list
        host_list = self.filter_node(host_list, data['ip_list'])
        self.cc_application_name = cmdb_client.get_cc_application_name()
        # get host list, return as soon as possible when empty
        if not host_list:
            return response.Response({
                'results': [],
                'cc_application_name': self.cc_application_name
            })
        # get resource from bcs cc
        project_cluster_resource = self.get_project_cluster_resource(request)
        exist_node_info = self.get_all_nodes(request, project_id)
        # add node use status, in order to display for frontend
        host_list = self.render_node_with_use_status(
            host_list, exist_node_info, project_cluster_resource)
        # paginator the host list
        pagination_data = custom_paginator(host_list, data['offset'], limit=data['limit'])
        # for frontend display
        cc_host_map = self.get_cc_host_mappings(pagination_data['results'])
        gse_host_status = gse.GSEClient.get_agent_status(request, cc_host_map.values())
        # compose the host list with gse status and host status
        self.update_agent_status(cc_host_map, gse_host_status)

        return response.Response({
            'results': list(cc_host_map.values()),
            'count': pagination_data['count'],
            'cc_application_name': self.cc_application_name
        })