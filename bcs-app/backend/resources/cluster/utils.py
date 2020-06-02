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

from backend.components import paas_cc
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes


def get_clusters(access_token, project_id):
    resp = paas_cc.get_all_clusters(access_token, project_id, desire_all_data=True)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f"get clusters error, {resp.get('message')}")
    return resp.get('data', {}).get('results', [])


def get_cluster_versions(access_token, kind="", ver_id="", env=""):
    resp = paas_cc.get_cluster_versions(access_token, kind=kind, ver_id=ver_id, env=env)
    if resp.get('code') != ErrorCode.NoError:
        raise error_codes.APIError(f"get cluster version, {resp.get('message')}")
    data = resp.get("data") or []
    version_list = []
    for info in data:
        configure = json.loads(info.get("configure", ''))
        version_list.append({
            "version_id": info["version"],
            "version_name": configure.get("version_name") or info["version"]
        })
    return version_list
