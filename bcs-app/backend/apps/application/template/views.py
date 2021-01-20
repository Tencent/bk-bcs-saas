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
"""
TODO: 模板相关的展示查询
"""
from backend.apps.application import constants
from backend.apps.application.base.base import BaseAPI, BaseMetric
from backend.apps.application.template import k8s_views, mesos_views
from backend.apps.application.utils import APIResponse


class TemplateSet(BaseAPI, BaseMetric):
    def tmpl_set(self, project_id, tmpl_set_id):
        """获取所有模板集"""
        all_tmpl_set = self.get_filter_tmpl_set(project_id, tmpl_set_id)
        all_tmpl_set_list = all_tmpl_set.values("id", "name")
        return all_tmpl_set_list

    def get_template(self, project_kind, tmpl_set_id_list, category):
        """获取模板集对应的模板"""
        if project_kind == constants.K8S_KIND:
            k8s_tmpl_client = k8s_views.K8STemplateSet()
            return k8s_tmpl_client.get_template(tmpl_set_id_list, category)
        else:
            pass

    def get(self, request, project_id):
        cluster_type, app_status, tmpl_set_id, app_id, ns_id = self.get_filter_params(request, project_id)
        project_kind = self.project_kind(request)
        # 获取模板集
        all_tmpl_set_list = self.get_filter_tmpl_set(project_id, tmpl_set_id)
        # 获取实例名称
        app_name = self.get_inst_name(app_id)
        # 获取模板
        category = self.get_request_category(request, project_kind)
        tmpl_info, newest_version_tmpl = self.get_template(project_kind, all_tmpl_set_list, category)
        print(app_name, tmpl_info, newest_version_tmpl)

        return APIResponse({"data": {}})
