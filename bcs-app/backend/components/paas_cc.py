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
import json
import logging
from django.conf import settings

from backend.components.utils import http_get, http_post, http_put, http_patch, http_delete
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.apps import constants
from backend.apps.cluster.models import CommonStatus

logger = logging.getLogger(__name__)

CC_HOST = settings.BCS_CC_HOST

DEFAULT_TIMEOUT = 20


def get_project(access_token, project_id):
    url = f'{CC_HOST}/projects/{project_id}/'
    params = {'access_token': access_token}
    project = http_get(url, params=params, timeout=20)
    return project


def get_projects(access_token):
    url = f'{CC_HOST}/projects/'
    params = {'access_token': access_token}
    project = http_get(url, params=params)
    return project


def update_project_new(access_token, project_id, data):
    """更新项目信息
    """
    url = f'{CC_HOST}/projects/{project_id}/'
    params = {"access_token": access_token}
    project = http_put(url, params=params, json=data)
    return project


def create_cluster(access_token, project_id, data):
    url = f'{CC_HOST}/projects/{project_id}/clusters/'
    # 判断环境
    env_name = data.get("environment")
    data["environment"] = settings.CLUSTER_ENV.get(env_name)
    params = {'access_token': access_token}
    return http_post(url, params=params, json=data)


def update_cluster(access_token, project_id, cluster_id, data):
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}'
    params = {'access_token': access_token}
    return http_put(url, params=params, json=data)


def get_cluster(access_token, project_id, cluster_id):
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}'
    params = {'access_token': access_token}
    return http_get(url, params=params)


def get_all_clusters(access_token, project_id, limit=None, offset=None, desire_all_data=0):
    url = f'{CC_HOST}/projects/{project_id}/clusters/'
    params = {'access_token': access_token}
    if limit:
        params['limit'] = limit
    if offset:
        params['offset'] = offset
    if desire_all_data:
        params['desire_all_data'] = desire_all_data
    return http_get(url, params=params)


def get_cluster_list(access_token, project_id, cluster_ids):
    url = f'{CC_HOST}/projects/{project_id}/clusters_list/'
    params = {'access_token': access_token}
    data = {'cluster_ids': cluster_ids} if cluster_ids else None
    return http_post(url, params=params, json=data)


def verify_cluster_exist(access_token, project_id, cluster_name):
    """校验cluster name是否存在
    """
    url = f'{CC_HOST}/projects/{project_id}/clusters/'
    params = {'name': cluster_name, 'access_token': access_token}
    return http_get(url, params=params)


def get_cluster_by_name(access_token, project_id, cluster_name):
    """get cluster info by cluster name
    """
    url = f'{CC_HOST}/projects/{project_id}/clusters/'
    params = {'name': cluster_name, 'access_token': access_token}
    return http_get(url, params=params)


def get_cluster_snapshot(access_token, project_id, cluster_id):
    """ 获取集群快照
    """
    if getattr(settings, 'BCS_CC_CLUSTER_CONFIG', None):
        path = settings.BCS_CC_CLUSTER_CONFIG.format(cluster_id=cluster_id)
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/v1/clusters/{cluster_id}/cluster_config'
    params = {"access_token": access_token}
    return http_get(url, params=params)


def get_area_list(access_token, source=''):
    url = f'{CC_HOST}/areas/'
    params = {"access_token": access_token, "source": source}
    return http_get(url, params=params)


def get_area_info(access_token, area_id):
    """查询指定区域的信息
    """
    url = f'{CC_HOST}/areas/{area_id}/'
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token
        })
    }
    return http_get(url, headers=headers)


def get_master_node_list(access_token, project_id, cluster_id):
    if getattr(settings, 'BCS_CC_GET_CLUSTER_MASTERS', None):
        path = settings.BCS_CC_GET_CLUSTER_MASTERS.format(
            project_id=project_id, cluster_id=cluster_id)
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/masters/'
    params = {"access_token": access_token}
    return http_get(url, params=params)


def get_project_master_list(access_token, project_id):
    if getattr(settings, 'BCS_CC_GET_PROJECT_MASTERS', None):
        path = settings.BCS_CC_GET_PROJECT_MASTERS.format(project_id=project_id)
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/projects/{project_id}/masters/'
    params = {"access_token": access_token}
    return http_get(url, params=params)


def create_node(access_token, project_id, cluster_id, data):
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/nodes/'
    params = {"access_token": access_token}
    return http_patch(url, params=params, json=data)


def get_node_list(access_token, project_id, cluster_id, params=()):
    if getattr(settings, 'BCS_CC_GET_PROJECT_NODES', None):
        path = settings.BCS_CC_GET_PROJECT_NODES.format(project_id=project_id)
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/projects/{project_id}/nodes/'
    params = dict(params)
    params.update({"access_token": access_token, "cluster_id": cluster_id})
    return http_get(url, params=params)


def get_node(access_token, project_id, node_id, cluster_id=""):
    if getattr(settings, 'BCS_CC_OPER_PROJECT_NODE', None):
        path = settings.BCS_CC_OPER_PROJECT_NODE.format(
            project_id=project_id, node_id=node_id)
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/projects/{project_id}/nodes/{node_id}/'
    params = {"access_token": access_token, "cluster_id": cluster_id}
    return http_get(url, params=params)


def update_node(access_token, project_id, node_id, data):
    if getattr(settings, 'BCS_CC_OPER_PROJECT_NODE', None):
        path = settings.BCS_CC_OPER_PROJECT_NODE.format(
            project_id=project_id, node_id=node_id)
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/projects/{project_id}/nodes/{node_id}/'
    params = {"access_token": access_token}
    return http_put(url, params=params, json=data)


def update_node_list(access_token, project_id, cluster_id, data):
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/nodes/'
    params = {"access_token": access_token}
    req_data = {
        "updates": data
    }
    return http_patch(url, params=params, json=req_data)


def get_cluster_history_data(access_token, project_id, cluster_id, metric, start_at, end_at):
    """获取集群概览历史数据
    """
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/history_data/'
    params = {'access_token': access_token,
              'start_at': start_at, 'end_at': end_at, 'metric': metric}
    return http_get(url, params=params)


def get_all_masters(access_token):
    """获取配置中心所有Master
    """
    url = f'{CC_HOST}/v1/masters/all_master_list/'
    params = {"desire_all_data": 1}
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({"access_token": access_token})
    }
    return http_get(url, params=params, headers=headers)


def get_all_nodes(access_token):
    """获取配置中心所有Node
    """
    url = f'{CC_HOST}/v1/nodes/all_node_list/'
    params = {"desire_all_data": 1}
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({"access_token": access_token})
    }
    return http_get(url, params=params, headers=headers)


def get_project_all_nodes(access_token, project_id):
    node_list_info = get_all_nodes(access_token)
    if node_list_info.get('code') != ErrorCode.NoError:
        raise error_codes.APIError.f("查询项目下node节点失败，已经通知管理员，请稍后!")
    else:
        data = node_list_info.get('data') or []
    master_list_info = get_all_masters(access_token)
    if master_list_info.get('code') != ErrorCode.NoError:
        raise error_codes.APIError.f("查询项目下master节点失败，已经通知管理员，请稍后!")
    data.extend(master_list_info.get('data') or [])
    return data


def get_project_nodes(access_token, project_id, is_master=False):
    """获取项目下已经添加的Master和Node
    """
    # add filter for master or node
    # node filter
    # filter_status = [CommonStatus.InitialCheckFailed, CommonStatus.InitialFailed, CommonStatus.Removed]
    # if is_master:
    filter_status = [CommonStatus.Removed]

    data = []
    # 获取Node
    node_list_info = get_all_nodes(access_token)
    if node_list_info["code"] == ErrorCode.NoError:
        if node_list_info.get("data", []):
            # 过滤掉removed和initial_failed
            data.extend(
                [
                    info
                    for info in node_list_info["data"]
                    if info.get("status") not in filter_status
                ]
            )
    else:
        raise error_codes.APIError.f(u"查询项目下node节点失败，已经通知管理员，请稍后!")
    # 获取master
    master_list_info = get_all_masters(access_token)
    if master_list_info["code"] == ErrorCode.NoError:
        if master_list_info.get("data", []):
            # 过滤掉removed和initial_failed
            data.extend(
                [
                    info
                    for info in master_list_info["data"]
                    if info.get("status") not in filter_status
                ]
            )
    else:
        raise error_codes.APIError.f("查询项目下master节点失败，已经通知管理员，请稍后!")
    return {
        info["inner_ip"]: True
        for info in data
    }


def get_namespace_list(access_token, project_id, with_lb=None, limit=None, offset=None, desire_all_data=None):
    """获取namespace列表
    """
    if getattr(settings, 'BCS_CC_OPER_PROJECT_NAMESPACES', None):
        path = settings.BCS_CC_OPER_PROJECT_NAMESPACES.format(project_id=project_id)
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/projects/{project_id}/namespaces/'
    params = {'access_token': access_token}
    if desire_all_data:
        params["desire_all_data"] = 1
    if limit:
        params['limit'] = limit
    if offset:
        params['offset'] = offset
    if with_lb:
        params['with_lb'] = with_lb
    return http_get(url, params=params)


def get_cluster_namespace_list(access_token, project_id, cluster_id,
                               with_lb=None, limit=None, offset=None, desire_all_data=None):
    """查询集群下命名空间的信息
    """
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/namespaces/'
    params = {"access_token": access_token}
    if desire_all_data:
        params["desire_all_data"] = 1
    if limit:
        params["limit"] = limit
    if offset:
        params["offset"] = offset
    if with_lb:
        params["with_lb"] = with_lb

    return http_get(url, params=params)


def create_namespace(access_token, project_id, cluster_id, name, description, creator,
                     env_type, has_image_secret=None):
    """创建namespace
    """
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/namespaces/'
    params = {'access_token': access_token}
    payload = {'name': name, 'description': description,
               'creator': creator, 'env_type': env_type}
    if has_image_secret is not None:
        payload['has_image_secret'] = has_image_secret
    return http_post(url, params=params, json=payload)


def get_namespace(access_token, project_id, namespace_id, with_lb=None):
    """获取单个namespace
    """
    if getattr(settings, 'BCS_CC_OPER_PROJECT_NAMESPACE', None):
        path = settings.BCS_CC_OPER_PROJECT_NAMESPACE.format(
            project_id=project_id, namespace_id=namespace_id)
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/projects/{project_id}/namespaces/{namespace_id}/'
    params = {'access_token': access_token}
    if with_lb:
        params['with_lb'] = with_lb
    return http_get(url, params=params)


def update_node_with_cluster(access_token, project_id, data):
    """批量更新节点所属集群及状态
    """
    url = '{host}/projects/{project_id}/nodes/'.format(
        host=CC_HOST, project_id=project_id
    )

    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token
        })
    }
    return http_put(url, json=data, headers=headers)


def get_zk_config(access_token, project_id, cluster_id, environment=None):
    if not environment:
        cluster = get_cluster(access_token, project_id, cluster_id)
        if cluster.get('code') != 0:
            raise error_codes.APIError(cluster.get('message'))
        environment = cluster['data']['environment']

    url = f'{CC_HOST}/zk_config/'
    params = {'access_token': access_token, 'environment': environment}
    zk_config = http_get(url, params=params, timeout=20)
    return zk_config


def get_jfrog_domain(access_token, project_id, cluster_id):
    """
    """
    url = f'{CC_HOST}/clusters/{cluster_id}/related/areas/info/'
    params = {"access_token": access_token}
    res = http_get(url, params=params)
    jfrog_registry = ''
    if res.get('code') == ErrorCode.NoError:
        data = res.get('data') or {}
        configuration = data.get('configuration') or {}
        # jfrog_registry = configuration.get('httpsJfrogRegistry')
        env_type = data.get('env_type')
        # 按集群环境获取仓库地址
        if env_type == "prod":
            jfrog_registry = configuration.get('httpsJfrogRegistry')
        else:
            jfrog_registry = configuration.get('testHttpsJfrogRegistry')
    else:
        logger.error(u"get jfrog domain error:%s\nurl:%s",
                     res.get('message'), url)
    return jfrog_registry


def get_jfrog_domain_list(access_token, project_id, cluster_id):
    url = f'{CC_HOST}/clusters/{cluster_id}/related/areas/info/'
    params = {"access_token": access_token}
    res = http_get(url, params=params)
    if res.get('code') != ErrorCode.NoError:
        logger.error(u"get jfrog domain error:%s\nurl:%s",
                     res.get('message'), url)
        return []
    data = res.get('data') or {}
    configuration = data.get('configuration') or {}
    domain_list = []
    for key in ['httpsJfrogRegistry', 'testHttpsJfrogRegistry']:
        if configuration.get(key):
            domain_list.append(configuration.get(key))
    return domain_list


def get_auth_project(access_token):
    """获取当前用户下有权限的项目
    """
    url = f'{CC_HOST}/auth_projects/'
    params = {"access_token": access_token, "filter_offlined": False}
    project = http_get(url, params=params)
    return project


def delete_cluster(access_token, project_id, cluster_id):
    """删除集群
    """
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/'
    params = {"access_token": access_token}
    return http_delete(url, params=params)


def delete_cluster_namespace(access_token, project_id, cluster_id):
    """删除集群下的命名空间
    """
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/batch_delete_namespaces/'
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token,
            "project_id": project_id
        })
    }
    return http_delete(url, headers=headers)


def get_base_cluster_config(access_token, project_id, params):
    """获取集群基本配置
    """
    if getattr(settings, 'BCS_CC_CLUSTER_CONFIG', None):
        path = settings.BCS_CC_CLUSTER_CONFIG.format(cluster_id='null')
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/v1/clusters/version_config/'
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token,
            "project_id": project_id
        })
    }
    return http_get(url, params=params, headers=headers)


def save_cluster_snapshot(access_token, data):
    """存储集群快照
    """
    if getattr(settings, 'BCS_CC_CLUSTER_CONFIG', None):
        path = settings.BCS_CC_CLUSTER_CONFIG.format(cluster_id=data['cluster_id'])
        url = f'{CC_HOST}{path}'
    else:
        url = f'{CC_HOST}/v1/clusters/{data["cluster_id"]}/cluster_config/'
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token,
            "project_id": data['project_id']
        })
    }
    return http_post(url, json=data, headers=headers)


def get_project_cluster_resource(access_token):
    """获取所有项目、集群信息
    """
    url = f'{CC_HOST}/v1/projects/resource/'
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token
        })
    }
    return http_get(url, headers=headers)


def update_master(access_token, project_id, cluster_id, data):
    """更新master信息
    """
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/masters/'
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token
        })
    }
    return http_put(url, json=data, headers=headers)


def delete_namespace(access_token, project_id, cluster_id, ns_id):
    url = f'{CC_HOST}/projects/{project_id}/clusters/{cluster_id}/namespaces/{ns_id}/'
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token
        })
    }
    return http_delete(url, headers=headers)


def get_cluster_versions(access_token, ver_id='', env='', kind=''):
    url = f'{CC_HOST}/v1/all/clusters/version_config/'
    headers = {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token
        })
    }
    params = {'ver_id': ver_id, 'environment': env, 'kind': kind}
    return http_get(url, params=params, headers=headers)