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
from typing import List

from django.conf import settings
from iam import IAM
from iam.apply import models

from .request import ActionResourcesRequest


class ApplyURLGenerator:
    iam = IAM(settings.APP_ID, settings.APP_TOKEN, settings.BK_IAM_HOST, settings.BK_PAAS_INNER_HOST)

    @classmethod
    def generate_apply_url(cls, username: str, action_request_list: List[ActionResourcesRequest]) -> str:
        """
        生成权限申请跳转 url
        参考 https://github.com/TencentBlueKing/iam-python-sdk/blob/master/docs/usage.md#14-获取无权限申请跳转url
        """
        app = cls._make_application(action_request_list)
        ok, message, url = cls.iam.get_apply_url(app, bk_username=username)
        if not ok:
            return settings.BK_IAM_APP_URL
        return url

    @staticmethod
    def _make_application(action_request_list: List[ActionResourcesRequest]) -> models.Application:
        """为 generate_apply_url 方法生成 models.Application"""
        actions = []

        for req in action_request_list:
            if req.resources:
                instances = [
                    models.ResourceInstance([models.ResourceNode(req.resource_type, res_id, res_id)])
                    for res_id in req.resources
                ]
                related_resource_type = models.RelatedResourceType(settings.APP_ID, req.resource_type, instances)
                action = models.ActionWithResources(req.action_id, [related_resource_type])
                actions.append(action)
            else:
                # 资源无关的 Application 构建
                action = models.ActionWithoutResources(req.action_id)
                actions.append(action)

        return models.Application(settings.APP_ID, actions=actions)
