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
import copy
from typing import Dict, List, Optional, Set

from .data import paas_cc_json


class FakePaaSCCMod:
    """A fake object for replacing the real components.paas_cc module"""

    def get_project(self, access_token: str, project_id: str) -> Dict:
        resp_get_project_ok = dict(paas_cc_json.resp_get_project_ok)
        resp_get_project_ok['data']['project_id'] = project_id
        return self._resp(resp_get_project_ok)

    def get_projects(self, access_token: str, query_params: Optional[Dict]) -> Dict:
        resp = self._resp(paas_cc_json.resp_filter_projects_ok)

        if not query_params:
            return resp

        project_id_list = query_params['project_ids'].split(',')
        resp['data']['results'][0]['project_id'] = project_id_list[0]

        return resp

    def get_all_clusters(self, access_token, project_id, limit=None, offset=None, desire_all_data=0):
        resp = self._resp(paas_cc_json.resp_get_clusters_ok)
        for info in resp['data']['results']:
            info['project_id'] = project_id
        return resp

    def get_clusters(self, access_token, project_id: str) -> Dict:
        return self._filter_fake_clusters(project_id)

    def get_cluster_list(self, access_token, project_id: str, cluster_ids: List) -> Dict:
        return self._filter_fake_clusters(project_id, set(cluster_ids))

    def _filter_fake_clusters(self, project_id: str, cluster_ids: Optional[Set] = None) -> dict:
        """获取模拟集群数据，并根据cluster_id筛选"""
        resp = self._resp(paas_cc_json.resp_get_clusters_ok)
        results = []
        for info in resp['data']['results']:
            if not cluster_ids or (cluster_ids and info["cluster_id"] in cluster_ids):
                info["project_id"] = project_id
                results.append(info)
        resp["data"]["results"] = results
        return resp

    def get_namespace_list(
        self, access_token, project_id, with_lb=None, limit=None, offset=None, desire_all_data=None
    ):
        resp = self._resp(paas_cc_json.resp_get_namespaces_ok)
        for info in resp['data']['results']:
            info['project_id'] = project_id
        return resp

    def get_namespace(self, access_token, project_id, namespace_id):
        resp = self._resp(paas_cc_json.resp_get_namespace_ok)
        resp['data']['id'] = namespace_id
        resp['data']['project_id'] = project_id
        return resp

    def get_jfrog_domain(self, access_token, project_id, cluster_id):
        return ""

    def get_image_registry_list(self, access_token, cluster_id):
        return ["http://harbor-api.service.consul"]

    def _resp(self, data, **kwargs):
        _data = copy.deepcopy(data)
        _data.update(kwargs)
        return _data


class FakeProjectPermissionAllowAll:
    """A fake object which replace the original ProjectPermission, allows all operations"""

    def can_create(self, username, raise_exception=False):
        return True

    def can_view(self, username, project_id, raise_exception=False):
        return True

    def can_edit(self, username, project_id, raise_exception=False):
        return True

    def query_authorized_users(self, project_id, action_id):
        return []

    def grant_related_action_perms(self, username, project_id, project_name):
        return []

    def verify_project(self, access_token, project_id, user_id):
        return {"code": 0}
