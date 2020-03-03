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
from rest_framework import viewsets, response
from rest_framework.renderers import BrowsableAPIRenderer
from django.utils.translation import ugettext_lazy as _

from backend.components import paas_cc
from backend.utils.errcodes import ErrorCode
from backend.activity_log import client
from backend.apps.cluster.models import CommonStatus
from backend.utils.error_codes import error_codes
from backend.accounts.bcs_perm import Cluster
from backend.apps.cluster.models import ClusterInstallLog
from backend.apps.application import constants as app_constants
from backend.components import prometheus
from backend.apps.cluster.constants import ClusterStatusName
from backend.utils.basic import normalize_metric, normalize_datetime
from backend.apps.cluster import constants as cluster_constants
from backend.apps.cluster.utils import cluster_env_transfer, status_transfer
from backend.utils.renderers import BKAPIRenderer
from backend.apps.cluster import serializers as cluster_serializers
from backend.apps.cluster.views_bk import cluster
from backend.apps.cluster.views_bk.tools import cmdb

DEFAULT_OPER_USER = settings.DEFAULT_OPER_USER

logger = logging.getLogger(__name__)


class ClusterBase:

    def get_cluster(self, request, project_id, cluster_id):
        """get cluster info
        """
        cluster_resp = paas_cc.get_cluster(
            request.user.token.access_token, project_id, cluster_id)
        if cluster_resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIErrorf(cluster_resp.get('message'))
        cluster_data = cluster_resp.get('data') or {}
        return cluster_data

    def get_cluster_node(self, request, project_id, cluster_id):
        """get cluster node list
        """
        cluster_node_resp = paas_cc.get_node_list(
            request.user.token.access_token, project_id, cluster_id,
            params={'limit': cluster_constants.DEFAULT_NODE_LIMIT}
        )
        if cluster_node_resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(cluster_node_resp.get('message'))
        data = cluster_node_resp.get('data') or {}
        return data.get('results') or []


class ClusterPermBase:

    def can_view_cluster(self, request, project_id, cluster_id):
        perm = Cluster(request, project_id, cluster_id)
        perm.can_view(raise_exception=True)


class ClusterCreateListViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def cluster_has_node(self, request, project_id):
        """cluster has node
        format: {cluster_id: True/False}
        """
        cluster_node_resp = paas_cc.get_node_list(
            request.user.token.access_token, project_id, None,
            params={'limit': cluster_constants.DEFAULT_NODE_LIMIT}
        )
        data = cluster_node_resp.get('data') or {}
        results = data.get('results') or []
        # compose the map for cluste and node
        return {
            info['cluster_id']: True
            for info in results
            if info['status'] not in cluster_constants.FILTER_NODE_STATUS
        }

    def get_cluster_list(self, request, project_id):
        cluster_resp = paas_cc.get_all_clusters(
            request.user.token.access_token, project_id, desire_all_data=1
        )
        if cluster_resp.get('code') != ErrorCode.NoError:
            logger.error('get cluster error, %s', cluster_resp)
            return {}
        return cluster_resp.get('data') or {}

    def get_cluster_create_perm(self, request, project_id):
        test_cluster_perm = Cluster(
            request, project_id, cluster_constants.NO_RES, resource_type="cluster_test"
        )
        can_create_test = test_cluster_perm.can_create(raise_exception=False)
        prod_cluster_perm = Cluster(
            request, project_id, cluster_constants.NO_RES, resource_type="cluster_prod"
        )
        can_create_prod = prod_cluster_perm.can_create(raise_exception=False)
        return can_create_test, can_create_prod

    def list(self, request, project_id):
        """get project cluster list
        """
        cluster_info = self.get_cluster_list(request, project_id)
        cluster_data = cluster_info.get('results') or []
        cluster_node_map = self.cluster_has_node(request, project_id)
        # add allow delete perm
        for info in cluster_data:
            info['environment'] = cluster_env_transfer(info['environment'])
            # allow delete cluster
            allow_delete = False if cluster_node_map.get(info['cluster_id']) else True
            info['allow'] = info['allow_delete'] = allow_delete
        perm_can_use = True if request.GET.get('perm_can_use') == '1' else False

        cluster_results = Cluster.hook_perms(
            request, project_id, cluster_data, filter_use=perm_can_use)
        # add disk resource
        try:
            cluster_results = prometheus.fixed_disk_usage(cluster_results)
        except Exception as err:
            logger.error('request prometheus err, detail: %s', err)
        # add can create cluster perm for prod/test
        can_create_test, can_create_prod = self.get_cluster_create_perm(request, project_id)

        return response.Response({
            'code': ErrorCode.NoError,
            'data': {'count': len(cluster_results), 'results': cluster_results},
            'permissions': {
                'test': can_create_test,
                'prod': can_create_prod,
                'create': can_create_test or can_create_prod
            }
        })

    def list_clusters(self, request, project_id):
        cluster_info = self.get_cluster_list(request, project_id)
        cluster_data = cluster_info.get('results') or []
        return response.Response({'clusters': cluster_data})

    def create(self, request, project_id):
        """create cluster
        """
        cluster_client = cluster.CreateCluster(request, project_id)
        return cluster_client.create()


class ClusterCheckDeleteViewSet(ClusterBase, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def check_cluster(self, request, project_id, cluster_id):
        """检查集群是否允许删除
        - 检查集群的状态是创建失败的
        - 集群下没有node节点
        """
        cluster_node_list = self.get_cluster_node(request, project_id, cluster_id)
        allow = False if len(cluster_node_list) else True
        return response.Response({"allow": allow})

    def delete(self, request, project_id, cluster_id):
        """删除项目下集群
        """
        cluster_client = cluster.DeleteCluster(request, project_id, cluster_id)
        return cluster_client.delete()


class ClusterFilterViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get(self, request, project_id):
        """check cluster name exist
        """
        name = request.GET.get("name")
        cluster_resp = paas_cc.get_cluster_by_name(
            request.user.token.access_token, project_id, name
        )
        if cluster_resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(cluster_resp.get('message'))
        data = cluster_resp.get('data') or {}
        return response.Response({
            'is_exist': True if data.get('count') else False
        })


class ClusterCreateGetUpdateViewSet(ClusterBase, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def retrieve(self, request, project_id, cluster_id):
        cluster_data = self.get_cluster(request, project_id, cluster_id)

        cluster_data['environment'] = cluster_env_transfer(cluster_data['environment'])
        return response.Response({
            "code": ErrorCode.NoError,
            "data": cluster_data
        })

    def reinstall(self, request, project_id, cluster_id):
        cluster_client = cluster.ReinstallCluster(request, project_id, cluster_id)
        return cluster_client.reinstall()

    def get_params(self, request):
        slz = cluster_serializers.UpdateClusterSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        return dict(slz.validated_data)

    def update_cluster(self, request, project_id, cluster_id, data):
        result = paas_cc.update_cluster(
            request.user.token.access_token, project_id, cluster_id, data
        )
        if result.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(result.get('message'))
        return result.get('data') or {}

    def update_data(self, data, project_id, cluster_id, cluster_perm):
        if data['cluster_type'] == 'public':
            data['related_projects'] = [project_id]
            cluster_perm.register(cluster_id, "公共集群", "prod")
        elif data.get('name'):
            cluster_perm.update_cluster(cluster_id, data['name'])
        return data

    def update(self, request, project_id, cluster_id):
        cluster_perm = Cluster(request, project_id, cluster_id)
        cluster_perm.can_edit(raise_exception=True)
        data = self.get_params(request)
        data = self.update_data(data, project_id, cluster_id, cluster_perm)
        # update cluster info
        with client.ContextActivityLogClient(
                project_id=project_id,
                user=request.user.username,
                resource_type='cluster',
                resource_id=cluster_id,
        ).log_modify():
            cluster_info = self.update_cluster(
                request, project_id, cluster_id, data
            )
        # render environment for frontend
        cluster_info["environment"] = cluster_env_transfer(cluster_info["environment"])

        return response.Response(cluster_info)


class ClusterInstallLogView(ClusterBase, viewsets.ModelViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)
    queryset = ClusterInstallLog.objects.all()

    def get_queryset(self, project_id, cluster_id):
        return super().get_queryset().filter(
            project_id=project_id, cluster_id=cluster_id
        ).order_by("-create_at")

    def get_display_status(self, curr_status):
        return status_transfer(
            curr_status,
            cluster_constants.CLUSTER_RUNNING_STATUS,
            cluster_constants.CLUSTER_FAILED_STATUS
        )

    def get_log_data(self, logs, project_id, cluster_id):
        if not logs:
            return {'status': 'none'}
        data = {
            'project_id': project_id,
            'cluster_id': cluster_id,
            'status': self.get_display_status(logs[0].status),
            'log': []
        }
        for info in logs:
            data['task_url'] = info.log_params.get('task_url') or ''
            info.status = self.get_display_status(info.status)
            slz = cluster_serializers.ClusterInstallLogSLZ(instance=info)
            data['log'].append(slz.data)
        return data

    def can_view_cluster(self, request, project_id, cluster_id):
        """has view cluster perm
        """
        # when cluster exist, check view perm
        try:
            self.get_cluster(request, project_id, cluster_id)
        except Exception as err:
            logger.error('request cluster info, detial is %s', err)
            return
        cluster_perm = Cluster(request, project_id, cluster_id)
        cluster_perm.can_view(raise_exception=True)

    def get(self, request, project_id, cluster_id):
        # view perm
        self.can_view_cluster(request, project_id, cluster_id)
        # get log
        logs = self.get_queryset(project_id, cluster_id)
        data = self.get_log_data(logs, project_id, cluster_id)

        return response.Response(data)


class ClusterInfo(ClusterPermBase, ClusterBase, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_master_count(self, request, project_id, cluster_id):
        """获取集群master信息
        """
        master_info = paas_cc.get_master_node_list(request.user.token.access_token, project_id, cluster_id)
        if master_info.get("code") != ErrorCode.NoError:
            raise error_codes.APIError(master_info.get("message"))
        data = master_info.get("data") or {}
        return data.get('count') or 0

    def get_node_count(self, request, project_id, cluster_id):
        # get node count
        node_results = self.get_cluster_node(request, project_id, cluster_id)
        return len([info for info in node_results if info['status'] not in [CommonStatus.Removed]])

    def get_area(self, request, area_id):
        """get area info
        """
        area_info = paas_cc.get_area_info(request.user.token.access_token, area_id)
        if area_info.get('code') != ErrorCode.NoError:
            raise error_codes.APIError(area_info.get('message'))
        return area_info.get('data') or {}

    def cluster_info(self, request, project_id, cluster_id):
        # can view cluster
        self.can_view_cluster(request, project_id, cluster_id)
        cluster = self.get_cluster(request, project_id, cluster_id)
        cluster['cluster_name'] = cluster.get('name')
        cluster['created_at'] = normalize_datetime(cluster['created_at'])
        cluster['updated_at'] = normalize_datetime(cluster['updated_at'])
        status = cluster.get('status', 'normal')
        cluster['chinese_status_name'] = ClusterStatusName[status].value
        # get area info
        area_info = self.get_area(request, cluster.get('area_id'))
        cluster['area_name'] = _(area_info.get('chinese_name'))
        # get master count
        cluster['master_count'] = self.get_master_count(request, project_id, cluster_id)
        # get node count
        cluster['node_count'] = self.get_node_count(request, project_id, cluster_id)
        if request.project.kind == app_constants.MESOS_KIND:
            # mesos单位是MB，需要转换为GB
            total_mem = normalize_metric(cluster['total_mem'] / 1024)
        else:
            total_mem = normalize_metric(cluster['total_mem'])
        cluster['total_mem'] = total_mem

        return response.Response(cluster)


class ClusterMasterInfo(ClusterPermBase, viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def get_master_ips(self, request, project_id, cluster_id):
        """get master inner ip info
        """
        master_resp = paas_cc.get_master_node_list(request.user.token.access_token, project_id, cluster_id)
        if master_resp.get("code") != ErrorCode.NoError:
            raise error_codes.APIError(master_resp.get("message"))
        data = master_resp.get("data") or {}
        master_ip_info = data.get("results") or []
        return [info["inner_ip"] for info in master_ip_info if info.get("inner_ip")]

    def responseslz(self, info):
        return {
            'host_name': info.get('HostName'),
            'idc': info.get('IDCUnit'),
            'inner_ip': info.get('InnerIP'),
            'agent': 1,
            'device_class': info.get('DeviceClass'),
            'server_rack': info.get('serverRack')
        }

    def cluster_master_info(self, request, project_id, cluster_id):
        self.can_view_cluster(request, project_id, cluster_id)
        ip_only = request.query_params.get('ip_only')
        # get master ip
        master_ips = self.get_master_ips(request, project_id, cluster_id)
        if ip_only == 'true':
            return response.Response([{'inner_ip': ip} for ip in master_ips])
        # get cc hosts
        cc_host_info = cmdb.CMDBClient(request).get_cc_hosts()
        # compose the data
        ret_data = []
        for info in cc_host_info:
            # may be many eths
            ip_list = info.get('InnerIP', '').split(',')
            if not ip_list:
                continue
            for ip in ip_list:
                if ip in master_ips:
                    ret_data.append(self.responseslz(info))
                break
        return response.Response(ret_data)


class ClusterVersionViewSet(viewsets.ViewSet):
    renderer_classes = (BKAPIRenderer, BrowsableAPIRenderer)

    def versions(self, request, project_id):
        resp = paas_cc.get_cluster_versions(
            request.user.token.access_token, kind=cluster_constants.ClusterType[request.project.kind])
        if resp.get('code') != ErrorCode.NoError:
            data = []
        data = [info['version'] for info in resp.get('data') or []]

        return response.Response(data)
