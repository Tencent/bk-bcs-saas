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
from typing import Dict, List, Optional, Union

from django.conf import settings
from iam import IAM, OP, Action, MultiActionRequest, Request, Resource, Subject
from iam.api.client import Client
from iam.api.http import http_get
from iam.apply import models
from iam.exceptions import AuthAPIError


class IAMClient(Client):
    def list_subjects(self, data: Dict):
        """"""
        path = f"/api/v1/systems/{self._app_code}/policies/-/subjects"
        ok, message, subjects = self._call_iam_api(http_get, path, data)
        if not ok:
            raise AuthAPIError(message)
        return subjects

    def list_policies(self, data: Dict):
        """"""
        policies = []
        page, page_size = 1, 100
        data["page_size"] = page_size

        while True:
            data["page"] = page
            ok, message, p = self._list_policies(data)
            if not ok:
                raise AuthAPIError(message)

            policies.extend(p["results"])

            left_count = p["count"] - len(p["results"]) - (page - 1) * page_size
            if left_count <= 0:
                return policies

            page += 1

    def _list_policies(self, data: Dict):
        path = f"/api/v1/systems/{self._app_code}/policies"
        ok, message, data = self._call_iam_api(http_get, path, data)
        return ok, message, data


class BCSIAM(IAM):
    def __init__(self, app_code: str, app_secret: str, bk_iam_host: str, bk_paas_host: str):
        self._client = IAMClient(app_code, app_secret, bk_iam_host, bk_paas_host)

    def grant_resource_creator_action(
        self, bk_username: str, resource_type_id: str, resource_id: str, resource_name: str
    ):
        """
        用于创建资源时，注册用户 bk_username 对资源 resource_id 的关联操作权限.
        具体的关联操作见权限模型的 resource_creator_actions 字段
        """
        data = {
            "type": resource_type_id,
            "id": resource_id,
            "name": resource_name,
            "system": settings.APP_ID,
            "creator": bk_username,
        }
        return self._client.grant_resource_creator_actions(None, bk_username, data)

    # def do_policy_query(self, request) -> Optional[Dict]:
    #     # 1. validate
    #     if not isinstance(request, Request):
    #         raise AuthInvalidRequest("request should be instance of iam.auth.models.Request")
    #
    #     request.validate()
    #
    #     # 2. _client.policy_query
    #     policies = self._do_policy_query(request)
    #
    #     # the polices maybe none
    #     if not policies:
    #         return None
    #
    #     return policies
    #
    # def query_authorized_users(self, action_id, resource_type_id, resource_id):
    #     id_list = []
    #     policies = self._client.list_policies({"action_id": action_id})
    #     for p in policies:
    #         if self._match_resource_id(p["expression"], resource_type_id, resource_id):
    #             id_list.append(str(p["id"]))
    #     subjects = self._client.list_subjects({"ids": ",".join(id_list)}) if id_list else []
    #
    #     has_admin = False
    #     authorized_users = []
    #     for s in subjects:
    #         if s["subject"]["id"] == "admin":
    #             has_admin = True
    #         authorized_users.append({"id": s["subject"]["id"], "name": s["subject"]["name"]})
    #     # admin用户默认有所有权限，需要主动添加进列表中(list_subjects一般情况下没有admin)
    #     if not has_admin:
    #         authorized_users.append({"id": "admin", "name": "admin"})
    #
    #     return authorized_users
    #
    # def _match_resource_id(self, expression, resource_type_id, resource_id):
    #     if expression["op"] in [OP.AND, OP.OR]:
    #         return any([self._match_resource_id(exp, resource_type_id, resource_id) for exp in expression["content"]])
    #
    #     if expression["field"] != f"{resource_type_id}.id":
    #         return False
    #
    #     if expression["op"] == OP.IN:
    #         if resource_id in expression["value"]:
    #             return True
    #         return False
    #
    #     if expression["op"] == OP.EQ:
    #         if resource_id == expression["value"]:
    #             return True
    #         return False
    #
    #     if expression["op"] == OP.ANY:
    #         return True
    #     return False


class ResourceRequest:
    resource_type: str = ''
    attr: Optional[Dict] = None

    def __init__(self, res: Union[List[str], str], attr: Optional[Dict] = None, **attr_kwargs):
        """
        :param res: 单个资源 ID 或资源 ID 列表
        :param attr: 属性字典。如 {'_bk_iam_path_': f'/project,{{project_id}}/'}
        :param attr_kwargs: 用于替换 attr 中可能需要 format 的值
        """
        self.res = res
        if attr:
            self.attr = attr
        self.attr_kwargs = dict(**attr_kwargs)

    def make_resources(self) -> List[Resource]:
        if isinstance(self.res, str):
            return [Resource(settings.APP_ID, self.resource_type, self.res, self._make_attribute(self.res))]

        return [
            Resource(settings.APP_ID, self.resource_type, res_id, self._make_attribute(res_id)) for res_id in self.res
        ]

    def _make_attribute(self, resource_id: str) -> Dict:
        return {}


class Permission:
    """
    对接 IAM 的权限基类
    """

    iam = BCSIAM(settings.APP_ID, settings.APP_TOKEN, settings.BK_IAM_HOST, settings.BK_PAAS_INNER_HOST)

    def resource_type_allowed(self, username: str, action_id: str) -> bool:
        """
        判断用户是否具备某个操作的权限
        note: 权限判断与资源实例无关，如创建某资源
        """
        request = self._make_request(username, action_id)
        return self.iam.is_allowed(request)

    def resource_inst_allowed(self, username: str, action_id: str, res_request: ResourceRequest) -> bool:
        """
        判断用户对某个资源实例是否具有指定操作的权限
        note: 权限判断与资源实例有关，如更新某个具体资源

        :params res_maker: 单个资源
        """
        request = self._make_request(username, action_id, resources=res_request.make_resources())
        return self.iam.is_allowed(request)

    def resource_type_multi_actions_allowed(self, username: str, action_ids: List[str]) -> Dict[str, bool]:
        """
        判断用户是否具备多个操作的权限
        note: 权限判断与资源实例无关，如创建某资源

        :returns 示例 {'project_create': True}
        """
        return {action_id: self.resource_type_allowed(username, action_id) for action_id in action_ids}

    def resource_inst_multi_actions_allowed(
        self, username: str, action_ids: List[str], res_request: ResourceRequest
    ) -> Dict[str, bool]:
        """
        判断用户对某个资源实例是否具有多个操作的权限. 权限判断与资源实例有关，如更新某个具体资源
        :params res_maker: 多个资源
        :returns 示例 {'project_view': True, 'project_edit': False}
        """
        actions = [Action(action_id) for action_id in action_ids]
        request = MultiActionRequest(
            settings.APP_ID, Subject("user", username), actions, res_request.make_resources(), None
        )
        return self.iam.resource_multi_actions_allowed(request)

    def batch_resource_multi_actions_allowed(
        self, username: str, action_ids: List[str], res_request: ResourceRequest
    ) -> Dict[str, Dict[str, bool]]:
        """
        判断用户对某些资源是否具有某些操作的权限
        :returns 示例 {'0ad86c25363f4ef8adcb7ac67a483837': {'project_view': True, 'project_edit': False}}
        """
        actions = [Action(action_id) for action_id in action_ids]
        request = MultiActionRequest(settings.APP_ID, Subject("user", username), actions, [], None)
        return self.iam.batch_resource_multi_actions_allowed(request, res_request.make_resources())

    def generate_apply_url(self, username: str, action_id: str, resource_id=None):
        """生成权限申请跳转 url"""
        app = self._make_application(action_id, resource_id)
        ok, message, url = self.iam.get_apply_url(app, bk_username=username)
        if not ok:
            return settings.BK_IAM_APP_URL
        return url

    def _make_request(self, username: str, action_id: str, resources: Optional[List[Resource]] = None) -> Request:
        return Request(
            settings.APP_ID,
            Subject("user", username),
            Action(action_id),
            resources,
            None,
        )

    def _make_application(self):
        pass

    # def _make_application(self, action_id: str, resource_id: str) -> models.Application:
    #     if not resource_id:
    #         # 资源无关的 Application 构建
    #         action = models.ActionWithoutResources(action_id)
    #         actions = [action]
    #         return models.Application(settings.APP_ID, actions)
    #
    #     instance = models.ResourceInstance([models.ResourceNode(self.resource_type, resource_id, resource_id)])
    #     related_resource_type = models.RelatedResourceType(settings.APP_ID, self.resource_type, [instance])
    #     action = models.ActionWithResources(action_id, [related_resource_type])
    #     return models.Application(settings.APP_ID, actions=[action])
