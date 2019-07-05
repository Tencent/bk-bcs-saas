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
from backend.components import paas_cc
from backend.utils.error_codes import error_codes
from backend.utils.errcodes import ErrorCode


def get_project_cluster_info(access_token, project_id):
    """get all cluster from project
    """
    project_cluster = paas_cc.get_all_clusters(access_token, project_id, desire_all_data=1)
    if project_cluster.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(project_cluster.get('message'))
    return project_cluster.get('data') or {}


def get_cluster_id_map(access_token, project_id):
    """get cluster id map
    format: cluster_id: {'cluster_name': cluster1, 'cluster_env_num': 1, 'cluster_env': 'test' ...}
    """
    # NOTE: 未完成
    project_cluster_info = get_project_cluster_info(access_token, project_id)
    cluster_results = project_cluster_info.get('results') or []
    return {
        info['cluster_id']: {
            'cluster_name': info['name']
        }
        for info in cluster_results
    }


def get_project_namespaces(access_token, project_id):
    """get all namespace from project
    """
    ns_resp = paas_cc.get_namespace_list(access_token, project_id, desire_all_data=True)
    if ns_resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(ns_resp.get('message'))
    data = ns_resp.get('data') or {}
    return data.get('results') or []
