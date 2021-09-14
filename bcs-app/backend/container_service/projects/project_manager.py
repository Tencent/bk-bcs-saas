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
from typing import Dict

from backend.components import base as comp_base
from backend.components import paas_cc
from backend.components.bcs_api import constants, project
from backend.utils.error_codes import error_codes

from .base.constants import ProjectKindName

logger = logging.getLogger(__name__)


def create_project(access_token: str, project_config: project.ProjectConfig) -> Dict:
    """创建cluster manager中项目信息"""
    try:
        client = project.BcsProjectApiClient(comp_base.ComponentAuth(access_token))
        resp = client.create_project(project_config)
    except Exception as e:
        raise error_codes.APIError(f"create clustermanager project error, {e}")
    return resp


def update_project(access_token: str, project_config: project.UpdatedProjectConfig) -> Dict:
    """更新cluster manager中项目信息"""
    try:
        client = project.BcsProjectApiClient(comp_base.ComponentAuth(access_token))
        resp = client.update_project(project_config)
    except Exception as e:
        raise error_codes.APIError(f"update clustermanager project error, {e}")
    return resp


def update_or_create_project(access_token: str, project_id: str, data: Dict) -> Dict:
    """创建cluster manager所属的项目信息
    NOTE: 当调用接口出现异常后，现阶段不抛出异常；待下线bcs cc模块时，调整为必选步骤
    """
    # TODO: bcs cc服务下掉后，删除对应的接口
    bcs_cc_client = paas_cc.PaaSCCClient(comp_base.ComponentAuth(access_token))
    project_data = bcs_cc_client.update_project(project_id, data)

    updated_project_config = project.UpdatedProjectConfig(
        projectID=project_id,
        updater=data["updator"],
        name=project_data["project_name"],
        kind=ProjectKindName,
        businessID=project_data["cc_app_id"],
    )
    # 更新项目信息
    try:
        resp = update_project(access_token, updated_project_config)
    except Exception as e:
        logger.error("update clustermanager project failed, %s", e)
        return project_data
    # 根据code判断项目是否存在，当项目不存在时，调用创建项目接口
    if resp.get("code") == constants.RECORD_NOT_EXIST_CODE:
        # 组装写入cluster manager的数据
        reserved_config = project.ProjectReservedConfig(
            bgID=project_data["bg_id"],
            bgName=project_data["bg_name"],
            deptName=project_data["dept_name"],
            deptID=project_data["dept_id"],
            centerID=project_data["center_id"],
            centerName=project_data["center_name"],
            isSecret=project_data["is_secrecy"],
            isOffline=project_data["is_offlined"],
            useBKRes=project_data["use_bk"],
            projectType=project_data["project_type"],
        )
        basic_config = project.ProjectBasicConfig(
            projectID=project_id,
            name=project_data["project_name"],
            englishName=project_data["english_name"],
            kind="k8s",
            businessID=project_data["cc_app_id"],
            description=project_data["description"],
        )
        project_config = project.ProjectConfig(
            creator=project_data["creator"], basic_config=basic_config, reserved_config=reserved_config
        )
        # 当提示项目不存在时，需要添加项目
        try:
            create_project(access_token, project_config)
        except Exception as e:
            logger.error("update or create clustermanager project failed, %s", e)

    return project_data
