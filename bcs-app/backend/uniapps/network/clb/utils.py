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
import re

from django.utils.translation import ugettext_lazy as _

from backend.accounts import bcs_perm
from backend.apps.constants import ProjectKind
from backend.components import paas_cc
from backend.components.bcs import mesos
from backend.components.clb import describe_clb, get_clb_regions
from backend.components.utils import http_get
from backend.uniapps.network.clb.constants import MESOS_CLB_NAMESPACE
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes

logger = logging.getLogger(__name__)


def get_deployments(access_token, project_id, project_kind, cluster_id, name=None):
    """查询deployment, 包含状态及对应的message"""
    if project_kind == ProjectKind.MESOS.value:
        namespace = MESOS_CLB_NAMESPACE
        client = mesos.MesosClient(access_token, project_id, cluster_id, None)
        resp = client.get_deployment_with_post(
            name=name, namespace=namespace, field='data.metadata.name,data.status,data.message'
        )
        if resp.get('code') != ErrorCode.NoError:
            return {}
            # raise error_codes.APIError(f'get deployment status error, {resp.get("message")}')
        data = resp.get('data') or []
        deployment_dict = {}
        for info in data:
            info_data = info.get('data') or {}
            metadata = info_data.get('metadata') or {}
            deployment_dict[(cluster_id, metadata.get('name'))] = {
                'clb_status': info_data.get('status'),
                'clb_message': info_data.get('message'),
            }
        return deployment_dict
    else:
        pass


def describe_clb_detail(access_token, username, cc_app_id, region):
    data = describe_clb(access_token, username, cc_app_id, region)
    clb_dict = {}
    for info in data:
        clb_dict[info['clbName']] = {'clb_id': info['clbId'], 'vpc_id': info['vpcId'], 'subnet_id': info['subnetId']}
    return clb_dict


def create_mesos_deployment(access_token, project_id, cluster_id, namespace, mesos_json):
    client = mesos.MesosClient(access_token, project_id, cluster_id, None)
    resp = client.create_deployment(namespace, mesos_json)
    if (resp.get('code') != ErrorCode.NoError) and ('already exist' not in resp.get('message', '')):
        raise error_codes.APIError(f'create mesos deployment error, {resp.get("message")}')


def delete_mesos_deployment(access_token, project_id, cluster_id, namespace, name):
    client = mesos.MesosClient(access_token, project_id, cluster_id, None)
    resp = client.delete_deployment(namespace, name)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'delete mesos deployment error, {resp.get("message")}')


def get_project_clusters(access_token, project_id):
    resp = paas_cc.get_all_clusters(access_token, project_id, desire_all_data=1)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'get project cluster error, {resp.get("message")}')
    data = resp.get('data') or {}
    return data.get('results') or []


def get_cluster_name(access_token, project_id, cluster_id):
    resp = paas_cc.get_cluster(access_token, project_id, cluster_id)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'get cluster detail error, {resp.get("message")}')
    data = resp.get('data') or {}
    return data.get('name')


def get_cluster_id_names_map(access_token, project_id):
    resp = paas_cc.get_all_clusters(access_token, project_id, desire_all_data=1)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'get project cluster error, {resp.get("message")}')
    data = resp.get('data') or {}
    results = data.get('results') or []
    return {info['cluster_id']: info['name'] for info in results if info}


def can_use_cluster(request, project_id, cluster_id):
    perm_client = bcs_perm.Cluster(request, project_id, cluster_id)
    return perm_client.can_use(raise_exception=False)


def get_taskgroup_ip(request, project_id, cluster_id, name, namespace):
    client = mesos.MesosClient(request.user.token.access_token, project_id, cluster_id, None)
    resp = client.get_mesos_app_taskgroup(app_name=name, namespace=namespace, field='data.podIP')
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(_("获取mesos taskgroup出现异常，{}").format(resp.get("message")))
    data = resp.get('data') or []
    if not data:
        raise error_codes.APIError(_("taskgroup返回数据为空"))
    data = data[-1].get('data') or {}
    pod_ip = data.get('podIP')
    if not pod_ip:
        raise error_codes.APIError(_("查询pod ip为空"))
    return pod_ip


def request_clb_status(request, project_id, record):
    pod_ip = get_taskgroup_ip(request, project_id, record['cluster_id'], record['resource_name'], record['namespace'])
    resp = http_get(f"http://{pod_ip}:{record['metric_port']}/status")
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(_("查询clb状态出现异常，{}").format(resp.get("message")))
    return resp.get('data') or {}


def get_clb_region_list(access_token):
    data = get_clb_regions(access_token)
    region_list = []
    for regions in data.values():
        for info in regions:
            region_name = re.findall(r'[(](.*?)[)]', info.get("regionName", ""))
            if not region_name:
                continue
            region_list.append({"region": info["region"], "region_name": region_name[-1]})

    return region_list
