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

from backend.apps.depot.api import create_project_path_by_api

logger = logging.getLogger(__name__)


def backend_create_depot_path(request, project_id, pre_cc_app_id):
    try:
        create_project_path_by_api(
            request.user.token.access_token, project_id, request.project.english_name
        )
    except Exception as err:
        logger.error("创建项目仓库路径失败，详细信息: %s" % err)


def start_project_task(request, project_id, data, pre_cc_app_id):
    backend_create_depot_path(request, project_id, pre_cc_app_id)
