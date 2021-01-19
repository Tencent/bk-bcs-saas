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
from backend.apps import constants
from backend.components import paas_cc
from backend.components.bcs import k8s, mesos
from backend.resources.cluster.constants import ClusterCOES
from backend.utils.errcodes import ErrorCode
from backend.utils.exceptions import APIError


def k8s_containers(request, project_id, cluster_id, host_ips):
    """k8s pod容器信息"""
    client = k8s.K8SClient(request.user.token.access_token, project_id, cluster_id, None)
    rsp = client.get_pod(host_ips, field="data.status.containerStatuses.containerID,data.status.hostIP")
    if rsp.get("code") != ErrorCode.NoError:
        return {}
    containers = {}
    for info in rsp["data"]:
        containers.setdefault(info["data"]["status"]["hostIP"], 0)
        containers[info["data"]["status"]["hostIP"]] += len(info["data"]["status"]["containerStatuses"])
    return containers


def mesos_containers(request, project_id, cluster_id, host_ips):
    """mesos taskgroup容器信息"""
    client = mesos.MesosClient(request.user.token.access_token, project_id, cluster_id, None)
    rsp = client.get_taskgroup(
        host_ips,
        fields="data.containerStatuses.containerID,data.hostIP",
    )
    if rsp.get("code") != ErrorCode.NoError:
        return {}
    containers = {}
    for info in rsp['data']:
        containers.setdefault(info.get("data", {}).get('hostIP'), 0)
        containers[info["data"]['hostIP']] += len(info["data"]["containerStatuses"])

    return containers


def get_node_metric(request, access_token, project_id, cluster_id, cluster_type):
    node = paas_cc.get_node_list(access_token, project_id, cluster_id, params={"limit": 10000})
    if node.get('code') != 0:
        raise APIError(node.get('message'))
    # 过滤掉状态为removed的机器
    node_data = [
        info
        for info in node.get("data", {}).get("results") or []
        if info.get("status") not in [constants.NodeStatus.REMOVED.value]
    ]
    # 重新组装数据
    node = {
        "count": len(node_data),
        "results": node_data,
    }
    node_total = node['count']
    node_actived = 0
    node_disabled = 0

    if cluster_type != ClusterCOES.MESOS.value:
        # namespace 获取处理
        client = k8s.K8SClient(access_token, project_id, cluster_id=cluster_id, env=None)
        namespace = client.get_namespace()
        if not namespace.get('result'):
            raise APIError(namespace.get('message'))

        # 节点状态处理 计算k8s有容器的节点
        if node_total > 0:
            node_ips = [i['inner_ip'] for i in node['results']]
            containers = k8s_containers(request, project_id, cluster_id, node_ips)
            for node in node_ips:
                if containers.get(node, 0) > 0:
                    node_actived += 1

    else:
        # 节点状态处理 计算mesos有容器的节点
        if node_total > 0:
            node_ips = [i['inner_ip'] for i in node['results']]
            containers = mesos_containers(request, project_id, cluster_id, node_ips)
            for node in node_ips:
                if containers.get(node, 0) > 0:
                    node_actived += 1

    node_disabled = node_total - node_actived
    data = {'total': node_total, 'actived': node_actived, 'disabled': node_disabled}
    return data
