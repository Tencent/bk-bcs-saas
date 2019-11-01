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
import base64
import logging

from celery import shared_task

from backend.accounts import bcs_perm
from backend.components import paas_cc, paas_auth
from backend.apps.configuration.namespace import resources
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.apps.constants import ProjectKind
from backend.utils import FancyDict

logger = logging.getLogger(__name__)

# 后续可能使用，先只注释
# def get_username(access_token):
#     user = paas_auth.get_user_by_access_token(access_token)
#     username = user.get('user_id')
#     # TODO: 如果后续有轮训任务，查询不到具体用户，是否使用项目创建者
#     if not username:
#         return 'anonymous'
#     return username


# def get_project(access_token, project_id):
#     """获取project信息
#     单独通过接口获取的目的是因为，如果后续有主动轮训时，方便适配
#     """
#     resp = paas_cc.get_project(access_token, project_id)
#     if resp.get('code') != ErrorCode.NoError:
#         raise error_codes.APIError(f'get project error, {resp.get("message")}')
#     data = resp.get('data') or {}
#     if not data:
#         raise error_codes.APIError(f'get project error, not found project info')
#     return data


def get_namespaces_by_bcs(access_token, project_id, project_kind, cluster_id):
    ns_client = resources.Namespace(access_token, project_id, project_kind)
    return ns_client.list(cluster_id)


def get_cluster_namespace_map(access_token, project_id):
    """获取项目下命名空间
    因为项目确定了容器编排类型，并且为减少多次请求的耗时，
    直接查询项目下的命名空间信息
    """
    # return data format: {'cluster_id': {'ns_name': 'ns_id'}}
    resp = paas_cc.get_namespace_list(access_token, project_id, desire_all_data=1)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'get project namespace error, {resp.get("message")}')
    cluster_namespace_map = {}
    data = resp.get('data') or {}
    results = data.get('results') or []
    for info in results:
        cluster_id = info['cluster_id']
        if cluster_id in cluster_namespace_map:
            cluster_namespace_map[cluster_id][info['name']] = info['id']
        else:
            cluster_namespace_map[cluster_id] = {info['name']: info['id']}
    return cluster_namespace_map


def create_cc_namespace(access_token, project_id, cluster_id, namespace, creator):
    resp = paas_cc.create_namespace(
        access_token, project_id, cluster_id,
        namespace, None, creator, 'prod', True
    )
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'create namespace error, {resp.get("message")}')
    return resp['data']


def delete_cc_namespace(access_token, project_id, cluster_id, namespace_id):
    resp = paas_cc.delete_namespace(access_token, project_id, cluster_id, namespace_id)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f'delete namespace error, {resp.get("message")}')


def register_auth(request, project_id, cluster_id, ns_id, ns_name):
    perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES, cluster_id)
    perm.register(ns_id, ns_name)


def delete_auth(request, project_id, ns_id):
    perm = bcs_perm.Namespace(request, project_id, ns_id)
    perm.delete()


def compose_request(access_token, username):
    """组装request，以便于使用auth api时使用
    """
    return FancyDict({
        'user': FancyDict({
            'username': username,
            'token': FancyDict({
                'access_token': access_token
            })
        }),
    })


@shared_task
def create_ns_flow(access_token, project_id, project_code, project_kind, cluster_id, ns_list, creator):
    if not ns_list:
        return
    request = compose_request(access_token, creator)
    for ns_name in ns_list:
        ns_client = resources.Namespace(access_token, project_id, project_kind)
        ns_client.create_secret(project_code, cluster_id, ns_name)
        ns_info = create_cc_namespace(access_token, project_id, cluster_id, ns_name, creator)
        register_auth(request, project_id, cluster_id, ns_info['id'], ns_name)


@shared_task
def delete_ns_flow(access_token, project_id, project_kind, cluster_id, ns_id_map, ns_list, username):
    # 因为mesos下的命名空间在被实例化后的资源占用后，才能查询到数据, 所以针对mesos不考虑删除的问题
    if (project_kind == ProjectKind.MESOS.value) or (not ns_list):
        return
    request = compose_request(access_token, username)
    for ns_name in ns_list:
        ns_id = ns_id_map[ns_name]
        delete_auth(request, project_id, ns_id)
        delete_cc_namespace(access_token, project_id, cluster_id, ns_id)


@shared_task
def sync_namespace(access_token, project_id, project_code, project_kind, cluster_id_list, username):
    """
    1. search bcs namespaces, example A
    2. search cc namespaces, example B
    3. diff cc and bcs namespaces:
       - if (bcs - cc), create cc namespace, jfrog account, secret and register auth,
       - if (cc - bcs), delete cc namespace records when project is k8s
    """
    # TODO: 先不校验权限
    cc_cluster_namespace_map = get_cluster_namespace_map(access_token, project_id)
    for cluster_id in cluster_id_list:
        bcs_ns_list = get_namespaces_by_bcs(access_token, project_id, project_kind, cluster_id)
        ns_id_map = cc_cluster_namespace_map.get(cluster_id) or {}
        cc_ns_list = ns_id_map.keys()

        # 只在线上存在的命名空间，需要进行创建操作
        only_bcs_ns_list = list(set(bcs_ns_list) - set(cc_ns_list))
        # create cc namespace record, create secret and register auth
        create_ns_flow.delay(
            access_token, project_id, project_code, project_kind, cluster_id, only_bcs_ns_list, username
        )

        # 只在bcs cc上存在的命名空间，需要进行删除操作
        # NOTE: 删除只针对k8s，因为mesos的命名空间只有在实例化资源后，才会查询到
        only_cc_ns = list(set(cc_ns_list) - set(bcs_ns_list))
        # delete cc namespace record and delete auth, when project_kind is k8s
        delete_ns_flow.delay(
            access_token, project_id, project_kind, cluster_id, ns_id_map, only_cc_ns, username
        )