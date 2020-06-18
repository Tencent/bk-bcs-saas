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
from backend.components import paas_cc, bcs
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes


def get_namespaces(access_token, project_id):
    resp = paas_cc.get_namespace_list(access_token, project_id, desire_all_data=True)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f"get namespace error, {resp.get('message')}")
    return resp.get('data', {}).get('results', [])


def get_namespace_by_id(access_token, project_id, namespace_id):
    resp = paas_cc.get_namespace(access_token, project_id, namespace_id)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f"get namespace error, {resp.get('message')}")
    return resp.get("data") or {}


def get_namespaces_by_cluster_id(access_token, project_id, cluster_id):
    resp = paas_cc.get_cluster_namespace_list(access_token, project_id, cluster_id, desire_all_data=True)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f"get namespace error, {resp.get('message')}")

    return resp.get('data', {}).get('results', [])


def get_k8s_realtime_namespaces(access_token, project_id, cluster_id):
    """获取集群中实时的namespace
    """
    client = bcs.k8s.K8SClient(access_token, project_id, cluster_id, env=None)
    resp = client.get_namespace()
    if resp.get("code") != ErrorCode.NoError:
        raise error_codes.APIError(f"get k8s namespace error, resp.get('message')")
    return resp.get("data") or []


def delete_cc_namespace(access_token, project_id, cluster_id, namespace_id):
    resp = paas_cc.delete_namespace(access_token, project_id, cluster_id, namespace_id)
    if resp.get("code") != ErrorCode.NoError:
        raise error_codes.APIError(f"delete namespace error, {resp.get('message')}")


def create_cc_namespace(access_token, project_id, cluster_id, namespace, creator):
    resp = paas_cc.create_namespace(
        access_token, project_id, cluster_id,
        namespace, None, creator, "prod", False
    )
    if resp.get("code") != ErrorCode.NoError:
        raise error_codes.APIError(f"create cc namespace error, {resp.get('message')}")
    return resp["data"]
