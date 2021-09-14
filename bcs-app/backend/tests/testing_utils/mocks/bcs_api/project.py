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
from typing import Dict

from backend.components.bcs_api.constants import RECORD_NOT_EXIST_CODE


class StubBcsProjectApiClient:
    """使用假数据的 BCS project Api client 对象"""

    def __init__(self, *args, **kwargs):
        pass

    def create_project(self, *args, **kwargs) -> Dict:
        return {"code": 0, "data": self.make_project_data()}

    def query_project(self, project_id) -> Dict:
        return self.make_project_data()

    def update_project(self, *args, **kwargs) -> Dict:
        return {"code": 0, "data": self.make_project_data()}

    def update_project_not_exist(self, *args, **kwargs) -> Dict:
        return {"code": RECORD_NOT_EXIST_CODE}

    @staticmethod
    def make_project_data() -> Dict:
        return {
            "projectID": "string",
            "name": "string",
            "englishName": "string",
            "creator": "string",
            "updater": "string",
            "projectType": 0,
            "useBKRes": True,
            "description": "string",
            "isOffline": True,
            "kind": "string",
            "businessID": "string",
            "deployType": 0,
            "bgID": "string",
            "bgName": "string",
            "deptID": "string",
            "deptName": "string",
            "centerID": "string",
            "centerName": "string",
            "isSecret": True,
            "credentials": {
                "additionalProp1": {"key": "string", "secret": "string"},
                "additionalProp2": {"key": "string", "secret": "string"},
                "additionalProp3": {"key": "string", "secret": "string"},
            },
            "createTime": "string",
            "updateTime": "string",
        }
